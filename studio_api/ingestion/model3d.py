from __future__ import annotations

import json
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelMetadata:
    format: str
    schema: str | None = None
    unit: str | None = None
    componentCount: int = 0
    bbox: tuple[float, float, float, float, float, float] | None = None
    names: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)


def extract_step_metadata(path: Path) -> ModelMetadata:
    text = path.read_text(encoding="latin-1", errors="replace")
    names = [match.group(1) for match in re.finditer(r"PRODUCT\('([^']+)'", text)]
    points = _cartesian_points(text)
    return ModelMetadata(
        format="step",
        schema=_first_match(text, r"FILE_SCHEMA\(\('([^']+)'"),
        unit="mm" if ".MILLI.,.METRE." in text else None,
        componentCount=len(names),
        bbox=_bbox3(points),
        names=names[:50],
    )


def extract_ifc_metadata(path: Path) -> ModelMetadata:
    text = path.read_text(encoding="utf-8", errors="replace")
    names = []
    for match in re.finditer(r"IFC(?:BUILDINGELEMENTPROXY|FURNISHINGELEMENT|PRODUCT|ELEMENT)\(([^;]*)\)", text):
        quoted = re.findall(r"'([^']*)'", match.group(1))
        if len(quoted) >= 2:
            names.append(quoted[1])
    points = _cartesian_points(text)
    return ModelMetadata(
        format="ifc",
        schema=_first_match(text, r"FILE_SCHEMA\(\('([^']+)'"),
        unit="mm" if "MILLI" in text.upper() else None,
        componentCount=len(names),
        bbox=_bbox3(points),
        names=[name for name in names[:50] if name],
    )


def extract_glb_metadata(path: Path) -> ModelMetadata:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("Not a GLB file")
    version, total_length = struct.unpack_from("<II", data, 4)
    if version != 2:
        raise ValueError("Only GLB 2.0 is supported")
    json_length, chunk_type = struct.unpack_from("<I4s", data, 12)
    if chunk_type != b"JSON":
        raise ValueError("First GLB chunk is not JSON")
    payload = json.loads(data[20:20 + json_length].rstrip(b" \x00").decode("utf-8"))
    accessors = payload.get("accessors") if isinstance(payload.get("accessors"), list) else []
    points = []
    for accessor in accessors:
        if isinstance(accessor, dict) and accessor.get("type") == "VEC3" and "min" in accessor and "max" in accessor:
            points.append(tuple(float(value) for value in accessor["min"]))
            points.append(tuple(float(value) for value in accessor["max"]))
    nodes = payload.get("nodes") if isinstance(payload.get("nodes"), list) else []
    names = [str(node.get("name")) for node in nodes if isinstance(node, dict) and node.get("name")]
    meshes = payload.get("meshes") if isinstance(payload.get("meshes"), list) else []
    return ModelMetadata(
        format="glb",
        schema=f"glTF {payload.get('asset', {}).get('version', '2.0')}",
        unit="m",
        componentCount=len(nodes) or len(meshes),
        bbox=_bbox3(points),
        names=names[:50],
        diagnostics=[f"declaredLength:{total_length}"],
    )


def _first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1) if match else None


def _cartesian_points(text: str) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for match in re.finditer(r"(?:IFC)?CARTESIAN_POINT\((?:'[^']*',)?\(?\(([^)]*)\)\)?\)", text):
        values = [float(item) for item in match.group(1).split(",")[:3]]
        if len(values) == 3:
            points.append((values[0], values[1], values[2]))
    return points


def _bbox3(points: list[tuple[float, float, float]]) -> tuple[float, float, float, float, float, float] | None:
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
