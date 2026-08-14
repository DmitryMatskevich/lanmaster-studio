from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import Settings, get_settings


def connect(settings: Settings | None = None) -> sqlite3.Connection:
    settings = settings or get_settings()
    db_path = settings.sqlite_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def session(settings: Settings | None = None) -> Iterator[sqlite3.Connection]:
    conn = connect(settings)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migration_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "migrations"


def apply_migrations(settings: Settings | None = None) -> list[str]:
    applied: list[str] = []
    with session(settings) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version TEXT PRIMARY KEY,
              applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        existing = {
            row["version"]
            for row in conn.execute("SELECT version FROM schema_migrations")
        }
        for path in sorted(migration_dir().glob("*.sql")):
            version = path.stem
            if version in existing:
                continue
            conn.executescript(path.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                (version,),
            )
            applied.append(version)
    return applied

