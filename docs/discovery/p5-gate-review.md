# Gate P5 Review

Result: passed.

## Gate Criteria

The Editor MVP gate requires a user, without chat, to open a checked PMD model,
select a component, change an allowed parameter, get a preview, see a diff, and
create a revision. The editor must not define PMD semantics through client-side
exceptions.

## Evidence

- The API exposes immutable revision details through `GET /api/v1/revisions/{id}`
  so the UI can read the committed PMD payload instead of inventing component
  hierarchy on the client.
- The model route derives component tree and editable numeric properties from the
  selected PMD revision.
- Commit preserves the current PMD structure and updates only the edited
  parameters, preventing loss of assembly/component metadata across revisions.
- The Playwright E2E test creates a published PMD fixture through public API
  calls, opens `/models/{id}`, selects the mounting rail component, changes the
  allowed `width` parameter, runs preview, verifies diff visibility, commits a
  revision, and repeats the flow on desktop and narrow viewports.
- The E2E suite verifies nonblank viewer canvas pixels, accessible workspace
  labelling, required editor headings and no overlap between key panels.

## Verification

- `.venv/bin/python scripts/generate_openapi.py`
- `.venv/bin/python scripts/generate_ts_client.py`
- `.venv/bin/python -m pytest`
- `python3 scripts/verify_skeleton.py`
- `python3 scripts/verify_compose.py`
- `npm ci --prefix frontend`
- `npm audit --prefix frontend --audit-level=moderate`
- `npm run frontend:build`
- `npm run frontend:test`
- `PYTHON=.venv/bin/python npm --prefix frontend run test:e2e`

Gate P5 is complete. Next checkpoint: P6-01 production document/artifact upload
lifecycle and isolated ingestion pool.
