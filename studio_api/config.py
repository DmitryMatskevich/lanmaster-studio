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
    )
