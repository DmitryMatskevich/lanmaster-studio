CREATE TABLE artifacts (
  id TEXT PRIMARY KEY,
  object_key TEXT NOT NULL UNIQUE,
  sha256 TEXT NOT NULL,
  media_type TEXT NOT NULL,
  size INTEGER NOT NULL,
  scope TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'ready')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX idx_artifacts_status_created
  ON artifacts(status, created_at);
