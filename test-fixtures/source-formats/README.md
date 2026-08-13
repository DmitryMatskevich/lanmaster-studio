# Source Format Fixtures

These are small deterministic fixtures for P0/P3 toolchain smoke. They are not
official LANMASTER pilot sources and must not be used as geometry evidence for a
product card.

| Fixture | Purpose |
|---|---|
| `minimal-panel.svg` | SVG vector parsing/render smoke |
| `minimal-panel.dxf` | DXF entity parsing smoke |
| `minimal-panel.dwg` | DWG reader smoke, copied from the existing `lanmaster-cad/tmp/libredwg-smoke/smoke.dwg` fixture |
| `frwaj-open-frame.step` | STEP reader smoke, copied from a generated FRWAJ baseline candidate |

The official selected-pilot source matrix remains PDF/HTML/JSON only unless a
manufacturer-published CAD source is found.
