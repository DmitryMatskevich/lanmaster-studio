from __future__ import annotations

from pathlib import Path

import pytest

from studio_api.ingestion.pdf import extract_pdf


def _pdf(content_stream: bytes, *, image: bool = False) -> bytes:
    image_object = b"5 0 obj << /Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length 3 >> stream\nabc\nendstream endobj\n" if image else b""
    return b"\n".join([
        b"%PDF-1.4",
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        b"3 0 obj << /Type /Page /Parent 2 0 R /Resources << /XObject << /Im1 5 0 R >> >> /Contents 4 0 R >> endobj",
        b"4 0 obj << /Length " + str(len(content_stream)).encode("ascii") + b" >> stream",
        content_stream,
        b"endstream endobj",
        image_object,
        b"trailer << /Root 1 0 R >>",
        b"%%EOF",
    ])


def test_pdf_vector_extraction_with_region_provenance(tmp_path: Path):
    path = tmp_path / "vector.pdf"
    path.write_bytes(_pdf(b"BT (Mounting dimensions) Tj ET\n10 20 30 40 re S\n"))

    result = extract_pdf(path)

    assert result.format == "pdf"
    assert result.mode == "vector"
    assert result.pageCount == 1
    assert result.pages[0].text == "Mounting dimensions"
    assert result.pages[0].vectorOperators >= 2
    assert result.pages[0].regions[-1].bbox == (10.0, 20.0, 30.0, 40.0)


def test_pdf_raster_and_mixed_classification(tmp_path: Path):
    raster = tmp_path / "raster.pdf"
    raster.write_bytes(_pdf(b"q /Im1 Do Q", image=True))
    mixed = tmp_path / "mixed.pdf"
    mixed.write_bytes(_pdf(b"BT (Door) Tj ET\nq /Im1 Do Q\n0 0 10 10 re S", image=True))

    assert extract_pdf(raster).mode == "raster"
    mixed_result = extract_pdf(mixed)
    assert mixed_result.mode == "mixed"
    assert mixed_result.pages[0].rasterImages == 1
    assert mixed_result.pages[0].text == "Door"


def test_pdf_rejects_non_pdf(tmp_path: Path):
    path = tmp_path / "bad.pdf"
    path.write_text("not pdf", encoding="utf-8")

    with pytest.raises(ValueError, match="Not a PDF"):
        extract_pdf(path)
