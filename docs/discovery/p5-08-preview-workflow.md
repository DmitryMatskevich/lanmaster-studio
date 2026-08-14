# P5-08 Patch Preview Workflow

Status: passed.

## Scope

- Added preview workflow panel on the model route.
- Wired property values into atomic `setParameter` patch operations.
- Workflow creates a draft, applies patch, reloads draft token and enqueues preview.
- Added UI states for idle, patching, queued, running and error.
- Added progress refresh, cancel and retry actions through the generated API client.

## Verification

- `npm ci --prefix frontend`
- `npm audit --prefix frontend --audit-level=moderate` -> 0 vulnerabilities.
- `npm run frontend:build` -> passed.
- `npm run frontend:test` -> passed.
- `.venv/bin/python -m pytest` -> 12 passed.
- `python3 scripts/verify_skeleton.py` -> passed.
- `python3 scripts/verify_compose.py` -> passed.

## Web Smoke

- Created a model and draft through the API.
- Applied a patch through `POST /api/v1/drafts/{draft_id}/patches`.
- Reloaded the draft token and enqueued preview through `POST /api/v1/drafts/{draft_id}/preview`.
- Preview returned `202 Accepted` with `jobId` and `eventsUrl`.
- `GET /assets/main.js` contained `Preview workflow`, `Preview patch`,
  `previewDraft`, `applyPatch`, `cancelJob` and `retryJob`.

## Gate

P5-08 is complete. Next checkpoint: P5-09 before/after, diff, QA panel, undo/redo.
