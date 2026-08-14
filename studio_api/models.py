from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ErrorDetail(BaseModel):
    path: Optional[str] = None
    target: Optional[str] = None
    message: str


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    traceId: str
    details: List[ErrorDetail] = Field(default_factory=list)


class ModelCreate(BaseModel):
    article: str = Field(min_length=1, max_length=120)
    manufacturer: str = Field(default="LANMASTER", min_length=1, max_length=120)
    series: Optional[str] = Field(default=None, max_length=120)
    name: Optional[str] = Field(default=None, max_length=240)


class ModelSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    article: str
    manufacturer: str
    series: Optional[str] = None
    name: Optional[str] = None
    status: Literal["draft", "published", "archived"] = "draft"
    activeRevisionId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class ModelList(BaseModel):
    items: List[ModelSummary]
    nextCursor: Optional[str] = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    database: Literal["ok"]


class UserInfo(BaseModel):
    subject: str
    displayName: str
    roles: List[str]
    authMode: str


class DraftCreate(BaseModel):
    baseRevisionId: Optional[str] = None


class DraftSummary(BaseModel):
    id: str
    modelId: str
    baseRevisionId: Optional[str] = None
    headRevisionToken: str
    status: Literal["open", "committed", "abandoned"]
    createdAt: datetime
    updatedAt: datetime


class PatchCreate(BaseModel):
    baseRevisionToken: str
    operations: List[Dict[str, Any]] = Field(min_length=1)


class PatchSummary(BaseModel):
    id: str
    draftId: str
    actor: str
    operations: List[Dict[str, Any]]
    status: Literal["accepted"]
    createdAt: datetime


class DraftCommit(BaseModel):
    baseRevisionToken: str
    schemaVersion: str = "2.0.0"
    pmd: Dict[str, Any]


class RevisionSummary(BaseModel):
    id: str
    modelId: str
    parentId: Optional[str] = None
    schemaVersion: str
    contentHash: str
    createdAt: datetime


class JobCreate(BaseModel):
    type: str = Field(min_length=1, max_length=80)
    inputHash: str = Field(min_length=1, max_length=160)
    payload: Dict[str, Any] = Field(default_factory=dict)


class JobSummary(BaseModel):
    id: str
    type: str
    state: Literal["queued", "running", "succeeded", "failed", "cancelled"]
    inputHash: str
    idempotencyKey: Optional[str] = None
    attempt: int
    progress: int
    workerId: Optional[str] = None
    heartbeatAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime


class WorkerClaimRequest(BaseModel):
    workerId: str = Field(min_length=1, max_length=120)
    types: List[str] = Field(default_factory=list)


class WorkerHeartbeat(BaseModel):
    workerId: str = Field(min_length=1, max_length=120)
    progress: int = Field(ge=0, le=100)


class PreviewRequest(BaseModel):
    baseRevisionToken: str
    profile: str = Field(default="web-preview", max_length=80)
    clientRequestId: Optional[str] = Field(default=None, max_length=160)


class JobAccepted(BaseModel):
    jobId: str
    status: Literal["queued", "running"]
    affectedComponentIds: List[str] = Field(default_factory=list)
    eventsUrl: str


class ReleaseCreate(BaseModel):
    profile: str = Field(default="catalog-full", max_length=80)
    clientRequestId: Optional[str] = Field(default=None, max_length=160)


class ReleaseSummary(BaseModel):
    id: str
    revisionId: str
    profile: str
    status: Literal["queued", "running", "succeeded", "failed", "cancelled"]
    jobId: Optional[str] = None
    manifestArtifactId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class UploadIntentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=240)
    mediaType: str = Field(min_length=1, max_length=160)
    size: int = Field(gt=0)
    sha256: str = Field(min_length=64, max_length=71)
    scope: str = Field(default="source", max_length=80)


class UploadIntent(BaseModel):
    artifactId: str
    uploadUrl: str
    objectKey: str
    expiresAt: datetime


class UploadComplete(BaseModel):
    artifactId: str


class ArtifactSummary(BaseModel):
    id: str
    objectKey: str
    sha256: str
    mediaType: str
    size: int
    scope: str
    status: Literal["pending", "ready"]
    createdAt: datetime


class DownloadUrl(BaseModel):
    artifactId: str
    downloadUrl: str
    expiresAt: datetime


class EventSummary(BaseModel):
    sequence: int
    type: str
    resourceType: str
    resourceId: str
    payload: Dict[str, Any]
    createdAt: datetime


class EventList(BaseModel):
    items: List[EventSummary]
    nextSequence: Optional[int] = None
