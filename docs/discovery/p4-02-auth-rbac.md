# P4-02 Auth And RBAC Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-02 adds the authentication boundary needed before lifecycle writes:

- dev authentication abstraction through explicit `X-Dev-User` and
  `X-Dev-Roles` headers;
- production/OIDC mode abstraction that rejects dev headers until real OIDC is
  configured;
- role model: `viewer`, `engineer`, `admin`;
- RBAC dependencies for read and write endpoints;
- `GET /api/v1/auth/me`;
- generated OpenAPI and TypeScript client update;
- negative tests for insufficient role, unknown role and unconfigured OIDC mode.

This does not configure a production identity provider. That remains an
environment/deployment decision; the application boundary now prevents silent
fallback to dev auth in non-dev mode.

## Role Matrix

| Endpoint | viewer | engineer | admin |
|---|---:|---:|---:|
| `GET /api/v1/auth/me` | yes | yes | yes |
| `GET /api/v1/models` | yes | yes | yes |
| `GET /api/v1/models/{model_id}` | yes | yes | yes |
| `POST /api/v1/models` | no | yes | yes |

## Verification

Commands:

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
.venv/bin/python scripts/verify_skeleton.py
DATABASE_URL=sqlite:///./var/p4-02-web-check.db .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8089
curl -fsS -H 'X-Dev-User: viewer@example.test' http://127.0.0.1:8089/api/v1/auth/me
curl -sS -o /tmp/p4-02-viewer.json -w '%{http_code}' -X POST http://127.0.0.1:8089/api/v1/models -H 'content-type: application/json' -H 'X-Dev-Roles: viewer' -d '{"article":"RBAC-WEB-DENIED"}'
curl -sS -o /tmp/p4-02-engineer.json -w '%{http_code}' -X POST http://127.0.0.1:8089/api/v1/models -H 'content-type: application/json' -H 'X-Dev-Roles: engineer' -d '{"article":"RBAC-WEB-ALLOWED"}'
curl -fsS 'http://127.0.0.1:8089/api/v1/models?query=ALLOWED' -H 'X-Dev-Roles: viewer'
curl -fsS http://127.0.0.1:8089/docs
```

Results:

- `pytest`: 5 passed.
- scaffold verifier: passed.
- viewer write smoke returned `403`.
- engineer write smoke returned `201`.
- viewer read smoke returned the created model.
- Swagger UI `/docs` loaded and referenced `/api/v1/openapi.json`.

## Next

P4-03: Model/Revision/Draft/Patch lifecycle with immutable commit and
optimistic locking.

