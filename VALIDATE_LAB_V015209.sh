#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$ROOT"
echo '=== VALIDATE LAB v0.152.0.9 — INTERACTIVE RESPONSE SURFACE & PARAMETER EXPLORER ==='

python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"

php -l sustainable-catalyst-lab.php >/dev/null
php -l templates/lab-app.php >/dev/null
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php -l includes/class-sc-lab-production-safe-boot-v015205.php >/dev/null
php -l includes/class-sc-lab-production-safe-boot-v015206.php >/dev/null
php -l includes/class-sc-lab-interactive-4d-front-door-v015207.php >/dev/null
php -l includes/class-sc-lab-response-surface-parameter-explorer-v015209.php >/dev/null
php -l includes/class-sc-lab-research-program-intelligence-v01380.php >/dev/null

node --check assets/js/sc-lab-safe-bootstrap-v015209.js
node --check assets/js/sc-lab-response-surface-parameter-explorer-v015209.js

# Core scientific/runtime regression line. Use a supported Python when available.
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then
  PYTHON_BIN="$SC_LAB_TEST_PYTHON"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
else
  PYTHON_BIN="$(command -v python3)"
fi
if ! "$PYTHON_BIN" -c 'import fastapi,pydantic,numpy,scipy,pandas,sympy,pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v015209-py${PYVER}}"
  if [ ! -x "$VENV/bin/python" ]; then mkdir -p "$(dirname "$VENV")"; "$PYTHON_BIN" -m venv "$VENV"; fi
  if ! "$VENV/bin/python" -c 'import fastapi,pydantic,numpy,scipy,pandas,sympy,pytest' >/dev/null 2>&1; then
    "$VENV/bin/python" -m pip install --upgrade pip
    "$VENV/bin/python" -m pip install -r backend/requirements.txt pytest
  fi
  PYTHON_BIN="$VENV/bin/python"
fi
echo "Validation Python: $($PYTHON_BIN --version 2>&1)"
"$PYTHON_BIN" -m py_compile backend/app/cross_workspace_research_dependency_graph_v01520.py backend/app/main.py backend/app/methods/numerical.py
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_cross_workspace_research_dependency_graph_v01520.py \
 backend/tests/test_scientific_workflow_experiment_orchestration_v01510.py \
 backend/tests/test_integrated_computational_research_laboratory_v01500.py \
 backend/tests/test_scientific_model_validation_benchmark_laboratory_v01490.py \
 backend/tests/test_multimodal_scientific_experiment_workspace_v01480.py \
 backend/tests/test_graph_machine_learning_experiment_workspace_v01470.py \
 backend/tests/test_graph_network_science_research_workspace_v01460.py \
 backend/tests/test_simulation_computational_experiment_workspace_v01450.py \
 backend/tests/test_statistical_econometric_research_workspace_v01440.py \
 backend/tests/test_computational_linguistics_research_workspace_v01430.py \
 backend/tests/test_integrated_neural_research_workspace_v01420.py \
 backend/tests/test_reproducible_neural_research_package_v01418.py \
 backend/tests/test_embedding_explorer_v01417.py \
 backend/tests/test_neural_explainability_workspace_v01416.py \
 backend/tests/test_ablation_study_framework_v01415.py \
 backend/tests/test_hyperparameter_study_search_results_v01414.py \
 backend/tests/test_model_comparison_experiment_matrix_v01413.py \
 backend/tests/test_training_curves_metrics_checkpoint_visualization_v01412.py \
 backend/tests/test_neural_architecture_training_configuration_v01411.py \
 backend/tests/test_machine_learning_experiment_workspace_v01410.py \
 backend/tests/test_scientific_research_operating_system_v01400.py \
 backend/tests/test_numerical_methods_v0270.py

php tests/test-v015201-navigation-recovery.php
php tests/test-v015202-full-panel-navigation.php
php tests/test-v015203-critical-bootstrap.php
php tests/test-v015204-frontend-bundle.php
php tests/test-v015205-production-safe-boot.php
php tests/test-v015206-safe-boot-stabilization.php

