from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .shadow import ShadowExitCriteria


@dataclass(frozen=True)
class PilotApproval:
    pilot_id: str
    article: str
    revision_id: str
    manifest_hash: str
    approver: str
    approved_at: Optional[datetime]
    status: str
    notes: List[str]


@dataclass(frozen=True)
class PilotReleaseDecision:
    release_allowed: bool
    blockers: List[str]


def evaluate_pilot_release(
    approval: Optional[PilotApproval],
    shadow: ShadowExitCriteria,
    required_manifest_hash_prefix: str = "sha256:",
) -> PilotReleaseDecision:
    blockers: List[str] = []
    if not shadow.exit_criteria_met:
        blockers.extend(shadow.blockers or ["Shadow exit criteria are not met."])
    if approval is None:
        blockers.append("Domain approval is missing.")
    else:
        if approval.status != "signed":
            blockers.append(f"Domain approval status is {approval.status!r}; required 'signed'.")
        if approval.approved_at is None:
            blockers.append("Domain approval timestamp is missing.")
        if not approval.manifest_hash.startswith(required_manifest_hash_prefix):
            blockers.append("Release manifest hash is missing or not canonical SHA-256.")
        if not approval.approver:
            blockers.append("Domain approver identity is missing.")
    return PilotReleaseDecision(release_allowed=not blockers, blockers=blockers)

