"""Read a saved ``.seg.nrrd`` -- including a MULTI-LAYER one -- without Slicer.

``volume_io.read_nrrd`` deliberately handles one case: a 3-D scalar volume. A
segmentation is not that. Slicer writes overlapping segments as a **4-D** file
whose first ``sizes:`` entry is a ``list`` axis of LAYERS, and a segment is then
addressed by the pair ``(layer, label value)`` -- two segments can carry the same
label value in different layers, and one layer can carry several segments under
different values. ``Fragment Reduction_1.seg.nrrd`` of case 0001 does exactly
that: ``Right Ilium`` is (layer 1, value 2) and ``Left Ilium`` is (layer 0, value
2). Reading such a file as "non-zero", or by label value alone, silently unions
two different bones.

Three properties of these files are load-bearing and none of them announces
itself:

* **The layer axis is the FASTEST-varying one.** ``sizes: 2 1036 577 763`` with
  ``kinds: list domain domain domain`` reshapes, in C order, to
  ``(763, 577, 1036, 2)`` -- so the layer is the *last* array index, not the
  first. Indexing ``array[layer]`` instead of ``array[..., layer]`` returns a
  slab of the volume rather than a layer of it: it is in bounds, it is the right
  dtype, and every segment then comes back nearly empty.
* **``space: left-posterior-superior``.** Rows 0 and 1 of IJK->RAS must be
  negated, exactly as in :mod:`volume_io`. Skipping the flip mirrors the left
  hemipelvis onto the right, which still produces a finite displacement.
* **``encoding: gzip``.** The bytes after the header are a DEFLATE stream, and a
  decompressed segmentation is far larger than the file: 2.8 MB on disk becomes
  912 MB of voxels. So the payload is decompressed to a temp file and
  memory-mapped rather than held whole, and every measure below is taken in
  slabs. Peak resident memory is a slab, not a volume.

The segment table itself lives in NRRD's ``key:=value`` metadata
(``Segment0_Name``, ``Segment0_Layer``, ``Segment0_LabelValue``), which
``volume_io._parse_header`` drops on purpose so a metadata key cannot shadow a
real field. It is parsed here instead, which is what lets a caller ask for a
segment by NAME.

Deliberately NOT used: ``Segment<N>_Extent``, the segment's own bounding box.
Cropping to it would be a large speed-up and there is no cheap way to prove it is
not stale -- the extent is the segment's TIGHT box, so foreground on its faces is
expected and a truncated read looks exactly like a correct one. Every scan below
therefore covers the whole layer. The cost is seconds; the alternative is a
fragment silently measured with a slice missing.

Qt-free and Slicer-free, so ``scripts/check_pelvic_analysis.py`` can exercise it
outside Slicer.
"""

from __future__ import annotations

import logging
import os
import re
import tempfile
import zlib
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

# The NRRD type table is volume_io's. Imported rather than copied: a second copy
# is a second thing to keep correct, and the failure of a stale one -- a type
# reinterpreted at the wrong width -- is silent.
from .volume_io import _TYPES as _NRRD_TYPES

logger = logging.getLogger(__name__)

