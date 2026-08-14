# P7-01 Shadow Build Pilot and Operational Metrics

Status: engineering scaffold complete; four-week observation window pending.

## Scope

- Added a deterministic shadow-build metric record for pilot articles.
- Shadow results are explicitly non-publishable: release still requires P7-02 signed acceptance.
- Added exit criteria evaluation for the P7 requirement: at least 28 observed calendar days,
  success rate threshold and p95 build duration threshold.
- Recorded the active observation state separately from completion, so the gate cannot be
  passed by code alone.

## Current Observation Window

- Starts: 2026-08-14.
- Earliest eligible P7-01 exit review: 2026-09-10 after 28 observed calendar days.
- Current result: not passed until real runs cover the window.

## Verification

- `.venv/bin/python -m pytest tests/test_shadow_pilot.py`

## Gate

P7-01 is not fully complete yet because the roadmap requires real shadow observation for
not less than four calendar weeks. Engineering support is in place and ready for automated
recording by the production pilot runner.
