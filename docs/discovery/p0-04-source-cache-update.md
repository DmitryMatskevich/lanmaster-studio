# P0-04 Source Cache Update

Evidence date: 2026-08-13.

This update narrows the P0-04 source-readiness blocker by caching official
product pages for the selected wall-cabinet and open-frame pilots.

## Cached Sources

| Pilot | Cached Source | SHA-256 | CAD Branch |
|---|---|---|---|
| `TWT-CBWNG-12U-6x6-BK` | `lanmaster-cad/sources/twt-cbwng/product.html` | `cbcc415940421a6cfcd62e699e7d1edd291140fc73d8237b6fd1629b298f5564` | `studio-p0-source-cache` |
| `TWT-FRWAJ-12U-GY` | `lanmaster-cad/sources/twt-frwaj-xu-gy/product.html` | `11add4a3c98cfb4ca3ab9f47ce6882ec2042c518d5f17b54051f3128766637d6` | `studio-p0-source-cache` |

Source metadata was added at:

- `lanmaster-cad/sources/twt-cbwng/source.json`
- `lanmaster-cad/sources/twt-frwaj-xu-gy/source.json`

## Extracted Facts

`TWT-CBWNG-12U-6x6-BK` official page evidence:

- dimensions: 600 x 550 x 658 mm (D x W x H)
- packaging: 640 x 220 x 600 mm (D x W x H)
- gross/net mass: 21 / 20 kg
- capacity: 12U
- maximum wall-cabinet load: 60 kg
- color: RAL 7021
- wall mounting: 4 points
- rear rails: fixed 63 mm from rear panel
- front rails: adjustable 50-130 mm from door
- cable entries: top, rear and bottom

`TWT-FRWAJ-12U-GY` official page evidence:

- height variants: 6U, 9U, 12U
- adjustable depth range: 461-664 mm
- maximum mounted equipment load: 25 kg
- vertical mounting rails: 2
- removable front mounting frame opens 190 degrees
- color: RAL 7035
- material: cold-rolled steel

## Remaining Gaps

- No drawing/table PDF link was visible on either official product page.
- `TWT-CBWNG-12U-6x6-BK` still lacks a local v1 card.
- `TWT-FRWAJ-12U-GY` current v1 net mass remains implausible and must be corrected or approved as a known defect before baseline.
- CAD compatibility suite still has the existing `test_rfa_extract` part-count failure.

## Result

P0-04 is still not complete, but source readiness improved from missing source
cache to cached official product-page evidence with explicit residual gaps.
