#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.152.0.2 — FULL-PANEL NAVIGATION & GRAPH STUDIO RECOVERY ==='
python3 -m py_compile backend/app/cross_workspace_research_dependency_graph_v01520.py backend/app/main.py
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
 backend/tests/test_scientific_research_operating_system_v01400.py
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-runtime-repair-v02631.php >/dev/null
php tests/test-v015201-navigation-recovery.php
php tests/test-v015202-full-panel-navigation.php
node --check assets/js/sc-lab-app.js
node --check assets/js/sc-lab-runtime-v02631.js
node --check assets/js/sc-lab-navigation-recovery-v015201.js
node tests/test-v015201-navigation-recovery.js
node tests/test-v01520.js
python3 - <<'PY'
from pathlib import Path
import json,re
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.152.0.2'
assert m['featureVersion']=='0.152.0'
assert m['crossWorkspaceResearchDependencyGraphVersion']=='0.152.0'
assert m['v015202FullPanelDomRetentionRecovery'] is True
assert m['v015202SingleModuleShellRemovesInactivePanels'] is False
assert m['v015202InPageModuleNavigationRestored'] is True
assert m['v015202GraphStudioPanelRetainedInDom'] is True
assert m['v015202BackendBehaviorChanged'] is False
runtime=(root/'includes/class-sc-lab-runtime-repair-v02631.php').read_text()
assert "self::deactivate($panel['html'])" in runtime
assert 'private static function deactivate' in runtime
assert runtime.count("if ($slug === $selected) { $body .= self::activate") == 0
app=(root/'templates/lab-app.php').read_text()
assert 'data-open-module="graph-studio"' in app
assert 'data-lab-module="graph-studio"' in app
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/cross-workspace-research-dependency-graph/v01520/',main))==120
print('PASS - v0.152.0.2 release contract')
PY
echo 'PASS - Lab v0.152.0.2 local validation complete.'
