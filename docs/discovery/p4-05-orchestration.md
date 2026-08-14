# P4-05 Preview And Release Orchestration Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-05 adds orchestration endpoints on top of the P4-04 queue:

- draft preview request returns `202 Accepted` with `jobId` and `eventsUrl`;
- preview validates draft `headRevisionToken` before enqueue;
- revision release request creates a queued release record and release job;
- release creation supports `Idempotency-Key`;
- release state is readable by viewer role;
- OpenAPI and TypeScript client include orchestration methods.

Actual CAD worker execution, artifact storage, signed URLs and release manifest
materialization remain P4-06+ scope.

## Implemented Endpoints

- `POST /api/v1/drafts/{draft_id}/preview`
- `POST /api/v1/revisions/{revision_id}/releases`
- `GET /api/v1/releases/{release_id}`

## Verification

Commands:

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
.venv/bin/python scripts/verify_skeleton.py
DATABASE_URL=sqlite:///./var/p4-05-web-check.db .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8092
# HTTP smoke: create model -> draft -> preview 202 -> commit -> release 202 -> read release
```

Results:

- `pytest`: 8 passed.
- scaffold verifier: passed.
- preview returned `202` and `eventsUrl=/api/v1/events?jobId=...`.
- release returned `202`, `rel_*`, queued status and linked release job.
- viewer read release returned `200`.
- Swagger UI `/docs` loaded and referenced `/api/v1/openapi.json`.

## Next

P4-06: object storage and signed URLs with scoped URLs and hash verification.

