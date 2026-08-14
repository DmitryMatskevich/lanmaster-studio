CREATE TABLE organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE models (
  id TEXT PRIMARY KEY,
  article TEXT NOT NULL,
  manufacturer TEXT NOT NULL,
  series TEXT,
  name TEXT,
  status TEXT NOT NULL CHECK (status IN ('draft', 'published', 'archived')),
  active_revision_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_models_manufacturer_article
  ON models(manufacturer, article);

CREATE TABLE revisions (
  id TEXT PRIMARY KEY,
  model_id TEXT NOT NULL REFERENCES models(id) ON DELETE CASCADE,
  parent_id TEXT REFERENCES revisions(id),
  schema_version TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  pmd_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE drafts (
  id TEXT PRIMARY KEY,
  model_id TEXT NOT NULL REFERENCES models(id) ON DELETE CASCADE,
  base_revision_id TEXT REFERENCES revisions(id),
  head_revision_token TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('open', 'committed', 'abandoned')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  state TEXT NOT NULL CHECK (state IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')),
  input_hash TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 1,
  progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

