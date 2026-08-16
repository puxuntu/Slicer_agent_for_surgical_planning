"""Prepare a DICOM case dataset: pick each case's diagnostic series, write NRRD.

One module for every dataset shaped like ``Test_data/<Name>/Original/<case>/``,
a flat folder of DICOM per case. Which datasets exist is a table
(:data:`DATASETS`) rather than a copy of this file per extension -- the
selection rule, the resume logic and the reader are the same question each
time, and two copies of them would answer it differently within a month.

**Which series to keep** is the only real decision, and the obvious reading of
"smallest spacing, most slices" gets it wrong on this data. A case typically
looks like:

    n=246  0.49 mm in-plane  1.0 mm thick   "1.0 x 1.0"      <- keep
    n=245  0.49 mm in-plane  1.0 mm thick   "1.0 x 1.0"      <- keep (its pair)
    n= 82  0.49 mm in-plane  3.0 mm thick   "3.0 x 3.0"
    n= 61  0.47 mm in-plane  0.49 mm thick  "3D_Sinus"
    n= 21  0.16 mm in-plane  --             "3D_Default"     <- SMALLEST spacing

The 3D reformats have the finest in-plane spacing of anything in the case, so
ranking on spacing first selects a 21-slice reformat over the 246-slice scan.
Slice COUNT is therefore the primary key and spacing only breaks ties: for one
patient scanned over one region, more slices IS thinner slices.

**Pairs are kept, not deduplicated.** These scanners emit the same
reconstruction twice under adjacent series numbers (302/304), differing by a
slice or none at all. Near-identical series are both kept, and they are not
redundant: they are what a reader compares.

**Cases with several DISTINCT thin-slice series are flagged, not guessed at.**
A long-bone trauma CT can hold one thin reconstruction per scanned region at
different fields of view (0.97 / 0.75 / 0.59 mm in-plane). The rule keeps the
largest, which is a defensible default and may still be the wrong region for a
given fracture -- so `select_series` records the runners-up and the sweep says
so, rather than presenting one region as if it were the only one.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


class Dataset:
    """Where one extension's cases live, and what to ignore."""

    def __init__(self, name: str, skip_suffix: str = "_Post"):
        self.name = name
        self.data_dir = os.path.join("Test_data", name)
        self.skip_suffix = skip_suffix

    def original(self, workspace_root: str) -> str:
        return os.path.join(workspace_root, self.data_dir, ORIGINAL_SUBDIR)

    def processed(self, workspace_root: str) -> str:
        return os.path.join(workspace_root, self.data_dir, PROCESSED_SUBDIR)


ORIGINAL_SUBDIR = "Original"
PROCESSED_SUBDIR = "Processed"

#: Every dataset this panel offers. Adding one is a line here plus nothing else.
DATASETS: Dict[str, Dataset] = {
    "PedicleScrewPlanner": Dataset("PedicleScrewPlanner"),
    "LongBoneFractureReduction": Dataset("LongBoneFractureReduction"),
}

#: Post-operative scans are a different question and are not part of these sets.
#: `endswith` also catches the stray "_Post_Post" folder in one of them.
SKIP_SUFFIX = "_Post"

#: A series with fewer slices than this is a scout, a dose report or a
#: single-frame reformat -- never the diagnostic reconstruction.
MIN_SLICES = 30

#: A second series is kept alongside the best one when it is within BOTH
#: tolerances: essentially the same reconstruction under another series number.
#: Deliberately tight -- 3.0 mm vs 1.0 mm is 200% apart and must never pair.
SLICE_COUNT_TOLERANCE = 0.05        # 5% of the best series' slice count
SPACING_TOLERANCE = 0.05            # 5% of its slice spacing

#: A series NOT kept but this close in slice count to the one that was is
#: probably another scanned REGION rather than a rejected reconstruction. Worth
#: a warning, never a silent second output.
RIVAL_FRACTION = 0.5

#: Concurrent cases. Bounded by memory rather than CPU -- each case holds two
#: large volumes while it writes them.
CASE_WORKERS = 4


def is_case_folder(name: str, skip_suffix: str = SKIP_SUFFIX) -> bool:
    """A case to process: any folder that is not a post-operative scan."""
    return bool(name) and not name.endswith(skip_suffix)


def list_cases(original_dir: str) -> List[str]:
    """Case folder names, numerically where they are numbers."""
    if not os.path.isdir(original_dir):
        return []
    names = [n for n in os.listdir(original_dir)
             if os.path.isdir(os.path.join(original_dir, n)) and is_case_folder(n)]

    def key(name):
        return (0, int(name)) if name.isdigit() else (1, 0, name)

    return sorted(names, key=key)


#: ``<case>.nrrd`` or ``<case>_<series>.nrrd`` -- the two shapes output_name emits.
_OUTPUT_RE = re.compile(r"^(?P<case>.+?)(?:_[^_]+)?\.nrrd$", re.IGNORECASE)


