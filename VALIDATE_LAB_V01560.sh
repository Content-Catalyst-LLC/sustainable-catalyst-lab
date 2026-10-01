#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"
echo '=== VALIDATE LAB v0.156.0 — DISTRIBUTED, HPC & ACCELERATED RESEARCH COORDINATION ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-distributed-hpc-accelerated-coordination-v01560.php >/dev/null
node --check assets/js/sc-lab-distributed-hpc-accelerated-coordination-v01560.js
python3 -m py_compile backend/app/distributed_hpc_accelerated_coordination_v01560.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01560-py${PYVER}}"
  [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"
  "$VENV/bin/python" -m pip install -q pytest
  PYTHON_BIN="$VENV/bin/python"
fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_distributed_hpc_accelerated_coordination_v01560.py
python3 - <<'PY'
from pathlib import Path
import json,re
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.156.0'; assert m['featureVersion']=='0.156.0'
for key in [
 'v01560DistributedHpcAcceleratedResearchCoordination','v01560ComputeTargetRegistry','v01560ResourceIntent',
 'v01560AcceleratorAwarePlacement','v01560HpcJobArrayPlanning','v01560ExecutionWavePlanning',
 'v01560WorkspaceScheduler','v01560SlurmScheduler','v01560PbsScheduler','v01560LsfScheduler','v01560KubernetesScheduler',
 'v01560ManualExternalScheduler','v01560ExecutionReceipts','v01560ExplicitCampaignTrialSync','v01560ExplicitFailedWorkReplan',
 'v01560ManifestDigestVerification','v01560HumanScientificReviewRequired','v01560V01550CampaignLayerRetained',
 'v01560V01540ProtocolNotebookRetained','v01560V01530FourDWorkspaceRetained']:
    assert m.get(key) is True,key
assert m['v01560SchedulerContractCount']==6
for key in ['v01560CredentialsStored','v01560AutomaticDispatch','v01560AutomaticFailover','v01560ArbitraryCodeExecution','v01560ScientificValidityAutomaticallyEstablished']:
    assert m.get(key) is False,key
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/distributed-hpc-accelerated-coordination/v01560/',main))==18
assert 'distributedHpcAcceleratedCoordination' in main
module=(root/'backend/app/distributed_hpc_accelerated_coordination_v01560.py').read_text()
for token in ['slurm','pbs','lsf','kubernetes','acceleratorAwarePlacement','automaticDispatch','automaticFailover','manifestDigest']:
    assert token in module,token
js=(root/'assets/js/sc-lab-distributed-hpc-accelerated-coordination-v01560.js').read_text()
assert 'eval(' not in js and 'new Function(' not in js
plugin=(root/'sustainable-catalyst-lab.php').read_text()
assert 'Version: 0.156.0' in plugin
assert 'SC_Lab_Distributed_HPC_Accelerated_Coordination_V01560::init();' in plugin
print('PASS - v0.156.0 release contract')
PY
echo 'PASS - Lab v0.156.0 local validation complete.'
