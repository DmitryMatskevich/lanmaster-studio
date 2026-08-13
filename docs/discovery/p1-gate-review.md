# P1 Gate Review

Status: passed.

Evidence date: 2026-08-13.

CAD evidence commit: `4a172c40` on `lanmaster-cad/main` (PR #1).

## Delivery Matrix

| ID | Evidence | Result |
|---|---|---|
| P1-01 | PMD 2.0 Draft 2020-12 schema, examples and negative fixtures | pass |
| P1-02 | Strict Pydantic models and shared conformance corpus | pass |
| P1-03 | Unit normalization, canonical JSON and SHA-256 content identity | pass |
| P1-04 | Duplicate, dangling, hash, unit and interface validation | pass |
| P1-05 | Allowlisted AST, dimension checks, deterministic graph and cycle rejection | pass |
| P1-06 | Typed atomic patches, inverse, roles/hooks and affected subgraph | pass |
| P1-07 | Bounded `box/extrude/cut/pattern/import-profile` grammar | pass |
| P1-08 | Pinned import-step contract and default-deny legacy policy | pass |
| P1-09 | Acceptance remains a separate read-only top-level specification | pass |
| P1-10 | Open frame, floor cabinet and wall cabinet structural fixtures | pass |

## Gate Evidence

- `require_valid_document()` is the complete pre-CAD gate: units, semantic
  references, backend policy, expression AST, dimensions and cycles.
- Expressions are parsed but never compiled or evaluated. Legacy execution is
  denied unless `(generator, generatorVersion)` is explicitly allowlisted.
- Patch affected sets include transitive parameters, definition users,
  parameter overrides and assembly ancestors.
- Independent high-reasoning read-only review first found four defects in
  conformance, affected sets, vector dimensions and STEP interface typing.
  All were fixed with regression tests; repeated review found no High/Medium
  findings and returned `Gate P1: PASS`.

## Verification

- PMD suite: `83 passed in 0.75s`.
- Full `lanmaster-cad` suite: `189 passed, 6 subtests passed, 10 warnings in
  158.40s`.
- The warnings are existing `ezdxf` deprecations and documented perforation
  workload warnings; no test failed.

## Decision

Gate P1 is passed. PMD validates autonomously, executes no document-provided
code, represents three different compositions without cabinet-specific core
fields, and deterministically calculates the affected subgraph.

P2 may start at P2-01. API, frontend, editor and RAG remain blocked until Gate
P3 / PMD Stable.
