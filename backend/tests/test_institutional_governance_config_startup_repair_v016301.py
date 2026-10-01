from __future__ import annotations
import ast
from pathlib import Path
import tempfile

from app.config import Settings
from app.institutional_research_governance_review_federation_v01630 import InstitutionalResearchGovernanceReviewFederationManager

ROOT = Path(__file__).resolve().parents[2]
CONFIG = (ROOT / "backend/app/config.py").read_text()
MAIN = (ROOT / "backend/app/main.py").read_text()

NEW_FIELDS = [
    "institutional_review_federation_db_path",
    "institutional_review_federation_persistent_disk_mounted",
    "institutional_review_federation_max_institutions",
    "institutional_review_federation_max_bodies",
    "institutional_review_federation_max_links",
    "institutional_review_federation_max_cases",
    "institutional_review_federation_max_assignments",
    "institutional_review_federation_max_decisions",
    "institutional_review_federation_max_attestations",
    "institutional_review_federation_max_snapshots",
    "institutional_review_federation_history_limit",
]

def _settings_annotations() -> set[str]:
    tree = ast.parse(CONFIG)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            return {n.target.id for n in node.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)}
    raise AssertionError("Settings class not found")

def test_new_federation_namespace_is_complete_and_distinct():
    names = _settings_annotations()
    for field in NEW_FIELDS:
        assert field in names, field
    assert "SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_DB_PATH" in CONFIG
    assert "SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH" in CONFIG
    assert "institutional_governance_db_path" in names
    assert "institutional_governance_max_principals" in names

def test_v01630_manager_binding_resolves_every_settings_attribute():
    start = MAIN.index("institutional_governance_v01630 = InstitutionalResearchGovernanceReviewFederationManager(")
    line = MAIN[start: MAIN.index("\n", start)]
    assert "settings.institutional_review_federation_db_path" in line
    assert "settings.institutional_governance_max_bodies" not in line
    settings = Settings()
    import re
    refs = re.findall(r"settings\.([A-Za-z0-9_]+)", line)
    assert refs
    for name in refs:
        assert hasattr(settings, name), name

def test_federation_manager_starts_with_repaired_configuration_contract():
    s = Settings()
    with tempfile.TemporaryDirectory() as td:
        m = InstitutionalResearchGovernanceReviewFederationManager(
            str(Path(td) / "federation.sqlite3"), None, None,
            s.institutional_review_federation_persistent_disk_mounted,
            10, 10, 10, 10, 10, 10, 10, 10, 100,
        )
        h = m.health()
        assert h["ok"] is True
        assert h["version"] == "0.163.0"
        assert h["automaticCaseApproval"] is False

def test_patch_capability_is_advertised_in_compute_health_source():
    assert '"institutionalGovernanceConfigStartupRepair"' in MAIN
    assert '"version":"0.163.0.1"' in MAIN
    assert '"legacyInstitutionalGovernanceNamespacePreserved":True' in MAIN
