from __future__ import annotations

import importlib
import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse

from fastapi.testclient import TestClient


def _client(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'studio-test.db'}"
    os.environ["STUDIO_STORAGE_DIR"] = str(tmp_path / "storage")
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


def test_preview_and_release_orchestration_contract(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"}

    model = client.post(
        "/api/v1/models",
        headers=engineer,
        json={"article": "P4-05-ORCHESTRATION"},
    ).json()
    draft = client.post(
        f"/api/v1/models/{model['id']}/drafts",
        headers=engineer,
        json={},
    ).json()

    stale_preview = client.post(
        f"/api/v1/drafts/{draft['id']}/preview",
        headers=engineer,
        json={"baseRevisionToken": "stale", "profile": "web-preview"},
    )
    assert stale_preview.status_code == 409

    preview = client.post(
        f"/api/v1/drafts/{draft['id']}/preview",
        headers={**engineer, "Idempotency-Key": "preview-p4-05"},
        json={"baseRevisionToken": draft["headRevisionToken"], "profile": "web-preview"},
    )
    assert preview.status_code == 202
    preview_body = preview.json()
    assert preview_body["jobId"].startswith("job_")
    assert preview_body["eventsUrl"] == f"/api/v1/events?jobId={preview_body['jobId']}"

    revision = client.post(
        f"/api/v1/drafts/{draft['id']}/commit",
        headers=engineer,
        json={
            "baseRevisionToken": draft["headRevisionToken"],
            "pmd": {"schemaVersion": "2.0.0", "id": "p4-05"},
        },
    ).json()

    release = client.post(
        f"/api/v1/revisions/{revision['id']}/releases",
        headers={**engineer, "Idempotency-Key": "release-p4-05"},
        json={"profile": "catalog-full"},
    )
    assert release.status_code == 202
    release_body = release.json()
    assert release_body["id"].startswith("rel_")
    assert release_body["revisionId"] == revision["id"]
    assert release_body["status"] == "queued"
    assert release_body["jobId"].startswith("job_")

    repeated_release = client.post(
        f"/api/v1/revisions/{revision['id']}/releases",
        headers={**engineer, "Idempotency-Key": "release-p4-05"},
        json={"profile": "catalog-full"},
    )
    assert repeated_release.status_code == 202
    assert repeated_release.json()["id"] == release_body["id"]


def test_object_storage_upload_complete_and_signed_url(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"}
    data = b"lanmaster artifact"
    digest = hashlib.sha256(data).hexdigest()

    intent = client.post(
        "/api/v1/documents/upload-intents",
        headers=engineer,
        json={
            "filename": "source.txt",
            "mediaType": "text/plain",
            "size": len(data),
            "sha256": digest,
            "scope": "source",
        },
    )
    assert intent.status_code == 201
    body = intent.json()
    upload_path = Path(urlparse(body["uploadUrl"]).path)
    upload_path.write_bytes(data)

    completed = client.post(
        "/api/v1/documents/complete-upload",
        headers=engineer,
        json={"artifactId": body["artifactId"]},
    )
    assert completed.status_code == 200
    artifact = completed.json()
    assert artifact["status"] == "ready"
    assert artifact["sha256"] == digest

    download = client.get(
        f"/api/v1/artifacts/{body['artifactId']}/download-url",
        headers={"X-Dev-Roles": "viewer"},
    )
    assert download.status_code == 200
    assert f"artifactId={body['artifactId']}" in download.json()["downloadUrl"]
    downloaded = client.get(download.json()["downloadUrl"])
    assert downloaded.status_code == 200
    assert downloaded.content == data

    bad = client.post(
        "/api/v1/documents/upload-intents",
        headers=engineer,
        json={
            "filename": "bad.txt",
            "mediaType": "text/plain",
            "size": 99,
            "sha256": digest,
            "scope": "source",
        },
    ).json()
    Path(urlparse(bad["uploadUrl"]).path).write_bytes(data)
    mismatch = client.post(
        "/api/v1/documents/complete-upload",
        headers=engineer,
        json={"artifactId": bad["artifactId"]},
    )
    assert mismatch.status_code == 422


def test_events_rest_replay_and_websocket_replay(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"}

    job = client.post(
        "/api/v1/jobs",
        headers={**engineer, "Idempotency-Key": "events-job"},
        json={"type": "preview", "inputHash": "sha256:events"},
    ).json()
    client.post(
        "/api/v1/workers/claim",
        headers=engineer,
        json={"workerId": "events-worker", "types": ["preview"]},
    )
    client.post(
        f"/api/v1/jobs/{job['id']}/heartbeat",
        headers=engineer,
        json={"workerId": "events-worker", "progress": 25},
    )

    replay = client.get(
        "/api/v1/events",
        headers={"X-Dev-Roles": "viewer"},
        params={"resourceType": "job", "resourceId": job["id"]},
    )
    assert replay.status_code == 200
    events = replay.json()["items"]
    assert [event["type"] for event in events] == ["job.queued", "job.running", "job.heartbeat"]
    assert events[-1]["payload"]["progress"] == 25

    after = events[0]["sequence"]
    after_replay = client.get(
        "/api/v1/events",
        headers={"X-Dev-Roles": "viewer"},
        params={"afterSequence": after, "resourceType": "job", "resourceId": job["id"]},
    )
    assert [event["type"] for event in after_replay.json()["items"]] == ["job.running", "job.heartbeat"]

    with client.websocket_connect(f"/api/v1/ws?afterSequence={after}") as ws:
        message = ws.receive_json()
    assert any(event["type"] == "job.heartbeat" for event in message["items"])


def test_audit_events_and_trace_correlation(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer", "X-Trace-Id": "tr_test_trace"}

    created = client.post(
        "/api/v1/models",
        headers=engineer,
        json={"article": "P4-08-AUDIT"},
    )
    assert created.status_code == 201
    assert created.headers["X-Trace-Id"] == "tr_test_trace"
    model = created.json()

    viewer_denied = client.get(
        "/api/v1/audit-events",
        headers={"X-Dev-Roles": "viewer"},
    )
    assert viewer_denied.status_code == 403

    audit = client.get(
        "/api/v1/audit-events",
        headers={"X-Dev-Roles": "admin"},
        params={"traceId": "tr_test_trace", "resourceType": "model", "resourceId": model["id"]},
    )
    assert audit.status_code == 200
    items = audit.json()["items"]
    assert len(items) == 1
    assert items[0]["actor"] == "engineer@example.test"
    assert items[0]["action"] == "model.create"
    assert items[0]["traceId"] == "tr_test_trace"


def test_observability_summary_metrics_and_dashboard(tmp_path):
    client = next(_client(tmp_path))
    engineer = {"X-Dev-User": "engineer@example.test", "X-Dev-Roles": "engineer"}

    client.post("/api/v1/models", headers=engineer, json={"article": "P4-09-METRICS"})
    client.post(
        "/api/v1/jobs",
        headers=engineer,
        json={"type": "preview", "inputHash": "sha256:p4-09"},
    )

    viewer_denied = client.get("/api/v1/observability/summary", headers={"X-Dev-Roles": "viewer"})
    assert viewer_denied.status_code == 403

    summary = client.get("/api/v1/observability/summary", headers={"X-Dev-Roles": "admin"})
    assert summary.status_code == 200
    body = summary.json()
    assert body["service"] == "LANMASTER Studio"
    assert body["modelsTotal"] == 1
    assert body["auditEventsTotal"] >= 2
    assert {"state": "queued", "count": 1} in body["jobsByState"]

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "lanmaster_studio_models_total 1" in metrics.text
    assert 'lanmaster_studio_jobs{state="queued"} 1' in metrics.text

    dashboard = client.get("/api/v1/observability/dashboard", headers={"X-Dev-Roles": "admin"})
    assert dashboard.status_code == 200
    assert "LANMASTER Studio Observability" in dashboard.text
    assert "queued: 1" in dashboard.text