# Preserve the v0.152.0.7 behavior test while adapting only the release-header assertion.
COMPAT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/sc-lab-v015209-compat.XXXXXX")"
trap 'rm -rf "$COMPAT_DIR"' EXIT
cp tests/test-v015207-interactive-4d-compute.php "$COMPAT_DIR/test-v015207.php"
python3 - "$COMPAT_DIR/test-v015207.php" "$ROOT" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); root=sys.argv[2]
s=p.read_text().replace("$root=dirname(__DIR__);", "$root='"+root.replace("'","\\'")+"';")
s=s.replace("'release header'=>strpos($main,'Version: 0.152.0.7')!==false,", "'release header patch-compatible'=>strpos($main,'Version: 0.152.0.9')!==false,")
p.write_text(s)
PY
php "$COMPAT_DIR/test-v015207.php"
rm -rf "$COMPAT_DIR"; trap - EXIT

php tests/test-v015209-response-surface-parameter-explorer.php
node tests/test-v015205-production-safe-boot.js
node tests/test-v015206-safe-boot-stabilization.js
node tests/test-v015207-interactive-4d-compute.js
node tests/test-v015209-response-surface-parameter-explorer.js
node tests/test-v01520.js

python3 - <<'PY'
from pathlib import Path
import hashlib,json,re
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.152.0.9'
assert m['featureVersion']=='0.152.0'
assert m['crossWorkspaceResearchDependencyGraphVersion']=='0.152.0'
assert m['v015208PHPOutputSafetyRepair'] is True
assert m['v015208PHPOutputSafetyGate'] is True
assert m['v015209InteractiveResponseSurfaceParameterExplorer'] is True
assert m['v015209ModelFamilyCount']==4
assert m['v015209ComputeMethod']=='simulation.parameter_sweep'
assert m['v015209ThreeInputDimensions'] is True
assert m['v015209ZOutputMappings']==3
assert m['v015209MaxXSamples']==41
assert m['v015209MaxYLevels']==7
assert m['v015209MaxWSlices']==5
assert m['v015209MaxEvaluations']==1435
assert m['v015209MaxParallelRequests']==3
assert m['v015209RunMetadata'] is True
assert m['v015209BaselineComparison'] is True
assert m['v015209SavedConfigurations'] is True
assert m['v015209SavedConfigurationStorage']=='browser-localStorage'
assert m['v015209PngExport'] is True and m['v015209JsonExport'] is True and m['v015209CsvExport'] is True
assert m['v015209PHPOutputSafetyGateRetained'] is True
assert m['v015209ComputeExecutionExplicitUserAction'] is True
assert m['v015209BackendBehaviorChanged'] is False
assert m['v015209ScientificBehaviorChanged'] is False
assert m['v015209VisualizationIsEvidence'] is False
assert m['v015209ComputedModelOutputIsObservation'] is False
assert m['v015209AutomaticScientificValidity'] is False
fixed=root/'includes/class-sc-lab-research-program-intelligence-v01380.php'
assert fixed.read_bytes().startswith(b'<?php')
assert hashlib.sha256(fixed.read_bytes()).hexdigest()=='f25fb2c2e15a0c4cb2a79c37209dcb62b15ba9a8cc28f0ac25d44a31cd37a256'
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/cross-workspace-research-dependency-graph/v01520/',main))==120
registry=(root/'backend/app/registry.py').read_text()
assert 'simulation.parameter_sweep' in registry
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    f=root/rel
    assert f.is_file(),rel
    actual=hashlib.sha256(f.read_bytes()).hexdigest()
    assert actual==expected,(rel,expected,actual)
print('PASS - v0.152.0.9 release contract, v0.152.0.8 output-safety retention, and WordPress integrity manifest')
PY

echo 'PASS - Lab v0.152.0.9 local validation complete.'
