# P6-02 PDF Ingestion Pipeline

## Scope

P6-02 adds the first production-side PDF extraction layer for vector, raster and
mixed source drawings. The goal is deterministic headless evidence with page and
region provenance before later RAG indexing stages.

## Implemented

- Added `studio_api.ingestion.pdf.extract_pdf`.
- The extractor validates the PDF signature and scans content streams.
- It classifies PDF sources as `vector`, `raster`, `mixed` or `empty`.
- It extracts simple text strings, vector operator counts, image references and
  rectangle regions.
- Extraction output includes page-level provenance and region records with page,
  kind, bbox and text fields.
- Added fixtures covering vector, raster, mixed and invalid-PDF cases.

## Verification

- `.venv/bin/python -m pytest tests/test_pdf_ingestion.py -q`
- `.venv/bin/python -m pytest`

P6-02 is complete. Next checkpoint: P6-03 SVG/DXF/DWG ingestion and LibreDWG
adapter.
