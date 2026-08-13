# ADR-0004: Stable Component Identifiers

Status: proposed

## Context

Studio needs bidirectional selection between tree and 3D scene, and releases need
the same component identity across GLB, STEP, IFC, DXF, manifests and reports.

## Decision

`componentId` is the stable instance key. Human display names are not keys. The
same `componentId` must be emitted into GLB node extras, STEP/IFC properties,
DXF metadata where supported, manifests, verification reports and Studio trees.

## Consequences

- Exporters must preserve IDs independently of localized names.
- PMD validation rejects duplicate and dangling component references.
- Any importer/read-back test must verify IDs, not just file existence.
