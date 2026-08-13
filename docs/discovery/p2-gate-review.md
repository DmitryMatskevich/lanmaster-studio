# P2 Gate Review

Status: passed.

Evidence date: 2026-08-13.

CAD evidence commit: `a6864229` on `lanmaster-cad/main` (PR #2).

## Delivery Matrix

| ID | Evidence | Result |
|---|---|---|
| P2-01 | Typed `AssemblyIR`, invariants and accepted exporter ADR | pass |
| P2-02 | Deterministic tree compiler, rigid transforms and interfaces | pass |
| P2-03 | Exact declarative B-Rep and pinned profile import | pass |
| P2-04 | STEP root/hash/unit/valid-solid preflight | pass |
| P2-05 | Explicit versioned legacy registry and bounded input/output | pass |
| P2-06 | Content cache, cloning, sharing and affected invalidation | pass |
| P2-07 | GLB extras, structural validation and identity read-back | pass |
| P2-08 | STEP/IFC stable IDs, deterministic identity and read-back | pass |
| P2-09 | DXF views/layers/IDs plus artifact hash manifest | pass |
| P2-10 | Read-only acceptance verification and publication gate | pass |
| P2-11 | Explicit v1 adapter/dispatcher; old CLI remains unchanged | pass |
| P2-12 | Headless validate/preview/release/compare commands | pass |

## Gate Evidence

- One compiler process registers declarative, import-step and default-deny
  allowlisted legacy backends. Actual CLI preview tests execute all three paths.
- Preview and release use the same stable component/shape IDs. Preview manifests
  are non-publishable; release requires checks and geometry and promotes only a
  completely staged artifact set.
- GLB, STEP, IFC4, IFC4X3, DXF2D and DXF3D have identity read-back tests. STEP
  occurrence IDs and IFC GUIDs are deterministic and model-scoped.
- A warm cache cannot hide changed STEP or profile assets because hash preflight
  runs before lookup. Compare uses exact per-shape world-space B-Rep fingerprints.
- Schema-v1 `build`/`export` routes were not auto-dispatched through PMD and the
  full legacy regression remains green.

## Verification

- P2 focused suite: `75 passed`.
- Full `lanmaster-cad` suite: `264 passed, 6 subtests passed, 22 warnings in
  167.39s`.
- Real CLI release: publishable manifest; STEP, IFC4, IFC4X3, GLB, DXF2D and
  report emitted; all artifact sizes and SHA-256 hashes matched.
- First independent review found two High and four Medium findings. All were
  reproduced, fixed and protected by negative tests.
- Repeated independent read-only review found no High/Medium findings and
  returned `Gate P2: PASS`.

## Decision

Gate P2 is passed. The compiler has a working vertical PMD build/release route,
stable cross-format identities, strict publication behavior and explicit v1
compatibility. PMD 2.0 is not stable yet: STEP AP242 qualification and external
Khronos/Three.js GLB validation remain P3 format-matrix work.

P3 may start at P3-01. API, frontend, editor and RAG remain blocked until Gate
P3 / PMD Stable.
