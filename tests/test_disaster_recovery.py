from __future__ import annotations

from datetime import datetime, timedelta, timezone

from studio_api.pilot.dr import BackupManifest, RestoreDrill, evaluate_restore_drill


def _manifest():
    created = datetime(2026, 8, 14, tzinfo=timezone.utc)
    return BackupManifest(
        backup_id="bak_1",
        created_at=created,
        database_hash="sha256:db",
        object_store_hash="sha256:objects",
        retained_until=created + timedelta(days=90),
        encrypted=True,
    )


def test_restore_drill_passes_when_hashes_and_slos_match():
    manifest = _manifest()
    drill = RestoreDrill(
        drill_id="drill_1",
        backup_id=manifest.backup_id,
        restored_at=datetime(2026, 8, 14, 1, tzinfo=timezone.utc),
        database_hash=manifest.database_hash,
        object_store_hash=manifest.object_store_hash,
        rpo_minutes=10,
        rto_minutes=20,
        checks={"api_health": True, "artifact_download": True, "revision_read": True},
    )

    result = evaluate_restore_drill(manifest, drill, max_rpo_minutes=15, max_rto_minutes=30)

    assert result.passed is True
    assert result.blockers == []


def test_restore_drill_blocks_hash_mismatch_and_failed_checks():
    manifest = _manifest()
    drill = RestoreDrill(
        drill_id="drill_1",
        backup_id=manifest.backup_id,
        restored_at=None,
        database_hash="sha256:wrong",
        object_store_hash=manifest.object_store_hash,
        rpo_minutes=16,
        rto_minutes=40,
        checks={"api_health": True, "artifact_download": False},
    )

    result = evaluate_restore_drill(manifest, drill, max_rpo_minutes=15, max_rto_minutes=30)

    assert result.passed is False
    assert "Restored database hash does not match backup manifest." in result.blockers
    assert "Restore checks failed: artifact_download." in result.blockers

