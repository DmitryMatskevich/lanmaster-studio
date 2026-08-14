# P6-09 Chat UI

## Scope

P6-09 adds the first chat/proposal UI surface with sources, ambiguities and
accept/reject controls.

## Implemented

- Added `ChatProposalPanel` to the model workspace.
- Chat prepares a proposal instead of mutating a draft directly.
- Proposal view shows sources and ambiguities.
- Accept/reject are explicit user actions.
- E2E covers proposal preparation, source/ambiguity visibility and accept state.

## Verification

- `npm run frontend:build`
- `npm run frontend:test`
- `PYTHON=.venv/bin/python npm --prefix frontend run test:e2e`
- `.venv/bin/python -m pytest`

P6-09 is complete. Next checkpoint: P6-10 prompt injection/data isolation tests
and kill switch.
