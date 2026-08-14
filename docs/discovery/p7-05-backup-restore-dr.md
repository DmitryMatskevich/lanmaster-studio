# P7-05 Backup, Restore, Retention and DR Drill

Status: engineering scaffold complete; real environment drill pending.

## Scope

- Added backup manifest contract for database/object-store hashes, encryption and
  retention.
- Added restore drill evidence contract.
- Added machine-checkable RPO/RTO, hash parity and smoke-check blockers.

## Required Production Evidence

P7-05 still requires an actual restore drill in the pilot environment with:

- encrypted backup manifest;
- database and object-store hash match after restore;
- API health, revision read and artifact download checks;
- measured RPO/RTO within accepted limits.

## Verification

- `.venv/bin/python -m pytest tests/test_disaster_recovery.py`

## Gate

The DR evaluator is implemented. Final acceptance remains pending until a real
backup/restore drill is executed against the pilot stack.
