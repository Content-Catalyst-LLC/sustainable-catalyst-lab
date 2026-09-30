#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.152.0.7 — INTERACTIVE 4D FRONT DOOR & COMPUTE RECONNECTION ==='
python3 -m py_compile backend/app/cross_workspace_research_dependency_graph_v01520.py backend/app/main.py backend/app/methods/numerical.py
PYTHONPATH=backend pytest -q \
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
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php -l includes/class-sc-lab-production-safe-boot-v015205.php >/dev/null
php -l includes/class-sc-lab-production-safe-boot-v015206.php >/dev/null
php -l includes/class-sc-lab-interactive-4d-front-door-v015207.php >/dev/null
php tests/test-v015201-navigation-recovery.php
php tests/test-v015202-full-panel-navigation.php
php tests/test-v015203-critical-bootstrap.php
php tests/test-v015204-frontend-bundle.php
php tests/test-v015205-production-safe-boot.php
php tests/test-v015206-safe-boot-stabilization.php
php tests/test-v015207-interactive-4d-compute.php
node --check assets/js/sc-lab-safe-bootstrap-v015207.js
node --check assets/js/sc-lab-4d-front-door-v015207.js
node tests/test-v015205-production-safe-boot.js
node tests/test-v015206-safe-boot-stabilization.js
node tests/test-v015207-interactive-4d-compute.js
node tests/test-v01520.js
python3 - <<'PY2'
from pathlib import Path
import json,re
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.152.0.7'
assert m['featureVersion']=='0.152.0'
assert m['crossWorkspaceResearchDependencyGraphVersion']=='0.152.0'
assert m['v015207Interactive4DFrontDoor'] is True
assert m['v015207Bounded4DRuntime'] is True
assert m['v015207SafeShellRetained'] is True
assert m['v015207ComputeHealthReconnected'] is True
assert m['v015207ComputeCapabilitiesReconnected'] is True
assert m['v015207ComputeParameterSweepEnabled'] is True
assert m['v015207ComputeMethod']=='simulation.parameter_sweep'
assert m['v015207ComputeExecutionExplicitUserAction'] is True
assert m['v015207BrowserDemoCount']==6
assert m['v015207FourthDimensionControlCount']==4
assert m['v015207LegacyModuleFleetEager'] is False
assert m['v015207OptionalMegaBundleEager'] is False
assert m['v015207ProductionBudgetMonitorEager'] is False
assert m['v015207LegacyPresentationRuntimeEager'] is False
assert m['v015207BackendBehaviorChanged'] is False
assert m['v015207ScientificValidityAutomaticallyEstablished'] is False
assert m['v015207VisualizationIsEvidence'] is False
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/cross-workspace-research-dependency-graph/v01520/',main))==120
registry=(root/'backend/app/registry.py').read_text()
assert 'simulation.parameter_sweep' in registry
js=(root/'assets/js/sc-lab-4d-front-door-v015207.js').read_text()
assert 'MutationObserver' not in js
assert 'setInterval(' not in js
assert 'simulation.parameter_sweep' in js
assert 'requestAnimationFrame' in js
assert 'computeHealthUrl' in js and 'computeCapabilitiesUrl' in js and 'computeRunUrl' in js
print('PASS - v0.152.0.7 release contract')
PY2
echo 'PASS - Lab v0.152.0.7 local validation complete.'
