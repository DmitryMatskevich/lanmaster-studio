# P6-01 Upload And Ingestion Lifecycle

## Scope

P6-01 hardens the P4 artifact upload skeleton for production-style source
ingestion.

## Implemented

- Upload intent creation enforces configured max object size.
- Upload intent creation enforces allowlisted media types and artifact scopes.
- Complete-upload verifies immutable size and SHA-256 before publishing an
  artifact.
- Complete-upload runs a bounded local scan and rejects known malware signature
  test content.
- Ready artifacts are immutable: a second complete attempt returns conflict
  instead of mutating the artifact again.
- A successfully completed artifact queues an `ingest.document` job with payload
  routed to the `isolated-ingestion` pool.
- `.env.example` documents the upload limit, media type allowlist and scope
  allowlist.

## Verification

- `.venv/bin/python scripts/generate_openapi.py`
- `.venv/bin/python scripts/generate_ts_client.py`
- `.venv/bin/python -m pytest`
- `python3 scripts/verify_skeleton.py`
- `python3 scripts/verify_compose.py`

P6-01 is complete. Next checkpoint: P6-02 production PDF vector/raster/mixed
extraction pipeline.
