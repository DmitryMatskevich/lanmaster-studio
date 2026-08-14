# P7-06 Production Deployment, Autoscaling and Alerts

Status: engineering scaffold complete; real production deployment pending.

## Scope

- Added production deployment readiness evaluator.
- Checks include pinned image digest, required environment variables, health
  checks, alert configuration, autoscaling bounds and rollback runbook.
- Production readiness requires at least two replicas and SHA-256-pinned image.

## Required Production Evidence

P7-06 final acceptance requires actual production deployment evidence:

- deployed image digest;
- health checks from production;
- configured alert rules;
- autoscaling policy;
- rollback runbook location.

## Verification

- `.venv/bin/python -m pytest tests/test_deployment_readiness.py`

## Gate

The readiness evaluator is implemented. Final P7-06 pass remains pending until
the production stack is deployed and verified.
