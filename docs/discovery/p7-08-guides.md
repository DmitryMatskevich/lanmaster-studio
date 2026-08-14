# P7-08 Engineer, Librarian and Administrator Guides

Status: scaffold complete; new-user walkthrough pending.

## Scope

- Added engineer guide for source review, PMD edits, preview and release gates.
- Added librarian guide for catalog/source evidence, component tables and email
  response rules.
- Added administrator guide for production operations, backups, monitoring and
  rollback.
- Added guide coverage verifier.

## Verification

- `.venv/bin/python scripts/verify_guides.py`
- `.venv/bin/python -m pytest tests/test_guides.py`

## Gate

Guide content is present and machine-checked. Final P7-08 acceptance requires
walkthrough by new users.
