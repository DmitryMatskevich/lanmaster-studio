from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta

from .db import session
from .models import (
    DraftCommit,
    DraftSummary,
    ArtifactSummary,
    AuditEventList,
    AuditEventSummary,
    DownloadUrl,
    EventList,
    EventSummary,
    JobCreate,
    JobAccepted,
    JobSummary,
    ModelCreate,
    ModelSummary,
    CountByState,
    ObservabilitySummary,
    PatchCreate,
    PatchSummary,
    PreviewRequest,
    ReleaseCreate,
    ReleaseSummary,
    RevisionList,
    RevisionSummary,
    UploadComplete,
    UploadIntent,
    UploadIntentCreate,
    WorkerClaimRequest,
    WorkerHeartbeat,
    new_id,
    utc_now,
)
from .storage import object_path, sha256_file, sign_download_path
from .trace import get_trace_id


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


def _row_to_artifact(row) -> ArtifactSummary:
    return ArtifactSummary(
        id=row["id"],
        objectKey=row["object_key"],
        sha256=row["sha256"],
        mediaType=row["media_type"],
        size=row["size"],
        scope=row["scope"],
        status=row["status"],
        createdAt=datetime.fromisoformat(row["created_at"]),
    )


def _row_to_event(row) -> EventSummary:
    return EventSummary(
        sequence=row["sequence"],
        type=row["type"],
        resourceType=row["resource_type"],
        resourceId=row["resource_id"],
        payload=json.loads(row["payload_json"]),
        createdAt=datetime.fromisoformat(row["created_at"]),
    )


def _row_to_audit(row) -> AuditEventSummary:
    return AuditEventSummary(
        id=row["id"],
        actor=row["actor"],
        action=row["action"],
        resourceType=row["resource_type"],
        resourceId=row["resource_id"],
        traceId=row["trace_id"],
        payload=json.loads(row["payload_json"]),
        createdAt=datetime.fromisoformat(row["created_at"]),
    )


