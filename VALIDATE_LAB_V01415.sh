#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
python3 -m py_compile backend/app/ablation_study_framework_v01415.py backend/app/main.py
python3 -m pytest -q \
  backend/tests/test_ablation_study_framework_v01415.py \
  backend/tests/test_hyperparameter_study_search_results_v01414.py \
  backend/tests/test_model_comparison_experiment_matrix_v01413.py \
  backend/tests/test_training_curves_metrics_checkpoint_visualization_v01412.py \
  backend/tests/test_neural_architecture_training_configuration_v01411.py \
  backend/tests/test_machine_learning_experiment_workspace_v01410.py \
  backend/tests/test_scientific_research_operating_system_v01400.py
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-ablation-study-framework-v01415.php >/dev/null
php tests/test-v01415-release-integrity.php
node tests/test-v01415.js
python3 - <<'PY2'
import json,re
from pathlib import Path
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.141.5'; assert m['featureVersion']=='0.141.5'; assert m['ablationStudyFrameworkVersion']=='0.141.5'; assert m['v01415RequiredRouteCount']==30
assert m['v014001WordPressInstalledRuntimeScope'] is True and m['v014001MutableDataExcluded'] is True
s=(root/'backend/app/main.py').read_text()
counts={
 'v01415':len(re.findall(r'@app\.(?:get|post)\("/v1/ablation-study-framework/v01415/',s)),
 'v01414':len(re.findall(r'@app\.(?:get|post)\("/v1/hyperparameter-study-search-results/v01414/',s)),
 'v01413':len(re.findall(r'@app\.(?:get|post)\("/v1/model-comparison-experiment-matrix/v01413/',s)),
 'v01412':len(re.findall(r'@app\.(?:get|post)\("/v1/training-curves-metrics-checkpoint-visualization/v01412/',s)),
 'v01411':len(re.findall(r'@app\.(?:get|post)\("/v1/neural-architecture-training-configuration/v01411/',s)),
 'v01410':len(re.findall(r'@app\.(?:get|post)\("/v1/machine-learning-experiment-workspace/v01410/',s)),
 'v01400':len(re.findall(r'@app\.(?:get|post)\("/v1/scientific-research-operating-system/v01400/',s)),
}
assert counts=={'v01415':30,'v01414':31,'v01413':30,'v01412':29,'v01411':33,'v01410':27,'v01400':25},counts
print('PASS:',counts)
PY2
echo 'PASS - Lab v0.141.5 local validation complete.'
