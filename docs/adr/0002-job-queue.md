# ADR-0002: Job Queue

Status: accepted

## Context

Preview, verification, release and ingestion jobs are too heavy for synchronous
HTTP requests and need progress, retry, cancellation and worker isolation.

## Decision

Use Redis-backed workers for local MVP queueing, with an abstraction around job
envelopes, idempotency keys, heartbeats and state transitions. The final library
choice is deferred to P4, but the contract must support preview and release
queues separately.

## Consequences

- API returns `jobId` for heavy operations.
- Redis is transport/state cache only, not the source of truth.
- Worker messages become contract-tested before API/editor work starts.
