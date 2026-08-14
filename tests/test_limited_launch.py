from __future__ import annotations

from studio_api.pilot.launch import LimitedLaunchReadiness, evaluate_limited_launch


def test_limited_launch_passes_when_all_owners_training_and_gates_exist():
    readiness = LimitedLaunchReadiness(
        pilot_articles=["TWT-CBB-42U-6x10-P1"],
        owners={"TWT-CBB-42U-6x10-P1": "owner@example.test"},
        trained_roles={"engineer": True, "librarian": True, "administrator": True},
        support_channel="studio-support@example.test",
        sla_defined=True,
        prerequisite_gates={"P7-01": True, "P7-02": True, "P7-03": True},
    )

    result = evaluate_limited_launch(readiness)

    assert result.ready is True
    assert result.blockers == []


def test_limited_launch_blocks_missing_owner_training_and_failed_gates():
    readiness = LimitedLaunchReadiness(
        pilot_articles=["TWT-CBB-42U-6x10-P1"],
        owners={},
        trained_roles={"engineer": True, "librarian": False},
        support_channel="",
        sla_defined=False,
        prerequisite_gates={"P7-01": False, "P7-02": False},
    )

    result = evaluate_limited_launch(readiness)

    assert result.ready is False
    assert "Pilot articles have no owners: TWT-CBB-42U-6x10-P1." in result.blockers
    assert "Required roles are not trained: librarian." in result.blockers
    assert "Prerequisite gates are not passed: P7-01, P7-02." in result.blockers

