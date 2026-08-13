# P0-07 Local Toolchain Smoke

Status: partial. Real pilot PDF sources and generated pilot artifacts were
checked. Real SVG/DXF/DWG/STEP source files are not present in `lanmaster-cad/sources`.

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
| SVG | 0 | gap |
| DWG | 0 | gap, tool present only |
| DXF/STEP/STP/IFC/GLB source files | 0 | gap for source-intake; generated artifacts smoke checked |

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

P0-07 is partially satisfied for local tool availability and output-format parser
smoke. It is not a full source-intake pass because real SVG/DWG/CAD source files
for selected pilots are missing.
