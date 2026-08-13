# ADR-0007: LLM Provider And Data Retention

Status: proposed

## Context

Chat/RAG must assist PMD editing without letting an LLM execute CAD, access
secrets, or write files directly.

## Decision

Hide providers behind an LLM abstraction that accepts scoped context and returns
typed `EditIntent`/`PMDPatchProposal` objects. Provider choice, external data
transfer permission and retention policy must be configured per deployment.

## Consequences

- LLM output is untrusted input and always validated/authorized.
- Citations and source fragments are stored with proposals.
- Kill switch and prompt-injection tests are required before P6 gate.
