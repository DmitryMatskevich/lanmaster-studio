from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response, WebSocket, status
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .auth import Role, UserContext, current_user, require_roles
from .config import get_settings
from .db import apply_migrations, connect
from .models import HealthResponse, ModelCreate, ModelList, ModelSummary, UserInfo
from .models import (
    ArtifactSummary,
    AuditEventList,
    DownloadUrl,
    EventList,
    DraftCommit,
    DraftCreate,
    DraftSummary,
    JobCreate,
    JobAccepted,
    JobSummary,
    ObservabilitySummary,
    PatchCreate,
    PatchSummary,
    PreviewRequest,
    ReleaseCreate,
    ReleaseSummary,
    RevisionDetail,
    RevisionList,
    UploadComplete,
    UploadIntent,
    UploadIntentCreate,
    RevisionSummary,
    WorkerClaimRequest,
    WorkerHeartbeat,
)
from .repository import (
    abandon_draft,
    apply_patch,
    cancel_job,
    claim_job,
    commit_draft,
    create_draft,
    create_model,
    create_download_url,
    create_upload_intent,
    get_draft,
    get_job,
    get_model,
    complete_upload,
    get_artifact,
    artifact_object_key,
    heartbeat_job,
    enqueue_job,
    enqueue_preview,
    create_release,
    get_release,
    get_observability_summary,
    list_events,
    list_audit_events,
    list_models,
    list_revisions,
    get_revision,
    retry_job,
    record_audit,
)
from .storage import object_path, verify_download_signature
from .trace import new_trace_id, trace_id_var


settings = get_settings()
FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    apply_migrations(settings)
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or new_trace_id()
    token = trace_id_var.set(trace_id)
    try:
        response = await call_next(request)
    finally:
        trace_id_var.reset(token)
    response.headers["X-Trace-Id"] = trace_id
    return response


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    with connect(settings) as conn:
        conn.execute("SELECT 1").fetchone()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=__version__,
        database="ok",
    )


