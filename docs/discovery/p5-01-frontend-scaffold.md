# P5-01 Frontend Scaffold

Status: passed.

## Scope

- Added React/TypeScript frontend package under `frontend/`.
- Added lightweight browser routing for `/models`, `/models/new` and `/models/:modelId`.
- Wired dev-auth session headers into the generated TypeScript API client.
- Added a model list screen, create-model screen and model route screen.
- Added responsive CSS with compact operational layout.
- Added static frontend serving from FastAPI when `frontend/dist` exists.
- Updated Dockerfile to build the frontend in a Node stage and copy `frontend/dist` into the API image.
- Added CI checks for frontend install, audit, build and scaffold verifier.

## Verification

- `npm ci --prefix frontend`
- `npm audit --prefix frontend --audit-level=moderate` -> 0 vulnerabilities.
- `npm run frontend:build` -> passed.
- `npm run frontend:test` -> passed.
- `.venv/bin/python -m pytest` -> 12 passed.
- `python3 scripts/verify_skeleton.py` -> passed.
- `python3 scripts/verify_compose.py` -> passed.
- `docker compose up --build -d` -> frontend stage built with `npm ci` reporting 0 vulnerabilities.

## Web Smoke

- `GET /models` and `GET /models/new` return the React shell through FastAPI SPA fallback.
- `GET /assets/main.js` returns the frontend bundle with generated API client auth headers.
- `GET /api/v1/auth/me` with dev headers returns the engineer session.
- Docker compose smoke verified `/models/new`, bundle delivery and API auth, then stopped the stack with `docker compose down`.

## Gate

P5-01 is complete. Next checkpoint: P5-02 catalog, search and revision selector.
