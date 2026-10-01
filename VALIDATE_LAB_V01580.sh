#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}";cd "$ROOT"
echo '=== VALIDATE LAB v0.158.0 — SCIENTIFIC REPRODUCTION & INDEPENDENT REPLICATION NETWORK ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-scientific-reproduction-independent-replication-network-v01580.php >/dev/null
php tests/test-v01580-scientific-reproduction-independent-replication-network.php
node --check assets/js/sc-lab-scientific-reproduction-independent-replication-network-v01580.js
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node tests/test-v01580-scientific-reproduction-independent-replication-network.js
python3 -m py_compile backend/app/scientific_reproduction_independent_replication_network_v01580.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ];then PYTHON_BIN="$SC_LAB_TEST_PYTHON";elif command -v python3.12 >/dev/null 2>&1;then PYTHON_BIN="$(command -v python3.12)";else PYTHON_BIN="$(command -v python3)";fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1;then PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')";VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01580-py${PYVER}}";[ -x "$VENV/bin/python" ]||"$PYTHON_BIN" -m venv "$VENV";"$VENV/bin/python" -m pip install -q pytest;PYTHON_BIN="$VENV/bin/python";fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py backend/tests/test_cross_study_replication_meta_experiment_v01570.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text());assert m['releaseVersion']=='0.158.0';assert m['featureVersion']=='0.158.0'
for k in ['v01580ScientificReproductionIndependentReplicationNetwork','v01580ReplicationNodeRegistry','v01580DeclaredIndependence','v01580ImmutableReplicationPlans','v01580PreregistrationReferences','v01580ProtocolLineage','v01580ExplicitWorkspaceHandoffs','v01580ResultReceipts','v01580HumanReviewRecords','v01580NetworkCoverageViews','v01580NetworkManifestDigestVerification','v01580HumanScientificReviewRequired','v01580V015701RepairRetained','v01580V01570CrossStudyWorkspaceRetained']:assert m.get(k) is True,k
for k in ['v01580IndependenceInferred','v01580AutomaticExecution','v01580AutomaticReplicationJudgment','v01580AutomaticCausalInference','v01580AutomaticScientificValidity','v01580CredentialsStored','v01580ScientificComputeMethodsChanged']:assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text();assert 'Version: 0.158.0' in plugin;assert 'SC_Lab_Scientific_Reproduction_Independent_Replication_Network_V01580::init();' in plugin
main=(root/'backend/app/main.py').read_text();assert 'scientificReproductionIndependentReplicationNetwork' in main and '"version":"0.158.0"' in main
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text();assert 'replication-network/v01580' in repair and 'data-v01580-workspace' in repair
print('PASS - v0.158.0 release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
echo 'PASS - Lab v0.158.0 local validation complete.'
