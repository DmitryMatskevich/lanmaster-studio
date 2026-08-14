# P5-11 Responsive, Accessibility And Visual E2E Suite

## Scope

P5-11 adds browser-based verification for the Studio editor scaffold across a
desktop viewport and a narrow viewport.

## Implemented

- Added Playwright Chromium E2E coverage launched by `npm --prefix frontend run
  test:e2e`.
- The E2E script starts the FastAPI app against an isolated SQLite database,
  creates a model through the public API, opens `/models/{id}`, and exercises
  viewer tool controls.
- Desktop and narrow screenshots are written to `frontend/e2e-artifacts/`.
- The test validates:
  - the rendered viewer canvas is nonblank using PNG pixel inspection;
  - the workspace has an accessible `main` label;
  - expected editor headings are present;
  - key model workspace panels do not overlap in either viewport.
- CI installs Playwright Chromium and runs the E2E suite after frontend build and
  static checks.

## Verification

- `npx --prefix frontend playwright install chromium`
- `npm run frontend:build`
- `npm run frontend:test`
- `PYTHON=.venv/bin/python npm --prefix frontend run test:e2e`

Screenshots generated locally:

- `frontend/e2e-artifacts/desktop.png`
- `frontend/e2e-artifacts/narrow.png`
