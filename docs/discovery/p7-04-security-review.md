# P7-04 Security Review, SBOM and Dependency Policy

Status: engineering scaffold complete; independent security approval pending.

## Scope

- Added reproducible dependency policy verification.
- Python runtime/test dependencies must be exactly pinned in `requirements.txt`.
- Frontend dependency policy requires `frontend/package-lock.json`.
- Added generated SBOM evidence at `docs/discovery/p7-04-sbom.json`.
- `npm audit --prefix frontend --audit-level=moderate` remains a required gate.

## Verification

- `.venv/bin/python scripts/verify_security_policy.py`
- `.venv/bin/python -m pytest tests/test_security_policy.py tests/test_rag_security.py`
- `npm audit --prefix frontend --audit-level=moderate`

## Gate

P7-04 cannot fully pass until an independent security review signs off that
critical/high findings are closed. The dependency/SBOM portion is now
machine-checkable.
