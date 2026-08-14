from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from studio_api.ingestion.model3d import extract_glb_metadata, extract_ifc_metadata, extract_step_metadata


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "test-fixtures" / "source-formats"


def test_step_metadata_from_controlled_fixture():
    result = extract_step_metadata(FIXTURES / "frwaj-open-frame.step")

    assert result.format == "step"
    assert result.schema and "AUTOMOTIVE_DESIGN" in result.schema
    assert result.unit == "mm"
    assert result.componentCount > 0
    assert result.bbox is not None


def test_ifc_metadata(tmp_path: Path):
    path = tmp_path / "fixture.ifc"
    path.write_text(
        "\n".join([
            "ISO-10303-21;",
            "HEADER; FILE_SCHEMA(('IFC4X3')); ENDSEC;",
            "DATA;",
            "#1=IFCBUILDINGELEMENTPROXY('1',$,'Rail',$,$,$,$,$,$);",
            "#2=IFCCARTESIANPOINT((0.,0.,0.));",
            "#3=IFCCARTESIANPOINT((600.,1000.,2055.));",
            "ENDSEC; END-ISO-10303-21;",
        ]),
        encoding="utf-8",
    )

    result = extract_ifc_metadata(path)

    assert result.format == "ifc"
    assert result.schema == "IFC4X3"
    assert result.componentCount == 1
    assert result.names == ["Rail"]


def test_glb_metadata(tmp_path: Path):
    path = tmp_path / "fixture.glb"
    payload = {
        "asset": {"version": "2.0"},
        "nodes": [{"name": "Cabinet"}],
        "meshes": [{}],
        "accessors": [{"type": "VEC3", "min": [0, 0, 0], "max": [1, 2, 3]}],
    }
    raw_json = json.dumps(payload).encode("utf-8")
    padding = (4 - len(raw_json) % 4) % 4
    json_chunk = raw_json + b" " * padding
    total_length = 12 + 8 + len(json_chunk)
    path.write_bytes(b"glTF" + struct.pack("<II", 2, total_length) + struct.pack("<I4s", len(json_chunk), b"JSON") + json_chunk)

    result = extract_glb_metadata(path)

    assert result.format == "glb"
    assert result.schema == "glTF 2.0"
    assert result.componentCount == 1
    assert result.bbox == (0.0, 0.0, 0.0, 1.0, 2.0, 3.0)


def test_glb_rejects_invalid_file(tmp_path: Path):
    path = tmp_path / "bad.glb"
    path.write_bytes(b"bad")

    with pytest.raises(ValueError, match="Not a GLB"):
        extract_glb_metadata(path)
