from __future__ import annotations

from pathlib import Path

from studio_api.ingestion.chunks import chunk_text, chunks_from_regions


ROOT = Path(__file__).resolve().parents[1]


def test_chunk_text_is_stable_and_overlapping():
    text = " ".join(f"token{i}" for i in range(120))

    chunks = chunk_text(
        artifact_id="art_test",
        source_kind="pdf",
        text=text,
        page=2,
        region="r1",
        max_chars=120,
        overlap=20,
    )

    assert len(chunks) > 1
    assert chunks[0].id == chunk_text(
        artifact_id="art_test",
        source_kind="pdf",
        text=text,
        page=2,
        region="r1",
        max_chars=120,
        overlap=20,
    )[0].id
    assert chunks[0].artifactId == "art_test"
    assert chunks[0].page == 2


def test_chunks_from_regions_preserves_metadata():
    chunks = chunks_from_regions(
        artifact_id="art_regions",
        source_kind="pdf",
        regions=[{"id": "bbox-1", "page": 1, "kind": "text", "bbox": [0, 0, 10, 10], "text": "Door handle dimension"}],
    )

    assert len(chunks) == 1
    assert chunks[0].region == "bbox-1"
    assert chunks[0].metadata["bbox"] == [0, 0, 10, 10]


def test_postgres_schema_has_full_text_and_pgvector_contract():
    schema = (ROOT / "postgres" / "schema.sql").read_text(encoding="utf-8")

    assert "CREATE EXTENSION IF NOT EXISTS vector" in schema
    assert "search_vector TSVECTOR" in schema
    assert "embedding VECTOR(1536)" in schema
    assert "USING GIN(search_vector)" in schema
    assert "vector_cosine_ops" in schema
    assert "index_version" in schema