def record_audit(actor: str, action: str, resource_type: str, resource_id: str, payload: dict | None = None) -> AuditEventSummary:
    audit_id = new_id("aud")
    with session() as conn:
        conn.execute(
            """
            INSERT INTO audit_events (
              id, actor, action, resource_type, resource_id, trace_id,
              payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                actor,
                action,
                resource_type,
                resource_id,
                get_trace_id(),
                json.dumps(payload or {}, sort_keys=True, ensure_ascii=False),
                utc_now().isoformat(),
            ),
        )
        row = conn.execute("SELECT * FROM audit_events WHERE id = ?", (audit_id,)).fetchone()
    return _row_to_audit(row)


def _record_event(conn, event_type: str, resource_type: str, resource_id: str, payload: dict) -> None:
    conn.execute(
        """
        INSERT INTO events (type, resource_type, resource_id, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_type,
            resource_type,
            resource_id,
            json.dumps(payload, sort_keys=True, ensure_ascii=False),
            utc_now().isoformat(),
        ),
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


def list_revisions(model_id: str) -> RevisionList | None:
    with session() as conn:
        model = conn.execute("SELECT id FROM models WHERE id = ?", (model_id,)).fetchone()
        if model is None:
            return None
        rows = conn.execute(
            "SELECT * FROM revisions WHERE model_id = ? ORDER BY created_at DESC, id DESC",
            (model_id,),
        ).fetchall()
    return RevisionList(items=[_row_to_revision(row) for row in rows])


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
        _record_event(conn, "job.queued", "job", job_id, {"state": "queued", "type": payload.type})
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
        _record_event(conn, "job.cancelled", "job", job_id, {"state": "cancelled"})
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
        _record_event(conn, "job.retried", "job", job_id, {"state": "queued", "attempt": row["attempt"] + 1})
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
        _record_event(conn, "job.running", "job", row["id"], {"state": "running", "workerId": payload.workerId})
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
        _record_event(conn, "job.heartbeat", "job", job_id, {"progress": payload.progress, "workerId": payload.workerId})
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
        _record_event(conn, "release.queued", "release", release_id, {"revisionId": revision_id, "jobId": job.id})
        row = conn.execute("SELECT * FROM releases WHERE id = ?", (release_id,)).fetchone()
    return _row_to_release(row)


def get_release(release_id: str) -> ReleaseSummary | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM releases WHERE id = ?", (release_id,)).fetchone()
    return _row_to_release(row) if row else None


def create_upload_intent(payload: UploadIntentCreate) -> UploadIntent:
    now = utc_now().isoformat()
    artifact_id = new_id("art")
    safe_name = payload.filename.replace("/", "_").replace("\\", "_")
    object_key = f"{payload.scope}/{artifact_id}/{safe_name}"
    object_path(object_key)
    with session() as conn:
        conn.execute(
            """
            INSERT INTO artifacts (
              id, object_key, sha256, media_type, size, scope, status,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """,
            (
                artifact_id,
                object_key,
                payload.sha256.removeprefix("sha256:"),
                payload.mediaType,
                payload.size,
                payload.scope,
                now,
                now,
            ),
        )
    expires = (utc_now() + timedelta(minutes=15)).replace(microsecond=0)
    return UploadIntent(
        artifactId=artifact_id,
        uploadUrl=f"file://{object_path(object_key)}",
        objectKey=object_key,
        expiresAt=expires,
    )


def complete_upload(payload: UploadComplete) -> ArtifactSummary | None | str:
    now = utc_now().isoformat()
    with session() as conn:
        row = conn.execute("SELECT * FROM artifacts WHERE id = ?", (payload.artifactId,)).fetchone()
        if row is None:
            return None
        path = object_path(row["object_key"])
        if not path.exists():
            return "OBJECT_MISSING"
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != row["size"] or actual_hash != row["sha256"]:
            return "HASH_OR_SIZE_MISMATCH"
        conn.execute(
            "UPDATE artifacts SET status = 'ready', updated_at = ? WHERE id = ?",
            (now, payload.artifactId),
        )
        _record_event(conn, "artifact.ready", "artifact", payload.artifactId, {"status": "ready"})
        updated = conn.execute("SELECT * FROM artifacts WHERE id = ?", (payload.artifactId,)).fetchone()
    return _row_to_artifact(updated)


def get_artifact(artifact_id: str) -> ArtifactSummary | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
    return _row_to_artifact(row) if row else None


def create_download_url(artifact_id: str) -> DownloadUrl | None | str:
    with session() as conn:
        row = conn.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
        if row is None:
            return None
        if row["status"] != "ready":
            return "ARTIFACT_NOT_READY"
        url, expires = sign_download_path(artifact_id, row["object_key"])
    return DownloadUrl(
        artifactId=artifact_id,
        downloadUrl=url,
        expiresAt=datetime.fromtimestamp(expires, tz=utc_now().tzinfo),
    )


def artifact_object_key(artifact_id: str) -> str | None:
    with session() as conn:
        row = conn.execute("SELECT object_key FROM artifacts WHERE id = ? AND status = 'ready'", (artifact_id,)).fetchone()
    return row["object_key"] if row else None


def list_events(after_sequence: int = 0, resource_type: str | None = None, resource_id: str | None = None, limit: int = 100) -> EventList:
    limit = max(1, min(limit, 500))
    sql = "SELECT * FROM events WHERE sequence > ?"
    params: list[object] = [after_sequence]
    if resource_type:
        sql += " AND resource_type = ?"
        params.append(resource_type)
    if resource_id:
        sql += " AND resource_id = ?"
        params.append(resource_id)
    sql += " ORDER BY sequence ASC LIMIT ?"
    params.append(limit)
    with session() as conn:
        rows = conn.execute(sql, params).fetchall()
    items = [_row_to_event(row) for row in rows]
    next_seq = items[-1].sequence if items else after_sequence
    return EventList(items=items, nextSequence=next_seq)


def list_audit_events(trace_id: str | None = None, resource_type: str | None = None, resource_id: str | None = None, limit: int = 100) -> AuditEventList:
    limit = max(1, min(limit, 500))
    sql = "SELECT * FROM audit_events WHERE 1=1"
    params: list[object] = []
    if trace_id:
        sql += " AND trace_id = ?"
        params.append(trace_id)
    if resource_type:
        sql += " AND resource_type = ?"
        params.append(resource_type)
    if resource_id:
        sql += " AND resource_id = ?"
        params.append(resource_id)
    sql += " ORDER BY created_at ASC LIMIT ?"
    params.append(limit)
    with session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return AuditEventList(items=[_row_to_audit(row) for row in rows])


def _count_by(conn, table: str, column: str) -> list[CountByState]:
    rows = conn.execute(
        f"SELECT {column} AS state, COUNT(*) AS count FROM {table} GROUP BY {column} ORDER BY {column}"
    ).fetchall()
    return [CountByState(state=row["state"], count=row["count"]) for row in rows]


def get_observability_summary(service: str, version: str) -> ObservabilitySummary:
    with session() as conn:
        models_total = conn.execute("SELECT COUNT(*) AS count FROM models").fetchone()["count"]
        drafts_open = conn.execute("SELECT COUNT(*) AS count FROM drafts WHERE status = 'open'").fetchone()["count"]
        events_total = conn.execute("SELECT COUNT(*) AS count FROM events").fetchone()["count"]
        audit_total = conn.execute("SELECT COUNT(*) AS count FROM audit_events").fetchone()["count"]
        last_sequence = conn.execute("SELECT COALESCE(MAX(sequence), 0) AS sequence FROM events").fetchone()["sequence"]
        jobs_by_state = _count_by(conn, "jobs", "state")
        releases_by_status = _count_by(conn, "releases", "status")
        artifacts_by_status = _count_by(conn, "artifacts", "status")
    return ObservabilitySummary(
        service=service,
        version=version,
        modelsTotal=models_total,
        draftsOpen=drafts_open,
        jobsByState=jobs_by_state,
        releasesByStatus=releases_by_status,
        artifactsByStatus=artifacts_by_status,
        eventsTotal=events_total,
        auditEventsTotal=audit_total,
        lastEventSequence=last_sequence,
        generatedAt=utc_now(),
    )
