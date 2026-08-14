# P7-02 Domain Approval and Pilot Release Gate

Status: engineering scaffold complete; signed domain approval pending.

## Scope

- Added an explicit pilot release decision contract.
- Release approval requires:
  - P7-01 shadow exit criteria passed;
  - signed domain approval;
  - approver identity;
  - approval timestamp;
  - canonical SHA-256 manifest hash.
- Missing approval, short shadow window or malformed manifest hash blocks release.

## Current Result

The gate is intentionally closed. No selected pilot is releaseable until the
real shadow observation window completes and Domain/Approver signs acceptance.

## Verification

- `.venv/bin/python -m pytest tests/test_pilot_approval.py tests/test_shadow_pilot.py`

## Gate

P7-02 cannot fully pass without external signed acceptance. The code contract now
prevents accidental release before that approval exists.
