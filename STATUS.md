# LANMASTER Studio Status

milestone: P4 Studio API, data and workers
active ID: P5-11 Responsive, accessibility and visual E2E suite

completed IDs:
- P0-01: repository scaffold, CI skeleton, issue labels, ownership metadata
- P0-02: inventoried current CAD generators, exporters, family routing and
  compatibility tests without editing `lanmaster-cad`
- P0-03: selected pilot candidates and recorded source hashes/gaps
- P0-04: partial only; recorded existing CBB baseline candidate evidence
- P0-04: partial source-cache update for wall-cabinet/open-frame pilots
- P0-04: partial FRWAJ temporary export baseline candidate with known mass defect
- P0-04: failed CBWNG legacy baseline candidate with known geometry limitation
- P0-05: drafted ADR-0001 through ADR-0009 as proposed
- P0-06: drafted proposed preview SLOs, release gates and parity tolerances
- P0-07: scoped local toolchain smoke for PDF/HTML pilot sources and generated
  pilot artifacts
- Gate P0: passed with CBWNG/FRWAJ accepted as legacy-only red baselines
- P0 remediation: FRWAJ source-fact correction, controlled source-format
  fixtures, protected-main evidence and repeated Gate P0 review
- P1-01: PMD core entities, JSON Schema 2020-12, examples and negative fixtures
- P1-02: strict Pydantic models and shared schema-conformance corpus
- P1-03: units, canonical JSON and stable SHA-256 content hash
- P1-04: stable ID, reference, import hash/unit and interface validation
- P1-05: safe expression AST, dimensions, cycles and dependency graph
- P1-06: typed atomic patches, inverse, authorization and affected-set calculation
- P1-07: bounded declarative geometry MVP grammar
- P1-08: import-step and default-deny legacy-python contracts
- P1-09: acceptance specification separated from assembly and geometry
- P1-10: three structurally different PMD fixtures
- Gate P1: passed after independent review, remediation and repeated review
- P2-01: typed AssemblyIR and exporter-facing invariants with accepted CAD ADR
- P2-02: deterministic compiler for assembly, placements and interfaces
- P2-03: exact-B-Rep declarative backend including pinned SVG/DXF profiles
- P2-04: pinned local STEP backend with pre-cache hash/unit/shape verification
- P2-05: default-deny legacy backend with explicit registry and bounded builtin
- P2-06: cloned component cache, content keys and affected-set invalidation
- P2-07: stable GLB IDs/extras plus structural GLB 2.0 validation and read-back
- P2-08: stable STEP/IFC IDs and deterministic IFC GUID/read-back contracts
- P2-09: DXF2D/DXF3D IDs/layers/views and SHA-256 release manifest
- P2-10: read-only acceptance runner and non-publishable preview contract
- P2-11: explicit v1 adapter/dispatcher without changing old CLI routing
- P2-12: `pmd validate/preview/release/compare` headless CLI workflow
- Gate P2: passed after two independent reviews and remediation of all findings
- P3-01: v1 to PMD converter and migration report
- P3-02: headless PDF/SVG/DXF/DWG/STEP intake with provenance and diagnostics
- P3-03: complex floor cabinet pilot migrated through PMD
- P3-04: wall cabinet pilot represented without unverified component reuse
- P3-05: open frame pilot represented without cabinet-required schema fields
- P3-06: non-cabinet PDU/imported STEP pilot represented
- P3-07: declarative, import-step and legacy backends covered by pilots
- P3-08: input/output format matrix completed
- P3-09: legacy/PMD semantic parity completed
- P3-10: PMD 2.0 stable contract and schema compatibility suite completed
- P3-11: catalog migration cost/classification evidence completed
- Gate P3: passed; PMD Stable is complete
- P4-01: FastAPI scaffold, SQLite migration runner, OpenAPI generation,
  generated TypeScript client and API contract tests
- P4-02: dev/OIDC auth abstraction and RBAC with negative tests
- P4-03: Model/Revision/Draft/Patch lifecycle with immutable commit and
  optimistic locking
- P4-04: Queue and CAD worker protocol with idempotency, cancel, retry,
  claim and heartbeat
