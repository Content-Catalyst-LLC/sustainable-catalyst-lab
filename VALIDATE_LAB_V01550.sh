#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"
echo '=== VALIDATE LAB v0.155.0 — BATCH EXPERIMENT, SWEEP & ENSEMBLE ORCHESTRATION ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-batch-experiment-sweep-ensemble-v01550.php >/dev/null
node --check assets/js/sc-lab-batch-experiment-sweep-ensemble-v01550.js
python3 -m py_compile backend/app/batch_experiment_sweep_ensemble_v01550.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01550-py${PYVER}}"
  [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"
  "$VENV/bin/python" -m pip install -q pytest
  PYTHON_BIN="$VENV/bin/python"
fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_batch_experiment_sweep_ensemble_v01550.py
python3 - <<'PY'
from pathlib import Path
import json,re
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.155.0'
assert m['featureVersion']=='0.155.0'
for key in [
 'v01550BatchExperimentSweepEnsembleOrchestration','v01550ParameterSweep','v01550HyperparameterSearch',
 'v01550MonteCarloCampaigns','v01550FactorialCampaigns','v01550RepeatedTrials','v01550EnsembleCampaigns',
 'v01550DeterministicTrialSpecifications','v01550DeterministicSeedLineage','v01550ExplicitWorkspaceExecutionHandoffs',
 'v01550PartialFailureRecovery','v01550ExplicitRetry','v01550DescriptiveAggregation','v01550ManifestDigestVerification',
 'v01550HumanScientificReviewRequired','v01550V01540ProtocolNotebookRetained','v01550V01530FourDWorkspaceRetained']:
    assert m.get(key) is True,key
assert m['v01550AutomaticDispatch'] is False
assert m['v01550ArbitraryCodeExecution'] is False
assert m['v01550ScientificValidityAutomaticallyEstablished'] is False
main=(root/'backend/app/main.py').read_text()
assert len(re.findall(r'@app\.(?:get|post)\("/v1/batch-experiment-sweep-ensemble/v01550/',main))==13
assert 'batchExperimentSweepEnsemble' in main
module=(root/'backend/app/batch_experiment_sweep_ensemble_v01550.py').read_text()
for token in ['parameter-sweep','hyperparameter-search','monte-carlo','factorial','repeated-trials','ensemble','automaticDispatch','manifestDigest']:
    assert token in module,token
js=(root/'assets/js/sc-lab-batch-experiment-sweep-ensemble-v01550.js').read_text()
assert 'eval(' not in js and 'new Function(' not in js
plugin=(root/'sustainable-catalyst-lab.php').read_text()
assert 'Version: 0.155.0' in plugin
assert 'SC_Lab_Batch_Experiment_Sweep_Ensemble_V01550::init();' in plugin
print('PASS - v0.155.0 release contract')
PY
echo 'PASS - Lab v0.155.0 local validation complete.'