_NUMBER = re.compile(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")
_SEGMENT_KEY = re.compile(r"^Segment(\d+)_(.+)$")

#: Read the header out of this many bytes. A segmentation header runs to a few
#: kilobytes; the conversion-parameter blob alone is ~1.5 KB.
_HEADER_PROBE_BYTES = 1 << 20

#: Decompress into memory below this, to a temp file above it. 256 MB is well
#: over any single-fragment file and well under the multi-hundred-megabyte
#: whole-pelvis ones, which are the reason the memmap path exists.
INLINE_LIMIT_BYTES = 256 << 20

#: One slab of a scan, in bytes of mask. Peak is a small multiple of this (the
#: padded slab plus the neighbour test's temporaries), so it is set well below
#: what a single whole-volume mask would cost.
SLAB_BYTES = 32 << 20


def _numbers(text: str) -> List[float]:
    return [float(x) for x in _NUMBER.findall(text or "")]


class Segment(object):
    """One segment of a segmentation: how to find its voxels, and its name."""

    __slots__ = ("index", "name", "label", "layer", "extent", "color")

    def __init__(self, index: int, name: str, label: int, layer: int,
                 extent: Optional[Sequence[int]], color: str):
        self.index = index
        self.name = name
        self.label = label
        self.layer = layer
        self.extent = extent
        self.color = color

    def __repr__(self):
        return "<Segment %r layer=%d label=%d>" % (self.name, self.layer, self.label)


class Segmentation(object):
    """A ``.seg.nrrd`` open for reading. Close it, or use it as a context manager.

    ``close()`` is not optional on the memmap path: Windows will not delete a
    file while a mapping of it is live, so a caller that leaks one leaves a
    multi-hundred-megabyte temp file behind for the rest of the session.
    """

    def __init__(self, path: str):
        self.path = path
        (self._fields, self._meta, self.ijk_to_ras, self._sizes,
         self.dimension, self._offset, self._dtype) = _read_header(path)
        self.segments = _read_segments(self._meta)
        self.shape = tuple(reversed(self._sizes))              # C order
        self.layers = self._sizes[0] if self.dimension == 4 else 1
        self._temp_path = None
        self._array = None

    # -- lifetime ----------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, *_unused):
        self.close()
        return False

    def close(self):
        array, self._array = self._array, None
        mapping = getattr(array, "_mmap", None)
        del array
        if mapping is not None:
            try:
                mapping.close()
            except Exception:
                logger.debug("Closing the memory map failed", exc_info=True)
        temp, self._temp_path = self._temp_path, None
        if temp:
            try:
                os.remove(temp)
            except OSError:
                logger.info("Could not remove the temporary file %s", temp,
                            exc_info=True)

    # -- data --------------------------------------------------------------
    @property
    def array(self) -> np.ndarray:
        """The voxel block, ``(nk, nj, ni)`` or ``(nk, nj, ni, layers)``."""
        if self._array is None:
            self._array, self._temp_path = _open_payload(
                self.path, self._offset, self._dtype, self.shape,
                self._fields.get("encoding", "raw"))
        return self._array

    def layer_volume(self, layer: int) -> np.ndarray:
        """The ``(nk, nj, ni)`` block a segment of ``layer`` lives in."""
        if self.dimension == 3:
            if layer:
                raise ValueError("%s is a single-layer segmentation, but a "
                                 "segment asks for layer %d"
                                 % (os.path.basename(self.path), layer))
            return self.array
        if not 0 <= layer < self.layers:
            raise ValueError("%s: layer %d is outside 0..%d"
                             % (os.path.basename(self.path), layer, self.layers - 1))
        return self.array[..., layer]

    # -- lookup ------------------------------------------------------------
    def by_name(self) -> Dict[str, Segment]:
        """``{normalised name: segment}``. A duplicate name keeps the first."""
        table: Dict[str, Segment] = {}
        for segment in self.segments:
            key = normalise_name(segment.name)
            if key and key not in table:
                table[key] = segment
        return table

    def names(self) -> List[str]:
        return [segment.name for segment in self.segments]


def normalise_name(name: str) -> str:
    """Segment names are compared case- and whitespace-insensitively.

    ``Left Ilium - Fragment 1`` has to match itself across two files written in
    two different sessions; nothing else about the spelling is normalised,
    because the name is the only thing pairing a reduction with its ground truth
    and quietly equating two different ones would score the wrong bone.
    """
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


# ---------------------------------------------------------------------------
# The header
# ---------------------------------------------------------------------------

def _read_header(path: str):
    with open(path, "rb") as handle:
        probe = handle.read(_HEADER_PROBE_BYTES)
    cut = probe.find(b"\n\n")
    if cut < 0:
        raise ValueError("%s: no blank line ending the NRRD header" % path)
    text = probe[:cut].decode("latin-1")

    fields: Dict[str, str] = {}
    meta: Dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if ":=" in line:
            key, _unused, value = line.partition(":=")
            meta[key.strip()] = value.strip()
            continue
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()

    dimension = int(fields.get("dimension", "0"))
    if dimension not in (3, 4):
        raise ValueError("%s: expected a 3-D or 4-D segmentation, got dimension %s"
                         % (path, fields.get("dimension")))
    sizes = [int(x) for x in fields["sizes"].split()]
    if len(sizes) != dimension:
        raise ValueError("%s: %d sizes for a %d-D file"
                         % (path, len(sizes), dimension))

    kinds = fields.get("kinds", "").split()
    if dimension == 4:
        # Enforced, not assumed. Every measure here indexes the layer as the
        # LAST array axis, which is only right while the list axis is the first
        # of `sizes:`. A file written the other way round would still reshape,
        # still be in bounds, and hand back a slab of the volume as a "layer".
        if kinds[:1] != ["list"]:
            raise ValueError("%s: a 4-D segmentation whose first axis is %r, not "
                             "'list' -- the layer axis is not where this reader "
                             "expects it" % (path, kinds[:1]))
        if sizes[0] < 1:
            raise ValueError("%s: %d layers" % (path, sizes[0]))

    base = _NRRD_TYPES.get(fields.get("type", "").strip().lower())
    if base is None:
        raise ValueError("%s: unsupported NRRD type %r" % (path, fields.get("type")))
    if base[-1] == "1":
        dtype = np.dtype(base)                       # single byte: no endianness
    else:
        endian = fields.get("endian", "").strip().lower()
        if endian not in ("little", "big"):
            raise ValueError("%s: multi-byte type %r with no 'endian:' field"
                             % (path, fields.get("type")))
        dtype = np.dtype(("<" if endian == "little" else ">") + base)

    columns = [_numbers(part) for part in fields.get("space directions", "").split(")")
               if "(" in part]
    if len(columns) != 3 or any(len(column) != 3 for column in columns):
        raise ValueError("%s: cannot read 'space directions' %r"
                         % (path, fields.get("space directions")))
    origin = _numbers(fields.get("space origin", ""))
    if len(origin) != 3:
        raise ValueError("%s: cannot read 'space origin' %r"
                         % (path, fields.get("space origin")))

    ijk_to_ras = np.eye(4)
    for index, column in enumerate(columns):
        ijk_to_ras[:3, index] = column
    ijk_to_ras[:3, 3] = origin

    space = re.sub(r"[^a-z]+", " ", fields.get("space", "").lower()).strip()
    if space in ("left posterior superior", "lps"):
        ijk_to_ras[0, :] *= -1.0
        ijk_to_ras[1, :] *= -1.0
    elif space not in ("right anterior superior", "ras"):
        raise ValueError("%s: unhandled NRRD space %r" % (path, fields.get("space")))

    return fields, meta, ijk_to_ras, sizes, dimension, cut + 2, dtype


def _read_segments(meta: Dict[str, str]) -> List[Segment]:
    grouped: Dict[int, Dict[str, str]] = {}
    for key, value in meta.items():
        match = _SEGMENT_KEY.match(key)
        if match:
            grouped.setdefault(int(match.group(1)), {})[match.group(2)] = value

    segments: List[Segment] = []
    for index in sorted(grouped):
        entry = grouped[index]
        name = entry.get("Name", "")
        if not name:
            continue
        try:
            label = int(entry.get("LabelValue", "1"))
            layer = int(entry.get("Layer", "0"))
        except ValueError:
            logger.info("Segment %d has an unreadable Layer/LabelValue", index)
            continue
        extent = None
        if entry.get("Extent"):
            try:
                numbers = [int(x) for x in entry["Extent"].split()]
                extent = numbers if len(numbers) == 6 else None
            except ValueError:
                extent = None
        segments.append(Segment(index, name, label, layer, extent,
                                entry.get("Color", "")))
    return segments


# ---------------------------------------------------------------------------
# The payload
# ---------------------------------------------------------------------------

def _open_payload(path, offset, dtype, shape, encoding):
    """``(array, temp path or None)`` for the voxel block."""
    encoding = (encoding or "raw").strip().lower()
    count = int(np.prod(shape))
    nbytes = count * dtype.itemsize

    if encoding in ("raw", "identity"):
        # Nothing to decompress: map the file itself, and own no temp file.
        return np.memmap(path, dtype=dtype, mode="r", offset=offset,
                         shape=tuple(shape)), None
    if encoding not in ("gzip", "gz"):
        raise ValueError("%s: unsupported NRRD encoding %r" % (path, encoding))

    if nbytes <= INLINE_LIMIT_BYTES:
        with open(path, "rb") as handle:
            handle.seek(offset)
            raw = zlib.decompress(handle.read(), 16 + zlib.MAX_WBITS)
        if len(raw) < nbytes:
            raise ValueError("%s: voxel data is %d bytes, expected %d"
                             % (path, len(raw), nbytes))
        return np.frombuffer(raw[:nbytes], dtype=dtype).reshape(shape), None

    handle, temp_path = tempfile.mkstemp(prefix="slicerai_seg_", suffix=".raw")
    written = 0
    try:
        with os.fdopen(handle, "wb") as sink, open(path, "rb") as source:
            source.seek(offset)
            engine = zlib.decompressobj(16 + zlib.MAX_WBITS)
            while True:
                chunk = source.read(1 << 22)
                if not chunk:
                    break
                block = engine.decompress(chunk)
                if block:
                    sink.write(block)
                    written += len(block)
            block = engine.flush()
            if block:
                sink.write(block)
                written += len(block)
        if written < nbytes:
            # Loud, for volume_io's reason: numpy would map the prefix happily
            # and the missing slices would read as whatever followed them.
            raise ValueError("%s: voxel data is %d bytes, expected %d"
                             % (path, written, nbytes))
        return (np.memmap(temp_path, dtype=dtype, mode="r", shape=tuple(shape)),
                temp_path)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            logger.info("Could not remove the temporary file %s", temp_path,
                        exc_info=True)
        raise


# ---------------------------------------------------------------------------
# Measuring one segment, in slabs
# ---------------------------------------------------------------------------

def voxel_volume_mm3(ijk_to_ras: Sequence[Sequence[float]]) -> float:
    """The volume of one voxel: |det| of the direction columns."""
    return float(abs(np.linalg.det(np.asarray(ijk_to_ras, dtype=float)[:3, :3])))


def _interior(mask: np.ndarray) -> np.ndarray:
    """True where the voxel AND all six face neighbours are set.

    The array's own boundary planes are left False, which is the right answer at
    the volume's edge -- a voxel there has a missing neighbour and so is surface.
    Within a slab, the caller's one-plane halo is what makes the interior rows
    see their real neighbours.
    """
    out = np.zeros(mask.shape, dtype=bool)
    if min(mask.shape) < 3:
        return out
    out[1:-1, 1:-1, 1:-1] = (
        mask[1:-1, 1:-1, 1:-1]
        & mask[:-2, 1:-1, 1:-1] & mask[2:, 1:-1, 1:-1]
        & mask[1:-1, :-2, 1:-1] & mask[1:-1, 2:, 1:-1]
        & mask[1:-1, 1:-1, :-2] & mask[1:-1, 1:-1, 2:])
    return out


def measure_segment(segmentation: Segmentation, segment: Segment,
                    slab_bytes: int = SLAB_BYTES,
                    with_surface: bool = True) -> Dict[str, Any]:
    """``{voxels, volume_mm3, centroid (RAS), surface (N,3) RAS}`` for one segment.

    Scanned in slabs with a one-plane halo, so peak memory is a slab and not a
    volume, and the centroid is accumulated from per-axis marginal counts rather
    than from a coordinate list -- ``np.nonzero`` over a half-full 32 MB slab
    would itself cost 380 MB.

    ``with_surface=False`` skips the six-neighbour pass, which is most of the
    cost. It is for a segment whose SIZE is wanted but whose shape is not -- a
    reduction segment the ground truth does not name, which is listed so the
    reader can see it was seen, but which is not scored against anything.
    """
    volume = segmentation.layer_volume(segment.layer)
    nk, nj, ni = volume.shape
    plane = max(1, nj * ni)
    step = max(1, int(slab_bytes) // plane)

    voxels = 0
    sum_i = sum_j = sum_k = 0.0
    pieces: List[np.ndarray] = []
    axis_i = np.arange(ni, dtype=np.float64)
    axis_j = np.arange(nj, dtype=np.float64)

    for start in range(0, nk, step):
        stop = min(nk, start + step)
        low = max(0, start - 1)
        high = min(nk, stop + 1)
        padded = np.asarray(volume[low:high]) == segment.label
        core = padded[start - low: stop - low]
        counts_k = core.sum(axis=(1, 2))
        found = int(counts_k.sum())
        if not found:
            continue
        voxels += found
        sum_k += float(np.dot(counts_k.astype(np.float64),
                              np.arange(start, stop, dtype=np.float64)))
        sum_j += float(np.dot(core.sum(axis=(0, 2)).astype(np.float64), axis_j))
        sum_i += float(np.dot(core.sum(axis=(0, 1)).astype(np.float64), axis_i))

        if with_surface:
            boundary = core & ~_interior(padded)[start - low: stop - low]
            kk, jj, ii = np.nonzero(boundary)
            if ii.size:
                pieces.append(np.stack([ii, jj, kk + start], axis=1).astype(np.int32))

    matrix = np.asarray(segmentation.ijk_to_ras, dtype=np.float64)
    result: Dict[str, Any] = {
        "name": segment.name,
        "voxels": voxels,
        "volume_mm3": voxels * voxel_volume_mm3(matrix),
        "centroid": None,
        "surface": np.zeros((0, 3), dtype=np.float64),
    }
    if not voxels:
        return result
    mean_ijk = np.array([sum_i, sum_j, sum_k], dtype=np.float64) / float(voxels)
    result["centroid"] = mean_ijk @ matrix[:3, :3].T + matrix[:3, 3]
    if pieces:
        indices = np.concatenate(pieces, axis=0).astype(np.float64)
        result["surface"] = indices @ matrix[:3, :3].T + matrix[:3, 3]
    return result


def subsample(points: np.ndarray, limit: int) -> np.ndarray:
    """At most ``limit`` points, evenly spread through the array, deterministically.

    Deterministic because two runs of the same analysis must produce the same
    number: a random subsample would move the last decimal of every distance and
    make a re-run look like a change in the data.
    """
    points = np.asarray(points)
    if limit <= 0 or points.shape[0] <= limit:
        return points
    index = np.linspace(0, points.shape[0] - 1, int(limit)).astype(np.int64)
    return points[index]