- P4-05: Preview/release orchestration returning 202 jobs and queued releases
- P4-06: Object storage and signed URLs with hash/size verification
- P4-07: WebSocket events and REST replay
- P4-08: AuditEvent and trace correlation with admin-only query API
- P4-09: metrics, logs and trace dashboard skeleton
- P4-10: Docker Compose local stack
- Gate P4: passed; API/data/workers MVP is ready for P5 editor scaffolding
- P5-01: React/TypeScript app scaffold, routing, dev auth and API client
- P5-02: catalog, search and revision selector
- P5-03: virtualized tree component with 1000-node fixed-row hierarchy
- P5-04: Three.js viewer scaffold and resource lifecycle cleanup
- P5-05: bidirectional tree/viewer selection using componentId
- P5-06: viewer tools scaffold for visibility, isolate, views, section, measure and exploded view
- P5-07: schema-driven property editor scaffold
- P5-08: patch to preview workflow with progress, cancel and retry states
- P5-09: before/after diff, QA panel and undo/redo scaffold
- P5-10: commit, revision history and release UI scaffold

decisions/ADR:
- ADR index created at `docs/adr/README.md`.
- API, frontend, editor and RAG may start from P4 after PMD Stable gate P3.
- P4-01 uses SQLite for the local MVP stack; production database/provider
  remains a P4/P7 deployment decision.
- Remote branch protection is an external GitHub setting; local evidence is limited
  to CI and ownership configuration files.
- Pilot set starts with `TWT-CBB-42U-8x10-P1`, `TWT-CBWNG-12U-6x6-BK`,
  and `TWT-FRWAJ-12U-GY`; CBA is kept as documented fallback.
- `lanmaster-cad` P0/P1 changes were merged to `main` by PR #1 at `4a172c40`.
- `lanmaster-cad` P2 changes were merged to `main` by PR #2 at `a6864229`.
- PMD release uses staging and requires non-empty acceptance and geometry.
- STEP AP242 qualification is covered by P3 format-matrix evidence.

