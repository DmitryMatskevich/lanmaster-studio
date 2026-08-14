from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from studio_api.ingestion.chunks import SourceChunk


@dataclass(frozen=True)
class RetrievalHit:
    chunk: SourceChunk
    score: float
    citation: dict[str, object]
    reasons: list[str] = field(default_factory=list)


def hybrid_retrieve(
    query: str,
    chunks: list[SourceChunk],
    *,
    query_embedding: list[float] | None = None,
    embeddings: dict[str, list[float]] | None = None,
    filters: dict[str, object] | None = None,
    limit: int = 5,
) -> list[RetrievalHit]:
    terms = _terms(query)
    filtered = [chunk for chunk in chunks if _matches_filters(chunk, filters or {})]
    hits: list[RetrievalHit] = []
    for chunk in filtered:
        keyword_score = _keyword_score(terms, chunk.text)
        vector_score = _cosine(query_embedding, (embeddings or {}).get(chunk.id)) if query_embedding else 0.0
        if keyword_score == 0 and vector_score == 0:
            continue
        score = keyword_score * 0.7 + vector_score * 0.3
        reasons = []
        if keyword_score:
            reasons.append("keyword")
        if vector_score:
            reasons.append("vector")
        hits.append(RetrievalHit(chunk=chunk, score=score, citation=_citation(chunk), reasons=reasons))
    return sorted(hits, key=lambda hit: (-hit.score, hit.chunk.id))[:limit]


def rerank_with_citations(hits: list[RetrievalHit]) -> list[RetrievalHit]:
    return sorted(
        hits,
        key=lambda hit: (
            -hit.score,
            str(hit.citation.get("artifactId")),
            hit.citation.get("page") or 0,
            str(hit.citation.get("region") or ""),
        ),
    )


def _terms(query: str) -> list[str]:
    return [term for term in re.findall(r"[\w\-]+", query.lower()) if len(term) > 1]


def _keyword_score(terms: list[str], text: str) -> float:
    if not terms:
        return 0.0
    haystack = text.lower()
    matched = sum(1 for term in terms if term in haystack)
    return matched / len(terms)


def _cosine(left: list[float] | None, right: list[float] | None) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return max(0.0, numerator / (left_norm * right_norm))


def _matches_filters(chunk: SourceChunk, filters: dict[str, object]) -> bool:
    for key, expected in filters.items():
        actual = getattr(chunk, key, chunk.metadata.get(key))
        if isinstance(expected, (list, tuple, set)):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _citation(chunk: SourceChunk) -> dict[str, object]:
    citation: dict[str, object] = {
        "artifactId": chunk.artifactId,
        "sourceKind": chunk.sourceKind,
    }
    if chunk.page is not None:
        citation["page"] = chunk.page
    if chunk.region:
        citation["region"] = chunk.region
    if "bbox" in chunk.metadata:
        citation["bbox"] = chunk.metadata["bbox"]
    return citation
