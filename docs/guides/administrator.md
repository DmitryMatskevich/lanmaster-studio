# Administrator Guide

## Purpose

Operate Studio API, frontend, workers, object storage, database, monitoring and
incident response for the production pilot.

## Required Workflow

1. Deploy only SHA-256-pinned images.
2. Configure production authentication; development headers are not allowed in
   production.
3. Keep database and object storage backups encrypted and retained by policy.
4. Monitor API health, job queue age, worker heartbeat, storage errors and audit
   event failures.
5. Verify rollback to the legacy route for pilot articles before release.
6. Keep RAG kill switch and tenant-isolation controls enabled.

## Recovery Checks

After restore or rollback, verify `/health`, revision reads, artifact download,
audit trail continuity and legacy route restoration.

