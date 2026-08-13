# P0-04 Legacy Baseline

Acceptance criterion for full P0-04: immutable legacy baseline for every selected
pilot, including commit SHA, source hashes, CLI command/stdout/stderr/duration,
release artifacts, component inventory, metrics, renders, verification results
and known defects.

Immutable baseline manifest:

- `docs/discovery/p0-immutable-baseline-manifest.yml`
- artifact root: `/private/tmp/lanmaster-studio-p0-immutable-baseline`

Known-defect policy:

- CBWNG and FRWAJ defects are accepted only for legacy baseline evidence.
- IDS, verify, release, publication and future PMD parity gates are not weakened.
- Failed artifacts remain non-publishable.

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

### TWT-FRWAJ-12U-GY

Status: immutable local baseline candidate with unresolved IDS NetWeight policy.

Command:

```bash
cd /Users/dmitrij/Documents/3d_lanmaster/lanmaster-cad
.venv/bin/python -m lmcad.cli export params/TWT-FRWAJ-12U-GY.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300
.venv/bin/python -m lmcad.cli export params/TWT-FRWAJ-12U-GY.yaml --out /private/tmp/lanmaster-studio-p0-immutable-baseline --lod 300
```

Result:

- source-fact correction: `../lanmaster-cad/params/TWT-FRWAJ-12U-GY.yaml`
  now sets `net_weight_kg: null` because official source metadata does not
  publish item mass.
- corrected export exit code: 1
- corrected output root: `/private/tmp/lanmaster-studio-p0-immutable-baseline/TWT-FRWAJ-12U-GY`
- verify: passed
- IDS: IFC4 failed, IFC4X3 failed because NetWeight is absent after removing the
  untrusted mass value.
- GLB: 5 nodes, 60 triangles, 18,708 bytes
- BRep bodies: 5 valid bodies
- known fact: official source does not publish item mass; the previous 743 kg
  card value is not used as a source fact.

Artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `TWT-FRWAJ-12U-GY.manifest.json` | `45d76a0e603c2b307f514298c382305e44a047e0c30a435dc48337f0eaf59883` |
| `TWT-FRWAJ-12U-GY.step` | `6a4a4c84f06c722dbc6ff145cf1e4de799653186109407f238a0ccac3d052789` |
| `TWT-FRWAJ-12U-GY.stp` | `19f4bca21cf456b9fd7e0069672407a3fe9c6e21bd003e96c242ad8291fb59d5` |
| `TWT-FRWAJ-12U-GY.IFC4.ifc` | `a8fef6f9cd35139976131f3147bc127f5557dbd30555177e7d71a1dc823cb611` |
| `TWT-FRWAJ-12U-GY.IFC4X3.ifc` | `3831454ee4404ce428b5c9c8416af4ca3c5fe528c24fb4f1a43802ba66ee7305` |
| `TWT-FRWAJ-12U-GY.glb` | `19af29b7418a84bbdfd45781746aa7aa19ba83fa150dbb7331d3da40dd879ecb` |
| `TWT-FRWAJ-12U-GY.dxf` | `90a28cacee41dfd7efcc0e5ae2464c22fb9cfef7d8105afcff147bf078b4beb2` |
| `TWT-FRWAJ-12U-GY.3D.dxf` | `dfbf1673f752496025339305f929a8e32f485f84198299a96b9a374714f45830` |
| `TWT-FRWAJ-12U-GY.igs` | `03024d2f8a3fa3da67f4ffcaef89a27c40a332575dc84ccff439312a22416f88` |
| `views/TWT-FRWAJ-12U-GY.drawing.pdf` | `87d6f8ed595b4c997aef2fa40a8d59b59a56d627f256f12c5f660aa3b5928b14` |

This is not final P0-04 completion because the corrected source fact creates an
IDS policy blocker: either NetWeight must be obtained/approved for this article,
or the IDS/profile policy must explicitly allow missing mass for open-frame
fixtures before Gate P0.

### Still Missing

### TWT-CBWNG-12U-6x6-BK

