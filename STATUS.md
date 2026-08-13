# LANMASTER Studio Status

milestone: P0 Discovery, baseline and ADR

completed IDs:
- P0-01: repository scaffold, CI skeleton, issue labels, ownership metadata
- P0-02: inventoried current CAD generators, exporters, family routing and
  compatibility tests without editing `lanmaster-cad`
- P0-03: selected pilot candidates and recorded source hashes/gaps
- P0-04: partial only; recorded existing CBB baseline candidate evidence
- P0-04: partial source-cache update for wall-cabinet/open-frame pilots

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
- `docs/discovery/p0-02-cad-inventory.md`
- `docs/discovery/p0-03-source-manifest.yml`
- `docs/discovery/p0-04-baseline-candidates.md`
- `docs/discovery/p0-04-source-cache-update.md`
- `scripts/verify_skeleton.py`
- `../lanmaster-cad/sources/twt-cbwng/product.html`
- `../lanmaster-cad/sources/twt-cbwng/source.json`
- `../lanmaster-cad/sources/twt-frwaj-xu-gy/product.html`
- `../lanmaster-cad/sources/twt-frwaj-xu-gy/source.json`

test commands:
- `python3 scripts/verify_skeleton.py`
- `cd ../lanmaster-cad && .venv/bin/python - <<'PY' ...`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_golden.py tests/test_drawing_intake.py tests/test_change_report.py tests/test_revit_convert.py tests/test_rfa_extract.py -q`
- `cd ../lanmaster-cad && shasum -a 256 sources/twt-cbb-800/* sources/twt-cba/*`
- `find lanmaster-models/TWT-CBB-42U-8x10-P1 ...`
- `shasum -a 256 lanmaster-models/TWT-CBB-42U-8x10-P1/TWT-CBB-42U-8x10-P1.* lanmaster-models/TWT-CBB-42U-8x10-P1/src/*`
- `curl -sSL https://lanmaster.ru/twt-cbwng/ -o sources/twt-cbwng/product.html`
- `curl -sSL https://lanmaster.ru/twt-frwaj-xu-gy/ -o sources/twt-frwaj-xu-gy/product.html`
- `shasum -a 256 sources/twt-cbwng/product.html sources/twt-frwaj-xu-gy/product.html`
- `cd ../lanmaster-cad && python3 -m json.tool sources/twt-cbwng/source.json`
- `cd ../lanmaster-cad && python3 -m json.tool sources/twt-frwaj-xu-gy/source.json`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_rfa_extract.py -q`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_golden.py tests/test_drawing_intake.py tests/test_change_report.py tests/test_revit_convert.py tests/test_rfa_extract.py -q`

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

blockers:
- Gate P0 blocker resolved on branch `studio-p0-source-cache`: selected CAD
  compatibility suite is green after `784803de`.
- Gate P0 blocker: selected wall cabinet `TWT-CBWNG-12U-6x6-BK` and open frame
  `TWT-FRWAJ-12U-GY` now have cached official product pages, but still need
  drawing/table PDFs where available; `TWT-CBWNG-12U-6x6-BK` needs a v1 card;
  `TWT-FRWAJ-12U-GY` needs mass correction or known-defect approval.

next ID:
- P0-04 remains active; full baseline capture is blocked until source gaps and
  compatibility failure are resolved
