# P6-05 Chunking And Index Schema

## Scope

P6-05 adds the first indexing contract for ingestion outputs: deterministic
chunks with metadata plus a PostgreSQL full-text and pgvector schema.

## Implemented

- Added stable text chunking with bounded size and overlap.
- Added region-to-chunk conversion preserving page, region and bbox metadata.
- Added PostgreSQL schema for `source_chunks`.
- Schema includes `tsvector` generated full-text column and GIN index.
- Schema includes `vector(1536)` embedding column and IVFFLAT cosine index.
- Schema includes index-versioned rebuild run tracking.

## Verification

- `.venv/bin/python -m pytest tests/test_chunking.py -q`
- `.venv/bin/python -m pytest`

P6-05 is complete. Next checkpoint: P6-06 hybrid retrieval, filters, reranking
and citations.
