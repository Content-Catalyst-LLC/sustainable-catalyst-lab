#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$ROOT"
echo '=== VALIDATE LAB v0.152.0.11 — LINKED SCIENTIFIC VIEWS & CROSS-VIEW SELECTION ==='
python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"
php -l sustainable-catalyst-lab.php >/dev/null
php -l templates/lab-app.php >/dev/null
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php -l includes/class-sc-lab-production-safe-boot-v015205.php >/dev/null
php -l includes/class-sc-lab-production-safe-boot-v015206.php >/dev/null
php -l includes/class-sc-lab-interactive-4d-front-door-v015207.php >/dev/null
php -l includes/class-sc-lab-response-surface-parameter-explorer-v015209.php >/dev/null
php -l includes/class-sc-lab-uncertainty-sensitivity-ensemble-explorer-v015210.php >/dev/null
php -l includes/class-sc-lab-linked-scientific-views-v015211.php >/dev/null
php -l includes/class-sc-lab-research-program-intelligence-v01380.php >/dev/null
node --check assets/js/sc-lab-safe-bootstrap-v015211.js
node --check assets/js/sc-lab-linked-scientific-views-v015211.js
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then
  PYTHON_BIN="$SC_LAB_TEST_PYTHON"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
else
  PYTHON_BIN="$(command -v python3)"
fi
if ! "$PYTHON_BIN" -c 'import fastapi,pydantic,numpy,scipy,pandas,sympy,pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v015211-py${PYVER}}"
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
php tests/test-v015204-frontend-bundle.php
php tests/test-v015205-production-safe-boot.php
php tests/test-v015206-safe-boot-stabilization.php
COMPAT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/sc-lab-v015211-compat.XXXXXX")"
trap 'rm -rf "$COMPAT_DIR"' EXIT
for name in v015203-critical-bootstrap v015207-interactive-4d-compute v015209-response-surface-parameter-explorer v015210-uncertainty-sensitivity-ensemble; do
  cp "tests/test-${name}.php" "$COMPAT_DIR/test-${name}.php"
done
python3 - "$COMPAT_DIR" "$ROOT" <<'PYCOMPAT'
from pathlib import Path
import sys,re
compat=Path(sys.argv[1]); root=sys.argv[2]
for p in compat.glob('*.php'):
    s=p.read_text()
    s=s.replace("$root=dirname(__DIR__);", "$root='"+root.replace("'","\\'")+"';")
    s=s.replace("if(!preg_match('/Version:\\s+0\\.152\\.0\\.[3-9]/',$main)) exit(1);", "if(strpos($main,'Version: 0.152.0.11')===false) exit(1);")
    s=s.replace("'release header'=>strpos($main,'Version: 0.152.0.7')!==false,", "'release header patch-compatible'=>strpos($main,'Version: 0.152.0.11')!==false,")
    s=s.replace("'release header'=>strpos($main,'Version: 0.152.0.9')!==false,", "'release header patch-compatible'=>strpos($main,'Version: 0.152.0.11')!==false,")
    s=s.replace("'release header'=>strpos($main,'Version: 0.152.0.10')!==false,", "'release header patch-compatible'=>strpos($main,'Version: 0.152.0.11')!==false,")
    p.write_text(s)
PYCOMPAT
php "$COMPAT_DIR/test-v015203-critical-bootstrap.php"
php "$COMPAT_DIR/test-v015207-interactive-4d-compute.php"
php "$COMPAT_DIR/test-v015209-response-surface-parameter-explorer.php"
php "$COMPAT_DIR/test-v015210-uncertainty-sensitivity-ensemble.php"
rm -rf "$COMPAT_DIR"; trap - EXIT
php tests/test-v015211-linked-scientific-views.php
node tests/test-v015205-production-safe-boot.js
node tests/test-v015206-safe-boot-stabilization.js
node tests/test-v015207-interactive-4d-compute.js
node tests/test-v015209-response-surface-parameter-explorer.js
node tests/test-v015210-uncertainty-sensitivity-ensemble.js
node tests/test-v015211-linked-scientific-views.js
node tests/test-v01520.js
python3 - <<'PYCONTRACT'
from pathlib import Path
import hashlib,json,re
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.152.0.11'
assert m['featureVersion']=='0.152.0'
assert m['crossWorkspaceResearchDependencyGraphVersion']=='0.152.0'
assert m['v015208PHPOutputSafetyRepair'] is True
assert m['v015209InteractiveResponseSurfaceParameterExplorer'] is True
assert m['v015210FourDUncertaintySensitivityEnsembleExplorer'] is True
assert m['v015211LinkedScientificViews'] is True
assert m['v015211CrossViewSelection'] is True
assert m['v015211SharedSelectionSchema']=='sc-lab-linked-selection/1.0'
assert m['v015211SelectionEvent']=='sc-lab:linked-selection'
assert m['v015211SelectionHistoryLimit']==12
assert m['v015211PinLimit']==8
assert m['v015211GraphStudioHandoff'] is True
assert m['v015211GraphStudioHandoffSchema']=='sc-lab-graph-studio-selection-handoff/1.0'
assert m['v015211ResponseSurfaceRetained'] is True
assert m['v015211UncertaintySensitivityEnsembleRetained'] is True
assert m['v015211PHPOutputSafetyGateRetained'] is True
assert m['v015211ComputeExecutionExplicitUserAction'] is True
assert m['v015211BackendBehaviorChanged'] is False
assert m['v015211ScientificBehaviorChanged'] is False
assert m['v015211AutomaticCrossModelInference'] is False
assert m['v015211AutomaticCausalInference'] is False
assert m['v015211AutomaticScientificValidity'] is False
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/cross-workspace-research-dependency-graph/v01520/',main))==120
registry=(root/'backend/app/registry.py').read_text()
for method in ['simulation.parameter_sweep','uncertainty.monte_carlo_propagation','sensitivity.local_finite_difference']:
    assert method in registry, method
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    f=root/rel; assert f.is_file(),rel
    actual=hashlib.sha256(f.read_bytes()).hexdigest(); assert actual==expected,(rel,expected,actual)
print('PASS - v0.152.0.11 release contract and WordPress integrity manifest')
PYCONTRACT
echo 'PASS - Lab v0.152.0.11 local validation complete.'
