# P6-11 RAG Evaluation Corpus

## Scope

P6-11 adds a deterministic RAG/chat evaluation corpus and dashboard summary
contract.

## Implemented

- Added default corpus builder with 100 marked cases.
- Corpus covers source answers, clarification, missing information, edit intent
  proposals and prompt injection blocking.
- Added dashboard summary for evaluated count, pass count, coverage, pass rate
  and risk distribution.

## Verification

- `.venv/bin/python -m pytest tests/test_rag_evals.py -q`
- `.venv/bin/python -m pytest`

P6-11 is complete.
