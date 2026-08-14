CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS source_chunks (
  id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL,
  source_kind TEXT NOT NULL,
  page INTEGER,
  region TEXT,
  text TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED,
  embedding VECTOR(1536),
  index_version TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_source_chunks_artifact
  ON source_chunks(artifact_id);

CREATE INDEX IF NOT EXISTS idx_source_chunks_search
  ON source_chunks USING GIN(search_vector);

CREATE INDEX IF NOT EXISTS idx_source_chunks_embedding
  ON source_chunks USING IVFFLAT (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE TABLE IF NOT EXISTS source_chunk_index_runs (
  id TEXT PRIMARY KEY,
  index_version TEXT NOT NULL,
  artifact_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
  chunk_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
