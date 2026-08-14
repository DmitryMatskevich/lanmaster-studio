# P4-03 Lifecycle Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-03 adds the first persistent lifecycle contract:

- create draft from model;
- read draft state;
- apply typed patch records;
- enforce optimistic locking through `headRevisionToken`;
- commit draft into immutable revision with stable content hash;
- update model `activeRevisionId` only after commit;
- reject writes to closed drafts;
- abandon open draft;
- expose lifecycle endpoints in OpenAPI and generated TypeScript client.

This is a lifecycle scaffold. Preview/release job orchestration, CAD worker
execution and PMD semantic validation remain P4-04/P4-05 scope.

## Implemented Endpoints

- `POST /api/v1/models/{model_id}/drafts`
- `GET /api/v1/drafts/{draft_id}`
- `POST /api/v1/drafts/{draft_id}/patches`
- `POST /api/v1/drafts/{draft_id}/commit`
- `DELETE /api/v1/drafts/{draft_id}`

## Verification

Commands:

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
.venv/bin/python scripts/verify_skeleton.py
DATABASE_URL=sqlite:///./var/p4-03-web-check.db .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8090
# HTTP smoke: create model -> draft -> stale patch 409 -> patch -> commit -> published model
```

Results:

- `pytest`: 6 passed.
- scaffold verifier: passed.
- stale patch returned `409`.
- accepted patch recorded actor and operations.
- commit created `rev_*` revision with `sha256:*` content hash.
- model became `published` and points to committed `activeRevisionId`.
- Swagger UI `/docs` loaded and referenced `/api/v1/openapi.json`.

## Next

P4-04: queue and CAD worker protocol with retry/cancel/heartbeat/idempotency.

