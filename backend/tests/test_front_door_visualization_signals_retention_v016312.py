from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "backend" / "app" / "main.py"
MANIFEST = ROOT / "build" / "sc-lab-release-manifest.json"
PHP = ROOT / "includes" / "class-sc-lab-unified-workspace-shell-v016312.php"
JS = ROOT / "assets" / "js" / "sc-lab-unified-workspace-shell-v016312.js"
CSS = ROOT / "assets" / "css" / "sc-lab-unified-workspace-shell-v016312.css"


def test_backend_health_exposes_front_door_retention_repair_marker():
    text = MAIN.read_text()
    assert '"frontDoorVisualizationSignalsRetentionRepair"' in text
    assert '"version":"0.163.1.2"' in text
    assert '"featureVersion":"0.163.1"' in text


def test_repair_keeps_scientific_backend_semantics_unchanged():
    text = MAIN.read_text()
    start = text.index('"frontDoorVisualizationSignalsRetentionRepair"')
    line = text[start:text.index("\n", start)]
    assert '"backendBehaviorChanged":False' in line
    assert '"scientificComputeMethodsChanged":False' in line
    assert '"scientificSemanticsChanged":False' in line


def test_four_d_visualizer_is_persistent_front_door_not_specialist_module():
    js = JS.read_text()
    css = CSS.read_text()
    assert "restoreFrontDoorVisualization" in js
    modules_block = js[js.index("const MODULES = ["):js.index("];", js.index("const MODULES = ["))]
    assert "[data-v0710-visualizer]" not in modules_block
    assert "[data-v0710-visualizer]" in css
    specialist_rule = css[css.index("Only specialist workspaces"):css.index("[data-sc-lab-unified-shell-v016312] [data-sc-lab-shell-module].is-active")]
    assert "[data-v0710-visualizer]" not in specialist_rule


def test_scientific_signals_are_retained_open_and_refreshed():
    js = JS.read_text()
    css = CSS.read_text()
    assert "ensureScientificSignalsVisible" in js
    assert "[data-overview-signals]" in js
    assert "[data-overview-refresh]" in js
    assert "refresh.click()" in js
    assert "[data-overview-signals]" in css


def test_shell_is_appended_after_front_door_and_manages_ten_specialists():
    php = PHP.read_text()
    assert "inject_server_shell_after_front_door" in php
    assert "return $content . self::server_shell_markup();" in php
    assert "'specialistWorkspaceCount' => 10" in php
    assert "persistentFrontDoorFourD" in php
    assert "scientificSignalsVisibleOnOverview" in php


def test_release_manifest_records_front_door_retention_repair():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["releaseVersion"] in {"0.163.1.2", "0.163.1.3"}
    assert manifest["featureVersion"] == "0.163.1"
    assert manifest["v016312PersistentFrontDoorFourD"] is True
    assert manifest["v016312ScientificSignalsVisibleOnOverview"] is True
    assert manifest["v016312ShellAfterFrontDoor"] is True
    assert manifest["v016312SpecialistWorkspaceCount"] == 10
    assert manifest["v016312BackendPackageIncluded"] is True
