from __future__ import annotations

import re
import zlib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PdfRegion:
    page: int
    kind: str
    bbox: tuple[float, float, float, float] | None
    text: str | None = None


@dataclass(frozen=True)
class PdfPageExtraction:
    page: int
    text: str
    vectorOperators: int
    rasterImages: int
    regions: list[PdfRegion] = field(default_factory=list)


@dataclass(frozen=True)
class PdfExtraction:
    format: str
    mode: str
    pageCount: int
    pages: list[PdfPageExtraction]
    diagnostics: list[str] = field(default_factory=list)


STREAM_RE = re.compile(rb"stream\r?\n(?P<body>.*?)\r?\nendstream", re.DOTALL)
TEXT_RE = re.compile(rb"\((?P<text>(?:\\.|[^\\)])*)\)\s*Tj")
RECT_RE = re.compile(rb"(?P<x>-?\d+(?:\.\d+)?)\s+(?P<y>-?\d+(?:\.\d+)?)\s+(?P<w>-?\d+(?:\.\d+)?)\s+(?P<h>-?\d+(?:\.\d+)?)\s+re\b")
VECTOR_OP_RE = re.compile(rb"\b(?:m|l|c|v|y|h|re|S|s|f|F|B|b)\b")


def extract_pdf(path: Path) -> PdfExtraction:
    data = path.read_bytes()
    diagnostics: list[str] = []
    if not data.startswith(b"%PDF-"):
        raise ValueError("Not a PDF file")

    page_count = len(re.findall(rb"/Type\s*/Page\b(?!s)", data)) or 1
    raster_images = len(re.findall(rb"/Subtype\s*/Image\b", data))
    decoded_streams = _decode_streams(data, diagnostics)
    content = b"\n".join(decoded_streams)
    text_items = [_decode_pdf_string(match.group("text")) for match in TEXT_RE.finditer(content)]
    vector_regions = [
        PdfRegion(
            page=1,
            kind="vector-rect",
            bbox=(
                float(match.group("x")),
                float(match.group("y")),
                float(match.group("w")),
                float(match.group("h")),
            ),
        )
        for match in RECT_RE.finditer(content)
    ]
    text_regions = [
        PdfRegion(page=1, kind="text", bbox=None, text=item)
        for item in text_items
        if item
    ]
    vector_operators = len(VECTOR_OP_RE.findall(content))

    has_text = any(text_items)
    has_vector = vector_operators > 0
    has_raster = raster_images > 0
    mode = _mode(has_text=has_text, has_vector=has_vector, has_raster=has_raster)

    first_page = PdfPageExtraction(
        page=1,
        text="\n".join(item for item in text_items if item),
        vectorOperators=vector_operators,
        rasterImages=raster_images,
        regions=[*text_regions, *vector_regions],
    )
    pages = [first_page] + [
        PdfPageExtraction(page=index, text="", vectorOperators=0, rasterImages=0, regions=[])
        for index in range(2, page_count + 1)
    ]
    return PdfExtraction(
        format="pdf",
        mode=mode,
        pageCount=page_count,
        pages=pages,
        diagnostics=diagnostics,
    )


def _decode_streams(data: bytes, diagnostics: list[str]) -> list[bytes]:
    streams: list[bytes] = []
    for match in STREAM_RE.finditer(data):
        body = match.group("body").strip(b"\r\n")
        header = data[max(0, match.start() - 300):match.start()]
        if b"/FlateDecode" in header:
            try:
                body = zlib.decompress(body)
            except zlib.error as exc:
                diagnostics.append(f"flate-decode-failed:{exc}")
                continue
        streams.append(body)
    if not streams:
        diagnostics.append("no-content-streams")
    return streams


def _decode_pdf_string(value: bytes) -> str:
    replacements = {
        rb"\(": b"(",
        rb"\)": b")",
        rb"\\": b"\\",
        rb"\n": b"\n",
        rb"\r": b"\r",
        rb"\t": b"\t",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.decode("latin-1", errors="replace").strip()


def _mode(*, has_text: bool, has_vector: bool, has_raster: bool) -> str:
    if has_raster and (has_text or has_vector):
        return "mixed"
    if has_raster:
        return "raster"
    if has_vector or has_text:
        return "vector"
    return "empty"
