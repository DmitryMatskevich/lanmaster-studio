# LANMASTER Studio Status

milestone: P0 Discovery, baseline and ADR

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

decisions/ADR:
- ADR index created at `docs/adr/README.md`.
- API, frontend, editor and RAG are not scaffolded before PMD Stable gate P3.
- Remote branch protection is an external GitHub setting; local evidence is limited
  to CI and ownership configuration files.
- Pilot set starts with `TWT-CBB-42U-8x10-P1`, `TWT-CBWNG-12U-6x6-BK`,
  and `TWT-FRWAJ-12U-GY`; CBA is kept as documented fallback.
- `lanmaster-cad` source-cache changes are isolated on branch
  `studio-p0-source-cache`.

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
- `scripts/verify_skeleton.py`
- `../lanmaster-cad/sources/twt-cbwng/product.html`
- `../lanmaster-cad/sources/twt-cbwng/source.json`
- `../lanmaster-cad/sources/twt-frwaj-xu-gy/product.html`
- `../lanmaster-cad/sources/twt-frwaj-xu-gy/source.json`
- `../lanmaster-cad/params/TWT-CBWNG-12U-6x6-BK.yaml`
- `../lanmaster-cad/ids/wall_cabinet.IFC4.ids`
- `../lanmaster-cad/ids/wall_cabinet.IFC4X3.ids`

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

blockers:
- Gate P0 blocker resolved on branch `studio-p0-source-cache`: selected CAD
  compatibility suite is green after `784803de`.
- Gate P0 blocker: selected wall cabinet `TWT-CBWNG-12U-6x6-BK` and open frame
  `TWT-FRWAJ-12U-GY` now have cached official product pages and baseline
  candidates, but still need drawing/table PDFs where available and explicit
  known-defect approval/correction.

next ID:
- Gate P0 review remains blocked by incomplete P0-04 known-defect and immutable
  baseline evidence
