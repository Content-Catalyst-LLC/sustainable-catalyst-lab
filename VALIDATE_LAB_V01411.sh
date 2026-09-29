#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; cd "$ROOT"
python3 -m py_compile backend/app/neural_architecture_training_configuration_v01411.py backend/app/machine_learning_experiment_workspace_v01410.py backend/app/main.py
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-neural-architecture-training-configuration-v01411.php >/dev/null
php -l includes/class-sc-lab-machine-learning-experiment-workspace-v01410.php >/dev/null
php tests/test-v01411-release-integrity.php
node tests/test-v01411.js
(
 cd backend
 python3 -m pytest -q \
   tests/test_neural_architecture_training_configuration_v01411.py \
   tests/test_machine_learning_experiment_workspace_v01410.py \
   tests/test_scientific_research_operating_system_v01400.py \
   tests/test_scholarly_study_original_research_package_v01390.py \
   tests/test_research_program_intelligence_v01380.py \
   tests/test_research_change_impact_living_analysis_v01370.py
)
python3 - <<'PY2'
import json,re
m=json.load(open('build/sc-lab-release-manifest.json'))
assert m['releaseVersion']=='0.141.1' and m['featureVersion']=='0.141.1'
assert m['neuralArchitectureTrainingConfigurationVersion']=='0.141.1'
assert m['machineLearningExperimentWorkspaceVersion']=='0.141.0'
assert m['v014001WordPressInstalledRuntimeScope'] is True
files=m.get('wordpressCriticalFiles',{}); assert files and len(files)>100
for p in files: assert not re.match(r'^(backend|data|tests|scripts|sdk|examples|docs)/',p),p
from backend.app.main import app
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}
new={x for x in paths if x.startswith('/v1/neural-architecture-training-configuration/v01411')}
old={x for x in paths if x.startswith('/v1/machine-learning-experiment-workspace/v01410')}
ros={x for x in paths if x.startswith('/v1/scientific-research-operating-system/v01400')}
assert len(new)==33,len(new); assert len(old)==27,len(old); assert len(ros)==25,len(ros)
print(f'PASS: {len(new)} v0.141.1 routes; {len(old)} v0.141.0 routes; {len(ros)} v0.140.0 routes')
print(f'PASS: {len(files)} immutable WordPress runtime files in manifest')
PY2
echo 'PASS - Lab v0.141.1 local validation complete.'
