# ADR-0006: Partial Preview Cache

Status: proposed

## Context

Interactive editing needs fast server-confirmed preview without running full
STEP/IFC/DXF release for every parameter change.

## Decision

Use PMD dependency graph analysis to compute affected components and build either
a component GLB, assembly GLB or metadata-only response. Cache keys include the
canonical affected subtree, referenced asset hashes, compiler version, geometry
backend version and preview profile.

## Consequences

- Client-side transforms are input hints only, never accepted preview truth.
- Interface/placement changes may invalidate the full assembly preview.
- Stale cache behavior needs explicit regression tests.
