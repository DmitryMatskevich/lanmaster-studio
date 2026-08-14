# Gate P7 Review

Status: blocked by external/calendar evidence.

## Engineering Result

P7 engineering scaffolds are implemented and tested:

- P7-01 shadow build metrics and 28-day exit criteria;
- P7-02 signed domain approval release decision;
- P7-03 critical-path performance SLO evaluator;
- P7-04 dependency policy, SBOM and audit gate;
- P7-05 backup/restore DR evaluator;
- P7-06 production deployment readiness evaluator;
- P7-07 rollback rehearsal evaluator;
- P7-08 engineer/librarian/admin guides;
- P7-09 limited launch readiness evaluator.

## Verification

- `.venv/bin/python scripts/generate_openapi.py`
- `.venv/bin/python scripts/generate_ts_client.py`
- `.venv/bin/python scripts/verify_security_policy.py`
- `.venv/bin/python scripts/verify_guides.py`
- `.venv/bin/python -m pytest` -> 56 passed.
- `python3 scripts/verify_skeleton.py`
- `python3 scripts/verify_compose.py`
- `npm audit --prefix frontend --audit-level=moderate` -> 0 vulnerabilities.
- `npm run frontend:build`
- `npm run frontend:test`
- `PYTHON=.venv/bin/python npm --prefix frontend run test:e2e`

## Blockers

Gate P7 cannot be honestly passed yet because it requires real pilot evidence:

- P7-01: at least four calendar weeks of shadow observation; started 2026-08-14,
  earliest exit review 2026-09-10.
- P7-02: signed Domain/Approver acceptance and release manifests.
- P7-03: production-size benchmark data and SLO report.
- P7-04: independent security approval with critical/high findings closed.
- P7-05: real backup/restore DR drill.
- P7-06: actual production deployment, autoscaling and alerts evidence.
- P7-07: live rollback rehearsal to legacy without data loss.
- P7-08: guide walkthrough by new users.
- P7-09: owners, SLA, support and all prerequisite gates passed.

## Decision

Gate P7 is blocked, not failed. Code-side gates are in place and prevent release
until the required operational and human approvals exist.
