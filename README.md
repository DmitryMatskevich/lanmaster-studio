# LANMASTER Studio

Separate web application and orchestration workspace for LANMASTER Studio.

This repository owns the Studio application layer: web UI, API, workers orchestration,
audit, revision management, and future RAG/chat workflows. CAD geometry, PMD core,
compiler, geometry backends, exporters, and legacy compatibility remain in the
separate `lanmaster-cad` repository until their roadmap tasks explicitly require
changes there.

## Current Scope

Active roadmap checkpoint: P5-08 from `plan/lanmaster-studio/06-delivery-roadmap.md`.

The initial repository contains:

- CI skeleton for local and GitHub validation.
- Issue templates and labels for roadmap tracking.
- ADR directory for architecture decisions owned by Studio.
- P4-01 FastAPI scaffold, SQLite migrations, OpenAPI and generated TypeScript client.
- P4-02 dev/OIDC auth abstraction and RBAC contract.
- P4-03 model/revision/draft/patch lifecycle with optimistic locking.
- P4-04 SQLite-backed job queue and CAD worker protocol.
- P4-05 preview/release orchestration over queued jobs.
- P4-06 local object storage, upload verification and signed downloads.
- P4-07 durable REST/WebSocket event replay.
- P4-08 audit events and trace correlation across mutating API calls.
- P4-09 observability summary, Prometheus-style metrics and dashboard skeleton.
- P4-10 Docker Compose local API stack.
- P5-01 React/TypeScript frontend scaffold with routing, dev auth and API client wiring.
- P5-02 catalog search and revision selector.
- P5-03 virtualized component tree scaffold for large hierarchies.
- P5-04 Three.js viewer scaffold and resource lifecycle cleanup.
- P5-05 bidirectional tree/viewer component selection contract.
- P5-06 viewer tools scaffold for visibility, isolate, views, section, measure and exploded view.
- P5-07 schema-driven property editor scaffold.
- `STATUS.md` as the compact continuation log for Codex work.

API, frontend, editor, and RAG implementation may now start from P4 because
Gate P3 / PMD Stable has passed.

## Local Verification

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/generate_openapi.py
python scripts/generate_ts_client.py
pytest
python3 scripts/verify_skeleton.py
```

## Local API

```bash
. .venv/bin/activate
uvicorn studio_api.main:app --reload --port 8088
```

Useful URLs:

- `http://127.0.0.1:8088/health`
- `http://127.0.0.1:8088/api/v1/openapi.json`
- `http://127.0.0.1:8088/docs`
- `http://127.0.0.1:8088/api/v1/observability/dashboard`
- `http://127.0.0.1:8088/metrics`

## Docker Compose

```bash
docker compose up --build
```

The local container uses `.env.example` defaults, exposes the API on
`http://127.0.0.1:8088`, and persists SQLite plus uploaded artifacts in the
`studio-var` volume.

## Frontend

```bash
npm ci --prefix frontend
npm run frontend:build
npm run frontend:test
```

After `frontend:build`, FastAPI serves the editor scaffold from `/` when
`frontend/dist` exists.

## External Repository Setup

After creating the remote repository, configure:

- protected `main` branch;
- required CI status checks;
- CODEOWNERS review requirement;
- issue labels from `.github/labels.yml`.
