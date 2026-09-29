#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
python3 -m py_compile backend/app/embedding_explorer_v01417.py backend/app/main.py
python3 -m pytest -q \
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
php -l includes/class-sc-lab-embedding-explorer-v01417.php >/dev/null
php tests/test-v01417-release-integrity.php
node tests/test-v01417.js
python3 - <<'PY2'
import json,re
from pathlib import Path
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.141.7'; assert m['featureVersion']=='0.141.7'; assert m['embeddingExplorerVersion']=='0.141.7'; assert m['v01417RequiredRouteCount']==33
assert m['v014001WordPressInstalledRuntimeScope'] is True and m['v014001MutableDataExcluded'] is True
s=(root/'backend/app/main.py').read_text()
counts={
 'v01417':len(re.findall(r'@app\.(?:get|post)\("/v1/embedding-explorer/v01417/',s)),
 'v01416':len(re.findall(r'@app\.(?:get|post)\("/v1/neural-explainability-workspace/v01416/',s)),
 'v01415':len(re.findall(r'@app\.(?:get|post)\("/v1/ablation-study-framework/v01415/',s)),
 'v01414':len(re.findall(r'@app\.(?:get|post)\("/v1/hyperparameter-study-search-results/v01414/',s)),
 'v01413':len(re.findall(r'@app\.(?:get|post)\("/v1/model-comparison-experiment-matrix/v01413/',s)),
 'v01412':len(re.findall(r'@app\.(?:get|post)\("/v1/training-curves-metrics-checkpoint-visualization/v01412/',s)),
 'v01411':len(re.findall(r'@app\.(?:get|post)\("/v1/neural-architecture-training-configuration/v01411/',s)),
 'v01410':len(re.findall(r'@app\.(?:get|post)\("/v1/machine-learning-experiment-workspace/v01410/',s)),
 'v01400':len(re.findall(r'@app\.(?:get|post)\("/v1/scientific-research-operating-system/v01400/',s)),
}
expected={'v01417':33,'v01416':31,'v01415':30,'v01414':31,'v01413':30,'v01412':29,'v01411':33,'v01410':27,'v01400':25}
assert counts==expected,(counts,expected)
plugin=(root/'includes/class-sc-lab-plugin.php').read_text()
for x in ['ablation-study-framework-v01415','neural-explainability-workspace-v01416','embedding-explorer-v01417']: assert x in plugin
assert "class-sc-lab-embedding-explorer-v01417.php" in (root/'sustainable-catalyst-lab.php').read_text()
print('PASS:',counts)
PY2
echo 'PASS - Lab v0.141.7 local validation complete.'