@app.get(f"{settings.api_prefix}/models", response_model=ModelList, tags=["models"])
def api_list_models(
    query: Optional[str] = Query(default=None, max_length=120),
    limit: int = Query(default=50, ge=1, le=100),
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> ModelList:
    return ModelList(items=list_models(query=query, limit=limit))


@app.post(
    f"{settings.api_prefix}/models",
    response_model=ModelSummary,
    status_code=status.HTTP_201_CREATED,
    tags=["models"],
)
def api_create_model(
    payload: ModelCreate,
    response: Response,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> ModelSummary:
    model = create_model(payload)
    record_audit(_user.subject, "model.create", "model", model.id, {"article": model.article})
    response.headers["Location"] = f"{settings.api_prefix}/models/{model.id}"
    return model


@app.get(f"{settings.api_prefix}/models/{{model_id}}", response_model=ModelSummary, tags=["models"])
def api_get_model(
    model_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> ModelSummary:
    model = get_model(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@app.get(f"{settings.api_prefix}/models/{{model_id}}/revisions", response_model=RevisionList, tags=["models"])
def api_list_model_revisions(
    model_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> RevisionList:
    revisions = list_revisions(model_id)
    if revisions is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return revisions


@app.get(f"{settings.api_prefix}/revisions/{{revision_id}}", response_model=RevisionDetail, tags=["models"])
def api_get_revision(
    revision_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> RevisionDetail:
    revision = get_revision(revision_id)
    if revision is None:
        raise HTTPException(status_code=404, detail="Revision not found")
    return revision


@app.post(
    f"{settings.api_prefix}/models/{{model_id}}/drafts",
    response_model=DraftSummary,
    status_code=status.HTTP_201_CREATED,
    tags=["drafts"],
)
def api_create_draft(
    model_id: str,
    payload: DraftCreate,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> DraftSummary:
    try:
        draft = create_draft(model_id, payload.baseRevisionId)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if draft is None:
        raise HTTPException(status_code=404, detail="Model not found")
    record_audit(_user.subject, "draft.create", "draft", draft.id, {"modelId": model_id})
    return draft


@app.get(f"{settings.api_prefix}/drafts/{{draft_id}}", response_model=DraftSummary, tags=["drafts"])
def api_get_draft(
    draft_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> DraftSummary:
    draft = get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@app.post(f"{settings.api_prefix}/drafts/{{draft_id}}/patches", response_model=PatchSummary, tags=["drafts"])
def api_apply_patch(
    draft_id: str,
    payload: PatchCreate,
    user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> PatchSummary:
    result = apply_patch(draft_id, payload, actor=user.subject)
    if result is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    if result == "REVISION_CONFLICT":
        raise HTTPException(status_code=409, detail="Draft head revision token changed")
    if result == "DRAFT_CLOSED":
        raise HTTPException(status_code=409, detail="Draft is not open")
    record_audit(user.subject, "draft.patch", "draft", draft_id, {"patchId": result.id})
    return result


@app.post(f"{settings.api_prefix}/drafts/{{draft_id}}/commit", response_model=RevisionSummary, tags=["drafts"])
def api_commit_draft(
    draft_id: str,
    payload: DraftCommit,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> RevisionSummary:
    result = commit_draft(draft_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    if result == "REVISION_CONFLICT":
        raise HTTPException(status_code=409, detail="Draft head revision token changed")
    if result == "DRAFT_CLOSED":
        raise HTTPException(status_code=409, detail="Draft is not open")
    record_audit(_user.subject, "draft.commit", "revision", result.id, {"draftId": draft_id})
    return result


@app.delete(f"{settings.api_prefix}/drafts/{{draft_id}}", status_code=status.HTTP_204_NO_CONTENT, tags=["drafts"])
def api_abandon_draft(
    draft_id: str,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> Response:
    result = abandon_draft(draft_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    if result is False:
        raise HTTPException(status_code=409, detail="Draft is not open")
    record_audit(_user.subject, "draft.abandon", "draft", draft_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    f"{settings.api_prefix}/jobs",
    response_model=JobSummary,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["jobs"],
)
def api_enqueue_job(
    payload: JobCreate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> JobSummary:
    job = enqueue_job(payload, idempotency_key)
    record_audit(_user.subject, "job.enqueue", "job", job.id, {"type": job.type})
    return job


@app.get(f"{settings.api_prefix}/jobs/{{job_id}}", response_model=JobSummary, tags=["jobs"])
def api_get_job(
    job_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> JobSummary:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post(f"{settings.api_prefix}/jobs/{{job_id}}/cancel", response_model=JobSummary, tags=["jobs"])
def api_cancel_job(
    job_id: str,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> JobSummary:
    result = cancel_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if result == "JOB_TERMINAL":
        raise HTTPException(status_code=409, detail="Job is already terminal")
    record_audit(_user.subject, "job.cancel", "job", job_id)
    return result


@app.post(f"{settings.api_prefix}/jobs/{{job_id}}/retry", response_model=JobSummary, tags=["jobs"])
def api_retry_job(
    job_id: str,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> JobSummary:
    result = retry_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if result == "JOB_NOT_RETRYABLE":
        raise HTTPException(status_code=409, detail="Job is not retryable")
    record_audit(_user.subject, "job.retry", "job", job_id, {"attempt": result.attempt})
    return result


@app.post(f"{settings.api_prefix}/workers/claim", response_model=Optional[JobSummary], tags=["workers"])
def api_claim_job(
    payload: WorkerClaimRequest,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> Optional[JobSummary]:
    job = claim_job(payload)
    if job is not None:
        record_audit(_user.subject, "worker.claim", "job", job.id, {"workerId": payload.workerId})
    return job


@app.post(f"{settings.api_prefix}/jobs/{{job_id}}/heartbeat", response_model=JobSummary, tags=["workers"])
def api_heartbeat_job(
    job_id: str,
    payload: WorkerHeartbeat,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> JobSummary:
    result = heartbeat_job(job_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if result == "HEARTBEAT_REJECTED":
        raise HTTPException(status_code=409, detail="Heartbeat rejected for job state or worker")
    record_audit(_user.subject, "worker.heartbeat", "job", job_id, {"progress": payload.progress})
    return result


@app.post(
    f"{settings.api_prefix}/drafts/{{draft_id}}/preview",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["orchestration"],
)
def api_preview_draft(
    draft_id: str,
    payload: PreviewRequest,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> JobAccepted:
    result = enqueue_preview(draft_id, payload, idempotency_key)
    if result is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    if result == "REVISION_CONFLICT":
        raise HTTPException(status_code=409, detail="Draft head revision token changed")
    if result == "DRAFT_CLOSED":
        raise HTTPException(status_code=409, detail="Draft is not open")
    record_audit(_user.subject, "preview.enqueue", "job", result.jobId, {"draftId": draft_id})
    return result


@app.post(
    f"{settings.api_prefix}/revisions/{{revision_id}}/releases",
    response_model=ReleaseSummary,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["orchestration"],
)
def api_create_release(
    revision_id: str,
    payload: ReleaseCreate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> ReleaseSummary:
    release = create_release(revision_id, payload, idempotency_key)
    if release is None:
        raise HTTPException(status_code=404, detail="Revision not found")
    record_audit(_user.subject, "release.create", "release", release.id, {"revisionId": revision_id})
    return release


@app.get(f"{settings.api_prefix}/releases/{{release_id}}", response_model=ReleaseSummary, tags=["orchestration"])
def api_get_release(
    release_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> ReleaseSummary:
    release = get_release(release_id)
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    return release


@app.post(
    f"{settings.api_prefix}/documents/upload-intents",
    response_model=UploadIntent,
    status_code=status.HTTP_201_CREATED,
    tags=["artifacts"],
)
def api_create_upload_intent(
    payload: UploadIntentCreate,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> UploadIntent:
    intent = create_upload_intent(payload)
    record_audit(_user.subject, "artifact.upload_intent", "artifact", intent.artifactId, {"scope": payload.scope})
    return intent


@app.post(f"{settings.api_prefix}/documents/complete-upload", response_model=ArtifactSummary, tags=["artifacts"])
def api_complete_upload(
    payload: UploadComplete,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> ArtifactSummary:
    result = complete_upload(payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if result == "OBJECT_MISSING":
        raise HTTPException(status_code=409, detail="Uploaded object is missing")
    if result == "HASH_OR_SIZE_MISMATCH":
        raise HTTPException(status_code=422, detail="Uploaded object hash or size mismatch")
    record_audit(_user.subject, "artifact.complete_upload", "artifact", result.id, {"sha256": result.sha256})
    return result


@app.get(f"{settings.api_prefix}/artifacts/{{artifact_id}}", response_model=ArtifactSummary, tags=["artifacts"])
def api_get_artifact(
    artifact_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> ArtifactSummary:
    artifact = get_artifact(artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@app.get(f"{settings.api_prefix}/artifacts/{{artifact_id}}/download-url", response_model=DownloadUrl, tags=["artifacts"])
def api_download_url(
    artifact_id: str,
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> DownloadUrl:
    result = create_download_url(artifact_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if result == "ARTIFACT_NOT_READY":
        raise HTTPException(status_code=409, detail="Artifact is not ready")
    return result


@app.get(f"{settings.api_prefix}/artifacts/{{artifact_id}}/download", tags=["artifacts"])
def api_download_artifact(
    artifact_id: str,
    expires: int,
    signature: str,
) -> FileResponse:
    object_key = artifact_object_key(artifact_id)
    if object_key is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if not verify_download_signature(artifact_id, object_key, expires, signature):
        raise HTTPException(status_code=403, detail="Invalid or expired signature")
    return FileResponse(object_path(object_key))


@app.get(f"{settings.api_prefix}/events", response_model=EventList, tags=["events"])
def api_events(
    afterSequence: int = Query(default=0, ge=0),
    resourceType: Optional[str] = Query(default=None),
    resourceId: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    _user: UserContext = Depends(require_roles(Role.VIEWER, Role.ENGINEER, Role.ADMIN)),
) -> EventList:
    return list_events(
        after_sequence=afterSequence,
        resource_type=resourceType,
        resource_id=resourceId,
        limit=limit,
    )


@app.get(f"{settings.api_prefix}/audit-events", response_model=AuditEventList, tags=["audit"])
def api_audit_events(
    traceId: Optional[str] = Query(default=None),
    resourceType: Optional[str] = Query(default=None),
    resourceId: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    _user: UserContext = Depends(require_roles(Role.ADMIN)),
) -> AuditEventList:
    return list_audit_events(
        trace_id=traceId,
        resource_type=resourceType,
        resource_id=resourceId,
        limit=limit,
    )


@app.websocket(f"{settings.api_prefix}/ws")
async def api_ws(websocket: WebSocket, afterSequence: int = 0) -> None:
    await websocket.accept()
    events = list_events(after_sequence=afterSequence)
    await websocket.send_json(events.model_dump(mode="json"))
    await websocket.close()


@app.get(f"{settings.api_prefix}/auth/me", response_model=UserInfo, tags=["auth"])
def api_auth_me(user: UserContext = Depends(current_user)) -> UserInfo:
    return UserInfo(
        subject=user.subject,
        displayName=user.displayName,
        roles=[role.value for role in user.roles],
        authMode=user.authMode,
    )


@app.get(f"{settings.api_prefix}/observability/summary", response_model=ObservabilitySummary, tags=["observability"])
def api_observability_summary(
    _user: UserContext = Depends(require_roles(Role.ADMIN)),
) -> ObservabilitySummary:
    return get_observability_summary(settings.app_name, __version__)


def _metric_lines(summary: ObservabilitySummary) -> str:
    lines = [
        "# HELP lanmaster_studio_models_total Total Studio models.",
        "# TYPE lanmaster_studio_models_total gauge",
        f"lanmaster_studio_models_total {summary.modelsTotal}",
        "# HELP lanmaster_studio_drafts_open Open Studio drafts.",
        "# TYPE lanmaster_studio_drafts_open gauge",
        f"lanmaster_studio_drafts_open {summary.draftsOpen}",
        "# HELP lanmaster_studio_events_total Durable events stored.",
        "# TYPE lanmaster_studio_events_total counter",
        f"lanmaster_studio_events_total {summary.eventsTotal}",
        "# HELP lanmaster_studio_audit_events_total Audit events stored.",
        "# TYPE lanmaster_studio_audit_events_total counter",
        f"lanmaster_studio_audit_events_total {summary.auditEventsTotal}",
        "# HELP lanmaster_studio_last_event_sequence Last durable event sequence.",
        "# TYPE lanmaster_studio_last_event_sequence gauge",
        f"lanmaster_studio_last_event_sequence {summary.lastEventSequence}",
    ]
    for item in summary.jobsByState:
        lines.append(f'lanmaster_studio_jobs{{state="{item.state}"}} {item.count}')
    for item in summary.releasesByStatus:
        lines.append(f'lanmaster_studio_releases{{status="{item.state}"}} {item.count}')
    for item in summary.artifactsByStatus:
        lines.append(f'lanmaster_studio_artifacts{{status="{item.state}"}} {item.count}')
    return "\n".join(lines) + "\n"


@app.get("/metrics", response_class=PlainTextResponse, tags=["observability"])
def api_metrics() -> PlainTextResponse:
    summary = get_observability_summary(settings.app_name, __version__)
    return PlainTextResponse(_metric_lines(summary), media_type="text/plain; version=0.0.4")


@app.get(f"{settings.api_prefix}/observability/dashboard", response_class=HTMLResponse, tags=["observability"])
def api_observability_dashboard(
    _user: UserContext = Depends(require_roles(Role.ADMIN)),
) -> HTMLResponse:
    summary = get_observability_summary(settings.app_name, __version__)
    jobs = "".join(f"<li>{item.state}: {item.count}</li>" for item in summary.jobsByState) or "<li>none</li>"
    releases = "".join(f"<li>{item.state}: {item.count}</li>" for item in summary.releasesByStatus) or "<li>none</li>"
    artifacts = "".join(f"<li>{item.state}: {item.count}</li>" for item in summary.artifactsByStatus) or "<li>none</li>"
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>LANMASTER Studio Observability</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1f2937; }}
    main {{ max-width: 960px; }}
    section {{ border-top: 1px solid #d1d5db; padding: 16px 0; }}
    dl {{ display: grid; grid-template-columns: 220px 1fr; gap: 8px 20px; }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0; }}
  </style>
</head>
<body>
  <main>
    <h1>LANMASTER Studio Observability</h1>
    <section>
      <dl>
        <dt>Service</dt><dd>{summary.service}</dd>
        <dt>Version</dt><dd>{summary.version}</dd>
        <dt>Models</dt><dd>{summary.modelsTotal}</dd>
        <dt>Open drafts</dt><dd>{summary.draftsOpen}</dd>
        <dt>Events</dt><dd>{summary.eventsTotal}</dd>
        <dt>Audit events</dt><dd>{summary.auditEventsTotal}</dd>
        <dt>Last event sequence</dt><dd>{summary.lastEventSequence}</dd>
        <dt>Generated</dt><dd>{summary.generatedAt.isoformat()}</dd>
      </dl>
    </section>
    <section><h2>Jobs</h2><ul>{jobs}</ul></section>
    <section><h2>Releases</h2><ul>{releases}</ul></section>
    <section><h2>Artifacts</h2><ul>{artifacts}</ul></section>
  </main>
</body>
    </html>"""
    return HTMLResponse(html)


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")


    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_app(full_path: str) -> FileResponse:
        index_path = FRONTEND_DIST / "index.html"
        if full_path.startswith("api/") or full_path in {"health", "metrics"}:
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(index_path)