changed files:
- `README.md`
- `.gitignore`
- `STATUS.md`
- `.github/workflows/ci.yml`
- `.github/labels.yml`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/roadmap_task.yml`
- `docs/adr/README.md`
- `docs/adr/0001-repository-boundary-and-sdk-delivery.md`
- `docs/adr/0002-job-queue.md`
- `docs/adr/0003-object-storage-lifecycle.md`
- `docs/adr/0004-stable-component-identifiers.md`
- `docs/adr/0005-pmd-canonical-serialization.md`
- `docs/adr/0006-partial-preview-cache.md`
- `docs/adr/0007-llm-provider-and-data-retention.md`
- `docs/adr/0008-release-gates.md`
- `docs/adr/0009-openusd-after-mvp.md`
- `docs/discovery/p0-02-cad-inventory.md`
- `docs/discovery/p0-03-source-manifest.yml`
- `docs/discovery/p0-04-baseline-candidates.md`
- `docs/discovery/p0-04-source-cache-update.md`
- `docs/discovery/p0-06-slo-gates-and-tolerances.md`
- `docs/discovery/p0-07-toolchain-smoke.md`
- `docs/discovery/p0-gate-review.md`
- `docs/discovery/p0-protected-main-evidence.md`
- `docs/discovery/p0-immutable-baseline-manifest.yml`
- `docs/discovery/p0-adr-slo-decision-package.md`
- `docs/discovery/p1-gate-review.md`
- `docs/discovery/p2-gate-review.md`
- `docs/discovery/p4-01-api-scaffold.md`
- `docs/discovery/p4-02-auth-rbac.md`
- `docs/discovery/p4-03-lifecycle.md`
- `docs/discovery/p4-04-queue-worker.md`
- `docs/discovery/p4-05-orchestration.md`
- `docs/discovery/p4-06-storage.md`
- `docs/discovery/p4-07-events.md`
- `docs/discovery/p4-08-audit.md`
- `docs/discovery/p4-09-observability.md`
- `docs/discovery/p4-10-docker-compose.md`
- `docs/discovery/p4-gate-review.md`
- `docs/discovery/p5-01-frontend-scaffold.md`
- `docs/discovery/p5-02-catalog-revisions.md`
- `docs/discovery/p5-03-virtualized-tree.md`
- `docs/discovery/p5-04-three-viewer.md`
- `docs/discovery/p5-05-selection-sync.md`
- `docs/discovery/p5-06-viewer-tools.md`
- `docs/discovery/p5-07-property-editor.md`
- `docs/discovery/p5-08-preview-workflow.md`
- `docs/discovery/p5-09-diff-qa-undo.md`
- `scripts/verify_skeleton.py`
- `scripts/verify_source_fixtures.py`
- `pyproject.toml`
- `requirements.txt`
- `studio_api/__init__.py`
- `studio_api/config.py`
- `studio_api/db.py`
- `studio_api/main.py`
- `studio_api/models.py`
- `studio_api/repository.py`
- `migrations/0001_p4_01_core.sql`
- `scripts/init_db.py`
- `scripts/generate_openapi.py`
- `scripts/generate_ts_client.py`
- `openapi/openapi.json`
- `clients/typescript/src/index.ts`
- `tests/test_api_contract.py`
- `tests/test_generated_artifacts.py`
- `test-fixtures/source-formats/README.md`
- `test-fixtures/source-formats/manifest.yml`
- `test-fixtures/source-formats/minimal-panel.svg`
- `test-fixtures/source-formats/minimal-panel.dxf`
- `test-fixtures/source-formats/minimal-panel.dwg`
- `test-fixtures/source-formats/frwaj-open-frame.step`
- `../lanmaster-cad/sources/twt-cbwng/product.html`
- `../lanmaster-cad/sources/twt-cbwng/source.json`
- `../lanmaster-cad/sources/twt-frwaj-xu-gy/product.html`
- `../lanmaster-cad/sources/twt-frwaj-xu-gy/source.json`
- `../lanmaster-cad/params/TWT-CBWNG-12U-6x6-BK.yaml`
- `../lanmaster-cad/params/TWT-FRWAJ-12U-GY.yaml`
- `../lanmaster-cad/ids/wall_cabinet.IFC4.ids`
- `../lanmaster-cad/ids/wall_cabinet.IFC4X3.ids`
- `../lanmaster-cad/lmcad/pmd/schema/pmd-2.0.schema.json`
- `../lanmaster-cad/lmcad/pmd/__init__.py`
- `../lanmaster-cad/lmcad/pmd/io.py`
- `../lanmaster-cad/lmcad/pmd/models.py`
- `../lanmaster-cad/lmcad/pmd/README.md`
- `../lanmaster-cad/lmcad/pmd/canonical.py`
- `../lanmaster-cad/lmcad/pmd/expressions.py`
- `../lanmaster-cad/lmcad/pmd/patches.py`
- `../lanmaster-cad/lmcad/pmd/validation.py`
- `../lanmaster-cad/lmcad/pmd/examples/minimal_open_frame.json`
- `../lanmaster-cad/lmcad/pmd/fixtures/negative/missing_assembly.json`
- `../lanmaster-cad/lmcad/pmd/fixtures/negative/top_level_door.json`
- `../lanmaster-cad/lmcad/pmd/fixtures/negative/unsafe_geometry_backend.json`
- `../lanmaster-cad/tests/test_pmd_schema.py`
- `../lanmaster-cad/tests/test_pmd_models.py`
- `../lanmaster-cad/tests/test_pmd_canonical.py`
- `../lanmaster-cad/tests/test_pmd_contracts.py`
- `../lanmaster-cad/tests/test_pmd_expressions.py`
- `../lanmaster-cad/tests/test_pmd_patches.py`
- `../lanmaster-cad/tests/test_pmd_structural_fixtures.py`
- `../lanmaster-cad/tests/test_pmd_validation.py`
- `../lanmaster-cad/requirements.lock`
- `docs/discovery/p4-01-api-scaffold.md`
- `docs/discovery/p4-02-auth-rbac.md`

test commands:
- `python3 scripts/verify_skeleton.py`
- `cd ../lanmaster-cad && pdfinfo sources/twt-cbb-800/drawing_cbb800_f404.pdf`
- `cd ../lanmaster-cad && pdftotext sources/twt-cbb-800/table_cbb_f400.pdf -`
- `cd ../lanmaster-cad && .venv/bin/python - <<'PY' ... STEP/DXF/IFC/GLB parser smoke ...`
- `cd ../lanmaster-cad && pdfinfo -v`
- `cd ../lanmaster-cad && dwgread --version`
- `cd ../lanmaster-cad && .venv/bin/python - <<'PY' ...`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_golden.py tests/test_drawing_intake.py tests/test_change_report.py tests/test_revit_convert.py tests/test_rfa_extract.py -q`
- `cd ../lanmaster-cad && shasum -a 256 sources/twt-cbb-800/* sources/twt-cba/*`
- `find lanmaster-models/TWT-CBB-42U-8x10-P1 ...`
- `shasum -a 256 lanmaster-models/TWT-CBB-42U-8x10-P1/TWT-CBB-42U-8x10-P1.* lanmaster-models/TWT-CBB-42U-8x10-P1/src/*`
- `cd ../lanmaster-cad && .venv/bin/python -m lmcad.cli build params/TWT-FRWAJ-12U-GY.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300`
- `cd ../lanmaster-cad && .venv/bin/python -m lmcad.cli export params/TWT-FRWAJ-12U-GY.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300`
- `cd ../lanmaster-cad && .venv/bin/python -m lmcad.cli build params/TWT-CBWNG-12U-6x6-BK.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300`
- `cd ../lanmaster-cad && .venv/bin/python -m lmcad.cli export params/TWT-CBWNG-12U-6x6-BK.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300 --no-strict`
- `shasum -a 256 /private/tmp/lanmaster-studio-p0-baseline/TWT-CBWNG-12U-6x6-BK/TWT-CBWNG-12U-6x6-BK.* /private/tmp/lanmaster-studio-p0-baseline/TWT-CBWNG-12U-6x6-BK/views/*`
- `shasum -a 256 /private/tmp/lanmaster-studio-p0-baseline/TWT-FRWAJ-12U-GY/TWT-FRWAJ-12U-GY.* /private/tmp/lanmaster-studio-p0-baseline/TWT-FRWAJ-12U-GY/views/*`
- `curl -sSL https://lanmaster.ru/twt-cbwng/ -o sources/twt-cbwng/product.html`
- `curl -sSL https://lanmaster.ru/twt-frwaj-xu-gy/ -o sources/twt-frwaj-xu-gy/product.html`
- `shasum -a 256 sources/twt-cbwng/product.html sources/twt-frwaj-xu-gy/product.html`
- `cd ../lanmaster-cad && python3 -m json.tool sources/twt-cbwng/source.json`
- `cd ../lanmaster-cad && python3 -m json.tool sources/twt-frwaj-xu-gy/source.json`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_rfa_extract.py -q`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_golden.py tests/test_drawing_intake.py tests/test_change_report.py tests/test_revit_convert.py tests/test_rfa_extract.py -q`
- `python3 scripts/verify_skeleton.py`
- `find ../lanmaster-cad/sources -type f \( -iname '*.svg' -o -iname '*.dwg' -o -iname '*.dxf' -o -iname '*.step' -o -iname '*.stp' -o -iname '*.ifc' -o -iname '*.glb' \) -print`
- `find ../lanmaster-cad -path '*/.git' -prune -o -path '*/.venv' -prune -o -path '*/out' -prune -o -path '*/tmp' -prune -o -type f \( -iname '*.svg' -o -iname '*.dwg' -o -iname '*.dxf' -o -iname '*.step' -o -iname '*.stp' -o -iname '*.ifc' -o -iname '*.glb' \) -print`
- `cd ../lanmaster-cad && .venv/bin/python -m lmcad.cli export params/TWT-FRWAJ-12U-GY.yaml --out /private/tmp/lanmaster-studio-p0-immutable-baseline --lod 300`
- `../lanmaster-cad/.venv/bin/python scripts/verify_source_fixtures.py`
- `git remote -v`
- `git branch --show-current`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_pmd_schema.py -q`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_pmd_schema.py tests/test_pmd_models.py -q`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest -q`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest -q tests/test_pmd_schema.py tests/test_pmd_models.py tests/test_pmd_canonical.py tests/test_pmd_validation.py tests/test_pmd_expressions.py tests/test_pmd_patches.py tests/test_pmd_contracts.py tests/test_pmd_structural_fixtures.py`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest -q tests/test_pmd_ir.py tests/test_pmd_evaluation.py tests/test_pmd_compiler.py tests/test_pmd_declarative_backend.py tests/test_pmd_import_step_backend.py tests/test_pmd_legacy_backend.py tests/test_pmd_cache.py tests/test_pmd_exporters.py tests/test_pmd_verification.py tests/test_pmd_manifest.py tests/test_pmd_v1_adapter.py tests/test_pmd_workflow.py`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest -q`
- `cd ../lanmaster-cad && .venv/bin/python -m lmcad.cli pmd release lmcad/pmd/examples/minimal_open_frame.json --out /tmp/pmd-p2-cli-smoke --profile baseline`
- `python3 -m venv .venv`
- `.venv/bin/pip install -r requirements.txt`
- `.venv/bin/python scripts/init_db.py`
- `.venv/bin/python scripts/generate_openapi.py`
- `.venv/bin/python scripts/generate_ts_client.py`
- `.venv/bin/python -m pytest`
- `.venv/bin/python scripts/verify_skeleton.py`

