from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class DeploymentReadiness:
    environment: str
    image_digest: str
    required_env: Dict[str, bool]
    health_checks: Dict[str, bool]
    alerts: Dict[str, bool]
    autoscaling: Dict[str, int]
    rollback_runbook: str


@dataclass(frozen=True)
class DeploymentDecision:
    ready: bool
    blockers: List[str]


def evaluate_deployment_readiness(readiness: DeploymentReadiness) -> DeploymentDecision:
    blockers: List[str] = []
    if readiness.environment != "production":
        blockers.append(f"Environment is {readiness.environment!r}; required 'production'.")
    if not readiness.image_digest.startswith("sha256:"):
        blockers.append("Container image digest must be pinned by SHA-256.")
    missing_env = sorted(name for name, present in readiness.required_env.items() if not present)
    if missing_env:
        blockers.append("Missing required environment variables: " + ", ".join(missing_env) + ".")
    failed_health = sorted(name for name, passed in readiness.health_checks.items() if not passed)
    if failed_health:
        blockers.append("Health checks failed: " + ", ".join(failed_health) + ".")
    missing_alerts = sorted(name for name, configured in readiness.alerts.items() if not configured)
    if missing_alerts:
        blockers.append("Alerts are not configured: " + ", ".join(missing_alerts) + ".")
    min_replicas = readiness.autoscaling.get("minReplicas", 0)
    max_replicas = readiness.autoscaling.get("maxReplicas", 0)
    if min_replicas < 2:
        blockers.append("Production autoscaling requires at least 2 minimum replicas.")
    if max_replicas < min_replicas:
        blockers.append("Production autoscaling maxReplicas is lower than minReplicas.")
    if not readiness.rollback_runbook:
        blockers.append("Rollback runbook is missing.")
    return DeploymentDecision(ready=not blockers, blockers=blockers)

