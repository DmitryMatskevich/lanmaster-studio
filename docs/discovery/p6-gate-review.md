# Gate P6 Review

Result: passed.

## Gate Criteria

Gate P6 requires chat to create only verifiable proposals for stable PMD,
correctly report insufficient data, show sources, and not bypass the manual
preview/confirm/commit workflow.

## Evidence

- `EditIntent` is typed and validated before proposal creation.
- LLM provider boundary returns JSON only and does not execute tools directly.
- `PMDPatchProposal` authorizes operations by role and cannot become a patch
  until explicitly accepted.
- Chat proposal UI shows sources and ambiguities and exposes accept/reject
  controls.
- RAG security blocks prompt injection markers and supports a kill switch.
- Retrieval returns citations with artifact, source kind, page, region and bbox.
- Evaluation corpus contains 100 marked cases across answer, ambiguity, missing
  information, edit proposal and prompt-injection behavior.

## Verification

- `.venv/bin/python -m pytest`
- `npm run frontend:test`
- `PYTHON=.venv/bin/python npm --prefix frontend run test:e2e`

Gate P6 is complete. Next checkpoint: P7-01 production shadow build pilot.
