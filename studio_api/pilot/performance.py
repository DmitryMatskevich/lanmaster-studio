from __future__ import annotations

from dataclasses import dataclass
from statistics import median, quantiles
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class CriticalPathSample:
    name: str
    duration_seconds: float


@dataclass(frozen=True)
class CriticalPathProfile:
    sample_count: int
    p50_seconds: Optional[float]
    p95_seconds: Optional[float]
    max_seconds: Optional[float]
    by_stage_p95_seconds: Dict[str, float]
    slo_met: bool
    blockers: List[str]


def _p95(values: List[float]) -> float:
    if len(values) == 1:
        return values[0]
    return quantiles(values, n=20, method="inclusive")[18]


def profile_critical_path(
    samples: Iterable[CriticalPathSample],
    max_p50_seconds: float,
    max_p95_seconds: float,
    stage_limits_seconds: Optional[Dict[str, float]] = None,
) -> CriticalPathProfile:
    materialized = list(samples)
    blockers: List[str] = []
    if not materialized:
        return CriticalPathProfile(0, None, None, None, {}, False, ["No performance samples recorded."])

    durations = [max(0.0, sample.duration_seconds) for sample in materialized]
    p50_seconds = float(median(durations))
    p95_seconds = _p95(durations)
    max_seconds = max(durations)
    by_stage: Dict[str, List[float]] = {}
    for sample in materialized:
        by_stage.setdefault(sample.name, []).append(max(0.0, sample.duration_seconds))
    by_stage_p95 = {stage: _p95(values) for stage, values in sorted(by_stage.items())}

    if p50_seconds > max_p50_seconds:
        blockers.append(f"p50 is {p50_seconds:.3f}s; limit is {max_p50_seconds:.3f}s.")
    if p95_seconds > max_p95_seconds:
        blockers.append(f"p95 is {p95_seconds:.3f}s; limit is {max_p95_seconds:.3f}s.")
    for stage, limit in (stage_limits_seconds or {}).items():
        value = by_stage_p95.get(stage)
        if value is None:
            blockers.append(f"Stage {stage!r} has no samples.")
        elif value > limit:
            blockers.append(f"Stage {stage!r} p95 is {value:.3f}s; limit is {limit:.3f}s.")

    return CriticalPathProfile(
        sample_count=len(materialized),
        p50_seconds=p50_seconds,
        p95_seconds=p95_seconds,
        max_seconds=max_seconds,
        by_stage_p95_seconds=by_stage_p95,
        slo_met=not blockers,
        blockers=blockers,
    )

