from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_openapi_and_ts_client_are_generated() -> None:
    subprocess.run([sys.executable, "scripts/generate_openapi.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/generate_ts_client.py"], cwd=ROOT, check=True)

    spec = json.loads((ROOT / "openapi" / "openapi.json").read_text(encoding="utf-8"))
    assert spec["openapi"].startswith("3.")
    assert "ModelSummary" in spec["components"]["schemas"]

    client = (ROOT / "clients/typescript/src/index.ts").read_text(encoding="utf-8")
    assert "export class StudioApiClient" in client
    assert "async createModel" in client