Status: failed legacy baseline candidate with known geometry limitation.

CAD branch/commit:

- branch: `studio-p0-source-cache`
- card commit: `9607ef51`

Commands:

```bash
cd /Users/dmitrij/Documents/3d_lanmaster/lanmaster-cad
.venv/bin/python -m lmcad.cli build params/TWT-CBWNG-12U-6x6-BK.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300
.venv/bin/python -m lmcad.cli export params/TWT-CBWNG-12U-6x6-BK.yaml --out /private/tmp/lanmaster-studio-p0-baseline --lod 300 --no-strict
```

Result:

- build exit code: 1
- export exit code: 1 because `all_passed=false`
- export duration observed by command runner: 10.102 s
- output root: `/private/tmp/lanmaster-studio-p0-baseline/TWT-CBWNG-12U-6x6-BK`
- verify: failed
- failed checks: bbox X and Y
- official expected bbox: 550 x 600 x 658 mm
- current legacy output bbox: 542 x 354 x 658 mm
- IDS: IFC4 passed, IFC4X3 passed
- GLB: 10 nodes, 608 triangles, 47,872 bytes

Known limitation:

- Current v1 `wall_cabinet` route uses `generic_accessory` and models a door kit,
  not a complete wall cabinet body with rear panel, wall mounting, rails, cable
  entries and side panels.
- The official bbox is preserved in the card. The card is not tuned to make the
  legacy approximation pass.

Artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `TWT-CBWNG-12U-6x6-BK.manifest.json` | `fb3d9659be6930e817b698b22195ec049ed25d86cee44c3c2e9f333254d41e23` |
| `TWT-CBWNG-12U-6x6-BK.step` | `e1c61e23dce13a040b06f5b4e414efa68fd57e1bccec5e9785481d3dd4ae7b77` |
| `TWT-CBWNG-12U-6x6-BK.stp` | `9ea730f2c8c9c9f1af8dd0add3029b0f20a5f104d81c70b39d12dd54eecf0df6` |
| `TWT-CBWNG-12U-6x6-BK.IFC4.ifc` | `73e65680cb5b3afa0c5826ef8cfccbbb9197cc484c0555ef8c6a445f46b992b5` |
| `TWT-CBWNG-12U-6x6-BK.IFC4X3.ifc` | `2b84b60216fab6355221980c61c4f78a941ac29b6e5094cff70b6d10edeca76a` |
| `TWT-CBWNG-12U-6x6-BK.glb` | `22d9cad7ed9ab655cbe234adacab790e27ce16c0a498c16cfe8c3d71964eec0c` |
| `TWT-CBWNG-12U-6x6-BK.dxf` | `93e1b7f5a2c8bfb4508f4a031c0519d920ff63811f191e0b35580ea0453d7519` |
| `TWT-CBWNG-12U-6x6-BK.3D.dxf` | `b201e0b5f483060984945ac12e913b1316610917ddf6204d0f22000ffb74f019` |
| `TWT-CBWNG-12U-6x6-BK.igs` | `088a8616d15c40a7a1d2a8f2ac6f043388b0083267f2f677ee60979d0a4a55a8` |
| `views/TWT-CBWNG-12U-6x6-BK.drawing.pdf` | `e1765fb087630ed3c984be0499150bdc1fe50f9c8a09a8c80754a91030f0f866` |

This is not a passing baseline, but it is useful negative evidence for P3: PMD
must represent the wall-cabinet construction instead of inheriting the generic
door-kit shortcut.

### Still Missing

No complete passing baseline candidate is accepted yet for:

- `TWT-CBWNG-12U-6x6-BK`: official product-page HTML and v1 card exist, but
  legacy geometry fails official bbox and no drawing/table PDF is available.

## P0-04 Result

P0-04 is complete for Gate P0. CBB has a passing immutable local baseline.
CBWNG and FRWAJ have immutable local red baselines with accepted legacy-only
known defects recorded in `docs/discovery/p0-immutable-baseline-manifest.yml`.
The known defects do not authorize release publication.
