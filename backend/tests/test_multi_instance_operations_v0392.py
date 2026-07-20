from __future__ import annotations

import importlib
import json
import shutil
import sqlite3
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.multi_instance_operations import MultiInstanceOperationsManager, policies


def seed_db(path: Path, value: str = "alpha") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE records(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        db.execute("INSERT INTO records(value) VALUES(?)", (value,))


def manager(tmp_path: Path, instance_id: str = "instance-one", secret: str = "backup-secret") -> MultiInstanceOperationsManager:
    source = tmp_path / "source.sqlite3"
    if not source.exists():
        seed_db(source)
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "result.txt").write_text("verified scientific result\n")
    return MultiInstanceOperationsManager(
        str(tmp_path / "operations.sqlite3"),
        str(tmp_path / "backups"),
        instance_id,
        f"Lab {instance_id}",
        "production",
        "us-central",
        f"https://{instance_id}.example.org",
        secret,
        True,
        {"research-state": str(source)},
        str(artifacts),
        100,
        100_000_000,
        1000,
        24,
        240,
    )


def test_policy_and_stable_instance_manifest(tmp_path):
    store = manager(tmp_path)
    first = store.instance_manifest()
    second = store.instance_manifest()
    assert first["instanceId"] == second["instanceId"] == "instance-one"
    assert len(first["manifestHash"]) == 64 and len(second["manifestHash"]) == 64
    assert policies(True)["capabilities"]["activeFileOverwriteByApi"] is False
    assert store.health()["backupRootWritable"] is True


def test_consistent_backup_verification_and_artifact_manifest(tmp_path):
    store = manager(tmp_path)
    created = store.create_backup({"id": "backup-one", "artifactMode": "manifest"}, "alice")
    backup = created["backup"]
    assert created["verification"]["valid"] is True
    assert backup["manifest"]["sources"][0]["kind"] == "sqlite-snapshot"
    assert backup["manifest"]["artifacts"]["fileCount"] == 1
    assert backup["manifest"]["signature"]
    listed = store.list_backups()["backups"]
    assert listed[0]["id"] == "backup-one" and listed[0]["status"] == "verified"


