# P4-08 AuditEvent and Trace Correlation

Status: passed.

## Scope

- Added request trace propagation through `X-Trace-Id`; absent trace IDs are generated per request.
- Added immutable audit events for mutating API actions: model, draft, patch, commit, jobs, worker actions, preview/release, upload intent and upload completion.
- Added admin-only `GET /api/v1/audit-events` with filters by trace, resource type and resource id.
- Regenerated OpenAPI and TypeScript client support for audit events.

## Verification

- `.venv/bin/python scripts/generate_openapi.py`
- `.venv/bin/python scripts/generate_ts_client.py`
- `.venv/bin/python -m pytest` -> 11 passed.
- `.venv/bin/python scripts/verify_skeleton.py` -> passed.

## Web Smoke

Local API was started with SQLite on port 8095.

- `POST /api/v1/models` with `X-Trace-Id: tr_web_audit2` returned the same `X-Trace-Id` response header.
- `GET /api/v1/audit-events?traceId=tr_web_audit2&resourceType=model&resourceId=<model_id>` as admin returned the correlated `model.create` audit event.
- `GET /api/v1/audit-events` as viewer returned HTTP 403.
- `GET /docs` rendered Swagger UI for LANMASTER Studio.

## Gate

P4-08 is complete. Next checkpoint: P4-09 metrics, logs and trace dashboard skeleton.
