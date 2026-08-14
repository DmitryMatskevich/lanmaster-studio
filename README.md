# LANMASTER Studio

Separate web application and orchestration workspace for LANMASTER Studio.

This repository owns the Studio application layer: web UI, API, workers orchestration,
audit, revision management, and future RAG/chat workflows. CAD geometry, PMD core,
compiler, geometry backends, exporters, and legacy compatibility remain in the
separate `lanmaster-cad` repository until their roadmap tasks explicitly require
changes there.

## Current Scope

Active roadmap checkpoint: P4-02 from `plan/lanmaster-studio/06-delivery-roadmap.md`.

The initial repository contains:

- CI skeleton for local and GitHub validation.
- Issue templates and labels for roadmap tracking.
- ADR directory for architecture decisions owned by Studio.
- P4-01 FastAPI scaffold, SQLite migrations, OpenAPI and generated TypeScript client.
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

## External Repository Setup

After creating the remote repository, configure:

- protected `main` branch;
- required CI status checks;
- CODEOWNERS review requirement;
- issue labels from `.github/labels.yml`.
