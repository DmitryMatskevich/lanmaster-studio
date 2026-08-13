# ADR-0003: Object Storage Lifecycle

Status: proposed

## Context

Sources, previews, release artifacts, reports and extracted document assets must
be reproducible and addressable without storing large binaries in the database.

## Decision

Use an S3-compatible object-storage contract for production and a filesystem
implementation for local development. Artifacts are content-addressed or recorded
with SHA-256 in manifests. Preview artifacts may have lifecycle expiration;
release artifacts and accepted source documents are retained immutably.

## Consequences

- API serves artifacts through scoped signed URLs.
- Release publication requires hash verification.
- Storage lifecycle policy is part of P4/P7 operations.
