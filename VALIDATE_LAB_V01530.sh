#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$ROOT"
echo '=== VALIDATE LAB v0.153.0 — 4D COMPUTATIONAL RESEARCH WORKSPACE ==='
python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"
php -l sustainable-catalyst-lab.php >/dev/null
php -l templates/lab-app.php >/dev/null
php -l includes/class-sc-lab-4d-computational-research-workspace-v01530.php >/dev/null
php -l includes/class-sc-lab-front-door-layout-render-recovery-v015213.php >/dev/null
node --check assets/js/sc-lab-safe-bootstrap-v01530.js
node --check assets/js/sc-lab-linked-scientific-views-v01530.js
node --check assets/js/sc-lab-scene-persistence-provenance-handoff-v01530.js
node --check assets/js/sc-lab-4d-computational-research-workspace-v01530.js
python3 -m py_compile backend/app/computational_research_workspace_v01530.py backend/app/main.py backend/app/config.py

if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import fastapi,pydantic,numpy,scipy,pandas,sympy,pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"; VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01530-py${PYVER}}"; [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"; "$VENV/bin/python" -m pip install -q -r backend/requirements.txt pytest; PYTHON_BIN="$VENV/bin/python"
fi
echo "Validation Python: $($PYTHON_BIN --version 2>&1)"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_4d_computational_research_workspace_v01530.py \
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
php tests/test-v01530-4d-computational-research-workspace.php
node tests/test-v015205-production-safe-boot.js
node tests/test-v015206-safe-boot-stabilization.js
node tests/test-v015207-interactive-4d-compute.js
node tests/test-v015209-response-surface-parameter-explorer.js
node tests/test-v015210-uncertainty-sensitivity-ensemble.js
node tests/test-v015211-linked-scientific-views.js
node tests/test-v015212-scene-persistence-provenance-handoff.js
node tests/test-v015213-front-door-layout-render-recovery.js
node tests/test-v01530-4d-computational-research-workspace.js
node tests/test-v01520.js

python3 - <<'PY'
from pathlib import Path
import hashlib,json,re
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.153.0'
assert m['featureVersion']=='0.153.0'
assert m['v01530FourDComputationalResearchWorkspace'] is True
assert m['v01530ServerBackedProjectAssets'] is True
assert m['v01530ImmutableWorkspaceRevisions'] is True
assert m['v01530ForkLineage'] is True
assert m['v01530DescriptiveAssetComparison'] is True
assert m['v01530ComputeResultReferences'] is True
assert m['v01530VisualRecoveryBaselineRetained'] is True
assert m['v01530SceneStorageKeyPreservedFromV015212'] is True
assert m['v01530RestoringWorkspaceAssetRerunsCompute'] is False
assert m['v01530AutomaticCompute'] is False
assert m['v01530BackendBehaviorChanged'] is True
assert m['v01530ScientificComputeMethodsChanged'] is False
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/cross-workspace-research-dependency-graph/v01520/',main))==120
assert len(re.findall(r'@app\.(?:get|post|patch|delete)\("/v1/4d-computational-research-workspace/v01530/',main))==10
assert 'fourDComputationalResearchWorkspace' in main
module=(root/'backend/app/computational_research_workspace_v01530.py').read_text()
for token in ['immutableRevisions','forkLineage','automaticCompute','archiveInsteadOfDelete']:
    assert token in module, token
# v0.152.0.13 visual recovery remains the structural baseline.
tpl=(root/'templates/lab-app.php').read_text(); a=tpl.index('<aside class="sc-lab-v0710-controls"'); b=tpl.index('</aside>',a); rail=tpl[a:b]
for token in ['sc-lab-v015209-explorer','sc-lab-v015210-analysis','sc-lab-v015211-linked','sc-lab-v015212-persistence','sc-lab-v01530-workspace']:
    assert token not in rail, token
js=(root/'assets/js/sc-lab-linked-scientific-views-v01530.js').read_text(); assert 'getComputedStyle(d.documentElement).color' not in js; assert "grid:'#d9e2ea'" in js; assert "accent:'#ff3842'" in js
authority=(root/'includes/class-sc-lab-4d-computational-research-workspace-v01530.php').read_text()
for forbidden in ["sc-lab-optional-modules-v015204.js","sc-lab-production-stability-v0266.js","presentation-repair-v0481.js"]:
    assert forbidden not in authority, forbidden
for required in ["sc-lab-safe-bootstrap-v01530.js","sc-lab-linked-scientific-views-v01530.js","sc-lab-scene-persistence-provenance-handoff-v01530.js","sc-lab-4d-computational-research-workspace-v01530.js"]:
    assert required in authority, required
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    f=root/rel; assert f.is_file(),rel; assert hashlib.sha256(f.read_bytes()).hexdigest()==expected,rel
for rel,expected in m.get('backendCriticalFiles',{}).items():
    f=root/rel; assert f.is_file(),rel; assert hashlib.sha256(f.read_bytes()).hexdigest()==expected,rel
print('PASS - v0.153.0 release contract and integrity manifests')
PY
echo 'PASS - Lab v0.153.0 local validation complete.'
