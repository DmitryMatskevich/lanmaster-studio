from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, WebSocket, status
from fastapi.responses import FileResponse

from . import __version__
from .auth import Role, UserContext, current_user, require_roles
from .config import get_settings
from .db import apply_migrations, connect
from .models import HealthResponse, ModelCreate, ModelList, ModelSummary, UserInfo
from .models import (
    ArtifactSummary,
    DownloadUrl,
    EventList,
    DraftCommit,
    DraftCreate,
    DraftSummary,
    JobCreate,
    JobAccepted,
    JobSummary,
    PatchCreate,
    PatchSummary,
    PreviewRequest,
    ReleaseCreate,
    ReleaseSummary,
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
    list_events,
    list_models,
    retry_job,
)
from .storage import object_path, verify_download_signature


settings = get_settings()


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
    return enqueue_job(payload, idempotency_key)


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
    return result


@app.post(f"{settings.api_prefix}/workers/claim", response_model=Optional[JobSummary], tags=["workers"])
def api_claim_job(
    payload: WorkerClaimRequest,
    _user: UserContext = Depends(require_roles(Role.ENGINEER, Role.ADMIN)),
) -> Optional[JobSummary]:
    return claim_job(payload)


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
    return create_upload_intent(payload)


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