def processed_cases(processed_dir: str) -> set:
    """Case names that already have at least one volume written.

    Derived from the OUTPUT FILES rather than a progress file: the files are
    the real state, they survive a crash or a restart, and deleting one is how
    a user asks for that case to be redone. A sidecar progress file would have
    to be kept in step with them and would be wrong the moment it was not.
    """
    done = set()
    if not os.path.isdir(processed_dir):
        return done
    for name in os.listdir(processed_dir):
        match = _OUTPUT_RE.match(name)
        if not match:
            continue
        case = match.group("case")
        done.add(case)
        # `12_304.nrrd` matches with case="12_304" as well when the case name
        # itself contains an underscore, so record both readings and let the
        # caller intersect with the real case list.
        if "_" in case:
            done.add(case.rsplit("_", 1)[0])
    return done


def pending_cases(original_dir: str, processed_dir: str):
    """``(todo, done)`` -- the cases still to process, and those already written."""
    cases = list_cases(original_dir)
    finished = processed_cases(processed_dir)
    done = [c for c in cases if c in finished]
    todo = [c for c in cases if c not in finished]
    return todo, done


def _finite(value: Any) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number and number > 0 else None


def series_spacing(series: Dict[str, Any]) -> Optional[float]:
    """Through-plane spacing in mm: what "thin slice" actually means.

    ``SpacingBetweenSlices`` when present, else ``SliceThickness``. In-plane
    pixel spacing is deliberately NOT used here -- it is the field on which the
    3D reformats win.
    """
    return (_finite(series.get("spacing_between_slices"))
            or _finite(series.get("slice_thickness")))


def is_candidate(series: Dict[str, Any]) -> bool:
    """Could this series be the diagnostic reconstruction?"""
    if int(series.get("count") or 0) < MIN_SLICES:
        return False
    modality = str(series.get("modality") or "").upper()
    if modality and modality not in ("CT", "MR"):
        return False
    return series_spacing(series) is not None


def rank_key(series: Dict[str, Any]):
    """Sort key: most slices first, then thinnest, then finest in-plane.

    Slice count leads because it is the only field that separates a real scan
    from a reformat; spacing then decides between two scans of the same extent.
    """
    spacing = series_spacing(series) or float("inf")
    in_plane = _finite(series.get("pixel_spacing")) or float("inf")
    return (-int(series.get("count") or 0), spacing, in_plane)


