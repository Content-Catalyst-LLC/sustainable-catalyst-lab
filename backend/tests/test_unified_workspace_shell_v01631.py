from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "backend" / "app" / "main.py"
MANIFEST = ROOT / "build" / "sc-lab-release-manifest.json"


def _main_text():
    return MAIN.read_text()


def test_backend_health_exposes_unified_workspace_shell_release_marker():
    text = _main_text()
    assert '"unifiedWorkspaceShell"' in text
    assert '"version":"0.163.1"' in text
    assert '"progressiveModuleNavigation":True' in text
    assert '"singleVisibleWorkspace":True' in text


def test_shell_release_does_not_claim_scientific_backend_behavior_change():
    text = _main_text()
    start = text.index('"unifiedWorkspaceShell"')
    line = text[start:text.index("\n", start)]
    assert '"scientificComputeMethodsChanged":False' in line
    assert '"scientificSemanticsChanged":False' in line
    assert '"automaticExecution":False' in line


def test_v01630_governance_and_v016301_startup_repair_are_retained():
    text = _main_text()
    assert '"institutionalResearchGovernanceReviewFederation"' in text
    assert '"institutionalGovernanceConfigStartupRepair"' in text
    assert 'settings.institutional_review_federation_db_path' in text


def test_release_manifest_records_frontend_consolidation_and_backend_packaging():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["releaseVersion"] in {"0.163.1", "0.163.1.1", "0.163.1.2", "0.163.1.3"}
    assert manifest["featureVersion"] == "0.163.1"
    assert manifest["v01631UnifiedWorkspaceShell"] is True
    assert manifest["v01631ProgressiveModuleNavigation"] is True
    assert manifest["v01631SingleVisibleWorkspace"] is True
    assert manifest["v01631BackendPackageIncluded"] is True
    assert manifest["v01631ScientificComputeMethodsChanged"] is False
