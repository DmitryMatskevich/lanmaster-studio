# P5-09 Diff, QA and Undo

Status: passed.

## Scope

- Added before/after property baseline tracking.
- Added diff table showing old and new values with units.
- Added QA panel note that patch is visible before commit and release remains outside draft workflow.
- Added undo and redo stacks for property edits.
- Added accept-baseline action.

## Verification

- `npm ci --prefix frontend`
- `npm audit --prefix frontend --audit-level=moderate` -> 0 vulnerabilities.
- `npm run frontend:build` -> passed.
- `npm run frontend:test` -> passed.
- `.venv/bin/python -m pytest` -> 12 passed.
- `python3 scripts/verify_skeleton.py` -> passed.
- `python3 scripts/verify_compose.py` -> passed.

## Web Smoke

- `GET /models/demo` returned the React shell through FastAPI SPA fallback.
- `GET /assets/main.js` contained `Diff / QA`, `Undo`, `Redo`,
  `Accept baseline`, `patch visible before commit` and `diff-table`.
- The local UI route was opened in the Codex browser panel.

## Gate

P5-09 is complete. Next checkpoint: P5-10 commit, revision, history and release UI.
