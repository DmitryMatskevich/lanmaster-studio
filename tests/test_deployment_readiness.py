from __future__ import annotations

from studio_api.pilot.deployment import DeploymentReadiness, evaluate_deployment_readiness


def test_deployment_readiness_passes_for_pinned_healthy_production_stack():
    readiness = DeploymentReadiness(
        environment="production",
        image_digest="sha256:image",
        required_env={"DATABASE_URL": True, "STUDIO_STORAGE_DIR": True, "STUDIO_AUTH_MODE": True},
        health_checks={"api": True, "database": True, "worker": True},
        alerts={"api_error_rate": True, "job_queue_age": True, "storage_errors": True},
        autoscaling={"minReplicas": 2, "maxReplicas": 6},
        rollback_runbook="docs/runbooks/rollback.md",
    )

    result = evaluate_deployment_readiness(readiness)

    assert result.ready is True
    assert result.blockers == []


def test_deployment_readiness_blocks_unpinned_single_replica_and_missing_alerts():
    readiness = DeploymentReadiness(
        environment="staging",
        image_digest="latest",
        required_env={"DATABASE_URL": False},
        health_checks={"api": True, "worker": False},
        alerts={"api_error_rate": True, "job_queue_age": False},
        autoscaling={"minReplicas": 1, "maxReplicas": 1},
        rollback_runbook="",
    )

    result = evaluate_deployment_readiness(readiness)

    assert result.ready is False
    assert "Container image digest must be pinned by SHA-256." in result.blockers
    assert "Production autoscaling requires at least 2 minimum replicas." in result.blockers
    assert "Rollback runbook is missing." in result.blockers

