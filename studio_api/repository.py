from __future__ import annotations

import hashlib
import json
from datetime import datetime

from .db import session
from .models import (
    DraftCommit,
    DraftSummary,
    ModelCreate,
    ModelSummary,
    PatchCreate,
    PatchSummary,
    RevisionSummary,
    new_id,
    utc_now,
)


def _row_to_model(row) -> ModelSummary:
    return ModelSummary(
        id=row["id"],
        article=row["article"],
        manufacturer=row["manufacturer"],
        series=row["series"],
        name=row["name"],
        status=row["status"],
        activeRevisionId=row["active_revision_id"],
        createdAt=datetime.fromisoformat(row["created_at"]),
        updatedAt=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_draft(row) -> DraftSummary:
    return DraftSummary(
        id=row["id"],
        modelId=row["model_id"],
        baseRevisionId=row["base_revision_id"],
        headRevisionToken=row["head_revision_token"],
        status=row["status"],
        createdAt=datetime.fromisoformat(row["created_at"]),
        updatedAt=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_patch(row) -> PatchSummary:
    return PatchSummary(
        id=row["id"],
        draftId=row["draft_id"],
        actor=row["actor"],
        operations=json.loads(row["operations_json"]),
        status=row["status"],
        createdAt=datetime.fromisoformat(row["created_at"]),
    )


def _row_to_revision(row) -> RevisionSummary:
    return RevisionSummary(
        id=row["id"],
        modelId=row["model_id"],
        parentId=row["parent_id"],
        schemaVersion=row["schema_version"],
        contentHash=row["content_hash"],
        createdAt=datetime.fromisoformat(row["created_at"]),
    )


def _canonical_hash(payload: dict) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def create_model(payload: ModelCreate) -> ModelSummary:
    now = utc_now().isoformat()
    model_id = new_id("mdl")
    with session() as conn:
        conn.execute(
            """
            INSERT INTO models (
              id, article, manufacturer, series, name, status,
              active_revision_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'draft', NULL, ?, ?)
            """,
            (
                model_id,
                payload.article,
                payload.manufacturer,
                payload.series,
                payload.name,
                now,
                now,
            ),
        )
        row = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
    return _row_to_model(row)


def list_models(query: str | None = None, limit: int = 50) -> list[ModelSummary]:
    limit = max(1, min(limit, 100))
    sql = "SELECT * FROM models"
    params: list[object] = []
    if query:
        sql += " WHERE lower(article) LIKE ? OR lower(name) LIKE ?"
        needle = f"%{query.lower()}%"
        params.extend([needle, needle])
    sql += " ORDER BY updated_at DESC, id DESC LIMIT ?"
    params.append(limit)
    with session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_model(row) for row in rows]


def get_model(model_id: str) -> ModelSummary | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
    return _row_to_model(row) if row else None


def create_draft(model_id: str, base_revision_id: str | None = None) -> DraftSummary | None:
    now = utc_now().isoformat()
    draft_id = new_id("drf")
    token = new_id("tok")
    with session() as conn:
        model = conn.execute("SELECT id FROM models WHERE id = ?", (model_id,)).fetchone()
        if model is None:
            return None
        if base_revision_id is not None:
            base = conn.execute(
                "SELECT id FROM revisions WHERE id = ? AND model_id = ?",
                (base_revision_id, model_id),
            ).fetchone()
            if base is None:
                raise ValueError("Base revision does not belong to model")
        conn.execute(
            """
            INSERT INTO drafts (
              id, model_id, base_revision_id, head_revision_token, status,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'open', ?, ?)
            """,
            (draft_id, model_id, base_revision_id, token, now, now),
        )
        row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    return _row_to_draft(row)


def get_draft(draft_id: str) -> DraftSummary | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    return _row_to_draft(row) if row else None


def apply_patch(draft_id: str, payload: PatchCreate, actor: str) -> PatchSummary | str | None:
    now = utc_now().isoformat()
    patch_id = new_id("pat")
    next_token = new_id("tok")
    with session() as conn:
        draft = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if draft is None:
            return None
        if draft["status"] != "open":
            return "DRAFT_CLOSED"
        if draft["head_revision_token"] != payload.baseRevisionToken:
            return "REVISION_CONFLICT"
        conn.execute(
            """
            INSERT INTO patches (
              id, draft_id, actor, operations_json, status, created_at
            ) VALUES (?, ?, ?, ?, 'accepted', ?)
            """,
            (
                patch_id,
                draft_id,
                actor,
                json.dumps(payload.operations, sort_keys=True, ensure_ascii=False),
                now,
            ),
        )
        conn.execute(
            "UPDATE drafts SET head_revision_token = ?, updated_at = ? WHERE id = ?",
            (next_token, now, draft_id),
        )
        row = conn.execute("SELECT * FROM patches WHERE id = ?", (patch_id,)).fetchone()
    return _row_to_patch(row)


def commit_draft(draft_id: str, payload: DraftCommit) -> RevisionSummary | str | None:
    now = utc_now().isoformat()
    revision_id = new_id("rev")
    content_hash = _canonical_hash(payload.pmd)
    with session() as conn:
        draft = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if draft is None:
            return None
        if draft["status"] != "open":
            return "DRAFT_CLOSED"
        if draft["head_revision_token"] != payload.baseRevisionToken:
            return "REVISION_CONFLICT"
        conn.execute(
            """
            INSERT INTO revisions (
              id, model_id, parent_id, schema_version, content_hash, pmd_json,
              created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                revision_id,
                draft["model_id"],
                draft["base_revision_id"],
                payload.schemaVersion,
                content_hash,
                json.dumps(payload.pmd, sort_keys=True, ensure_ascii=False),
                now,
            ),
        )
        conn.execute(
            "UPDATE drafts SET status = 'committed', updated_at = ? WHERE id = ?",
            (now, draft_id),
        )
        conn.execute(
            """
            UPDATE models
            SET active_revision_id = ?, status = 'published', updated_at = ?
            WHERE id = ?
            """,
            (revision_id, now, draft["model_id"]),
        )
        row = conn.execute("SELECT * FROM revisions WHERE id = ?", (revision_id,)).fetchone()
    return _row_to_revision(row)


def abandon_draft(draft_id: str) -> bool | None:
    now = utc_now().isoformat()
    with session() as conn:
        draft = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if draft is None:
            return None
        if draft["status"] != "open":
            return False
        conn.execute(
            "UPDATE drafts SET status = 'abandoned', updated_at = ? WHERE id = ?",
            (now, draft_id),
        )
    return True
