# P0-06 SLOs, Release Gates And Parity Tolerances

Status: accepted by user instruction on 2026-08-13.

Acceptance criterion: define measurable preview SLOs, mandatory release gates and
legacy/PMD parity tolerances before PMD schema and compiler work begin.

Evidence date: 2026-08-13.

## Preview SLOs

| Operation | Target | Measurement |
|---|---:|---|
| API response without CAD work | p95 <= 300 ms | API timer, excludes queue wait |
| First job progress event | <= 1 s | event timestamp minus accepted job timestamp |
| Local declarative component preview | p50 <= 2 s, p95 <= 5 s | worker accepted to preview artifact published |
| Typical assembly preview | p50 <= 5 s, p95 <= 15 s | worker accepted to preview artifact published |
| Preview cache warm hit | at least 2x faster than cold for same affected subtree | cold/warm paired benchmark |
| Preview artifact publication | no stale artifact served for rejected validation | revision/cache-key audit |

Scope notes:

- Client-side visual transforms do not satisfy preview SLOs.
- A preview is counted only after server validation and worker-produced artifact
  publication.
- Preview SLOs are measured on pilot models first, then revised only by ADR.

## Release Gates

Mandatory gates before publication:

1. PMD/card source revision is immutable and identified by hash.
2. Compiler/legacy generator version and dependency lock hash are recorded.
3. Geometry build succeeds without using client state.
4. Verification report passes required checks for publication. Known defects may
   be recorded for baseline/parity evidence, but they do not make a failed
   artifact publishable.
5. STEP/STP, IFC4, IFC4X3, GLB, 2D DXF, 3D DXF, drawing PDF and manifest are
   generated when the product profile requires them.
6. Output files are independently re-opened or parsed where local tooling exists.
7. Stable component identifiers are present in manifest and every supported
   format mapping.
8. SHA-256 is recorded for every release artifact and source file.
9. Views/renders exist for required pilot cameras and are visually inspectable.
10. Audit entry records actor, command/job, source revision, result and known
    defects.
11. Publication is blocked on failed mandatory gates; no silent PMD-to-legacy
    fallback is allowed.

## Format Read-Back Gates

| Format | Minimum Gate |
|---|---|
| STEP/STP | parse/open succeeds, unit is mm, assembly/product names or IDs are readable |
| IFC4/IFC4X3 | IDS/profile validation passes, class/profile mapping matches expected family |
| GLB | JSON/chunk parse succeeds, nonzero nodes/meshes, material present, not over triangle/byte limits |
| 2D DXF | ezdxf open succeeds, expected layers/views/entities present |
| 3D DXF | ezdxf open succeeds, nonzero 3D entities/mesh faces, bbox plausible |
| drawing PDF | PDF opens/renders, page count nonzero, drawing exists for release profile |
| manifest | schema keys present, hashes cover artifacts, `all_passed` truthfully reflects gates |

## Legacy/PMD Parity Tolerances

Initial tolerances for pilot semantic parity:

| Metric | Tolerance | Notes |
|---|---:|---|
| Overall bounding box X/Y/Z | <= 0.8 mm or source tolerance, whichever is larger | Existing v1 pilot tolerances may be stricter. |
| Base at Z=0 | <= 0.5 mm | Required for BIM placement. |
| 19-inch rail opening | <= 1.0 mm | Applies to 19-inch rack/cabinet products. |
| Rail hole count | exact | Where holes are represented in selected LOD. |
| Required component IDs | exact set unless deviation is approved | PMD must not omit silently. |
| Component inventory count by semantic group | exact for confirmed groups | Unknown/inferred groups are listed separately. |
| GLB node/component map | exact for stable `componentId` set | Display names are not keys. |
| STEP/IFC component property map | exact for stable `componentId` set | Read-back required where supported. |
| Net mass | <= 10% for confirmed source mass | If source mass is missing/implausible, record known defect; do not tune geometry to pass. |
| Material/category/color | exact for confirmed source facts | Mixed-material products may use per-component evidence. |
| Visual pilot renders | no missing major components; reviewed from fixed cameras | Screenshot diff threshold added after golden images exist. |

Known-defect handling:

- A known defect must name the source of uncertainty and the artifact affected.
- Known defects do not become pass criteria. They may be accepted only as scoped
  legacy-baseline deviations and do not weaken IDS, release or publication gates.
- Existing v1 defects are recorded before PMD parity comparison and cannot be
  counted as PMD regressions.

## P0-06 Checklist

- Preview SLOs are measurable.
- Release gates are explicit and block publication.
- Read-back gates avoid treating file existence as correctness.
- Parity tolerances cover geometry, IDs, material, mass and visual evidence.
- Known-defect rules protect against fitting geometry to `verify`.

## Result

P0-06 is accepted for P1 entry by user instruction on 2026-08-13. Release gates
remain mandatory; known defects accepted during P0 classify legacy baseline
deviations only and do not authorize publication of failed artifacts.
