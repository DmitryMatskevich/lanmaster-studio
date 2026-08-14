from __future__ import annotations

import importlib
import os

from fastapi.testclient import TestClient


def _client(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'studio-test.db'}"
    import studio_api.config
    import studio_api.db
    import studio_api.main
    import studio_api.repository

    importlib.reload(studio_api.config)
    importlib.reload(studio_api.db)
    importlib.reload(studio_api.repository)
    importlib.reload(studio_api.main)
    with TestClient(studio_api.main.app) as client:
        yield client


def test_health_and_openapi_contract(tmp_path):
    client = next(_client(tmp_path))

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    openapi = client.get("/api/v1/openapi.json")
    assert openapi.status_code == 200
    spec = openapi.json()
    assert spec["info"]["title"] == "LANMASTER Studio"
    assert "/api/v1/models" in spec["paths"]
    assert "/api/v1/models/{model_id}" in spec["paths"]


def test_model_lifecycle_seed_contract(tmp_path):
    client = next(_client(tmp_path))

    created = client.post(
        "/api/v1/models",
        json={
            "article": "TWT-CBB-42U-6x10-P1",
            "manufacturer": "LANMASTER",
            "series": "TWT-CBB",
            "name": "Business 42U 600x1000",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["id"].startswith("mdl_")
    assert body["status"] == "draft"
    assert created.headers["location"] == f"/api/v1/models/{body['id']}"

    fetched = client.get(f"/api/v1/models/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["article"] == "TWT-CBB-42U-6x10-P1"

    listed = client.get("/api/v1/models", params={"query": "6x10"})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [body["id"]]

