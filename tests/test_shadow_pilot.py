from __future__ import annotations

from datetime import datetime, timedelta, timezone

from studio_api.pilot.shadow import evaluate_shadow_exit, record_shadow_build


def test_shadow_build_records_metrics_without_release_permission():
    run = record_shadow_build(
        pilot_id="pilot-cbb",
        article="TWT-CBB-42U-6x10-P1",
        legacy_hash="sha256:legacy",
        pmd_hash="sha256:pmd",
        started_at=datetime(2026, 8, 14, tzinfo=timezone.utc),
        duration_seconds=1.25,
        parity_score=1.0,
    )

    assert run.status == "succeeded"
    assert run.publishable is False
    assert run.duration_seconds == 1.25
    assert run.parity_score == 1.0


def test_shadow_exit_fails_before_calendar_window_even_when_builds_pass():
    start = datetime(2026, 8, 14, tzinfo=timezone.utc)
    runs = [
        record_shadow_build("pilot-cbb", "TWT-CBB-42U-6x10-P1", "sha256:l", "sha256:p", start),
        record_shadow_build("pilot-cbb", "TWT-CBB-42U-6x10-P1", "sha256:l", "sha256:p", start + timedelta(days=6)),
    ]

    result = evaluate_shadow_exit(runs)

    assert result.exit_criteria_met is False
    assert result.days_observed == 7
    assert "required 28" in result.blockers[0]


def test_shadow_exit_passes_after_required_window_and_slo():
    start = datetime(2026, 8, 14, tzinfo=timezone.utc)
    runs = [
        record_shadow_build(
            "pilot-cbb",
            "TWT-CBB-42U-6x10-P1",
            "sha256:l",
            "sha256:p",
            start + timedelta(days=offset),
            duration_seconds=1.0 + (offset % 3) * 0.2,
        )
        for offset in range(28)
    ]

    result = evaluate_shadow_exit(runs)

    assert result.exit_criteria_met is True
    assert result.run_count == 28
    assert result.days_observed == 28
    assert result.success_rate == 1.0

