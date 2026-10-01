from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "backend" / "app" / "main.py"
MANIFEST = ROOT / "build" / "sc-lab-release-manifest.json"
PHP = ROOT / "includes" / "class-sc-lab-4d-front-door-visual-polish-v016313.php"
JS = ROOT / "assets" / "js" / "sc-lab-4d-front-door-visual-polish-v016313.js"
CSS = ROOT / "assets" / "css" / "sc-lab-4d-front-door-visual-polish-v016313.css"


def test_health_exposes_visual_polish_release_marker():
    text = MAIN.read_text()
    assert '"frontDoorVisualPolishCompactLayout"' in text
    assert '"version":"0.163.1.3"' in text
    assert '"featureVersion":"0.163.1"' in text


def test_release_is_presentation_only_and_preserves_scientific_semantics():
    text = MAIN.read_text()
    start = text.index('"frontDoorVisualPolishCompactLayout"')
    line = text[start:text.index("\n", start)]
    assert '"backendBehaviorChanged":False' in line
    assert '"scientificComputeMethodsChanged":False' in line
    assert '"scientificSemanticsChanged":False' in line
    assert '"automaticExecution":False' in line


def test_manifest_records_compact_layout_without_advancing_feature_line():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["releaseVersion"] == "0.163.1.3"
    assert manifest["featureVersion"] == "0.163.1"
    assert manifest["v016313FourDHeroRetained"] is True
    assert manifest["v016313ResponseSurfacePrimary"] is True
    assert manifest["v016313AdvancedPanelsProgressive"] is True
    assert manifest["v016313ScientificSignalsRetained"] is True


def test_progressive_controls_are_additive_not_destructive():
    js = JS.read_text()
    assert ".sc-lab-v015210-analysis" in js
    assert ".sc-lab-v015211-linked" in js
    assert ".sc-lab-v015212-persistence" in js
    assert ".sc-lab-v01530-workspace" in js
    assert ".sc-lab-v015209-explorer" in js
    assert "sessionStorage" in js
    assert "remove()" not in js


def test_polish_assets_keep_four_d_and_signals_visible():
    css = CSS.read_text()
    php = PHP.read_text()
    assert "[data-v0710-visualizer]" in css
    assert "[data-overview-signals]" in css
    assert "advancedPanelsProgressive" in php
    assert "preserveScientificSignals" in php
    assert "scientificComputeMethodsChanged' => false" in php