def test_backup_tampering_is_detected(tmp_path):
    store = manager(tmp_path)
    created = store.create_backup({"id": "backup-tamper", "artifactMode": "none"}, "alice")
    archive_path = store.backup_root / created["backup"]["fileName"]
    replacement = archive_path.with_suffix(".replacement.zip")
    with zipfile.ZipFile(archive_path) as source, zipfile.ZipFile(replacement, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.endswith("research-state.sqlite3"):
                data = data + b"tampered"
            target.writestr(info, data)
    replacement.replace(archive_path)
    verified = store.verify_backup("backup-tamper", "auditor")
    assert verified["ok"] is False
    assert verified["verification"]["reason"] == "source-digest-mismatch"


def test_restore_is_staged_and_does_not_overwrite_source(tmp_path):
    store = manager(tmp_path)
    source = Path(store.source_paths["research-state"])
    before = source.read_bytes()
    store.create_backup({"id": "backup-restore", "artifactMode": "full"}, "alice")
    restored = store.stage_restore("backup-restore", {"id": "restore-one"}, "alice")["restore"]
    assert restored["status"] == "verified"
    assert restored["activeFilesOverwritten"] is False
    assert source.read_bytes() == before
    assert (store.restore_root / restored["targetName"] / "sc-lab-backup-backup-restore" / "manifest.json").is_file()


def test_migration_journal_is_verified_and_idempotent(tmp_path):
    store = manager(tmp_path)
    store.create_backup({"id": "backup-migration", "artifactMode": "none"}, "alice")
    plan = store.create_migration_plan({"id": "migration-one", "sourceVersion": "0.39.1", "targetVersion": "0.40.1"}, "alice")["migration"]
    assert plan["steps"][1]["id"] == "create-backup"
    dry_run = store.execute_migration("migration-one", {"backupId": "backup-migration", "dryRun": True}, "alice")
    assert dry_run["result"]["status"] == "validated"
    applied = store.execute_migration("migration-one", {"backupId": "backup-migration", "dryRun": False, "confirmation": "migration-one"}, "alice")
    assert applied["result"]["status"] == "completed"
    replay = store.execute_migration("migration-one", {"backupId": "backup-migration", "dryRun": False, "confirmation": "migration-one"}, "alice")
    assert replay["idempotentReplay"] is True


def test_signed_cross_instance_transfer_and_import(tmp_path):
    source = manager(tmp_path / "source", "instance-source", "shared-transfer-secret")
    target = manager(tmp_path / "target", "instance-target", "shared-transfer-secret")
    source.register_peer(target.instance_manifest(), "alice")
    source.create_backup({"id": "backup-transfer", "artifactMode": "none"}, "alice")
    transfer = source.create_transfer({"id": "transfer-one", "backupId": "backup-transfer", "targetInstanceId": "instance-target"}, "alice")
    assert transfer["verification"]["valid"] is True
    filename = transfer["transfer"]["fileName"]
    shutil.copyfile(source.transfer_root / filename, target.transfer_root / filename)
    imported = target.import_transfer({"fileName": filename}, "bob")
    assert imported["status"] == "imported"
    repeated = target.import_transfer({"fileName": filename}, "bob")
    assert repeated["status"] == "already-imported"


def test_recovery_drill_measures_rpo_and_rto(tmp_path):
    store = manager(tmp_path)
    store.create_backup({"id": "backup-drill", "artifactMode": "none"}, "alice")
    drill = store.run_recovery_drill({"id": "drill-one", "backupId": "backup-drill", "cleanupRestore": True}, "alice")["recoveryDrill"]
    assert drill["status"] == "passed"
    assert drill["rpoPassed"] is True and drill["rtoPassed"] is True
    assert drill["backupVerified"] is True and drill["restoreVerified"] is True
    assert drill["activeFilesOverwritten"] is False
    assert drill["stagedRestoreCleaned"] is True


def test_contract_instances(tmp_path):
    import jsonschema

    store = manager(tmp_path)
    instance = store.instance_manifest()
    backup = store.create_backup({"id": "backup-contract", "artifactMode": "none"}, "alice")["backup"]["manifest"]
    migration = store.create_migration_plan({"id": "migration-contract", "sourceVersion": "0.39.1", "targetVersion": "0.40.1"}, "alice")["migration"]
    peer = manager(tmp_path / "peer", "instance-peer")
    store.register_peer(peer.instance_manifest(), "alice")
    transfer = store.create_transfer({"id": "transfer-contract", "backupId": "backup-contract", "targetInstanceId": "instance-peer"}, "alice")["transfer"]
    drill = store.run_recovery_drill({"id": "drill-contract", "backupId": "backup-contract"}, "alice")["recoveryDrill"]
    contracts = Path(__file__).resolve().parents[1] / "contracts"
    for name, value in (
        ("instance-manifest-v0392.schema.json", instance),
        ("backup-manifest-v0392.schema.json", backup),
        ("migration-plan-v0392.schema.json", migration),
        ("instance-transfer-envelope-v0392.schema.json", {key: value for key, value in transfer.items() if key not in {"fileName", "bundleHash"}}),
        ("recovery-drill-v0392.schema.json", drill),
    ):
        schema = json.loads((contracts / name).read_text())
        jsonschema.Draft202012Validator(schema).validate(value)


def test_fastapi_routes(tmp_path, monkeypatch):
    source = tmp_path / "route-source.sqlite3"
    seed_db(source, "route")
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "route-key")
    monkeypatch.setenv("SC_LAB_MULTI_INSTANCE_OPERATIONS_DB_PATH", str(tmp_path / "route-ops.sqlite3"))
    monkeypatch.setenv("SC_LAB_BACKUP_ROOT", str(tmp_path / "route-backups"))
    monkeypatch.setenv("SC_LAB_INSTANCE_ID", "route-instance")
    monkeypatch.setenv("SC_LAB_BACKUP_SIGNING_SECRET", "route-backup-secret")
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(source))
    import app.config as config_module
    import app.main as main_module
    importlib.reload(config_module)
    importlib.reload(main_module)
    client = TestClient(main_module.app)
    headers = {"X-SC-Lab-Key": "route-key", "X-SC-Lab-Actor": "route-admin"}
    health = client.get("/v1/multi-instance-operations/health", headers=headers)
    assert health.status_code == 200 and health.json()["serviceVersion"] == "0.39.2"
    created = client.post("/v1/multi-instance-operations/backups", headers=headers, json={"id": "route-backup", "includeSources": ["jobs"], "artifactMode": "none"})
    assert created.status_code == 200 and created.json()["verification"]["valid"] is True
    drill = client.post("/v1/multi-instance-operations/recovery-drills", headers=headers, json={"id": "route-drill", "backupId": "route-backup"})
    assert drill.status_code == 200 and drill.json()["recoveryDrill"]["status"] == "passed"
