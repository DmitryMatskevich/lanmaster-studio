CREATE TABLE patches (
  id TEXT PRIMARY KEY,
  draft_id TEXT NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
  actor TEXT NOT NULL,
  operations_json TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('accepted')),
  created_at TEXT NOT NULL
);

CREATE INDEX idx_patches_draft_created
  ON patches(draft_id, created_at);
