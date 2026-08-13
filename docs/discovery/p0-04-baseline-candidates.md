# P0-04 Baseline Candidates

Acceptance criterion for full P0-04: immutable legacy baseline for every selected
pilot, including commit SHA, source hashes, CLI command/stdout/stderr/duration,
release artifacts, component inventory, metrics, renders, verification results
and known defects.

This file records evidence found locally without rebuilding or overwriting
artifacts.

## CAD State

- `lanmaster-cad` current commit: `16c6b49e3b1c63f6be5e0c6f7fac37d8a7b276d6`
- Commit date: `2026-08-13 10:21:08 +0300`
- Working tree: clean during P0-04 inspection

## TWT-CBB-42U-8x10-P1

Status: existing baseline candidate only.

Reason: release artifacts exist locally, but the manifest timestamp is
`2026-08-10 14:04:27 +0300`, before the current CAD commit. It is useful
evidence, but not a freshly captured immutable baseline for the current source
state.

Local artifact root:

- `/Users/dmitrij/Documents/3d_lanmaster/lanmaster-models/TWT-CBB-42U-8x10-P1`

Manifest summary:

- family: `floor_cabinet`
- schema_version: `1`
- LOD: `300`
- requirements_lock_sha256: `a95813de80e1a679`
- Python: `3.12.13`
- verify: passed
- GLB checks: passed
- BRep bodies: 106 valid bodies
- GLB: 106 nodes, 4376 triangles, 5864 vertices, 0.53 MB
- STEP: 2,957,776 bytes, mm, Z-up
- IFC profiles: IFC4 and IFC4X3 present
- DXF: 2D drawing and 3D DXF present
- Views: overview, orthographic, section, rail detail, node views and drawing PDF present

Artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `TWT-CBB-42U-8x10-P1.manifest.json` | `5d39edde298860d76fa049b28e74f860e501634a462337a7f9c1fbe5ae5d167f` |
| `TWT-CBB-42U-8x10-P1.step` | `394fb1951c98c736d4f71b2bce90795c44c84a87a01b6b53b01186416ac59865` |
| `TWT-CBB-42U-8x10-P1.stp` | `28def02d1d79f7a49383b4b3ab91c217d9b0820216dca8e2053becd1e877ba11` |
| `TWT-CBB-42U-8x10-P1.IFC4.ifc` | `ed25997c5154775b7ecc381d2a9fa7a4fa3a3ec5ca3da8d0b1ad4fcacffe818d` |
| `TWT-CBB-42U-8x10-P1.IFC4X3.ifc` | `bde4cb539caa5ee912fe5dae8297cf3e939f78bb591d33433ea78075979cba9f` |
| `TWT-CBB-42U-8x10-P1.glb` | `8abcad140eb55d8c0e041931a59eabb4ccd2e435de183153290f7abb99f14552` |
| `TWT-CBB-42U-8x10-P1.dxf` | `2abe425b622bf3366cfdeef637f13c9beb42313730a0087ede6f037fca26f294` |
| `TWT-CBB-42U-8x10-P1.3D.dxf` | `3f0b56bf812b181d53d6b70d21f6c6872e28bb29b2c112dd9fa1b1b1f7632a73` |
| `TWT-CBB-42U-8x10-P1.igs` | `97f69de770a78823ff1d358422f4728e98224b86a251ce4a774aaef096bf46e8` |

Source hashes inside the artifact directory:

| Source | SHA-256 |
|---|---|
| `src/previewdoc-383.pdf` | `217cd954288fe48598e6599eca8349e1ebebe4499456d38f2d51384b970e64c4` |
| `src/previewdoc-400.pdf` | `97885a5c92b0ba0aa22623c40d391c4547b538764a7ea6ba13baa33a3ef8c43f` |
| `src/previewdoc-404.pdf` | `e6f54cda980f2f2ab62491526818b7310fb7d0511a394bfa21139dc74d96668a` |

Known defects/open evidence:

- Baseline command, stdout/stderr and duration are not captured for this artifact set.
- Component inventory is present in the manifest but not yet exported as a standalone immutable report.
- Format read-back evidence is manifest-level only; independent re-open logs are not preserved here.
- The selected CAD compatibility suite currently has one failing test unrelated to this artifact:
  `tests/test_rfa_extract.py::test_compare_with_card_uses_generated_parts`.

## Remaining Pilots

No complete baseline candidate is accepted yet for:

- `TWT-CBWNG-12U-6x6-BK`: official product-page HTML is cached, but no local v1 card or drawing/table PDF exists yet.
- `TWT-FRWAJ-12U-GY`: official product-page HTML is cached and local v1 card exists, but drawing/table PDF is missing and the current mass value needs correction or approval.

## P0-04 Result

P0-04 is not complete. The CBB evidence is recorded as a baseline candidate.
Full baseline capture should wait until P0-03 source gaps are resolved and the
current CAD compatibility failure is either fixed or approved as a known defect.
