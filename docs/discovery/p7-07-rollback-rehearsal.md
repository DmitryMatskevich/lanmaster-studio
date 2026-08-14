# P7-07 Incident and Rollback Rehearsal

Status: engineering scaffold complete; live rehearsal pending.

## Scope

- Added rollback rehearsal evaluator for pilot articles.
- Rehearsal requires rollback target `legacy`.
- Blocks release if revision data, artifacts, audit evidence or legacy routing
  are missing after rollback.
- Checks recovery time against the accepted limit.

## Required Production Evidence

P7-07 final acceptance requires a live rehearsal on the pilot environment showing
that a selected article can be returned to the legacy route without data loss and
with an audit trail.

## Verification

- `.venv/bin/python -m pytest tests/test_rollback_rehearsal.py`

## Gate

The rollback evaluator is implemented. Final pass remains pending until the live
incident/rollback rehearsal is executed.
