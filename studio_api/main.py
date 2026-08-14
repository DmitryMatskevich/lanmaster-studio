from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status

from . import __version__
from .auth import Role, UserContext, current_user, require_roles
from .config import get_settings
from .db import apply_migrations, connect
from .models import HealthResponse, ModelCreate, ModelList, ModelSummary, UserInfo
from .models import DraftCommit, DraftCreate, DraftSummary, PatchCreate, PatchSummary, RevisionSummary
from .repository import (
    abandon_draft,
    apply_patch,
    commit_draft,
    create_draft,
    create_model,
    get_draft,
    get_model,
    list_models,
)


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


@app.get(f"{settings.api_prefix}/auth/me", response_model=UserInfo, tags=["auth"])
def api_auth_me(user: UserContext = Depends(current_user)) -> UserInfo:
    return UserInfo(
        subject=user.subject,
        displayName=user.displayName,
        roles=[role.value for role in user.roles],
        authMode=user.authMode,
    )
