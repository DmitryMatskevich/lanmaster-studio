from __future__ import annotations

from datetime import datetime, timedelta, timezone

from studio_api.pilot.approval import PilotApproval, evaluate_pilot_release
from studio_api.pilot.shadow import evaluate_shadow_exit, record_shadow_build


def _passing_shadow():
    start = datetime(2026, 8, 14, tzinfo=timezone.utc)
    runs = [
        record_shadow_build("pilot-cbb", "TWT-CBB-42U-6x10-P1", "sha256:l", "sha256:p", start + timedelta(days=day))
        for day in range(28)
    ]
    return evaluate_shadow_exit(runs)


def test_pilot_release_requires_domain_approval():
    decision = evaluate_pilot_release(None, _passing_shadow())

    assert decision.release_allowed is False
    assert "Domain approval is missing." in decision.blockers


def test_pilot_release_requires_passing_shadow_window():
    approval = PilotApproval(
        pilot_id="pilot-cbb",
        article="TWT-CBB-42U-6x10-P1",
        revision_id="rev_1",
        manifest_hash="sha256:manifest",
        approver="domain@example.test",
        approved_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
        status="signed",
        notes=[],
    )
    short_shadow = evaluate_shadow_exit(
        [record_shadow_build("pilot-cbb", "TWT-CBB-42U-6x10-P1", "sha256:l", "sha256:p")]
    )

    decision = evaluate_pilot_release(approval, short_shadow)

    assert decision.release_allowed is False
    assert any("required 28" in blocker for blocker in decision.blockers)


def test_pilot_release_allows_signed_approval_after_shadow_exit():
    approval = PilotApproval(
        pilot_id="pilot-cbb",
        article="TWT-CBB-42U-6x10-P1",
        revision_id="rev_1",
        manifest_hash="sha256:manifest",
        approver="domain@example.test",
        approved_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
        status="signed",
        notes=[],
    )

    decision = evaluate_pilot_release(approval, _passing_shadow())

    assert decision.release_allowed is True
    assert decision.blockers == []

