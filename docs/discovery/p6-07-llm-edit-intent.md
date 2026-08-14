# P6-07 LLM Provider And EditIntent

## Scope

P6-07 adds the typed boundary between retrieval/chat and PMD patch proposal
logic. LLM output is structured data only; it does not call tools directly.

## Implemented

- Added typed `EditIntent` and `EditOperation` Pydantic models.
- Added `LlmProvider` protocol with JSON completion boundary.
- Added static provider test double for deterministic tests.
- Added proposal helper that injects model/context and validates provider JSON.
- Added negative tests for unsupported operations and direct tool prompt attempts.

## Verification

- `.venv/bin/python -m pytest tests/test_edit_intents.py -q`
- `.venv/bin/python -m pytest`

P6-07 is complete. Next checkpoint: P6-08 PMDPatchProposal
validation/authorization workflow.