def select_series(series_list: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The series worth keeping for one case, best first.

    The best candidate, plus any other within both tolerances of it -- the
    scanner's duplicate reconstruction. Returns [] when nothing qualifies, which
    the caller reports rather than silently writing nothing.
    """
    candidates = [s for s in series_list if is_candidate(s)]
    if not candidates:
        return []
    candidates.sort(key=rank_key)
    best = candidates[0]
    best_count = int(best.get("count") or 0)
    best_spacing = series_spacing(best) or 0.0

    kept = [best]
    for series in candidates[1:]:
        count = int(series.get("count") or 0)
        spacing = series_spacing(series) or 0.0
        close_count = abs(count - best_count) <= max(1, best_count * SLICE_COUNT_TOLERANCE)
        close_spacing = (best_spacing > 0
                         and abs(spacing - best_spacing) <= best_spacing * SPACING_TOLERANCE)
        if close_count and close_spacing:
            kept.append(series)

    # Anything substantial that was NOT kept is recorded on the winner, so the
    # sweep can say "this case had another thin-slice series" instead of
    # presenting one scanned region as though it were the only one.
    rivals = [s for s in candidates[1:]
              if s not in kept
              and int(s.get("count") or 0) >= best_count * RIVAL_FRACTION
              and series_spacing(s) is not None
              and best_spacing > 0
              and abs((series_spacing(s) or 0) - best_spacing) <= best_spacing * 0.5]
    if rivals:
        best["rivals"] = rivals
    return kept


def output_name(case: str, series: Dict[str, Any], kept_count: int) -> str:
    """``<case>.nrrd``, or ``<case>_<series number>.nrrd`` when a case keeps two.

    The case folder names the output, as asked. Two kept series cannot both have
    that name, so the scanner's own series number disambiguates them -- the same
    number Slicer shows in its export dialog ("Export 304: 1.0 x 1.0"), so a
    file can be traced back to what produced it.
    """
    if kept_count <= 1:
        return "%s.nrrd" % case
    number = str(series.get("series_number") or "").strip()
    if not number:
        number = re.sub(r"[^A-Za-z0-9]+", "", str(series.get("uid", ""))[-6:]) or "x"
    return "%s_%s.nrrd" % (case, number)


def describe_series(series: Dict[str, Any]) -> str:
    """One line for the log."""
    spacing = series_spacing(series)
    return ("series %-6s n=%-4d spacing=%s mm  in-plane=%s mm  %s"
            % (series.get("series_number", "?"),
               int(series.get("count") or 0),
               ("%.3f" % spacing) if spacing else "?",
               ("%.3f" % _finite(series.get("pixel_spacing"))
                if _finite(series.get("pixel_spacing")) else "?"),
               str(series.get("description") or "")[:32]))


# ---------------------------------------------------------------------------
# The Slicer half: read DICOM, write compressed NRRD
# ---------------------------------------------------------------------------

#: Geometry tags are NOT in any DICOM plugin's precache list, so `fileValue`
#: re-parses the file for each one. Adding them BEFORE the import makes them
#: come from the database instead -- across 76 cases of ~900 files that is the
#: difference between a quick sweep and one that re-reads every header.
_PRECACHE_TAGS = ("0028,0030", "0018,0050", "0018,0088", "0020,0011")


def _prepare_database(database) -> None:
    """Ask the database to cache the tags this selection needs."""
    try:
        existing = list(database.tagsToPrecache)
    except Exception:
        return
    database.tagsToPrecache = sorted(set(existing) | set(_PRECACHE_TAGS))


def _ensure_dicom_module() -> None:
    """`slicer.dicomDatabase` and `slicer.modules.dicomPlugins` are created by
    the DICOM module, and `loadSeriesByUID` needs both. Selecting it once is
    what the Slicer docs prescribe before any scripted DICOM work.
    """
    import slicer                                            # noqa: PLC0415
    if getattr(slicer, "dicomDatabase", None) is not None \
            and getattr(slicer.modules, "dicomPlugins", None):
        return
    slicer.util.selectModule("DICOM")
    slicer.app.processEvents()


#: pydicom keywords for the scan. `specific_tags` makes pydicom stop after
#: these, so a header read costs a few hundred bytes instead of the whole file.
_SCAN_KEYWORDS = [
    "SeriesInstanceUID", "SeriesNumber", "SeriesDescription", "Modality",
    "SliceThickness", "SpacingBetweenSlices", "PixelSpacing",
]

#: Threads for the header scan. Pure file IO and parsing -- no MRML, so it is
#: safe off the main thread, and it is IO-bound enough that threads help.
SCAN_WORKERS = 8


def scan_series(case_dir: str) -> List[Dict[str, Any]]:
    """Group a case's files by series, reading headers only.

    Replaces indexing the whole case into the DICOM database just to find out
    what is in it. The database index parses every file AND writes a SQLite row
    per instance; this reads a few tags per file and nothing else, and then only
    the files of the chosen series are ever handed to the database.
    """
    import pydicom                                           # noqa: PLC0415
    from concurrent.futures import ThreadPoolExecutor        # noqa: PLC0415

    paths = [os.path.join(case_dir, n) for n in sorted(os.listdir(case_dir))]
    paths = [p for p in paths if os.path.isfile(p)]

    def _head(path):
        try:
            data = pydicom.dcmread(path, stop_before_pixels=True,
                                   specific_tags=_SCAN_KEYWORDS)
        except Exception:
            return None
        uid = getattr(data, "SeriesInstanceUID", None)
        if not uid:
            return None
        spacing = getattr(data, "PixelSpacing", None)
        return {
            "path": path,
            "uid": str(uid),
            "series_number": str(getattr(data, "SeriesNumber", "") or ""),
            "description": str(getattr(data, "SeriesDescription", "") or ""),
            "modality": str(getattr(data, "Modality", "") or ""),
            "slice_thickness": getattr(data, "SliceThickness", None),
            "spacing_between_slices": getattr(data, "SpacingBetweenSlices", None),
            "pixel_spacing": (spacing[0] if spacing is not None and len(spacing) else None),
        }

    grouped: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as pool:
        for head in pool.map(_head, paths):
            if head is None:
                continue
            row = grouped.get(head["uid"])
            if row is None:
                row = dict(head)
                row["count"] = 0
                row["files"] = []
                row.pop("path", None)
                grouped[head["uid"]] = row
            row["count"] += 1
            row["files"].append(head["path"])
    return list(grouped.values())


def save_compressed_nrrd(volume_node, path: str) -> bool:
    """Write ``volume_node`` to ``path`` as a COMPRESSED .nrrd.

    Goes through the node's own storage node rather than
    ``slicer.util.saveNode``: ``SetUseCompression(1)`` is exactly what the
    "Compress" checkbox in Slicer's export dialog sets, and writing through the
    storage node is the one path where it cannot be overridden by a writer
    picking its own defaults.
    """
    import slicer                                            # noqa: PLC0415

    storage = volume_node.GetStorageNode()
    if storage is None:
        volume_node.AddDefaultStorageNode()
        storage = volume_node.GetStorageNode()
    if storage is None:
        raise RuntimeError("volume has no storage node, cannot write it")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    storage.SetUseCompression(1)
    storage.SetFileName(path)
    if not storage.WriteData(volume_node):
        raise RuntimeError("Slicer refused to write %s" % os.path.basename(path))
    return os.path.isfile(path)


def process_case(case_dir: str, output_dir: str, case: str = "",
                 log=None) -> Dict[str, Any]:
    """Scan one case, keep the chosen series, write them as compressed NRRD.

    The order matters for speed: the SERIES ARE CHOSEN BEFORE THE DATABASE IS
    TOUCHED. Indexing a whole case means parsing ~900 files and writing a row
    per instance, most of them for reformats and scouts that will never be
    loaded; the header scan above answers the same question far more cheaply,
    and only the ~half of the files belonging to the chosen series are then
    indexed.

    A TEMPORARY database is still used for that half, because the load path
    (`loadSeriesByUID` -> DICOMScalarVolumePlugin) reads its tags through the
    database and re-parses the file for every tag that is not cached there --
    which is why loading straight from a file list is slower, not faster.
    """
    import slicer                                            # noqa: PLC0415
    from DICOMLib import DICOMUtils                          # noqa: PLC0415

    case = case or os.path.basename(case_dir.rstrip("/\\"))
    say = log or (lambda message: None)
    written: List[str] = []
    result: Dict[str, Any] = {"case": case, "written": written, "error": "",
                              "series_seen": 0, "series_kept": 0}

    rows = scan_series(case_dir)
    result["series_seen"] = len(rows)
    chosen = select_series(rows)
    result["series_kept"] = len(chosen)
    if not chosen:
        result["error"] = ("no series with at least %d slices and a known slice "
                           "spacing" % MIN_SLICES)
        say("  %s: %s (%d series seen)" % (case, result["error"], len(rows)))
        return result
    for series in chosen:
        say("  keep " + describe_series(series))

    wanted = [f for series in chosen for f in series["files"]]
    say("  indexing %d of %d file(s)" % (len(wanted), sum(r["count"] for r in rows)))

    _ensure_dicom_module()
    with DICOMUtils.TemporaryDICOMDatabase() as database:
        _prepare_database(database)
        indexer = _index_files(database, wanted)
        del indexer
        for series in chosen:
            node_ids = DICOMUtils.loadSeriesByUID([series["uid"]]) or []
            nodes = [slicer.mrmlScene.GetNodeByID(i) for i in node_ids]
            nodes = [n for n in nodes if n is not None
                     and n.IsA("vtkMRMLScalarVolumeNode")]
            if not nodes:
                say("  %s: series %s loaded no volume"
                    % (case, series.get("series_number")))
                result["error"] = result["error"] or "a chosen series loaded no volume"
                continue
            try:
                target = os.path.join(output_dir,
                                      output_name(case, series, len(chosen)))
                save_compressed_nrrd(nodes[0], target)
                written.append(target)
                say("  wrote %s (%.1f MB)"
                    % (os.path.basename(target), os.path.getsize(target) / 1e6))
            except Exception as exc:
                result["error"] = str(exc)
                say("  %s: %s" % (case, exc))
            finally:
                # Always, including on a write failure: volumes left behind
                # accumulate and slow every later case.
                for node in nodes:
                    slicer.mrmlScene.RemoveNode(node)
    return result


def _index_files(database, files: Sequence[str]):
    """Index just these files into ``database``.

    ``addListOfFiles`` rather than ``addDirectory``: the directory form indexes
    every scout, dose report and 3D reformat in the case as well, which is most
    of the files and none of the ones that get loaded.
    """
    import ctk                                               # noqa: PLC0415

    indexer = ctk.ctkDICOMIndexer()
    indexer.addListOfFiles(database, list(files), False)
    indexer.waitForImportFinished()
    return indexer


def simpleitk_available() -> bool:
    """Is the fast path usable? Cached after the first check."""
    global _SIMPLEITK_OK
    if _SIMPLEITK_OK is None:
        try:
            import SimpleITK                                 # noqa: F401,PLC0415
            _SIMPLEITK_OK = True
        except Exception:
            logger.info("SimpleITK unavailable; the Slicer DICOM path will be used")
            _SIMPLEITK_OK = False
    return _SIMPLEITK_OK


_SIMPLEITK_OK = None


def _process_all_via_slicer(workspace_root: str, dataset: Dataset,
                            log=None, should_stop=None) -> Dict[str, Any]:
    """The original, MRML-based sweep. One case at a time, main thread only."""
    say = log or (lambda message: None)
    original = dataset.original(workspace_root)
    processed = dataset.processed(workspace_root)
    os.makedirs(processed, exist_ok=True)
    cases, already = pending_cases(original, processed)
    if already:
        say("Resuming: %d already written, %d to go." % (len(already), len(cases)))
    results: List[Dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if should_stop is not None and should_stop():
            say("Stopped after %d case(s)." % (index - 1))
            break
        say("[%d/%d] %s" % (index, len(cases), case))
        try:
            results.append(process_case(os.path.join(original, case), processed,
                                        case=case, log=say))
        except Exception as exc:
            logger.warning("Case %s failed", case, exc_info=True)
            say("  %s: FAILED -- %s" % (case, exc))
            results.append({"case": case, "written": [], "error": str(exc),
                            "series_seen": 0, "series_kept": 0})
    written = sum(len(r["written"]) for r in results)
    failed = [r["case"] for r in results if r["error"] or not r["written"]]
    say("")
    say("Done: %d volume(s) -> %s" % (written, processed))
    return {"results": results, "written": written, "failed": failed,
            "output_dir": processed, "cases": len(cases)}


def verify_fast_path(workspace_root: str, dataset: Dataset,
                     log=None) -> Dict[str, Any]:
    """Check the fast path against a volume the OLD path already produced.

    Runs once before a resumed sweep. If the two disagree the sweep is not
    started: half a dataset in one geometry convention and half in another is
    the kind of fault that shows up months later in a result, not now in an
    error.
    """
    say = log or (lambda message: None)
    original = dataset.original(workspace_root)
    processed = dataset.processed(workspace_root)
    unused_todo, done = pending_cases(original, processed)
    if not done:
        return {"ok": True, "reason": "nothing written yet -- nothing to match"}
    case = done[-1]
    reference = ""
    for name in sorted(os.listdir(processed)):
        match = _OUTPUT_RE.match(name)
        if match and match.group("case").split("_")[0] == case:
            reference = os.path.join(processed, name)
            break
    if not reference:
        return {"ok": True, "reason": "no reference file found"}
    say("Checking the fast path against %s ..." % os.path.basename(reference))
    try:
        outcome = compare_with_existing(os.path.join(original, case), reference)
    except Exception as exc:
        logger.warning("Fast-path verification failed", exc_info=True)
        return {"ok": False, "hard": False,
                "reason": "verification raised: %s" % exc}
    if outcome["ok"]:
        say("  match: " + outcome["reason"])
        return outcome
    say("  MISMATCH: " + outcome["reason"])
    # Always show what the fast path sees, so the next step is obvious from the
    # console rather than needing another run to find out.
    diagnose_case(os.path.join(original, case), log=say)
    return outcome


def process_all(workspace_root: str, dataset: Dataset, log=None,
                should_stop=None, workers: int = CASE_WORKERS,
                verify: bool = True) -> Dict[str, Any]:
    """Every unprocessed case under ``Original/``, written to ``Processed/``.

    Cases run CONCURRENTLY: nothing here touches MRML, so the only limits are
    disk and memory. ``should_stop()`` is polled as results land, so a sweep can
    be interrupted; cases already finished stay finished, and re-running resumes
    from the outputs on disk.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: PLC0415

    say = log or (lambda message: None)
    if not simpleitk_available():
        # The Slicer path still works, it is just slower and single-file: MRML
        # is main-thread only, so it cannot be run concurrently or off the main
        # thread. Falling back keeps the button working on an install where
        # SimpleITK is missing rather than failing with an ImportError.
        say("SimpleITK is unavailable -- falling back to the Slicer DICOM path "
            "(slower, one case at a time, must run on the main thread).")
        return _process_all_via_slicer(workspace_root, dataset, log=say,
                                       should_stop=should_stop)
    original = dataset.original(workspace_root)
    processed = dataset.processed(workspace_root)
    os.makedirs(processed, exist_ok=True)
    cases, already = pending_cases(original, processed)

    if verify and cases:
        outcome = verify_fast_path(workspace_root, dataset, log=say)
        if not outcome.get("ok") and not outcome.get("hard"):
            # Could not check, as opposed to checked and disagreed. Blocking on
            # an inability to verify would strand the sweep over a missing
            # reference file; a proven disagreement is the thing worth stopping
            # for.
            say("Could not verify the fast path (%s) -- continuing anyway."
                % outcome.get("reason"))
        elif not outcome.get("ok"):
            say("Refusing to continue: the fast path does not reproduce the "
                "existing output. " + str(outcome.get("reason")))
            say("Run pedicle_dicom.diagnose_case(<case folder>, log=print) to "
                "look further, or pass verify=False to process_all to override.")
            return {"results": [], "written": 0, "failed": [], "cases": len(cases),
                    "output_dir": processed, "aborted": outcome.get("reason")}

    if already:
        say("Resuming: %d case(s) already written, %d to go (%d at a time)."
            % (len(already), len(cases), workers))
    else:
        say("%d case(s) to process, %d at a time." % (len(cases), workers))

    results: List[Dict[str, Any]] = []
    stopped = False
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        futures = {pool.submit(process_case_fast, os.path.join(original, case),
                               processed, case, say): case
                   for case in cases}
        for index, future in enumerate(as_completed(futures), start=1):
            case = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                logger.warning("Case %s failed", case, exc_info=True)
                say("  %s: FAILED -- %s" % (case, exc))
                results.append({"case": case, "written": [], "error": str(exc),
                                "series_seen": 0, "series_kept": 0})
            # Say what the case PRODUCED, not just that it ended. "30 done"
            # reads as "30 succeeded", and a case that wrote nothing finishes
            # exactly like one that wrote two volumes.
            last = results[-1]
            if last.get("written"):
                outcome = "%d volume(s)" % len(last["written"])
            else:
                outcome = "NO OUTPUT: %s" % (last.get("error") or "unknown")
            say("[%d/%d] %s -- %s" % (index, len(cases), case, outcome))
            if should_stop is not None and should_stop() and not stopped:
                stopped = True
                # Cancel what has not started; the running ones finish, so no
                # case is left half-written.
                for pending in futures:
                    pending.cancel()
                say("Stopping -- letting the running cases finish.")

    written = sum(len(r["written"]) for r in results)
    bad = [r for r in results if r["error"] or not r["written"]]
    failed = [r["case"] for r in bad]
    reasons = {r["case"]: (r["error"] or "produced no output") for r in bad}
    say("")
    say("Done: %d volume(s) from %d case(s) -> %s"
        % (written, len(results) - len(failed), processed))
    if bad:
        say("Needs a look (%d):" % len(bad))
        for case in sorted(reasons, key=lambda c: int(c) if c.isdigit() else 1e9):
            say("  %-6s %s" % (case, reasons[case]))
    return {"results": results, "written": written, "failed": failed,
            "reasons": reasons, "output_dir": processed, "cases": len(cases),
            "stopped": stopped}



# ---------------------------------------------------------------------------
# The fast path: SimpleITK + GDCM, no MRML
# ---------------------------------------------------------------------------
#
# Everything below runs in ITK's C++ -- series enumeration, geometric slice
# sorting, pixel reading and the compressed write. Nothing touches the MRML
# scene, which has two consequences that together are the whole speedup:
#
#   * No DICOM database. The database path parses every file to index it, then
#     DICOMScalarVolumePlugin reads ~6 tags per file back out of it in PYTHON
#     to group and sort. GDCM does the same job in one C++ pass.
#   * No main thread. MRML is main-thread only, so the old path could only ever
#     do one case at a time while Slicer sat idle. These calls release the GIL,
#     so cases run CONCURRENTLY (see CASE_WORKERS).
#
# The output is an ITK-written NRRD either way: Slicer's own writer is
# vtkITKImageWriter over the same ITK NrrdImageIO. `compare_with_existing`
# exists so that equivalence is checked against a file the old path produced
# rather than assumed.


#: Read with pydicom, not through SimpleITK's metadata dictionary.
#:
#: `ImageFileReader.ReadImageInformation()` populated NOTHING on this data --
#: every tag came back empty, so `series_spacing()` saw no thickness, every
#: series failed `is_candidate`, and most cases silently produced no output.
#: The few that did got names like `2_58182.nrrd`, because `output_name` fell
#: back to the tail of the series UID when the series number was blank; that
#: filename is what exposed it.
#:
#: pydicom reads these headers correctly (it is what the probe used), costs one
#: read per SERIES rather than per file, and is bundled with Slicer. GDCM is
#: still what enumerates and sorts -- only the tag reading moved.
_PYDICOM_KEYWORDS = [
    "SeriesInstanceUID", "SeriesNumber", "SeriesDescription", "Modality",
    "SliceThickness", "SpacingBetweenSlices", "PixelSpacing",
]


def _series_metadata(path: str) -> Dict[str, Any]:
    """The tags the selection needs, from one file's header."""
    import pydicom                                           # noqa: PLC0415

    try:
        data = pydicom.dcmread(path, stop_before_pixels=True,
                               specific_tags=_PYDICOM_KEYWORDS)
    except Exception:
        logger.debug("Could not read the header of %s", path, exc_info=True)
        return {}
    spacing = getattr(data, "PixelSpacing", None)
    return {
        "series_number": str(getattr(data, "SeriesNumber", "") or "").strip(),
        "description": str(getattr(data, "SeriesDescription", "") or "").strip(),
        "modality": str(getattr(data, "Modality", "") or "").strip(),
        "slice_thickness": getattr(data, "SliceThickness", None),
        "spacing_between_slices": getattr(data, "SpacingBetweenSlices", None),
        "pixel_spacing": (spacing[0] if spacing is not None and len(spacing) else None),
    }


def scan_series_fast(case_dir: str) -> List[Dict[str, Any]]:
    """Series in a case: enumerated and SORTED by GDCM, described by pydicom.

    ``GetGDCMSeriesFileNames`` returns each series' files already sorted by
    image position -- the geometric ordering the Slicer plugin reimplements in
    Python, and the part worth keeping in C++.
    """
    import SimpleITK as sitk                                 # noqa: PLC0415

    rows: List[Dict[str, Any]] = []
    series_reader = sitk.ImageSeriesReader()
    try:
        series_ids = list(series_reader.GetGDCMSeriesIDs(case_dir))
    except Exception:
        logger.warning("GDCM could not enumerate %s", case_dir, exc_info=True)
        return rows

    for series_id in series_ids:
        try:
            files = list(series_reader.GetGDCMSeriesFileNames(case_dir, series_id))
        except Exception:
            continue
        if not files:
            continue
        row: Dict[str, Any] = {"uid": series_id, "count": len(files),
                               "files": files}
        row.update(_series_metadata(files[0]))
        if series_spacing(row) is None and len(files) > 1:
            # Neither tag present. Derive the spacing from the slice positions
            # themselves rather than guessing -- and only from a real gap, so a
            # missing tag cannot make a reformat look like a thin-slice scan.
            derived = _spacing_from_positions(files)
            if derived:
                row["slice_thickness"] = derived
        rows.append(row)
    return rows


def _spacing_from_positions(files: Sequence[str]) -> Optional[float]:
    """Distance between the first two slices, from ImagePositionPatient."""
    import pydicom                                           # noqa: PLC0415

    try:
        positions = []
        for path in list(files)[:2]:
            data = pydicom.dcmread(path, stop_before_pixels=True,
                                   specific_tags=["ImagePositionPatient"])
            position = getattr(data, "ImagePositionPatient", None)
            if position is None:
                return None
            positions.append([float(v) for v in position])
        gap = sum((a - b) ** 2 for a, b in zip(*positions)) ** 0.5
        return gap if gap > 1e-4 else None
    except Exception:
        return None


def write_series_nrrd(files: Sequence[str], path: str) -> str:
    """Read a sorted DICOM series and write it as a COMPRESSED .nrrd."""
    import SimpleITK as sitk                                 # noqa: PLC0415

    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(list(files))
    image = reader.Execute()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # useCompression is the same gzip the "Compress" checkbox turns on -- both
    # end at ITK's NrrdImageIO.
    sitk.WriteImage(image, path, useCompression=True)
    if not os.path.isfile(path):
        raise RuntimeError("nothing was written to %s" % path)
    return path


def process_case_fast(case_dir: str, output_dir: str, case: str = "",
                      log=None) -> Dict[str, Any]:
    """One case, entirely in ITK. Safe to call off the main thread."""
    case = case or os.path.basename(str(case_dir).rstrip("/\\"))
    say = log or (lambda message: None)
    written: List[str] = []
    result: Dict[str, Any] = {"case": case, "written": written, "error": "",
                              "series_seen": 0, "series_kept": 0}

    try:
        entries = os.listdir(case_dir)
    except Exception as exc:
        result["error"] = "cannot read the case folder: %s" % exc
        say("  %s: %s" % (case, result["error"]))
        return result
    if not entries:
        result["error"] = "the case folder is EMPTY -- no DICOM to read"
        say("  %s: %s" % (case, result["error"]))
        return result

    rows = scan_series_fast(case_dir)
    result["series_seen"] = len(rows)
    chosen = select_series(rows)
    result["series_kept"] = len(chosen)
    if not chosen:
        best = max(rows, key=lambda r: int(r.get("count") or 0)) if rows else None
        detail = ("largest series has %d slice(s)" % int(best.get("count") or 0)
                  if best else "GDCM found no series at all")
        result["error"] = ("no series with at least %d slices and a known slice "
                           "spacing (%s)" % (MIN_SLICES, detail))
        say("  %s: %s" % (case, result["error"]))
        return result

    for series in chosen:
        say("  %s: keep %s" % (case, describe_series(series)))

    rivals = chosen[0].get("rivals") or []
    if rivals:
        result["rivals"] = len(rivals)
        say("  %s: NOTE -- %d other thin-slice series present, probably another "
            "scanned region. Only the largest was kept:" % (case, len(rivals)))
        for rival in rivals:
            # `rival`, NOT `series`: reusing the loop variable here is what
            # previously left `series` pointing at the last REJECTED series, so
            # the case wrote that one under its number (8 kept 302/304 and
            # wrote 8_204.nrrd).
            say("      not kept: " + describe_series(rival))

    # The write is its OWN loop over `chosen`. It was briefly nested inside the
    # `if rivals:` above, which meant a case with no rivals -- the normal case,
    # a plain duplicate pair -- silently wrote nothing at all and reported no
    # error, because nothing had raised.
    for series in chosen:
        target = os.path.join(output_dir, output_name(case, series, len(chosen)))
        try:
            write_series_nrrd(series["files"], target)
            written.append(target)
            say("  %s: wrote %s (%.1f MB)"
                % (case, os.path.basename(target), os.path.getsize(target) / 1e6))
        except Exception as exc:
            # Which SERIES, not just which case: a case can keep two, and ITK's
            # own message ("non-uniform sampling", a memory error) only makes
            # sense next to the series it was reading.
            reason = "series %s (%d slices): %s" % (
                series.get("series_number") or "?",
                int(series.get("count") or 0), exc)
            result["error"] = (result["error"] + "; " + reason
                               if result["error"] else reason)
            say("  %s: FAILED %s" % (case, reason))

    if not written and not result["error"]:
        # Should be unreachable: every path above either writes or records why.
        # "NO OUTPUT: unknown" is the shape of a bug, so say that rather than
        # printing a word that sends the reader looking for a data problem.
        result["error"] = ("kept %d series but wrote nothing and raised nothing "
                           "-- this is a bug, please report it" % len(chosen))
        say("  %s: %s" % (case, result["error"]))
    return result


def diagnose_case(case_dir: str, log=None) -> List[Dict[str, Any]]:
    """What the fast path sees in one case. Run this when something looks off.

        from SlicerAIAgentLib.experiments import pedicle_dicom
        pedicle_dicom.diagnose_case(r"...\\Original\\44", log=print)
    """
    say = log or (lambda message: None)
    rows = scan_series_fast(case_dir)
    if not rows:
        say("  GDCM found NO series in %s -- is SimpleITK present, and does the "
            "folder hold DICOM files?" % case_dir)
        return rows
    chosen = {id(r) for r in select_series(rows)}
    say("  %d series in %s:" % (len(rows), os.path.basename(case_dir)))
    for row in sorted(rows, key=rank_key):
        say("    %s %s" % ("KEEP" if id(row) in chosen else "    ",
                           describe_series(row)))
    return rows


def compare_with_existing(case_dir: str, existing_path: str) -> Dict[str, Any]:
    """Does the fast path reproduce a volume the OLD path already wrote?

    The question is whether the two agree on GEOMETRY, so the reference is
    matched by CONTENT, not by name: every series this case would now keep is
    tried, and the check passes if any one of them reproduces the file exactly.
    Deriving the series number back out of the filename -- which is what this
    did first -- turns a naming mismatch into what looks like a geometry
    failure, and reports the same message when the scan found nothing at all.

    Returns ``hard=True`` only for a real disagreement. "Could not compare" is
    reported separately, because refusing to run on an inability to check is a
    different decision from refusing on a proven mismatch.
    """
    import numpy as np                                       # noqa: PLC0415
    import SimpleITK as sitk                                 # noqa: PLC0415

    name = os.path.basename(existing_path)
    rows = scan_series_fast(case_dir)
    if not rows:
        return {"ok": False, "hard": True,
                "reason": "the fast path found NO series in %s -- it would "
                          "write nothing for every case" % case_dir}
    chosen = select_series(rows)
    if not chosen:
        return {"ok": False, "hard": True,
                "reason": "the fast path kept no series from %d found in %s"
                          % (len(rows), os.path.basename(case_dir))}

    try:
        old = sitk.ReadImage(existing_path)
    except Exception as exc:
        return {"ok": False, "hard": False,
                "reason": "could not read the reference %s: %s" % (name, exc)}

    def _close(a, b, tolerance):
        return len(a) == len(b) and all(abs(x - y) <= tolerance
                                        for x, y in zip(a, b))

    notes = []
    for series in chosen:
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(list(series["files"]))
        try:
            fresh = reader.Execute()
        except Exception as exc:
            notes.append("series %s failed to read: %s"
                         % (series.get("series_number"), exc))
            continue
        label = "series %s" % (series.get("series_number") or "?")
        if tuple(fresh.GetSize()) != tuple(old.GetSize()):
            notes.append("%s size %s vs %s" % (label, fresh.GetSize(), old.GetSize()))
            continue
        if not _close(fresh.GetSpacing(), old.GetSpacing(), 1e-4):
            notes.append("%s spacing %s vs %s"
                         % (label, fresh.GetSpacing(), old.GetSpacing()))
            continue
        if not _close(fresh.GetOrigin(), old.GetOrigin(), 1e-3):
            notes.append("%s origin %s vs %s"
                         % (label, fresh.GetOrigin(), old.GetOrigin()))
            continue
        if not _close(fresh.GetDirection(), old.GetDirection(), 1e-4):
            notes.append("%s orientation differs" % label)
            continue
        worst = int(np.abs(sitk.GetArrayViewFromImage(fresh).astype("int64")
                           - sitk.GetArrayViewFromImage(old).astype("int64")).max())
        if worst:
            notes.append("%s voxels differ by up to %d" % (label, worst))
            continue
        return {"ok": True, "hard": False,
                "reason": "%s reproduces %s exactly (size, spacing, origin, "
                          "orientation and every voxel)" % (label, name)}

    # Nothing matched. Whether that is a geometry disagreement or just a
    # different series being kept is visible in the notes, so hand them over
    # instead of collapsing it to one line.
    return {"ok": False, "hard": True,
            "reason": "no kept series reproduces %s -- %s"
                      % (name, "; ".join(notes) or "no comparison completed")}
