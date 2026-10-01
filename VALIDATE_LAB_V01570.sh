#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.157.0 — CROSS-STUDY REPLICATION & META-EXPERIMENT WORKSPACE ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-cross-study-replication-meta-experiment-v01570.php >/dev/null
node --check assets/js/sc-lab-cross-study-replication-meta-experiment-v01570.js
python3 -m py_compile backend/app/cross_study_replication_meta_experiment_v01570.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"; VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01570-py${PYVER}}"; [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"; "$VENV/bin/python" -m pip install -q pytest; PYTHON_BIN="$VENV/bin/python"
fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_cross_study_replication_meta_experiment_v01570.py
python3 - <<'PY'
from pathlib import Path
import json,re
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.157.0' and m['featureVersion']=='0.157.0'
true_keys=['v01570CrossStudyReplicationMetaExperimentWorkspace','v01570ImmutableStudyRevisions','v01570ImmutableEffectRecords','v01570WorkspaceFreeze','v01570DirectReplicationRelations','v01570ConceptualReplicationRelations','v01570MethodologicalReplicationRelations','v01570FixedEffectSynthesis','v01570RandomEffectsSynthesis','v01570HeterogeneityQ','v01570HeterogeneityI2','v01570HeterogeneityTau2','v01570PredictionIntervals','v01570LeaveOneOutSensitivity','v01570ExplicitHumanReplicationAssessment','v01570ExplicitReplicationCampaignHandoff','v01570ManifestDigestVerification','v01570HumanScientificReviewRequired','v01570V01560DistributedCoordinationRetained','v01570V01550CampaignLayerRetained','v01570V01540ProtocolNotebookRetained','v01570V01530FourDWorkspaceRetained']
for k in true_keys: assert m.get(k) is True,k
false_keys=['v01570AutomaticReplicationJudgment','v01570AutomaticCausalInference','v01570PublicationBiasInference','v01570StudyIndependenceInferred','v01570ScientificValidityAutomaticallyEstablished','v01570AutomaticCampaignCreation','v01570AutomaticExecution','v01570ArbitraryCodeExecution']
for k in false_keys: assert m.get(k) is False,k
main=(root/'backend/app/main.py').read_text(); assert len(re.findall(r'@app\.(?:get|post)\("/v1/cross-study-replication-meta-experiment/v01570/',main))==20
assert 'crossStudyReplicationMetaExperiment' in main
module=(root/'backend/app/cross_study_replication_meta_experiment_v01570.py').read_text()
for token in ['fixedEffect','randomEffects','I2Percent','tau2','leaveOneOut','automaticReplicationJudgment','publicationBiasInference','manifestDigest']: assert token in module,token
js=(root/'assets/js/sc-lab-cross-study-replication-meta-experiment-v01570.js').read_text(); assert 'eval(' not in js and 'new Function(' not in js
plugin=(root/'sustainable-catalyst-lab.php').read_text(); assert 'Version: 0.157.0' in plugin and 'SC_Lab_Cross_Study_Replication_Meta_Experiment_V01570::init();' in plugin
print('PASS - v0.157.0 release contract')
PY
echo 'PASS - Lab v0.157.0 local validation complete.'
