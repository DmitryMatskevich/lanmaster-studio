from __future__ import annotations

import importlib
import os

from fastapi.testclient import TestClient


def _client(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'studio-test.db'}"
    os.environ["STUDIO_AUTH_MODE"] = "dev"
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
        headers={"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"},
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


def test_dev_auth_and_rbac_negative_contract(tmp_path):
    client = next(_client(tmp_path))

    viewer = client.get("/api/v1/auth/me", headers={"X-Dev-User": "viewer@example.test"})
    assert viewer.status_code == 200
    assert viewer.json()["roles"] == ["viewer"]

    denied = client.post(
        "/api/v1/models",
        headers={"X-Dev-User": "viewer@example.test", "X-Dev-Roles": "viewer"},
        json={"article": "RBAC-DENIED"},
    )
    assert denied.status_code == 403

    bad_role = client.get("/api/v1/auth/me", headers={"X-Dev-Roles": "owner"})
    assert bad_role.status_code == 400

    allowed = client.post(
        "/api/v1/models",
        headers={"X-Dev-User": "admin@example.test", "X-Dev-Roles": "admin"},
        json={"article": "RBAC-ALLOWED"},
    )
    assert allowed.status_code == 201


def test_prod_auth_mode_rejects_dev_headers_until_oidc_configured(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'studio-test.db'}"
    os.environ["STUDIO_AUTH_MODE"] = "oidc"
    import studio_api.config
    import studio_api.db
    import studio_api.main
    import studio_api.repository

    importlib.reload(studio_api.config)
    importlib.reload(studio_api.db)
    importlib.reload(studio_api.repository)
    importlib.reload(studio_api.main)

    with TestClient(studio_api.main.app) as client:
        health = client.get("/health")
        assert health.status_code == 200

        denied = client.get(
            "/api/v1/auth/me",
            headers={"X-Dev-User": "admin@example.test", "X-Dev-Roles": "admin"},
        )
        assert denied.status_code == 501
        assert "OIDC authentication is not configured" in denied.json()["detail"]


def test_draft_patch_commit_lifecycle_with_optimistic_lock(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"}

    model = client.post(
        "/api/v1/models",
        headers=engineer,
        json={"article": "P4-03-LIFECYCLE"},
    ).json()

    draft_response = client.post(
        f"/api/v1/models/{model['id']}/drafts",
        headers=engineer,
        json={},
    )
    assert draft_response.status_code == 201
    draft = draft_response.json()
    token = draft["headRevisionToken"]

    conflict = client.post(
        f"/api/v1/drafts/{draft['id']}/patches",
        headers=engineer,
        json={
            "baseRevisionToken": "stale-token",
            "operations": [{"op": "setParameter", "path": "/width", "value": 600}],
        },
    )
    assert conflict.status_code == 409

    patch_response = client.post(
        f"/api/v1/drafts/{draft['id']}/patches",
        headers=engineer,
        json={
            "baseRevisionToken": token,
            "operations": [{"op": "setParameter", "path": "/width", "value": 600}],
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["actor"] == "engineer@example.test"

    updated_draft = client.get(f"/api/v1/drafts/{draft['id']}", headers={"X-Dev-Roles": "viewer"}).json()
    assert updated_draft["headRevisionToken"] != token

    commit_response = client.post(
        f"/api/v1/drafts/{draft['id']}/commit",
        headers=engineer,
        json={
            "baseRevisionToken": updated_draft["headRevisionToken"],
            "schemaVersion": "2.0.0",
            "pmd": {
                "schemaVersion": "2.0.0",
                "id": "p4-03-lifecycle",
                "parameters": {"width": 600},
            },
        },
    )
    assert commit_response.status_code == 200
    revision = commit_response.json()
    assert revision["id"].startswith("rev_")
    assert revision["contentHash"].startswith("sha256:")

    closed = client.post(
        f"/api/v1/drafts/{draft['id']}/patches",
        headers=engineer,
        json={
            "baseRevisionToken": updated_draft["headRevisionToken"],
            "operations": [{"op": "setParameter", "path": "/width", "value": 800}],
        },
    )
    assert closed.status_code == 409

    published = client.get(f"/api/v1/models/{model['id']}", headers={"X-Dev-Roles": "viewer"}).json()
    assert published["status"] == "published"
    assert published["activeRevisionId"] == revision["id"]


def test_job_queue_worker_protocol_and_idempotency(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"}

    first = client.post(
        "/api/v1/jobs",
        headers={**engineer, "Idempotency-Key": "p4-04-preview-1"},
        json={
            "type": "preview",
            "inputHash": "sha256:abc",
            "payload": {"draftId": "drf_test"},
        },
    )
    assert first.status_code == 202
    job = first.json()
    assert job["state"] == "queued"
    assert job["idempotencyKey"] == "p4-04-preview-1"

    repeated = client.post(
        "/api/v1/jobs",
        headers={**engineer, "Idempotency-Key": "p4-04-preview-1"},
        json={
            "type": "preview",
            "inputHash": "sha256:abc",
            "payload": {"draftId": "drf_test"},
        },
    )
    assert repeated.status_code == 202
    assert repeated.json()["id"] == job["id"]

    claimed = client.post(
        "/api/v1/workers/claim",
        headers=engineer,
        json={"workerId": "cad-worker-1", "types": ["preview"]},
    )
    assert claimed.status_code == 200
    assert claimed.json()["id"] == job["id"]
    assert claimed.json()["state"] == "running"

    heartbeat = client.post(
        f"/api/v1/jobs/{job['id']}/heartbeat",
        headers=engineer,
        json={"workerId": "cad-worker-1", "progress": 42},
    )
    assert heartbeat.status_code == 200
    assert heartbeat.json()["progress"] == 42

    wrong_worker = client.post(
        f"/api/v1/jobs/{job['id']}/heartbeat",
        headers=engineer,
        json={"workerId": "other-worker", "progress": 50},
    )
    assert wrong_worker.status_code == 409

    cancelled = client.post(f"/api/v1/jobs/{job['id']}/cancel", headers=engineer)
    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "cancelled"

    retried = client.post(f"/api/v1/jobs/{job['id']}/retry", headers=engineer)
    assert retried.status_code == 200
    assert retried.json()["state"] == "queued"
    assert retried.json()["attempt"] == 2
