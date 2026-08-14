# P6-04 STEP, IFC And GLB Metadata Extraction

## Scope

P6-04 adds source-side metadata extraction for 3D model exchange formats before
indexing and RAG stages.

## Implemented

- Added STEP metadata extraction for schema, units, product/component names and
  bbox from Cartesian points.
- Added IFC metadata extraction for schema, product names, component count and
  bbox from IFC Cartesian points.
- Added GLB 2.0 metadata extraction for asset schema, node names, component
  count and bbox from accessor min/max bounds.
- Added negative validation for invalid GLB files.
- Tests cover controlled STEP fixture plus generated minimal IFC and GLB
  fixtures.

## Verification

- `.venv/bin/python -m pytest tests/test_model3d_ingestion.py -q`
- `.venv/bin/python -m pytest`

P6-04 is complete. Next checkpoint: P6-05 chunking, metadata, PostgreSQL full
text and pgvector.
