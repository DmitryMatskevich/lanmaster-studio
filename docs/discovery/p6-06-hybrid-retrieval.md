# P6-06 Hybrid Retrieval

## Scope

P6-06 adds the first retrieval contract over indexed source chunks with filters,
reranking and citations.

## Implemented

- Added hybrid keyword/vector scoring over `SourceChunk` records.
- Added metadata and field filters.
- Added stable reranking for deterministic equal-score ordering.
- Added citation output with artifact, source kind, page, region and bbox.
- Added tests for filtered retrieval, keyword/vector reasons and stable rerank.

## Verification

- `.venv/bin/python -m pytest tests/test_retrieval.py -q`
- `.venv/bin/python -m pytest`

P6-06 is complete. Next checkpoint: P6-07 LLM provider abstraction and typed
`EditIntent`.
