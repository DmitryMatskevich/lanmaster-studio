from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status

from . import __version__
from .config import get_settings
from .db import apply_migrations, connect
from .models import HealthResponse, ModelCreate, ModelList, ModelSummary
from .repository import create_model, get_model, list_models


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
) -> ModelList:
    return ModelList(items=list_models(query=query, limit=limit))


@app.post(
    f"{settings.api_prefix}/models",
    response_model=ModelSummary,
    status_code=status.HTTP_201_CREATED,
    tags=["models"],
)
def api_create_model(payload: ModelCreate, response: Response) -> ModelSummary:
    model = create_model(payload)
    response.headers["Location"] = f"{settings.api_prefix}/models/{model.id}"
    return model


@app.get(f"{settings.api_prefix}/models/{{model_id}}", response_model=ModelSummary, tags=["models"])
def api_get_model(model_id: str) -> ModelSummary:
    model = get_model(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model
