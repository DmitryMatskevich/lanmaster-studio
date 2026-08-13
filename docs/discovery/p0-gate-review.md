# P0 Gate Review

Status: passed.

Evidence date: 2026-08-13.

## Gate Criteria

| Criterion | Evidence | Result |
|---|---|---|
| Separate `lanmaster-studio` repo exists | P0-01 scaffold, CI skeleton, CODEOWNERS, labels and verifier | pass |
| Current CAD generators/exporters/CLI are inventoried | `docs/discovery/p0-02-cad-inventory.md` | pass |
| Three mandatory pilot articles are selected with official source evidence | `docs/discovery/p0-03-source-manifest.yml` | pass with gaps recorded |
| Legacy baseline is reproducible for pilots | `docs/discovery/p0-immutable-baseline-manifest.yml` | pass with accepted legacy-known-defect baselines |
| ADR 1-9 are recorded | `docs/adr/0001` through `0009` | accepted |
| Preview SLOs, release gates and parity tolerances are recorded | `docs/discovery/p0-06-slo-gates-and-tolerances.md` | accepted |
| Local toolchain smoke covers available real pilot sources and controlled source-format fixtures | `docs/discovery/p0-07-toolchain-smoke.md` | scoped pass |
| Protected main evidence is recorded | `docs/discovery/p0-protected-main-evidence.md` | pass |
| Existing `lanmaster-cad` remains compatible | selected legacy suite: 49 passed, 10 warnings in 122.67s | pass |

## Known-Defect Baseline Evidence

- `TWT-CBWNG-12U-6x6-BK`: source-backed card exists, but legacy v1 build/export
  fails official bbox; current output is 542 x 354 x 658 mm against the official
  550 x 600 x 658 mm. This is accepted only as legacy baseline evidence under
  `P0-KD-CBWNG-LEGACY-WALL-GEOMETRY`.
- `TWT-FRWAJ-12U-GY`: source-fact correction removed the untrusted 743 kg card
  mass because the official page does not publish item mass. Geometry verify
  passes, but corrected export fails IDS until NetWeight is obtained/approved or
  the IDS policy explicitly allows missing mass for open-frame fixtures. This is
  accepted only as legacy baseline evidence under
  `P0-KD-FRWAJ-MISSING-NETWEIGHT`.
- These known defects do not weaken IDS, verify, release, publication or future
  PMD parity gates. Failed artifacts remain non-publishable.

## Decision

Gate P0 is passed for entering P1. CBWNG and FRWAJ are accepted as red
legacy-known-defect baselines only; they are not accepted as releaseable
artifacts.

API, frontend, editor and RAG remain out of scope before Gate P3 / PMD Stable.
