# P0-07 Local Toolchain Smoke

Status: scoped pass for P0. Real pilot PDF/HTML sources and generated pilot
artifacts were checked. Real SVG/DXF/DWG/STEP source files are not present in
`lanmaster-cad/sources`, so source-CAD intake is explicitly deferred to P3/P6
unless a pilot replacement brings those formats into the official source set.

Evidence date: 2026-08-13.

## Tool Versions

| Tool | Version / Evidence |
|---|---|
| Poppler `pdfinfo` | 25.08.0 |
| Poppler `pdftotext` | available at `/opt/homebrew/bin/pdftotext` |
| LibreDWG `dwgread` | 0.13.3 |
| LibreDWG `dwg2dxf` | available at `/opt/homebrew/bin/dwg2dxf` |
| Python | 3.12.13 in `lanmaster-cad/.venv` |
| OCP | 7.9.3.1 |
| ezdxf | 1.4.2 |
| IfcOpenShell | 0.8.5 |

## Source Availability

| Format | Real Files In `lanmaster-cad/sources` | P0-07 Result |
|---|---:|---|
| PDF | present | smoke checked on CBB source PDFs |
| SVG | 0 | out of P0 pilot-source scope |
| DWG | 0 | out of P0 pilot-source scope, tool present only |
| DXF/STEP/STP/IFC/GLB source files | 0 | out of P0 source-intake scope; generated artifacts smoke checked |

Scope decision:

- Pilot source matrix for P0 is scoped to official PDF/HTML/JSON cache evidence.
- Generated STEP/STP/IFC/GLB/DXF release artifacts are output fixtures, not
  source-side CAD fixtures.
- `P3-02` remains responsible for headless intake of PDF/SVG/DXF/DWG/STEP once
  real source fixtures exist; `P6-03` and `P6-04` remain production ingestion
  tasks.

Search evidence:

```bash
find /Users/dmitrij/Documents/3d_lanmaster/lanmaster-cad/sources -type f \( -iname '*.svg' -o -iname '*.dwg' -o -iname '*.dxf' -o -iname '*.step' -o -iname '*.stp' -o -iname '*.ifc' -o -iname '*.glb' \) -print
find /Users/dmitrij/Documents/3d_lanmaster/lanmaster-cad -path '*/.git' -prune -o -path '*/.venv' -prune -o -path '*/out' -prune -o -path '*/tmp' -prune -o -type f \( -iname '*.svg' -o -iname '*.dwg' -o -iname '*.dxf' -o -iname '*.step' -o -iname '*.stp' -o -iname '*.ifc' -o -iname '*.glb' \) -print
```

Result:

- `lanmaster-cad/sources`: no matching source-CAD files.
- `lanmaster-cad` excluding `.git`, `.venv`, `out` and `tmp`: one IFC request
  attachment exists under `var/requests/inbox/LMREQ-2026-000015/attachments`;
  it is not an official selected-pilot source fixture.

## PDF Smoke

Command:

```bash
pdfinfo sources/twt-cbb-800/drawing_cbb800_f404.pdf
```

Result:

- title: `CBB800_800(pages)`
- creator: Adobe Illustrator CC 23.0
- pages: 2
- encrypted: no
- page size: A4
- PDF version: 1.5
- file size: 2,462,377 bytes

Command:

```bash
pdftotext sources/twt-cbb-800/table_cbb_f400.pdf -
```

Result:

- exit code: 0
- extracted text: effectively empty
- implication: plain text extraction is insufficient for this source; raster/vector
  render or table-specific extraction is required before facts are confirmed.

## Generated Artifact Parser Smoke

Input root:

`/private/tmp/lanmaster-studio-p0-baseline/TWT-FRWAJ-12U-GY`

Command summary:

```bash
python - <<'PY'
# OCP STEPControl_Reader, ezdxf, ifcopenshell and GLB JSON chunk parse
PY
```

Results:

| Format | Result |
|---|---|
| STEP | `STEPControl_Reader.ReadFile` returned `IFSelect_RetDone` |
| 2D DXF | ezdxf opened `AC1024`, 72 modelspace entities |
| 3D DXF | ezdxf opened `AC1024`, 5 modelspace entities |
| IFC4 | IfcOpenShell opened schema `IFC4`, 9 `IfcProduct` objects |
| IFC4X3 | IfcOpenShell opened schema `IFC4X3`, 9 `IfcProduct` objects |
| GLB | magic `glTF`, version 2, 6 nodes, 5 meshes |

## Gaps

- No real SVG source fixture exists in current pilot source cache.
- No real DWG source fixture exists in current pilot source cache.
- No real source-side DXF/STEP/STP/IFC/GLB files exist in `sources`; only release
  artifacts were available for parser smoke.
- The FRWAJ artifact root is temporary and not immutable baseline storage.
- PDF table text extraction did not recover usable text; visual/vector pipeline
  must be validated before P3 intake work.

## Result

P0-07 is satisfied for the scoped P0 pilot-source matrix: local tool versions are
known, official PDF/HTML source availability is recorded, missing source-CAD
formats are backed by file-search evidence, and generated output artifacts have
parser-smoke coverage. Full source-CAD intake remains a later P3/P6 deliverable
because no selected pilot currently has official SVG/DWG/DXF/STEP source files.
