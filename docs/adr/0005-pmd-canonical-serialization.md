# ADR-0005: PMD Canonical Serialization

Status: proposed

## Context

PMD revisions, patches, cache keys and reproducibility depend on deterministic
identity independent of YAML formatting or key order.

## Decision

Normalize YAML input into canonical JSON before hashing or patching. Canonical
serialization uses stable key ordering, normalized units, schema-validated values
and explicit schema version. Hashes are computed over canonical JSON plus
referenced asset hashes where required.

## Consequences

- Formatting-only YAML edits do not create semantic revisions.
- Cache invalidation can use canonical component subtrees.
- Unit and schema conformance tests are required before PMD Stable.
