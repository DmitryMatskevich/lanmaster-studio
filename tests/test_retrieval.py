from __future__ import annotations

from studio_api.ingestion.chunks import SourceChunk
from studio_api.rag.retrieval import hybrid_retrieve, rerank_with_citations


def _chunk(id_: str, text: str, *, source_kind: str = "pdf", page: int = 1) -> SourceChunk:
    return SourceChunk(
        id=id_,
        artifactId="art_1",
        sourceKind=source_kind,
        page=page,
        region="r1",
        text=text,
        metadata={"bbox": [0, 0, 10, 10], "series": "TWT-CBB"},
    )


def test_hybrid_retrieval_filters_and_citations():
    chunks = [
        _chunk("chk_1", "mounting rail square holes 44.45 mm"),
        _chunk("chk_2", "door handle lock", source_kind="svg"),
    ]

    hits = hybrid_retrieve(
        "rail holes",
        chunks,
        query_embedding=[1.0, 0.0],
        embeddings={"chk_1": [1.0, 0.0], "chk_2": [0.0, 1.0]},
        filters={"sourceKind": "pdf", "series": "TWT-CBB"},
    )

    assert [hit.chunk.id for hit in hits] == ["chk_1"]
    assert hits[0].citation == {
        "artifactId": "art_1",
        "sourceKind": "pdf",
        "page": 1,
        "region": "r1",
        "bbox": [0, 0, 10, 10],
    }
    assert hits[0].reasons == ["keyword", "vector"]


def test_rerank_is_stable_for_equal_scores():
    first = hybrid_retrieve("door", [_chunk("chk_b", "door"), _chunk("chk_a", "door")], limit=10)
    reranked = rerank_with_citations(first)

    assert [hit.chunk.id for hit in reranked] == ["chk_a", "chk_b"]
