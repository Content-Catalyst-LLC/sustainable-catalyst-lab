#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
python3 -m py_compile backend/app/training_curves_metrics_checkpoint_visualization_v01412.py backend/app/main.py
python3 -m pytest -q backend/tests/test_training_curves_metrics_checkpoint_visualization_v01412.py backend/tests/test_neural_architecture_training_configuration_v01411.py backend/tests/test_machine_learning_experiment_workspace_v01410.py backend/tests/test_scientific_research_operating_system_v01400.py
php -l sustainable-catalyst-lab.php >/dev/null; php -l includes/class-sc-lab-training-curves-metrics-checkpoint-visualization-v01412.php >/dev/null
php tests/test-v01412-release-integrity.php; node tests/test-v01412.js
python3 - <<'PY2'
import json,re,hashlib
from pathlib import Path
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.141.2'; assert m['v01412RequiredRouteCount']==29
s=(root/'backend/app/main.py').read_text(); new=re.findall(r'@app\.(?:get|post)\("/v1/training-curves-metrics-checkpoint-visualization/v01412/',s); old=re.findall(r'@app\.(?:get|post)\("/v1/neural-architecture-training-configuration/v01411/',s); ml=re.findall(r'@app\.(?:get|post)\("/v1/machine-learning-experiment-workspace/v01410/',s); ros=re.findall(r'@app\.(?:get|post)\("/v1/scientific-research-operating-system/v01400/',s)
assert len(new)==29,len(new); assert len(old)==33,len(old); assert len(ml)==27,len(ml); assert len(ros)==25,len(ros)
print(f'PASS: {len(new)} v0.141.2 routes; {len(old)} v0.141.1; {len(ml)} v0.141.0; {len(ros)} v0.140.0')
PY2
echo 'PASS - Lab v0.141.2 local validation complete.'
