#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from studio_api.db import apply_migrations


def main() -> None:
    applied = apply_migrations()
    if applied:
        print("Applied migrations:", ", ".join(applied))
    else:
        print("Database already up to date")


if __name__ == "__main__":
    main()
