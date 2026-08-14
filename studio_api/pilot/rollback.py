from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RollbackRehearsal:
    article: str
    from_revision_id: str
    rollback_target: str
    data_loss_detected: bool
    artifact_loss_detected: bool
    audit_event_recorded: bool
    restored_legacy_route: bool
    recovery_minutes: float


@dataclass(frozen=True)
class RollbackDecision:
    passed: bool
    blockers: List[str]


def evaluate_rollback_rehearsal(rehearsal: RollbackRehearsal, max_recovery_minutes: float) -> RollbackDecision:
    blockers: List[str] = []
    if rehearsal.rollback_target != "legacy":
        blockers.append(f"Rollback target is {rehearsal.rollback_target!r}; required 'legacy'.")
    if rehearsal.data_loss_detected:
        blockers.append("Data loss was detected during rollback rehearsal.")
    if rehearsal.artifact_loss_detected:
        blockers.append("Artifact loss was detected during rollback rehearsal.")
    if not rehearsal.audit_event_recorded:
        blockers.append("Rollback audit event was not recorded.")
    if not rehearsal.restored_legacy_route:
        blockers.append("Legacy route was not restored for the article.")
    if rehearsal.recovery_minutes > max_recovery_minutes:
        blockers.append(
            f"Recovery time is {rehearsal.recovery_minutes:.1f} min; limit is {max_recovery_minutes:.1f} min."
        )
    return RollbackDecision(passed=not blockers, blockers=blockers)

