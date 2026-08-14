# P5-05 Tree and Viewer Selection

Status: passed.

## Scope

- Added shared `selectedComponentId` state on the model route.
- Tree rows select component IDs and reflect the selected row.
- Three.js viewer assigns `userData.componentId` and uses raycasting on canvas pointer events.
- Viewer selection calls back into the shared selection state.
- Selected viewer component is highlighted through material color.

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
- `GET /assets/main.js` contained `selectedComponentId`, `componentId`,
  `Raycaster`, `pointerdown` and selected tree-row logic.
- The local UI route was opened in the Codex browser panel.

## Gate

P5-05 is complete. Next checkpoint: P5-06 visibility, isolate, views, section,
measure and exploded view.
