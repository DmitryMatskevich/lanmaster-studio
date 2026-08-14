from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import quantiles
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class ShadowBuildRun:
    pilot_id: str
    article: str
    legacy_hash: str
    pmd_hash: str
    started_at: datetime
    duration_seconds: float
    parity_score: float
    status: str
    publishable: bool
    notes: List[str]


@dataclass(frozen=True)
class ShadowExitCriteria:
    run_count: int
    days_observed: int
    success_rate: float
    p95_seconds: Optional[float]
    exit_criteria_met: bool
    blockers: List[str]


def record_shadow_build(
    pilot_id: str,
    article: str,
    legacy_hash: str,
    pmd_hash: str,
    started_at: Optional[datetime] = None,
    duration_seconds: float = 0.0,
    parity_score: float = 1.0,
) -> ShadowBuildRun:
    """Create an immutable shadow-build metric record without enabling release."""
    observed_at = started_at or datetime.now(timezone.utc)
    normalized_score = max(0.0, min(1.0, parity_score))
    status = "succeeded" if normalized_score >= 0.995 else "failed"
    notes: List[str] = []
    if status == "failed":
        notes.append("PMD output differs from accepted legacy baseline beyond shadow tolerance.")
    return ShadowBuildRun(
        pilot_id=pilot_id,
        article=article,
        legacy_hash=legacy_hash,
        pmd_hash=pmd_hash,
        started_at=observed_at,
        duration_seconds=max(0.0, duration_seconds),
        parity_score=normalized_score,
        status=status,
        publishable=False,
        notes=notes,
    )


def evaluate_shadow_exit(
    runs: Iterable[ShadowBuildRun],
    minimum_days: int = 28,
    required_success_rate: float = 0.98,
    max_p95_seconds: float = 5.0,
) -> ShadowExitCriteria:
    materialized = sorted(runs, key=lambda run: run.started_at)
    blockers: List[str] = []
    if not materialized:
        return ShadowExitCriteria(0, 0, 0.0, None, False, ["No shadow build runs recorded."])

    first = materialized[0].started_at
    last = materialized[-1].started_at
    days_observed = max(0, (last.date() - first.date()).days + 1)
    successes = [run for run in materialized if run.status == "succeeded"]
    success_rate = len(successes) / len(materialized)
    durations = [run.duration_seconds for run in materialized]
    if len(durations) == 1:
        p95_seconds = durations[0]
    else:
        p95_seconds = quantiles(durations, n=20, method="inclusive")[18]

    if days_observed < minimum_days:
        blockers.append(f"Shadow observation window is {days_observed} days; required {minimum_days}.")
    if success_rate < required_success_rate:
        blockers.append(
            f"Shadow success rate is {success_rate:.3f}; required {required_success_rate:.3f}."
        )
    if p95_seconds > max_p95_seconds:
        blockers.append(f"Shadow p95 is {p95_seconds:.3f}s; limit is {max_p95_seconds:.3f}s.")

    return ShadowExitCriteria(
        run_count=len(materialized),
        days_observed=days_observed,
        success_rate=success_rate,
        p95_seconds=p95_seconds,
        exit_criteria_met=not blockers,
        blockers=blockers,
    )

