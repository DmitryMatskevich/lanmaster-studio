# ADR-0009: OpenUSD After MVP

Status: proposed

## Context

OpenUSD may be useful later for complex variants or interchange, but MVP already
has PMD, AssemblyIR, GLB, STEP, IFC and DXF obligations.

## Decision

Do not put OpenUSD on the MVP critical path. Treat it as a post-MVP optional
interchange/authoring investigation after PMD 2.0, compiler, pilots and editor
MVP are proven.

## Consequences

- No OpenUSD dependency is added in P0-P5.
- PMD and AssemblyIR remain the authoritative internal contracts.
- Future OpenUSD work must not weaken release gates for STEP/IFC/GLB/DXF.
