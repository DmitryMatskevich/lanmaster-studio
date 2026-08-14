#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    compose_path = ROOT / "docker-compose.yml"
    dockerfile = ROOT / "Dockerfile"
    env_example = ROOT / ".env.example"
    for path in (compose_path, dockerfile, env_example):
        if not path.exists():
            print(f"missing required file: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1

    compose_text = compose_path.read_text(encoding="utf-8")
    assert "studio-api:" in compose_text
    assert "context: ." in compose_text
    assert "${STUDIO_API_PORT:-8088}:8088" in compose_text
    assert "healthcheck:" in compose_text
    assert "studio-var:" in compose_text

    dockerfile_text = dockerfile.read_text(encoding="utf-8")
    assert "uvicorn" in dockerfile_text
    assert "HEALTHCHECK" in dockerfile_text
    assert "USER studio" in dockerfile_text
    assert "AS frontend-build" in dockerfile_text
    assert "frontend/dist" in dockerfile_text

    env_text = env_example.read_text(encoding="utf-8")
    assert "DATABASE_URL=sqlite:////app/var/studio.db" in env_text
    assert "STUDIO_STORAGE_DIR=/app/var/storage" in env_text

    print("Docker Compose verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
