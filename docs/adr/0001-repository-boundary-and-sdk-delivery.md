# ADR-0001: Repository Boundary And SDK Delivery

Status: accepted

## Context

`lanmaster-studio` must evolve independently from the existing CAD batch
pipeline. PMD core, compiler, AssemblyIR, geometry backends and exporters belong
to `lanmaster-cad`; web/API/orchestration belongs to `lanmaster-studio`.

## Decision

Keep separate repositories and release lifecycles. `lanmaster-studio` consumes
`lanmaster-cad` through a versioned SDK/container contract. Local development may
use editable paths, but production must pin an immutable package or image digest.

## Consequences

- Studio cannot import private legacy modules ad hoc.
- CAD changes require compatibility tests for old CLI behavior.
- No git submodule or shared git history is introduced.
