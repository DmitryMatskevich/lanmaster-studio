# P4-01 API Scaffold Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-01 establishes the first runnable LANMASTER Studio application layer:

- FastAPI application under `studio_api`;
- versioned `/api/v1` HTTP contract;
- local SQLite migration runner;
- core lifecycle tables for models, revisions, drafts and jobs;
- OpenAPI export at `openapi/openapi.json`;
- generated TypeScript client at `clients/typescript/src/index.ts`;
- CI contract tests.

This is intentionally not the editor, RAG, CAD worker or production deployment.
Those remain P4-02+ and P5/P6 scope.

## Implemented Endpoints

- `GET /health`
- `GET /api/v1/openapi.json`
- `GET /api/v1/models`
- `POST /api/v1/models`
- `GET /api/v1/models/{model_id}`

## Verification

Commands:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/init_db.py
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
.venv/bin/python scripts/verify_skeleton.py
DATABASE_URL=sqlite:///./var/web-check.db .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8088
curl -fsS http://127.0.0.1:8088/health
curl -fsS -X POST http://127.0.0.1:8088/api/v1/models -H 'content-type: application/json' -d '{"article":"LANMASTER-STUDIO-P4-01-WEB","series":"P4","name":"Web smoke model"}'
curl -fsS 'http://127.0.0.1:8088/api/v1/models?query=WEB'
curl -fsS http://127.0.0.1:8088/docs
```

Results:

- `pytest`: 3 passed.
- scaffold verifier: passed.
- `/health`: returned `status=ok`.
- OpenAPI: served as 3.1.0 with `/api/v1/models`.
- HTTP model create/list smoke: passed.
- Swagger UI `/docs`: loaded and referenced `/api/v1/openapi.json`.

## Next

P4-02: OIDC dev/prod abstraction and RBAC with negative tests.

