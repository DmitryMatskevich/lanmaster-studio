# LANMASTER Studio Status

milestone: P0 Discovery, baseline and ADR

completed IDs:
- P0-01: repository scaffold, CI skeleton, issue labels, ownership metadata
- P0-02: inventoried current CAD generators, exporters, family routing and
  compatibility tests without editing `lanmaster-cad`

decisions/ADR:
- ADR index created at `docs/adr/README.md`.
- API, frontend, editor and RAG are not scaffolded before PMD Stable gate P3.
- Remote branch protection is an external GitHub setting; local evidence is limited
  to CI and ownership configuration files.

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
- `scripts/verify_skeleton.py`

test commands:
- `python3 scripts/verify_skeleton.py`
- `cd ../lanmaster-cad && .venv/bin/python - <<'PY' ...`
- `cd ../lanmaster-cad && .venv/bin/python -m pytest tests/test_golden.py tests/test_drawing_intake.py tests/test_change_report.py tests/test_revit_convert.py tests/test_rfa_extract.py -q`

results:
- PASS: P0-01 scaffold verification passed
- PASS: catalog inventory found 1876 schema v1 cards and 0 YAML read errors
- PASS: P0 scaffold verification passed
- FAIL: selected CAD compatibility suite: 48 passed, 1 failed, 10 warnings in
  131.86s. Failure:
  `tests/test_rfa_extract.py::test_compare_with_card_uses_generated_parts`
  expected generated part count 100, current result is 108.

blockers:
- Gate P0 blocker: selected existing CAD compatibility suite is not green on
  current `lanmaster-cad` main. Needs regression fix or explicit known-defect
  baseline approval before Gate P0.

next ID:
- P0-03
