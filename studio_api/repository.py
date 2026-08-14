from __future__ import annotations

import hashlib
import json
from datetime import datetime

from .db import session
from .models import (
    DraftCommit,
    DraftSummary,
    JobCreate,
    JobAccepted,
    JobSummary,
    ModelCreate,
    ModelSummary,
    PatchCreate,
    PatchSummary,
    PreviewRequest,
    ReleaseCreate,
    ReleaseSummary,
    RevisionSummary,
    WorkerClaimRequest,
    WorkerHeartbeat,
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


def _row_to_job(row) -> JobSummary:
    return JobSummary(
        id=row["id"],
        type=row["type"],
        state=row["state"],
        inputHash=row["input_hash"],
        idempotencyKey=row["idempotency_key"],
        attempt=row["attempt"],
        progress=row["progress"],
        workerId=row["worker_id"],
        heartbeatAt=datetime.fromisoformat(row["heartbeat_at"]) if row["heartbeat_at"] else None,
        createdAt=datetime.fromisoformat(row["created_at"]),
        updatedAt=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_release(row) -> ReleaseSummary:
    return ReleaseSummary(
        id=row["id"],
        revisionId=row["revision_id"],
        profile=row["profile"],
        status=row["status"],
        jobId=row["job_id"],
        manifestArtifactId=row["manifest_artifact_id"],
        createdAt=datetime.fromisoformat(row["created_at"]),
        updatedAt=datetime.fromisoformat(row["updated_at"]),
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


def enqueue_job(payload: JobCreate, idempotency_key: str | None) -> JobSummary:
    now = utc_now().isoformat()
    with session() as conn:
        if idempotency_key:
            existing = conn.execute(
                "SELECT * FROM jobs WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                return _row_to_job(existing)
        job_id = new_id("job")
        conn.execute(
            """
            INSERT INTO jobs (
              id, type, state, input_hash, idempotency_key, payload_json,
              attempt, progress, created_at, updated_at
            ) VALUES (?, ?, 'queued', ?, ?, ?, 1, 0, ?, ?)
            """,
            (
                job_id,
                payload.type,
                payload.inputHash,
                idempotency_key,
                json.dumps(payload.payload, sort_keys=True, ensure_ascii=False),
                now,
                now,
            ),
        )
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_job(row)


def get_job(job_id: str) -> JobSummary | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_job(row) if row else None


def cancel_job(job_id: str) -> JobSummary | None | str:
    now = utc_now().isoformat()
    with session() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        if row["state"] in {"succeeded", "failed", "cancelled"}:
            return "JOB_TERMINAL"
        conn.execute(
            "UPDATE jobs SET state = 'cancelled', updated_at = ? WHERE id = ?",
            (now, job_id),
        )
        updated = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_job(updated)


def retry_job(job_id: str) -> JobSummary | None | str:
    now = utc_now().isoformat()
    with session() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        if row["state"] not in {"failed", "cancelled"}:
            return "JOB_NOT_RETRYABLE"
        conn.execute(
            """
            UPDATE jobs
            SET state = 'queued', attempt = attempt + 1, progress = 0,
                worker_id = NULL, heartbeat_at = NULL, updated_at = ?
            WHERE id = ?
            """,
            (now, job_id),
        )
        updated = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_job(updated)


def claim_job(payload: WorkerClaimRequest) -> JobSummary | None:
    now = utc_now().isoformat()
    with session() as conn:
        params: list[object] = []
        sql = "SELECT * FROM jobs WHERE state = 'queued'"
        if payload.types:
            sql += " AND type IN (" + ",".join("?" for _ in payload.types) + ")"
            params.extend(payload.types)
        sql += " ORDER BY created_at ASC LIMIT 1"
        row = conn.execute(sql, params).fetchone()
        if row is None:
            return None
        conn.execute(
            """
            UPDATE jobs
            SET state = 'running', worker_id = ?, heartbeat_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (payload.workerId, now, now, row["id"]),
        )
        updated = conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()
    return _row_to_job(updated)


def heartbeat_job(job_id: str, payload: WorkerHeartbeat) -> JobSummary | None | str:
    now = utc_now().isoformat()
    with session() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        if row["state"] != "running" or row["worker_id"] != payload.workerId:
            return "HEARTBEAT_REJECTED"
        conn.execute(
            """
            UPDATE jobs
            SET heartbeat_at = ?, progress = ?, updated_at = ?
            WHERE id = ?
            """,
            (now, payload.progress, now, job_id),
        )
        updated = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_job(updated)


def enqueue_preview(draft_id: str, payload: PreviewRequest, idempotency_key: str | None) -> JobAccepted | None | str:
    with session() as conn:
        draft = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if draft is None:
            return None
        if draft["status"] != "open":
            return "DRAFT_CLOSED"
        if draft["head_revision_token"] != payload.baseRevisionToken:
            return "REVISION_CONFLICT"
    job = enqueue_job(
        JobCreate(
            type="preview",
            inputHash=_canonical_hash(
                {
                    "draftId": draft_id,
                    "token": payload.baseRevisionToken,
                    "profile": payload.profile,
                }
            ),
            payload={
                "draftId": draft_id,
                "profile": payload.profile,
                "clientRequestId": payload.clientRequestId,
            },
        ),
        idempotency_key,
    )
    return JobAccepted(
        jobId=job.id,
        status=job.state,
        affectedComponentIds=[],
        eventsUrl=f"/api/v1/events?jobId={job.id}",
    )


def create_release(revision_id: str, payload: ReleaseCreate, idempotency_key: str | None) -> ReleaseSummary | None:
    now = utc_now().isoformat()
    with session() as conn:
        revision = conn.execute("SELECT * FROM revisions WHERE id = ?", (revision_id,)).fetchone()
        if revision is None:
            return None
    job = enqueue_job(
        JobCreate(
            type="release",
            inputHash=_canonical_hash(
                {
                    "revisionId": revision_id,
                    "profile": payload.profile,
                }
            ),
            payload={
                "revisionId": revision_id,
                "profile": payload.profile,
                "clientRequestId": payload.clientRequestId,
            },
        ),
        idempotency_key,
    )
    release_id = new_id("rel")
    with session() as conn:
        existing = None
        if idempotency_key:
            existing = conn.execute(
                "SELECT * FROM releases WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        if existing is not None:
            return _row_to_release(existing)
        conn.execute(
            """
            INSERT INTO releases (
              id, revision_id, profile, status, job_id, idempotency_key,
              created_at, updated_at
            ) VALUES (?, ?, ?, 'queued', ?, ?, ?, ?)
            """,
            (release_id, revision_id, payload.profile, job.id, idempotency_key, now, now),
        )
        row = conn.execute("SELECT * FROM releases WHERE id = ?", (release_id,)).fetchone()
    return _row_to_release(row)


def get_release(release_id: str) -> ReleaseSummary | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM releases WHERE id = ?", (release_id,)).fetchone()
    return _row_to_release(row) if row else None
