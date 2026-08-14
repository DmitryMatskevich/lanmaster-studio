from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LimitedLaunchReadiness:
    pilot_articles: List[str]
    owners: Dict[str, str]
    trained_roles: Dict[str, bool]
    support_channel: str
    sla_defined: bool
    prerequisite_gates: Dict[str, bool]


@dataclass(frozen=True)
class LimitedLaunchDecision:
    ready: bool
    blockers: List[str]


def evaluate_limited_launch(readiness: LimitedLaunchReadiness) -> LimitedLaunchDecision:
    blockers: List[str] = []
    if not readiness.pilot_articles:
        blockers.append("No pilot articles selected for limited launch.")
    missing_owners = sorted(article for article in readiness.pilot_articles if not readiness.owners.get(article))
    if missing_owners:
        blockers.append("Pilot articles have no owners: " + ", ".join(missing_owners) + ".")
    untrained_roles = sorted(role for role, trained in readiness.trained_roles.items() if not trained)
    if untrained_roles:
        blockers.append("Required roles are not trained: " + ", ".join(untrained_roles) + ".")
    if not readiness.support_channel:
        blockers.append("Support channel is missing.")
    if not readiness.sla_defined:
        blockers.append("SLA is not defined.")
    failed_gates = sorted(gate for gate, passed in readiness.prerequisite_gates.items() if not passed)
    if failed_gates:
        blockers.append("Prerequisite gates are not passed: " + ", ".join(failed_gates) + ".")
    return LimitedLaunchDecision(ready=not blockers, blockers=blockers)