results:
- PASS: P0-01 scaffold verification passed
- PASS: catalog inventory found 1876 schema v1 cards and 0 YAML read errors
- PASS: P0 scaffold verification passed
- FAIL: selected CAD compatibility suite: 48 passed, 1 failed, 10 warnings in
  131.86s. Failure:
  `tests/test_rfa_extract.py::test_compare_with_card_uses_generated_parts`
  expected generated part count 100, current result is 108.
- RESOLVED: RFA comparison report now includes `base` prefix inventory;
  focused RFA tests pass.
- PASS: source hashes recorded for cached CBB and CBA official PDFs/text files
- PASS: P0 scaffold verification passed with P0-03 source manifest
- PARTIAL: CBB existing release artifact set recorded as baseline candidate;
  manifest timestamp is 2026-08-10 14:04:27 +0300, before current CAD commit.
- PASS: P0 scaffold verification passed with P0-04 baseline-candidate note
- PARTIAL: official product pages cached for `TWT-CBWNG-12U-6x6-BK` and
  `TWT-FRWAJ-12U-GY`; hashes recorded.
- PASS: source metadata JSON validates for both cached product pages.
- PASS: P0 scaffold verification passed with source-cache update.
- PASS: selected CAD compatibility suite now passes: 49 passed, 10 warnings in
  130.15s on `lanmaster-cad` branch `studio-p0-source-cache`.
