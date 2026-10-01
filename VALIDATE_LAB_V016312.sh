#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.163.1.2 — FRONT-DOOR VISUALIZATION & SCIENTIFIC SIGNALS RETENTION REPAIR ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-unified-workspace-shell-v016312.php >/dev/null
php tests/test-v016312-front-door-visualization-signals-retention.php
if command -v node >/dev/null 2>&1; then
  node --check assets/js/sc-lab-unified-workspace-shell-v016312.js
  node tests/test-v016312-front-door-visualization-signals-retention.js
fi
python3 -m py_compile backend/app/main.py backend/tests/test_front_door_visualization_signals_retention_v016312.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v016312-py${PYVER}}"
  [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"
  "$VENV/bin/python" -m pip install -q pytest
  PYTHON_BIN="$VENV/bin/python"
fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_batch_experiment_sweep_ensemble_v01550.py \
 backend/tests/test_distributed_hpc_accelerated_coordination_v01560.py \
 backend/tests/test_cross_study_replication_meta_experiment_v01570.py \
 backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py \
 backend/tests/test_integrated_scientific_review_validation_publication_gate_v01590.py \
 backend/tests/test_sqlite_connection_lifecycle_v01590.py \
 backend/tests/test_computational_research_operating_system_ii_v01600.py \
 backend/tests/test_research_program_portfolio_orchestration_v01610.py \
 backend/tests/test_cross_project_dependency_research_resource_planning_v01620.py \
 backend/tests/test_institutional_research_governance_review_federation_v01630.py \
 backend/tests/test_institutional_governance_config_startup_repair_v016301.py \
 backend/tests/test_unified_workspace_shell_v01631.py \
 backend/tests/test_unified_workspace_shell_live_dom_repair_v016311.py \
 backend/tests/test_front_door_visualization_signals_retention_v016312.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.')
main=(root/'backend/app/main.py').read_text(); manifest=json.loads((root/'build/sc-lab-release-manifest.json').read_text()); js=(root/'assets/js/sc-lab-unified-workspace-shell-v016312.js').read_text(); php=(root/'includes/class-sc-lab-unified-workspace-shell-v016312.php').read_text(); css=(root/'assets/css/sc-lab-unified-workspace-shell-v016312.css').read_text()
assert manifest['releaseVersion']=='0.163.1.2'; assert manifest['featureVersion']=='0.163.1'
assert manifest['v016312PersistentFrontDoorFourD'] is True
assert manifest['v016312ScientificSignalsVisibleOnOverview'] is True
assert '"frontDoorVisualizationSignalsRetentionRepair": {"version":"0.163.1.2"' in main
assert 'restoreFrontDoorVisualization' in js and 'ensureScientificSignalsVisible' in js
mods=js[js.index('const MODULES = ['):js.index('];',js.index('const MODULES = ['))]
assert '[data-v0710-visualizer]' not in mods
assert 'return $content . self::server_shell_markup();' in php
assert 'sc-lab-v016312-frontdoor [data-v0710-visualizer]' in css
assert 'sc-lab-v016312-frontdoor [data-overview-signals]' in css
print('PASS - v0.163.1.2 front-door visualization/signals retention release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ]; then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"; fi
echo 'PASS - Lab v0.163.1.2 local validation complete.'
