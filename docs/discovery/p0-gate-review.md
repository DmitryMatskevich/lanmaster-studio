# P0 Gate Review

Status: blocked.

Evidence date: 2026-08-13.

## Gate Criteria

| Criterion | Evidence | Result |
|---|---|---|
| Separate `lanmaster-studio` repo exists | P0-01 scaffold, CI skeleton, CODEOWNERS, labels and verifier | pass |
| Current CAD generators/exporters/CLI are inventoried | `docs/discovery/p0-02-cad-inventory.md` | pass |
| Three mandatory pilot articles are selected with official source evidence | `docs/discovery/p0-03-source-manifest.yml` | pass with gaps recorded |
| Legacy baseline is reproducible for pilots | `docs/discovery/p0-04-baseline-candidates.md` | blocked |
| ADR 1-9 are recorded | `docs/adr/0001` through `0009` | proposed, needs owner decision |
| Preview SLOs, release gates and parity tolerances are recorded | `docs/discovery/p0-06-slo-gates-and-tolerances.md` | proposed, needs owner/QA decision |
| Local toolchain smoke covers available real pilot sources and controlled source-format fixtures | `docs/discovery/p0-07-toolchain-smoke.md` | scoped pass |
| Protected main evidence is recorded | `docs/discovery/p0-protected-main-evidence.md` | external blocker |
| Existing `lanmaster-cad` remains compatible | selected legacy suite: 49 passed, 10 warnings in 122.67s | pass |

## Blocking Evidence

- `TWT-CBB-42U-8x10-P1`: existing release artifacts are only a baseline
  candidate because the manifest predates current CAD compatibility changes.
- `TWT-CBWNG-12U-6x6-BK`: source-backed card exists, but legacy v1 build/export
  fails official bbox; current output is 542 x 354 x 658 mm against the official
  550 x 600 x 658 mm.
- `TWT-FRWAJ-12U-GY`: source-fact correction removed the untrusted 743 kg card
  mass because the official page does not publish item mass. Geometry verify
  passes, but corrected export fails IDS until NetWeight is obtained/approved or
  the IDS policy explicitly allows missing mass for open-frame fixtures.
- Baseline artifacts are stored as existing release outputs or temporary
  artifacts, not as an immutable gate-controlled baseline set.
- ADR and SLO/tolerance documents are proposed; owner/domain/QA approval is not
  recorded.
- Protected-main cannot be verified locally because no `lanmaster-studio` remote
  is configured.

## Decision

Gate P0 is not passed. Work may continue only inside P0 evidence/remediation
until one of these happens:

- QA/domain explicitly approves the CBWNG and FRWAJ deviations as known defects
  for legacy parity purposes;
- the affected legacy pilot cards/generators are corrected and old CLI
  regression tests remain green; or
- the pilot set is replaced with articles that have sufficient official sources
  and reproducible legacy baselines.

API, frontend, editor and RAG remain out of scope before Gate P3 / PMD Stable.