- PASS: P0 scaffold verification passed after recording compatibility fix.
- PASS: P0 scaffold verification passed after P0-05 ADR update.
- PARTIAL: FRWAJ build/export to temp baseline passed; STEP/STP/IGES/IFC4/IFC4X3/GLB/DXF/PDF/PNG hashes recorded.
- KNOWN DEFECT: FRWAJ mass remains implausible at about 743 kg; official page does not publish mass.
- PASS: P0 scaffold verification passed after FRWAJ baseline-candidate update.
- PASS: P0 scaffold verification passed after P0-06 checklist update.
- PARTIAL: P0-07 toolchain smoke passed for PDF metadata and generated STEP/DXF/IFC/GLB pilot artifacts.
- GAP: no real SVG/DWG/source-CAD files exist in current pilot source cache; PDF table text extraction was empty.
- PASS: P0 scaffold verification passed after P0-07 smoke report update.
- PARTIAL: CBWNG card added on `lanmaster-cad` branch `studio-p0-source-cache` at `9607ef51`.
- KNOWN DEFECT: CBWNG legacy build/export fails official bbox X/Y because current v1 route models a door kit, not a full wall cabinet.
- PASS: P0 scaffold verification passed after CBWNG baseline-candidate update.
- PASS: selected CAD compatibility suite still passes after CBWNG card/IDS update:
  49 passed, 10 warnings in 122.67s.
