# P7-03 Load and Performance Profiling

Status: engineering scaffold complete; production-size benchmark data pending.

## Scope

- Added critical-path sample aggregation for production pilot timings.
- Added p50/p95/max reporting.
- Added per-stage p95 checks so slow ingest, retrieval, preview or release stages
  can block the SLO independently.
- Added explicit blockers for missing benchmark stages.

## Required Production Evidence

Before P7-03 can be fully accepted, the pilot environment must record
production-size samples for source ingestion, retrieval/RAG, preview and release
critical paths. The scaffold now makes those results machine-checkable.

## Verification

- `.venv/bin/python -m pytest tests/test_performance_profile.py`

## Gate

P7-03 engineering support is complete. Final SLO confirmation remains pending
until real pilot load data exists.
