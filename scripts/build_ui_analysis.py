"""
Build pre-analysis for Slicer core UI files.

The output is a small, structured bridge from user-facing UI labels/actions to
nearby implementation code and API footprints.  It intentionally excludes
extension UI; extension-specific UI is analyzed during extension CLI generation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_PATH = PROJECT_ROOT / "Resources" / "Skills" / "slicer-skill-full"
DEFAULT_SOURCE_ROOT = DEFAULT_SKILL_PATH / "slicer-source"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "Resources" / "Slicer_UI_PreAnalysis" / "v1"


@dataclass
class UIControl:
    ui_file: str
    owner_class: str
    kind: str
    object_name: str
    widget_class: str = ""
    text: str = ""
    tool_tip: str = ""
    status_tip: str = ""
    properties: Dict[str, object] = field(default_factory=dict)
    implementation_files: List[str] = field(default_factory=list)
    matched_lines: List[str] = field(default_factory=list)
    slots: List[str] = field(default_factory=list)
    api_footprints: List[str] = field(default_factory=list)
    confidence: str = "ui_only"


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _safe_name(rel_path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", rel_path).replace("/", "__")


def _text_of_property(prop: ET.Element) -> Optional[object]:
    string_el = prop.find("string")
    if string_el is not None:
        return string_el.text or ""
    bool_el = prop.find("bool")
    if bool_el is not None:
        return bool_el.text or ""
    enum_el = prop.find("enum")
    if enum_el is not None:
        return enum_el.text or ""
    set_el = prop.find("set")
    if set_el is not None:
        return set_el.text or ""
    number_el = prop.find("number")
    if number_el is not None:
        return number_el.text or ""
    string_list = prop.find("stringlist")
    if string_list is not None:
        return [item.text or "" for item in string_list.findall("string")]
    return None


def _properties(el: ET.Element) -> Dict[str, object]:
    props: Dict[str, object] = {}
    for prop in el.findall("property"):
        name = prop.get("name") or ""
        if not name:
            continue
        value = _text_of_property(prop)
        if value is not None:
            props[name] = value
    return props


def _iter_ui_files(source_root: Path) -> Iterable[Path]:
    for path in source_root.rglob("*.ui"):
        rel = path.relative_to(source_root).as_posix()
        if rel.startswith("Extensions/"):
            continue
        yield path


def _iter_qrc_files(source_root: Path) -> Iterable[Path]:
    for path in source_root.rglob("*.qrc"):
        rel = path.relative_to(source_root).as_posix()
        if rel.startswith("Extensions/"):
            continue
        yield path


def _parse_ui_file(path: Path, source_root: Path) -> Tuple[str, List[UIControl]]:
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return "", []

    owner_el = root.find("class")
    owner_class = owner_el.text.strip() if owner_el is not None and owner_el.text else path.stem
    ui_rel = _rel(path, source_root)
    controls: List[UIControl] = []

    for widget in root.iter("widget"):
        object_name = widget.get("name") or ""
        if not object_name:
            continue
        props = _properties(widget)
        controls.append(UIControl(
            ui_file=ui_rel,
            owner_class=owner_class,
            kind="widget",
            object_name=object_name,
            widget_class=widget.get("class", ""),
            text=str(props.get("text", "")),
            tool_tip=str(props.get("toolTip", "")),
            status_tip=str(props.get("statusTip", "")),
            properties=props,
        ))

    for action in root.iter("action"):
        object_name = action.get("name") or ""
        if not object_name:
            continue
        props = _properties(action)
        controls.append(UIControl(
            ui_file=ui_rel,
            owner_class=owner_class,
            kind="action",
            object_name=object_name,
            text=str(props.get("text", "")),
            tool_tip=str(props.get("toolTip", "")),
            status_tip=str(props.get("statusTip", "")),
            properties=props,
        ))

    return owner_class, controls


def _candidate_impl_files(ui_path: Path, source_root: Path, owner_class: str) -> List[Path]:
    rel_parts = ui_path.relative_to(source_root).parts
    if "Resources" in rel_parts:
        owner_dir = source_root.joinpath(*rel_parts[:rel_parts.index("Resources")])
    else:
        owner_dir = ui_path.parent

    candidates: List[Path] = []
    class_stems = [owner_class]
    if not owner_class.endswith("Widget"):
        class_stems.append(f"{owner_class}Widget")
    if not owner_class.endswith("Private"):
        class_stems.append(f"{owner_class}Private")

    names = []
    for stem in class_stems:
        names.extend([
            f"{stem}.cxx",
            f"{stem}.cpp",
            f"{stem}.h",
            f"{stem}_p.h",
            f"{stem}.py",
        ])
    for root in [owner_dir, owner_dir / "Widgets", owner_dir.parent]:
        for name in names:
            p = root / name
            if p.exists() and p.is_file():
                candidates.append(p)

    # Fallback: exact owner-class files anywhere under the same broad module dir.
    if not candidates:
        broad_root = owner_dir
        while broad_root.parent != source_root and broad_root.name not in {"Base", "Libs", "Modules"}:
            broad_root = broad_root.parent
        search_root = broad_root if broad_root.exists() else source_root
        for p in search_root.rglob(f"{owner_class}.*"):
            if p.suffix.lower() in {".cxx", ".cpp", ".h", ".py"}:
                candidates.append(p)

    unique: List[Path] = []
    seen = set()
    for path in candidates:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def _extract_slot_names(line: str, object_name: str) -> List[str]:
    slots = []
    if object_name not in line:
        return slots
    for match in re.finditer(r"SLOT\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", line):
        slots.append(match.group(1))
    for match in re.finditer(r"&[A-Za-z_][A-Za-z0-9_:]*::([A-Za-z_][A-Za-z0-9_]*)", line):
        name = match.group(1)
        if name != object_name:
            slots.append(name)
    return sorted(set(slots))


def _extract_api_footprints(text: str) -> List[str]:
    names = set()
    for match in re.finditer(r"(?:->|\.)([A-Z][A-Za-z0-9_]+)\s*\(", text):
        names.add(match.group(1))
    for match in re.finditer(r"\b(vtkMRML[A-Za-z0-9_]+::[A-Za-z0-9_]+)\b", text):
        names.add(match.group(1))
    blocked = {"QObject", "QString", "QIcon", "QMenu", "QAction", "QWidget"}
    return sorted(n for n in names if n not in blocked)[:30]


def _extract_function_block(lines: List[str], owner_class: str, slot_name: str) -> str:
    patterns = [
        re.compile(rf"\b{re.escape(owner_class)}::\s*{re.escape(slot_name)}\s*\("),
        re.compile(rf"\b[A-Za-z_][A-Za-z0-9_:]*::\s*{re.escape(slot_name)}\s*\("),
    ]
    start = None
    for index, line in enumerate(lines):
        if any(pattern.search(line) for pattern in patterns):
            start = index
            break
    if start is None:
        return ""
    block = []
    brace_balance = 0
    seen_open = False
    for line in lines[start:start + 140]:
        block.append(line)
        brace_balance += line.count("{") - line.count("}")
        if "{" in line:
            seen_open = True
        if seen_open and brace_balance <= 0:
            break
    return "".join(block)


def _link_controls(
    controls: List[UIControl],
    impl_files: List[Path],
    source_root: Path,
) -> None:
    impl_contents: List[Tuple[Path, List[str], str]] = []
    for impl in impl_files:
        try:
            lines = impl.read_text(encoding="utf-8", errors="ignore").splitlines(True)
        except Exception:
            continue
        impl_contents.append((impl, lines, "".join(lines)))

    impl_rels = [_rel(path, source_root) for path in impl_files]
    for control in controls:
        control.implementation_files = impl_rels
        matched_context = []
        slots = set()
        apis = set()
        for impl, lines, full_text in impl_contents:
            for index, line in enumerate(lines):
                if control.object_name not in line:
                    continue
                context = "".join(lines[max(0, index - 2):min(len(lines), index + 3)])
                matched_context.append(f"{_rel(impl, source_root)}:{index + 1}: {line.strip()}")
                for slot in _extract_slot_names(line, control.object_name):
                    slots.add(slot)
                    block = _extract_function_block(lines, control.owner_class, slot)
                    if block:
                        apis.update(_extract_api_footprints(block))
                apis.update(_extract_api_footprints(context))

        control.matched_lines = matched_context[:12]
        control.slots = sorted(slots)
        control.api_footprints = sorted(apis)[:30]
        if control.api_footprints:
            control.confidence = "linked_to_api"
        elif control.slots:
            control.confidence = "linked_to_slot"
        elif control.matched_lines:
            control.confidence = "linked_to_code"
        else:
            control.confidence = "ui_only"


def _parse_qrc_file(path: Path, source_root: Path) -> Dict[str, object]:
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return {"qrc_file": _rel(path, source_root), "resources": []}
    resources = []
    for file_el in root.iter("file"):
        if file_el.text:
            resources.append(file_el.text.strip())
    return {"qrc_file": _rel(path, source_root), "resources": resources}


def _write_jsonl(path: Path, rows: Iterable[Dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _write_docs(output_dir: Path, by_ui_file: Dict[str, List[UIControl]]) -> None:
    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for ui_file, controls in sorted(by_ui_file.items()):
        if not controls:
            continue
        owner_class = controls[0].owner_class
        path = docs_dir / f"{_safe_name(ui_file)}.md"
        lines = [
            f"# Slicer UI Analysis: {ui_file}",
            "",
            f"- Owner class: `{owner_class}`",
            f"- UI file: `{ui_file}`",
            "",
            "This document maps user-facing Slicer UI controls to nearby implementation evidence. "
            "Use UI evidence to identify intent, then verify executable code against implementation/API evidence.",
            "",
        ]
        for control in controls:
            label_bits = [
                control.text,
                control.tool_tip,
                control.status_tip,
                control.object_name,
                control.widget_class,
            ]
            searchable = " | ".join(str(x) for x in label_bits if x)
            lines.extend([
                f"## {control.kind}: {control.object_name}",
                "",
                f"- Confidence: `{control.confidence}`",
                f"- Widget/action class: `{control.widget_class or control.kind}`",
                f"- Search text: {searchable or '(none)'}",
            ])
            if control.text:
                lines.append(f"- Text: {control.text}")
            if control.tool_tip:
                lines.append(f"- Tooltip: {control.tool_tip}")
            if control.status_tip:
                lines.append(f"- Status tip: {control.status_tip}")
            if control.implementation_files:
                lines.append("- Implementation candidates: " + ", ".join(f"`{p}`" for p in control.implementation_files))
            if control.matched_lines:
                lines.append("- Matched implementation lines:")
                lines.extend(f"  - `{line}`" for line in control.matched_lines)
            if control.slots:
                lines.append("- Connected slots/functions: " + ", ".join(f"`{s}`" for s in control.slots))
            if control.api_footprints:
                lines.append("- API footprints: " + ", ".join(f"`{a}`" for a in control.api_footprints))
            interesting_props = {
                k: v for k, v in control.properties.items()
                if k in {"nodeTypes", "checked", "checkable", "popupMode", "toolButtonStyle"}
            }
            if interesting_props:
                lines.append("- Key UI properties: " + json.dumps(interesting_props, ensure_ascii=False, sort_keys=True))
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")


def build_ui_analysis(source_root: Path, output_dir: Path, clean: bool = True) -> Dict[str, object]:
    source_root = source_root.resolve()
    output_dir = output_dir.resolve()
    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_ui_file: Dict[str, List[UIControl]] = {}
    all_controls: List[UIControl] = []
    ui_files = list(_iter_ui_files(source_root))
    for ui_path in ui_files:
        _, controls = _parse_ui_file(ui_path, source_root)
        impl_files = _candidate_impl_files(ui_path, source_root, controls[0].owner_class if controls else ui_path.stem)
        _link_controls(controls, impl_files, source_root)
        if controls:
            rel_ui = _rel(ui_path, source_root)
            by_ui_file[rel_ui] = controls
            all_controls.extend(controls)

    qrc_records = [_parse_qrc_file(path, source_root) for path in _iter_qrc_files(source_root)]
    _write_jsonl(output_dir / "ui_controls.jsonl", (asdict(c) for c in all_controls))
    _write_jsonl(output_dir / "ui_resources.jsonl", qrc_records)
    _write_docs(output_dir, by_ui_file)

    confidence_counts: Dict[str, int] = {}
    for control in all_controls:
        confidence_counts[control.confidence] = confidence_counts.get(control.confidence, 0) + 1
    manifest = {
        "version": 1,
        "source_root": str(source_root),
        "ui_file_count": len(ui_files),
        "qrc_file_count": len(qrc_records),
        "control_count": len(all_controls),
        "confidence_counts": confidence_counts,
        "docs_path": str(output_dir / "docs"),
        "virtual_search_prefix": "slicer-ui-analysis/",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Slicer core UI pre-analysis artifacts.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="Path to slicer-source")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--no-clean", action="store_true", help="Do not remove existing output directory first")
    args = parser.parse_args()

    source_root = Path(args.source_root)
    output_dir = Path(args.output_dir)
    if not source_root.is_dir():
        raise SystemExit(f"Slicer source root not found: {source_root}")
    manifest = build_ui_analysis(source_root, output_dir, clean=not args.no_clean)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