- PASS: P0-07 pilot source matrix scoped to official PDF/HTML/JSON cache
  evidence; source-CAD intake remains P3/P6 because no selected pilot has
  official SVG/DWG/DXF/STEP source fixtures.
- PASS: `../lanmaster-cad/sources` search found no source-CAD files.
- NOTE: broader CAD search excluding `.git`, `.venv`, `out` and `tmp` found one
  IFC request attachment under `var/requests/inbox/LMREQ-2026-000015`; it is
  not an official selected-pilot source fixture.
- PASS: P0 scaffold verification passed after P0-07 scope update.
- BLOCKED: Gate P0 review recorded; P0 is not passed because immutable baseline
  storage and domain/QA known-defect approval or corrections are still missing.
- BLOCKED: both `$run-agents` workers failed before doing work because their
  execution host `/Users/dmitrij/.local/bin/codex-code-mode-host` was missing.
- PARTIAL: FRWAJ source fact corrected in CAD card: `net_weight_kg` is now null
  because official source metadata does not publish item mass.
- BLOCKED: corrected FRWAJ export verifies geometry but exits 1 because IFC4 and
  IFC4X3 IDS fail without NetWeight.
- PASS: controlled SVG/DXF/DWG/STEP source-format fixtures verify with
  `../lanmaster-cad/.venv/bin/python scripts/verify_source_fixtures.py`.
- BLOCKED: protected-main evidence is local only; `git remote -v` produced no
  configured remote, so branch protection cannot be verified.
- PASS: focused CAD regression after FRWAJ source-fact correction:
  37 passed, 10 warnings in 120.65s.
- PASS: P0 scaffold verification passed after P0 remediation evidence update.
- PASS: GitHub remote created at
  `https://github.com/DmitryMatskevich/lanmaster-studio`.
- PASS: repository made public by explicit command approval so branch protection
  can be enabled on this account.
- PASS: protected main read-back: strict status check `Repository skeleton`,
  admin enforcement, no force pushes/deletions, conversation resolution required.
  Required review was removed from protection because a single-owner repository
  had no separate reviewer/code-owner available; CI protection remains enforced.
- PASS: ADR-0001 through ADR-0009 accepted by user instruction on 2026-08-13.
- PASS: P0-06 SLO/release/parity package accepted by user instruction on
  2026-08-13; known defects remain non-release baseline evidence only.
- PASS: immutable baseline manifest recorded at
  `docs/discovery/p0-immutable-baseline-manifest.yml`.
- PASS: Gate P0 passed for P1 entry; API/frontend/editor/RAG remain blocked
  until Gate P3 / PMD Stable.
- PASS: full `lanmaster-cad` pytest suite passed after Gate P0 update:
  106 passed, 10 warnings, 6 subtests passed in 144.15s.
- PASS: P1-01 PMD schema tests passed: 3 passed in 1.08s.
- PASS: full `lanmaster-cad` pytest suite passed after P1-01:
  109 passed, 10 warnings, 6 subtests passed in 153.55s.
- PASS: P1-02 focused PMD schema/model conformance suite passed:
  13 passed in 0.36s.
- PASS: full `lanmaster-cad` pytest suite passed after P1-02:
  119 passed, 10 warnings, 6 subtests passed in 150.67s.
- BLOCKED: `$run-agents` review worker could not inspect because
  `/Users/dmitrij/.local/bin/codex-code-mode-host` is missing.
- PASS: coordinator local review completed for P1-02; no P1-03 canonical JSON,
  content-hash, dependency-graph or semantic-reference implementation was
  introduced.
- PASS: P1-03 through P1-10 implemented and merged to `lanmaster-cad/main` by
  PR #1 at `4a172c40`.
- PASS: PMD schema/model/core suite: 83 passed in 0.75s.
- PASS: full `lanmaster-cad` suite: 189 passed, 10 warnings, 6 subtests passed
  in 158.40s.
- PASS: independent Gate P1 review findings were fixed; repeated read-only
  review found no High/Medium findings and returned Gate P1 PASS.
