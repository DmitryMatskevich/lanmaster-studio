# P4-07 Events And Replay Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-07 adds durable event replay:

- event table with monotonically increasing `sequence`;
- job queue, worker, release and artifact lifecycle events;
- REST replay with `afterSequence`, `resourceType`, `resourceId` and `limit`;
- WebSocket replay endpoint at `/api/v1/ws`;
- OpenAPI and TypeScript client include REST event listing.

The WebSocket endpoint currently sends replay and closes. Continuous push can be
layered on top of the same durable log without changing REST replay semantics.

## Verification

Commands:

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
DATABASE_URL=sqlite:///./var/p4-07-web-check.db .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8094
# HTTP smoke: enqueue -> claim -> heartbeat -> GET /events filtered by job
```

Results:

- `pytest`: 10 passed.
- REST replay returned `job.queued`, `job.running`, `job.heartbeat`.
- `afterSequence` replay and WebSocket replay are covered by contract tests.
- Swagger UI `/docs` loaded and referenced `/api/v1/openapi.json`.

## Next

P4-08: AuditEvent and trace correlation.

