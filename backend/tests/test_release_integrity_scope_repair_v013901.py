from app import release_integrity_scope_repair_v013901 as repair


def test_health_identifies_packaging_only_repair():
    data = repair.health()
    assert data["ok"] is True
    assert data["version"] == "0.139.0.1"
    assert data["baseRelease"] == "0.139.0"
    assert data["wordpressManifestScopeRepair"] is True
    assert data["backendScientificRuntimeChanged"] is False


def test_policy_forbids_missing_packaged_critical_files():
    policy = repair.policy()["policy"]
    assert policy["missingPackagedCriticalFilesPermitted"] is False
    assert policy["upgradeGate"] == "runtime/health must report verified before v0.140.0"