- PASS: Gate P1 evidence recorded in `docs/discovery/p1-gate-review.md`.
- PASS: P2 focused suite: 75 passed with only existing ezdxf/pyparsing warnings.
- PASS: full CAD regression after P2 remediation: 264 passed, 22 warnings,
  6 subtests passed in 167.39s.
- PASS: real PMD CLI release emitted STEP, IFC4, IFC4X3, GLB, DXF2D and report;
  manifest was publishable and all six artifact hashes matched.
- PASS: first independent P2 review found two High and four Medium defects;
  cache preflight, release gates/staging, B-Rep compare, IFC GUID scope and
  backend wiring were remediated with negative tests.
- PASS: repeated independent review found no High/Medium findings and returned
  Gate P2 PASS.
- PASS: P4-01 API scaffold contract tests passed: 3 passed.
- PASS: P4-01 web smoke passed through local Uvicorn: health, OpenAPI,
  model create/list and Swagger UI `/docs`.
- PASS: P4-02 auth/RBAC tests passed: 5 passed.
- PASS: P4-02 web smoke passed: viewer write denied, engineer write allowed,
  viewer read allowed and Swagger UI loaded.
- PASS: P4-03 lifecycle tests passed: 6 passed.
- PASS: P4-03 web smoke passed: stale patch rejected, patch accepted, commit
  created immutable revision and model became published.
- PASS: P4-04 queue/worker tests passed: 7 passed.
- PASS: P4-04 web smoke passed: idempotent enqueue, claim, heartbeat, cancel,
  retry and read state.
- PASS: P4-05 orchestration tests passed: 8 passed.
- PASS: P4-05 web smoke passed: preview 202, release 202, release read 200 and
  Swagger UI loaded.
- PASS: P4-06 storage tests passed: 9 passed.
- PASS: P4-06 web smoke passed: upload intent, hash/size checked complete,
  signed URL and actual download bytes.
- PASS: P4-07 events tests passed: 10 passed.
- PASS: P4-07 web smoke passed: durable REST event replay for job queued,
  running and heartbeat events.
- PASS: P4-08 audit tests passed: 11 passed.
- PASS: P4-08 web smoke passed: trace header, admin audit query, viewer 403
  and Swagger UI loaded.
- PASS: P4-09 observability tests passed: 12 passed.
- PASS: P4-09 web smoke passed: summary, `/metrics`, dashboard and Swagger UI.
- PASS: P4-10 Docker Compose local stack passed: pytest, scaffold verifier,
  compose verifier, `docker compose config`, container build/start, `/health`,
  `/metrics` and Swagger UI.
- PASS: Gate P4 verification passed: regenerated OpenAPI/client, 12 API tests,
  skeleton verifier, compose verifier, compose config and Docker web smoke.
- PASS: P5-01 frontend scaffold build/test/audit passed: `npm ci --prefix
  frontend`, `npm audit --prefix frontend --audit-level=moderate`,
  `npm run frontend:build`, `npm run frontend:test`.
- PASS: P5-02 API/frontend tests passed: 12 API tests, frontend audit/build/test,
  revision list API smoke and frontend `/models/{id}` route smoke.
- PASS: P5-03 frontend/API tests passed: virtualized tree verifier,
  frontend audit/build/test, 12 API tests and route/bundle web smoke.
- PASS: P5-04 frontend/API tests passed: Three.js viewer verifier,
  frontend audit/build/test, 12 API tests and route/bundle browser smoke.
- PASS: P5-05 frontend/API tests passed: selected component verifier,
  frontend audit/build/test, 12 API tests and route/bundle browser smoke.
- PASS: P5-06 frontend/API tests passed: viewer tools verifier,
  frontend audit/build/test, 12 API tests and route/bundle browser smoke.
- PASS: P5-07 frontend/API tests passed: property editor verifier,
  frontend audit/build/test, 12 API tests and route/bundle browser smoke.
- PASS: P5-08 frontend/API tests passed: preview workflow verifier,
  frontend audit/build/test, 12 API tests and API patch/preview web smoke.
- PASS: P5-09 frontend/API tests passed: diff/QA/undo verifier,
  frontend audit/build/test, 12 API tests and route/bundle browser smoke.

blockers:
- none for Gate P4.

next ID:
- P5-10: Commit, revision, history and release UI
