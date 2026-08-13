# ADR-0008: Release Gates

Status: proposed

## Context

Release artifacts can affect engineering/BIM consumers and must be reproducible
from committed PMD, compiler version and sources.

## Decision

Release only from an immutable revision. Mandatory gates include PMD validation,
full CAD build, verification report, STEP/IFC/GLB/DXF generation, read-back where
available, stable ID checks, SHA-256 manifest, permissions/audit check and
explicit publication decision.

## Consequences

- Failed gates block publication and do not silently fall back to legacy.
- Draft revisions cannot be released.
- Gate results are retained with manifest and audit events.
