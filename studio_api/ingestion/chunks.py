from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SourceChunk:
    id: str
    artifactId: str
    sourceKind: str
    page: int | None
    region: str | None
    text: str
    metadata: dict[str, object]


def chunk_text(
    *,
    artifact_id: str,
    source_kind: str,
    text: str,
    page: int | None = None,
    region: str | None = None,
    metadata: dict[str, object] | None = None,
    max_chars: int = 1200,
    overlap: int = 120,
) -> list[SourceChunk]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks: list[SourceChunk] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + max_chars)
        if end < len(normalized):
            split = normalized.rfind(" ", start, end)
            if split > start + max_chars // 2:
                end = split
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(_chunk(artifact_id, source_kind, page, region, chunk, metadata or {}, len(chunks)))
        if end == len(normalized):
            break
        start = max(0, end - overlap)
    return chunks


def chunks_from_regions(
    *,
    artifact_id: str,
    source_kind: str,
    regions: Iterable[dict[str, object]],
    max_chars: int = 1200,
) -> list[SourceChunk]:
    chunks: list[SourceChunk] = []
    for region in regions:
        text = str(region.get("text") or "")
        page = region.get("page") if isinstance(region.get("page"), int) else None
        region_id = str(region.get("id") or region.get("kind") or "")
        chunks.extend(
            chunk_text(
                artifact_id=artifact_id,
                source_kind=source_kind,
                text=text,
                page=page,
                region=region_id,
                metadata={key: value for key, value in region.items() if key != "text"},
                max_chars=max_chars,
            )
        )
    return chunks


def _chunk(
    artifact_id: str,
    source_kind: str,
    page: int | None,
    region: str | None,
    text: str,
    metadata: dict[str, object],
    index: int,
) -> SourceChunk:
    digest = hashlib.sha256(f"{artifact_id}:{source_kind}:{page}:{region}:{index}:{text}".encode("utf-8")).hexdigest()[:24]
    return SourceChunk(
        id=f"chk_{digest}",
        artifactId=artifact_id,
        sourceKind=source_kind,
        page=page,
        region=region,
        text=text,
        metadata=metadata,
    )
