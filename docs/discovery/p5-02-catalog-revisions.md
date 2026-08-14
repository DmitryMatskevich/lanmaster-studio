# P5-02 Catalog, Search and Revision Selector

Status: passed.

## Scope

- Added `GET /api/v1/models/{model_id}/revisions`.
- Regenerated OpenAPI and TypeScript client with `RevisionList` and `listRevisions`.
- Catalog screen now auto-loads models and preserves loading, empty and error states.
- Search submits through the API client with query filtering.
- Model route now loads model metadata and revision list together.
- Added revision selector with active revision default and empty state for models without revisions.

## Verification

- `.venv/bin/python scripts/generate_openapi.py`
- `.venv/bin/python scripts/generate_ts_client.py`
- `.venv/bin/python -m pytest` -> 12 passed.
- `npm ci --prefix frontend`
- `npm audit --prefix frontend --audit-level=moderate` -> 0 vulnerabilities.
- `npm run frontend:build` -> passed.
- `npm run frontend:test` -> passed.

## Web Smoke

- Created a model, draft and committed revision through the API.
- `GET /api/v1/models/{model_id}/revisions` returned the committed revision.
- `GET /models/{model_id}` returned the React shell through FastAPI SPA fallback.
- `GET /assets/main.js` contained `listRevisions` and the `Revision selector` UI.

## Gate

P5-02 is complete. Next checkpoint: P5-03 tree component with virtualized large hierarchy.
