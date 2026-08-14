# P4-04 Queue And Worker Protocol Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-04 adds a durable queue contract for CAD-heavy operations:

- enqueue job with `Idempotency-Key`;
- read job state;
- cancel non-terminal jobs;
- retry cancelled/failed jobs;
- worker claim by job type;
- worker heartbeat with progress and worker ownership check;
- generated OpenAPI and TypeScript client update;
- negative test for heartbeat from the wrong worker.

This is still an in-process SQLite-backed protocol for the developer stack. The
actual CAD execution, preview/release orchestration and object storage are
P4-05/P4-06 scope.

## Implemented Endpoints

- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`
- `POST /api/v1/jobs/{job_id}/cancel`
- `POST /api/v1/jobs/{job_id}/retry`
- `POST /api/v1/workers/claim`
- `POST /api/v1/jobs/{job_id}/heartbeat`

## Verification

Commands:

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
.venv/bin/python scripts/verify_skeleton.py
DATABASE_URL=sqlite:///./var/p4-04-web-check.db .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8091
# HTTP smoke: enqueue -> idempotent enqueue -> claim -> heartbeat -> cancel -> retry -> read
```

Results:

- `pytest`: 7 passed.
- scaffold verifier: passed.
- repeated enqueue with same `Idempotency-Key` returned same `job_id`.
- worker claim moved job from `queued` to `running`.
- heartbeat updated progress to `67`.
- cancel moved job to `cancelled`.
- retry moved job back to `queued` with `attempt=2`.
- Swagger UI `/docs` loaded and referenced `/api/v1/openapi.json`.

## Next

P4-05: preview/release orchestration returning `202 Accepted`, manifest and
gates.

