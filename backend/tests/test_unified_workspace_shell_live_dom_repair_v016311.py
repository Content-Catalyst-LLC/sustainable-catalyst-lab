from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "backend" / "app" / "main.py"
MANIFEST = ROOT / "build" / "sc-lab-release-manifest.json"
PHP = ROOT / "includes" / "class-sc-lab-unified-workspace-shell-v016311.php"
JS = ROOT / "assets" / "js" / "sc-lab-unified-workspace-shell-v016311.js"
CSS = ROOT / "assets" / "css" / "sc-lab-unified-workspace-shell-v016311.css"


def test_backend_health_exposes_live_dom_page_length_repair_release_marker():
    text = MAIN.read_text()
    assert '"unifiedWorkspaceShellLiveDomRepair"' in text
    assert '"version":"0.163.1.1"' in text
    assert '"featureVersion":"0.163.1"' in text
    assert '"pageLengthFailSafe":True' in text


def test_repair_keeps_scientific_backend_semantics_unchanged():
    text = MAIN.read_text()
    start = text.index('"unifiedWorkspaceShellLiveDomRepair"')
    line = text[start:text.index("\n", start)]
    assert '"backendBehaviorChanged":False' in line
    assert '"scientificComputeMethodsChanged":False' in line
    assert '"scientificSemanticsChanged":False' in line


def test_repair_targets_actual_live_dom_and_legacy_gate_ordering():
    php = PHP.read_text()
    js = JS.read_text()
    assert "PHP_INT_MAX" in php
    assert "enqueue_after_legacy_gate" in php
    assert "data-sc-lab-unified-shell-v016311" in php
    assert "[data-v0710-visualizer]" in js
    assert "resolveModule" in js


def test_css_fail_safe_collapses_specialist_stack_before_runtime_binding():
    css = CSS.read_text()
    for selector in (
        "[data-v0710-visualizer]", "[data-v01540-workspace]", "[data-v01550-workspace]",
        "[data-v01560-workspace]", "[data-v01570-workspace]", "[data-v01580-workspace]",
        "[data-v01590-workspace]", "[data-v01600-workspace]", "[data-v01610-workspace]",
        "[data-v01620-workspace]", "[data-v01630-workspace]",
    ):
        assert selector in css
    assert "[data-sc-lab-shell-module].is-active" in css


def test_release_manifest_records_repair_without_advancing_feature_line():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["releaseVersion"] in {"0.163.1.1", "0.163.1.2", "0.163.1.3"}
    assert manifest["featureVersion"] == "0.163.1"
    assert manifest["v016311LiveDomBindingRepair"] is True
    assert manifest["v016311LegacyAssetGateSurvival"] is True
    assert manifest["v016311ServerRenderedShell"] is True
    assert manifest["v016311PageLengthFailSafe"] is True
    assert manifest["v016311BackendPackageIncluded"] is True
