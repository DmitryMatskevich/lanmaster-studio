from __future__ import annotations

from studio_api.pilot.performance import CriticalPathSample, profile_critical_path


def test_profile_critical_path_passes_when_slo_and_stage_limits_met():
    samples = [
        CriticalPathSample("ingest", 0.4),
        CriticalPathSample("retrieve", 0.3),
        CriticalPathSample("preview", 1.2),
        CriticalPathSample("preview", 1.4),
    ]

    result = profile_critical_path(
        samples,
        max_p50_seconds=2.0,
        max_p95_seconds=3.0,
        stage_limits_seconds={"preview": 2.0},
    )

    assert result.slo_met is True
    assert result.sample_count == 4
    assert result.blockers == []
    assert result.by_stage_p95_seconds["preview"] <= 1.4


def test_profile_critical_path_blocks_missing_and_slow_stages():
    samples = [
        CriticalPathSample("ingest", 0.4),
        CriticalPathSample("preview", 6.0),
        CriticalPathSample("preview", 7.0),
    ]

    result = profile_critical_path(
        samples,
        max_p50_seconds=2.0,
        max_p95_seconds=5.0,
        stage_limits_seconds={"preview": 5.0, "release": 10.0},
    )

    assert result.slo_met is False
    assert any("p95" in blocker for blocker in result.blockers)
    assert "Stage 'release' has no samples." in result.blockers

