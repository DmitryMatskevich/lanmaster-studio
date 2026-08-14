# P6-08 PMDPatchProposal Workflow

## Scope

P6-08 adds the validation and authorization boundary between typed LLM edit
intents and real draft patches.

## Implemented

- Added `PMDPatchProposal` model.
- Added role-based authorization for proposal operations.
- Added conversion from `EditIntent` to proposal without mutating drafts.
- Added explicit conversion from accepted proposal to patch payload.
- Unauthorized or unaccepted proposals cannot become patch payloads.

## Verification

- `.venv/bin/python -m pytest tests/test_patch_proposals.py -q`
- `.venv/bin/python -m pytest`

P6-08 is complete. Next checkpoint: P6-09 chat UI, sources, ambiguities,
accept/reject.
