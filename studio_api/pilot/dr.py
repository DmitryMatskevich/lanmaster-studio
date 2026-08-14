from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BackupManifest:
    backup_id: str
    created_at: datetime
    database_hash: str
    object_store_hash: str
    retained_until: datetime
    encrypted: bool


@dataclass(frozen=True)
class RestoreDrill:
    drill_id: str
    backup_id: str
    restored_at: Optional[datetime]
    database_hash: str
    object_store_hash: str
    rpo_minutes: float
    rto_minutes: float
    checks: Dict[str, bool]


@dataclass(frozen=True)
class DisasterRecoveryDecision:
    passed: bool
    blockers: List[str]


def evaluate_restore_drill(
    manifest: BackupManifest,
    drill: RestoreDrill,
    max_rpo_minutes: float,
    max_rto_minutes: float,
) -> DisasterRecoveryDecision:
    blockers: List[str] = []
    if not manifest.encrypted:
        blockers.append("Backup manifest is not encrypted.")
    if drill.backup_id != manifest.backup_id:
        blockers.append("Restore drill uses a different backup id.")
    if drill.restored_at is None:
        blockers.append("Restore timestamp is missing.")
    if drill.database_hash != manifest.database_hash:
        blockers.append("Restored database hash does not match backup manifest.")
    if drill.object_store_hash != manifest.object_store_hash:
        blockers.append("Restored object-store hash does not match backup manifest.")
    if drill.rpo_minutes > max_rpo_minutes:
        blockers.append(f"RPO is {drill.rpo_minutes:.1f} min; limit is {max_rpo_minutes:.1f} min.")
    if drill.rto_minutes > max_rto_minutes:
        blockers.append(f"RTO is {drill.rto_minutes:.1f} min; limit is {max_rto_minutes:.1f} min.")
    failed_checks = sorted(name for name, passed in drill.checks.items() if not passed)
    if failed_checks:
        blockers.append("Restore checks failed: " + ", ".join(failed_checks) + ".")
    return DisasterRecoveryDecision(passed=not blockers, blockers=blockers)

