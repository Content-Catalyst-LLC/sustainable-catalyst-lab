#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.143.0 — COMPUTATIONAL LINGUISTICS RESEARCH WORKSPACE ==='
python3 -m py_compile \
  backend/app/computational_linguistics_research_workspace_v01430.py \
  backend/app/integrated_neural_research_workspace_v01420.py \
  backend/app/reproducible_neural_research_package_v01418.py \
  backend/app/embedding_explorer_v01417.py \
  backend/app/neural_explainability_workspace_v01416.py \
  backend/app/ablation_study_framework_v01415.py \
  backend/app/hyperparameter_study_search_results_v01414.py \
  backend/app/model_comparison_experiment_matrix_v01413.py \
  backend/app/training_curves_metrics_checkpoint_visualization_v01412.py \
  backend/app/neural_architecture_training_configuration_v01411.py \
  backend/app/machine_learning_experiment_workspace_v01410.py \
  backend/app/scientific_research_operating_system_v01400.py \
  backend/app/main.py
PYTHONPATH=backend pytest -q \
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
php -l includes/class-sc-lab-computational-linguistics-research-workspace-v01430.php >/dev/null
php -l includes/class-sc-lab-integrated-neural-research-workspace-v01420.php >/dev/null
php tests/test-v01430-release-integrity.php
node tests/test-v01430.js
python3 - <<'PY2'
import json,re,hashlib
from pathlib import Path
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.143.0'; assert m['featureVersion']=='0.143.0'; assert m['releaseName']=='Computational Linguistics Research Workspace'
assert m['computationalLinguisticsResearchWorkspaceVersion']=='0.143.0'; assert m['integratedNeuralResearchWorkspaceVersion']=='0.142.0'
assert m['v01430RequiredRouteCount']==48 and m['v01430OriginalLanguageFirst'] is True and m['v01430TranslationAsDerivedRepresentation'] is True
assert m['v01430WorkspaceExecutionAuthority'] is True and m['v01430LibrarySourceAuthority'] is True and m['v01430PlatformCoreCanonicalAuthority'] is True
assert m['v01430LabExecutesHeavyLinguisticCompute'] is False and m['v01430AutomaticSemanticEquivalence'] is False and m['v01430AutomaticScientificValidity'] is False
assert m['v014001WordPressInstalledRuntimeScope'] is True and m['v014001MutableDataExcluded'] is True
s=(root/'backend/app/main.py').read_text()
patterns={
 'v01430':r'@app\.(?:get|post)\("/v1/computational-linguistics-research-workspace/v01430/',
 'v01420':r'@app\.(?:get|post)\("/v1/integrated-neural-research-workspace/v01420/',
 'v01418':r'@app\.(?:get|post)\("/v1/reproducible-neural-research-package/v01418/',
 'v01417':r'@app\.(?:get|post)\("/v1/embedding-explorer/v01417/',
 'v01416':r'@app\.(?:get|post)\("/v1/neural-explainability-workspace/v01416/',
 'v01415':r'@app\.(?:get|post)\("/v1/ablation-study-framework/v01415/',
 'v01414':r'@app\.(?:get|post)\("/v1/hyperparameter-study-search-results/v01414/',
 'v01413':r'@app\.(?:get|post)\("/v1/model-comparison-experiment-matrix/v01413/',
 'v01412':r'@app\.(?:get|post)\("/v1/training-curves-metrics-checkpoint-visualization/v01412/',
 'v01411':r'@app\.(?:get|post)\("/v1/neural-architecture-training-configuration/v01411/',
 'v01410':r'@app\.(?:get|post)\("/v1/machine-learning-experiment-workspace/v01410/',
 'v01400':r'@app\.(?:get|post)\("/v1/scientific-research-operating-system/v01400/',
}
counts={k:len(re.findall(v,s)) for k,v in patterns.items()}
expected={'v01430':48,'v01420':39,'v01418':36,'v01417':33,'v01416':31,'v01415':30,'v01414':31,'v01413':30,'v01412':29,'v01411':33,'v01410':27,'v01400':25}
assert counts==expected,(counts,expected)
plugin=(root/'includes/class-sc-lab-plugin.php').read_text(); bootstrap=(root/'sustainable-catalyst-lab.php').read_text()
for x in ['computational-linguistics-research-workspace-v01430','project-workspace-computational-linguistics-v01430','integrated-neural-research-workspace-v01420']: assert x in plugin
assert 'class-sc-lab-computational-linguistics-research-workspace-v01430.php' in bootstrap
assert 'Version: 0.143.0' in bootstrap
for rel,expected_hash in m.get('backendCriticalFiles',{}).items():
    f=root/rel; assert f.exists(),f'missing backend critical file {rel}'; assert hashlib.sha256(f.read_bytes()).hexdigest()==expected_hash,f'backend hash mismatch {rel}'
print('PASS:',counts)
print('PASS: backend critical-file manifest verifies',len(m.get('backendCriticalFiles',{})),'files')
PY2
echo 'PASS - Lab v0.143.0 local validation complete.'
