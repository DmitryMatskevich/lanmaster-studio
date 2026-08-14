from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "LANMASTER Studio"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./var/studio.db"
    environment: str = "dev"
    auth_mode: str = "dev"
    storage_dir: str = "./var/storage"
    upload_max_size_bytes: int = 50 * 1024 * 1024
    upload_allowed_media_types: tuple[str, ...] = (
        "application/pdf",
        "image/svg+xml",
        "image/png",
        "image/jpeg",
        "text/plain",
        "application/dxf",
        "application/octet-stream",
        "model/gltf-binary",
        "model/step",
        "model/ifc",
    )
    upload_allowed_scopes: tuple[str, ...] = ("source", "model", "view", "release")
    rag_enabled: bool = True

    @property
    def sqlite_path(self) -> Path:
        if not self.database_url.startswith("sqlite:///"):
            raise ValueError("P4-01 supports sqlite:/// DATABASE_URL only")
        return Path(self.database_url.removeprefix("sqlite:///"))


def get_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./var/studio.db"),
        environment=os.environ.get("STUDIO_ENV", "dev"),
        auth_mode=os.environ.get("STUDIO_AUTH_MODE", "dev"),
        storage_dir=os.environ.get("STUDIO_STORAGE_DIR", "./var/storage"),
        upload_max_size_bytes=int(os.environ.get("STUDIO_UPLOAD_MAX_SIZE_BYTES", str(50 * 1024 * 1024))),
        upload_allowed_media_types=tuple(
            item.strip() for item in os.environ.get(
                "STUDIO_UPLOAD_ALLOWED_MEDIA_TYPES",
                "application/pdf,image/svg+xml,image/png,image/jpeg,text/plain,application/dxf,application/octet-stream,model/gltf-binary,model/step,model/ifc",
            ).split(",") if item.strip()
        ),
        upload_allowed_scopes=tuple(
            item.strip() for item in os.environ.get(
                "STUDIO_UPLOAD_ALLOWED_SCOPES",
                "source,model,view,release",
            ).split(",") if item.strip()
        ),
        rag_enabled=os.environ.get("STUDIO_RAG_ENABLED", "true").lower() in {"1", "true", "yes"},
    )
