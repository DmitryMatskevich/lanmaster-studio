CREATE TABLE releases (
  id TEXT PRIMARY KEY,
  revision_id TEXT NOT NULL REFERENCES revisions(id) ON DELETE CASCADE,
  profile TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')),
  job_id TEXT REFERENCES jobs(id),
  idempotency_key TEXT,
  manifest_artifact_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_releases_idempotency_key
  ON releases(idempotency_key)
  WHERE idempotency_key IS NOT NULL;

CREATE INDEX idx_releases_revision_created
  ON releases(revision_id, created_at);
