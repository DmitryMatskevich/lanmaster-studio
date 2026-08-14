from __future__ import annotations

from pathlib import Path

from studio_api.ingestion.cad import extract_dxf, extract_svg, inspect_dwg


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "test-fixtures" / "source-formats"


def test_svg_ingestion_entities_and_bbox():
    result = extract_svg(FIXTURES / "minimal-panel.svg")

    assert result.format == "svg"
    assert result.parser == "xml"
    assert [entity.kind for entity in result.entities] == ["rect", "line"]
    assert result.entities[0].bbox == (25.0, 25.0, 470.0, 483.4)


def test_dxf_ingestion_group_code_entities():
    result = extract_dxf(FIXTURES / "minimal-panel.dxf")

    assert result.format == "dxf"
    assert result.parser == "group-code"
    assert result.entities
    assert {entity.kind for entity in result.entities} & {"line", "lwpolyline"}


def test_dwg_adapter_records_libredwg_diagnostics():
    result = inspect_dwg(FIXTURES / "minimal-panel.dwg")

    assert result.format == "dwg"
    assert result.parser == "libredwg"
    assert result.diagnostics
    assert result.diagnostics[0].startswith("dwgread") or result.diagnostics == ["dwgread-missing"]
