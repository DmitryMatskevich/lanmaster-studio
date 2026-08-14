from __future__ import annotations

from studio_api.pilot.rollback import RollbackRehearsal, evaluate_rollback_rehearsal


def test_rollback_rehearsal_passes_for_legacy_restore_without_loss():
    rehearsal = RollbackRehearsal(
        article="TWT-CBB-42U-6x10-P1",
        from_revision_id="rev_pmd",
        rollback_target="legacy",
        data_loss_detected=False,
        artifact_loss_detected=False,
        audit_event_recorded=True,
        restored_legacy_route=True,
        recovery_minutes=8,
    )

    result = evaluate_rollback_rehearsal(rehearsal, max_recovery_minutes=15)

    assert result.passed is True
    assert result.blockers == []


def test_rollback_rehearsal_blocks_data_loss_and_missing_legacy_route():
    rehearsal = RollbackRehearsal(
        article="TWT-CBB-42U-6x10-P1",
        from_revision_id="rev_pmd",
        rollback_target="pmd",
        data_loss_detected=True,
        artifact_loss_detected=True,
        audit_event_recorded=False,
        restored_legacy_route=False,
        recovery_minutes=20,
    )

    result = evaluate_rollback_rehearsal(rehearsal, max_recovery_minutes=15)

    assert result.passed is False
    assert "Data loss was detected during rollback rehearsal." in result.blockers
    assert "Legacy route was not restored for the article." in result.blockers

