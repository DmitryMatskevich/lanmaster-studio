# P5-06 Viewer Tools

Status: passed.

## Scope

- Added icon-only viewer toolbar with tooltips and accessible labels.
- Added modes for visibility, isolate, saved views, section, measure and exploded view.
- Wired isolate, section, measure and exploded modes to viewer state.
- Added fixed-dimension measure readout.

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
- `GET /assets/main.js` contained `Viewer tools`, `Visibility`, `Isolate`,
  `Section`, `Measure`, `Exploded view`, `viewerMode` and `measure-readout`.
- The local UI route was opened in the Codex browser panel.

## Gate

P5-06 is complete. Next checkpoint: P5-07 schema-driven property editor.
