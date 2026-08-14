from __future__ import annotations

from datetime import datetime

from .db import session
from .models import ModelCreate, ModelSummary, new_id, utc_now


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

