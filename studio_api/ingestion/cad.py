from __future__ import annotations

import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CadEntity:
    kind: str
    layer: str | None = None
    bbox: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class CadExtraction:
    format: str
    parser: str
    entities: list[CadEntity]
    diagnostics: list[str] = field(default_factory=list)


def extract_svg(path: Path) -> CadExtraction:
    root = ET.parse(path).getroot()
    entities: list[CadEntity] = []
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "rect":
            x = _float(element.get("x"))
            y = _float(element.get("y"))
            width = _float(element.get("width"))
            height = _float(element.get("height"))
            entities.append(CadEntity(kind="rect", bbox=(x, y, width, height)))
        elif tag == "line":
            x1 = _float(element.get("x1"))
            y1 = _float(element.get("y1"))
            x2 = _float(element.get("x2"))
            y2 = _float(element.get("y2"))
            entities.append(CadEntity(kind="line", bbox=(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))))
        elif tag in {"circle", "ellipse", "path", "polyline", "polygon"}:
            entities.append(CadEntity(kind=tag))
    return CadExtraction(format="svg", parser="xml", entities=entities)


def extract_dxf(path: Path) -> CadExtraction:
    pairs = _dxf_pairs(path.read_text(encoding="utf-8", errors="replace").splitlines())
    entities: list[CadEntity] = []
    index = 0
    while index < len(pairs):
        code, value = pairs[index]
        if code == "0" and value in {"LINE", "CIRCLE", "ARC", "LWPOLYLINE", "POLYLINE", "TEXT", "MTEXT"}:
            entity_pairs: list[tuple[str, str]] = []
            index += 1
            while index < len(pairs) and pairs[index][0] != "0":
                entity_pairs.append(pairs[index])
                index += 1
            entities.append(CadEntity(kind=value.lower(), layer=_first(entity_pairs, "8"), bbox=_dxf_bbox(value, entity_pairs)))
            continue
        index += 1
    return CadExtraction(format="dxf", parser="group-code", entities=entities)


def inspect_dwg(path: Path) -> CadExtraction:
    if shutil.which("dwgread") is None:
        return CadExtraction(format="dwg", parser="libredwg", entities=[], diagnostics=["dwgread-missing"])
    completed = subprocess.run(
        ["dwgread", "--version"],
        check=True,
        text=True,
        capture_output=True,
    )
    probe = subprocess.run(
        ["dwgread", str(path)],
        check=False,
        text=True,
        capture_output=True,
        timeout=20,
    )
    diagnostics = [completed.stdout.strip().splitlines()[0]]
    if probe.returncode != 0:
        diagnostics.append(f"dwgread-returncode:{probe.returncode}")
        if probe.stderr.strip():
            diagnostics.append(probe.stderr.strip().splitlines()[0])
    else:
        diagnostics.append("dwgread-ok")
    return CadExtraction(format="dwg", parser="libredwg", entities=[], diagnostics=diagnostics)


def _float(value: str | None) -> float:
    if value is None:
        return 0.0
    return float(value.removesuffix("mm"))


def _dxf_pairs(lines: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for index in range(0, len(lines) - 1, 2):
        pairs.append((lines[index].strip(), lines[index + 1].strip()))
    return pairs


def _first(pairs: list[tuple[str, str]], code: str) -> str | None:
    for item_code, value in pairs:
        if item_code == code:
            return value
    return None


def _values(pairs: list[tuple[str, str]], code: str) -> list[float]:
    return [float(value) for item_code, value in pairs if item_code == code]


def _dxf_bbox(kind: str, pairs: list[tuple[str, str]]) -> tuple[float, float, float, float] | None:
    if kind == "LINE":
        xs = _values(pairs, "10") + _values(pairs, "11")
        ys = _values(pairs, "20") + _values(pairs, "21")
    elif kind in {"LWPOLYLINE", "POLYLINE"}:
        xs = _values(pairs, "10")
        ys = _values(pairs, "20")
    elif kind in {"CIRCLE", "ARC"}:
        center_x = _values(pairs, "10")
        center_y = _values(pairs, "20")
        radius = _values(pairs, "40")
        if not center_x or not center_y or not radius:
            return None
        return (center_x[0] - radius[0], center_y[0] - radius[0], radius[0] * 2, radius[0] * 2)
    else:
        return None
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
