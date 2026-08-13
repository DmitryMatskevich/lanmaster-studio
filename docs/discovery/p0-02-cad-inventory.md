# P0-02 CAD Inventory

Acceptance criterion: map current `lanmaster-cad` generators, exporters, family
routing, CLI contracts, and compatibility tests without changing legacy code.

Evidence date: 2026-08-13.

## Repository State

- Repository: `/Users/dmitrij/Documents/3d_lanmaster/lanmaster-cad`
- Branch/status: `main...origin/main`, clean working tree
- Cards: 1876 YAML files in `params/`
- Schemas: 1876 cards with `schema_version: 1`

Family counts from current cards:

| Family | Cards |
|---|---:|
| `rack_accessory` | 1168 |
| `cable_organizer` | 398 |
| `patch_panel` | 110 |
| `floor_cabinet` | 100 |
| `pdu` | 40 |
| `shelf` | 37 |
| `open_rack` | 23 |

No current cards are tagged `wall_cabinet`, although the CLI has a route for it.

## CLI Contracts

Primary entry point: `lmcad/cli.py`, `argparse` program `lmcad`.

Current subcommands:

| Command | Contract Surface | Compatibility Notes |
|---|---|---|
| `build CARD --out OUT --lod {300,400}` | Load v1 card, build parts, run `verify`, no export | Must keep exit code `0` only when verification passes. |
| `export CARD --out OUT --lod {300,400} [--no-strict]` | Build, verify, export full release set and manifest | Strict mode aborts on failed verify before artifacts reach users. |
| `inspect IFC` | Read IFC with `inspect_ifc_file` and print JSON | Supports release diagnostics and read-back evidence. |
| `validate IFC --family FAMILY --profile {IFC4,IFC4X3}` | Validate IFC against IDS/profile mapping | Existing IDS behavior is a regression surface. |
| `release-all --params DIR --out OUT --lod LOD` | Strict export across all parameter cards | Must remain available for catalog regression/shadow runs. |
| `batch CARD --out OUT --lod LOD --heights --widths --depths` | Deterministic type-size generation from one card | Mutates in-memory data only; does not use LLM. |
| `convert-revit-ifc INPUT --out OUT --backend ... [--diagnose]` | Optional Revit-backed IFC conversion facade | Depends on external Windows/Revit backend; not a required local gate. |
| `extract-rfa --input/--usbim-text --out` | Native/usBIM RFA data extraction | Source-intake helper, not release geometry. |
| `compare-rfa USBIM_JSON CARD --out` | Compare extracted RFA data against a card | Discovery/intake helper. |

Default export output is `../lanmaster-models` when that repository exists,
otherwise `lanmaster-cad/out`.

## Family Routing

Current route map in `lmcad/cli.py`:

| Family | Module |
|---|---|
| `floor_cabinet` | `lmcad.families.floor_cabinet` |
| `wall_cabinet` | `lmcad.families.generic_accessory` |
| `open_rack` | `lmcad.families.generic_accessory` |
| `shelf` | `lmcad.families.generic_accessory` |
| `pdu` | `lmcad.families.generic_accessory` |
| `patch_panel` | `lmcad.families.generic_accessory` |
| `cable_organizer` | `lmcad.families.generic_accessory` |
| `mounting_profile` | `lmcad.families.generic_accessory` |
| `rack_accessory` | `lmcad.families.generic_accessory` |

Compatibility risk: most catalog families share `generic_accessory`, which derives
many details from article/name parsing and `verify.required_components`. PMD 2.0
must not preserve this as a geometry-selection mechanism.

## Generator Modules

| Module | Role | Notable Contract |
|---|---|---|
| `lmcad.families.floor_cabinet` | Deterministic 19-inch floor cabinet generator | LOD ladder `200/300/400`; real rail/door/frame/accessory parts; expensive perforation guarded. |
| `lmcad.families.generic_accessory` | Deterministic accessory/product generator | Handles rack accessories, PDU outlets, patch panels, organizers, shelves, racks and parsed standard details. |
| `lmcad.standard_components` | Component inventory/classification helper | Reads `verify.required_components`; important migration smell. |
| `lmcad.verify` | Geometry and GLB verification | Existing release gate; checks must remain read-only in PMD work. |
| `lmcad.guid` | Deterministic IFC GUID generation | Stable IDs are protected by tests. |
| `lmcad.ids_spec` | IDS save/validate helper | Tied to IFC profile/family mapping. |

## Exporters

| Module | Outputs | Read-back / Verification Surface |
|---|---|---|
| `lmcad.exporters.mesh` | STEP, GLB, preview PNG, rendered views | GLB orientation, readable node/mesh names, material checks, STEP names. |
| `lmcad.exporters.ifc` | IFC4 and IFC4X3 | IFC class/profile map, GUIDs, properties, direct IFC geometry. |
| `lmcad.exporters.drawing` | 2D DXF drawing, 3D DXF, drawing PDF | Layer set, views, dimensions/text, PDF drawing evidence. |
| `lmcad.exporters.exchange` | STP, IGES, DWG attempt wrapper, re-exported DXF helpers | STP follows STEP path; IGES loses assembly names by design; DWG is external-conversion only. |
| `lmcad.exporters.sections` | Section/detail rendered views | Floor-cabinet-specific visual evidence. |
| `lmcad.change_report` | Change PDF/report | Request workflow and change-release evidence. |

## Existing Compatibility Tests

Targeted tests that should stay green before and after PMD/CAD contract work:

| Test File | Coverage |
|---|---|
| `tests/test_golden.py` | Pilot geometry, LOD ladder, GUIDs, IFC class map, PDU details, GLB/STEP readability, exports and generic family behavior. |
| `tests/test_drawing_intake.py` | PDF/SVG/DXF/DWG/STEP intake smoke behavior. |
| `tests/test_request_queue.py` | Email/request workflow, attachment policy, release completion, file routing. |
| `tests/test_change_report.py` | Change report generation from manifests. |
| `tests/test_revit_convert.py` | Revit IFC facade diagnostics and configured-runner behavior. |
| `tests/test_rfa_extract.py` | RFA/usBIM extraction parsing. |

Minimum compatibility command for P0/P1 work that does not touch CAD code:

```bash
cd /Users/dmitrij/Documents/3d_lanmaster/lanmaster-cad
.venv/bin/python -m pytest tests/test_golden.py tests/test_drawing_intake.py tests/test_change_report.py tests/test_revit_convert.py tests/test_rfa_extract.py -q
```

Full request-queue coverage is separate because it is large and should be run
when request workflow, release packaging, or queue code is touched.

## P0-02 Result

P0-02 is satisfied for the local checkpoint: module map and compatibility-test
list are recorded. No legacy files were edited.

Open follow-up for P0-03/P0-04: choose pilots and capture immutable baselines
with command output, hashes, artifacts, metrics, and known defects.
