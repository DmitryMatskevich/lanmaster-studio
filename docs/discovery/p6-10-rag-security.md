# P6-10 RAG Security

## Scope

P6-10 adds prompt injection, data isolation and kill-switch controls for the RAG
path.

## Implemented

- Added `STUDIO_RAG_ENABLED` kill switch.
- Added prompt injection marker checks before RAG processing.
- Added tenant isolation decision helper for retrieved chunks.
- Added tests for kill switch, prompt injection and cross-tenant access.

## Verification

- `.venv/bin/python -m pytest tests/test_rag_security.py -q`
- `.venv/bin/python -m pytest`

P6-10 is complete. Next checkpoint: P6-11 RAG/chat evaluation corpus and
dashboard.
