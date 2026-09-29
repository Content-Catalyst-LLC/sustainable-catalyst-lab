#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
python3 -m py_compile backend/app/model_comparison_experiment_matrix_v01413.py backend/app/main.py
python3 -m pytest -q backend/tests/test_model_comparison_experiment_matrix_v01413.py backend/tests/test_training_curves_metrics_checkpoint_visualization_v01412.py backend/tests/test_neural_architecture_training_configuration_v01411.py backend/tests/test_machine_learning_experiment_workspace_v01410.py backend/tests/test_scientific_research_operating_system_v01400.py
php -l sustainable-catalyst-lab.php >/dev/null; php -l includes/class-sc-lab-model-comparison-experiment-matrix-v01413.php >/dev/null
php tests/test-v01413-release-integrity.php; node tests/test-v01413.js
python3 - <<'PY2'
import json,re
from pathlib import Path
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.141.3'; assert m['v01413RequiredRouteCount']==30
s=(root/'backend/app/main.py').read_text(); new=re.findall(r'@app\.(?:get|post)\("/v1/model-comparison-experiment-matrix/v01413/',s); v12=re.findall(r'@app\.(?:get|post)\("/v1/training-curves-metrics-checkpoint-visualization/v01412/',s); v11=re.findall(r'@app\.(?:get|post)\("/v1/neural-architecture-training-configuration/v01411/',s); ml=re.findall(r'@app\.(?:get|post)\("/v1/machine-learning-experiment-workspace/v01410/',s); ros=re.findall(r'@app\.(?:get|post)\("/v1/scientific-research-operating-system/v01400/',s)
assert len(new)==30,len(new); assert len(v12)==29,len(v12); assert len(v11)==33,len(v11); assert len(ml)==27,len(ml); assert len(ros)==25,len(ros)
print(f'PASS: {len(new)} v0.141.3 routes; {len(v12)} v0.141.2; {len(v11)} v0.141.1; {len(ml)} v0.141.0; {len(ros)} v0.140.0')
PY2
echo 'PASS - Lab v0.141.3 local validation complete.'
