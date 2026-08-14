# P6-03 SVG, DXF And DWG Ingestion

## Scope

P6-03 adds headless ingestion for SVG/DXF sources and a LibreDWG-backed DWG
adapter smoke path.

## Implemented

- Added `studio_api.ingestion.cad.extract_svg`.
- Added `studio_api.ingestion.cad.extract_dxf`.
- Added `studio_api.ingestion.cad.inspect_dwg` using `dwgread` when available.
- SVG extraction records common drawing entities and bounding boxes for `rect`
  and `line`.
- DXF extraction reads group-code entities and captures layer plus simple entity
  bounding boxes for lines, circles/arcs and polylines.
- DWG adapter records LibreDWG diagnostics and returns a controlled diagnostic
  if `dwgread` is unavailable.
- Tests cover the controlled SVG, DXF and DWG fixtures.

## Verification

- `dwgread --version`
- `.venv/bin/python -m pytest tests/test_cad_ingestion.py -q`
- `.venv/bin/python -m pytest`

P6-03 is complete. Next checkpoint: P6-04 STEP/IFC/GLB metadata extraction.
