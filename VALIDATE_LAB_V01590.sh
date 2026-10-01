#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}";cd "$ROOT"
echo '=== VALIDATE LAB v0.159.0 — INTEGRATED SCIENTIFIC REVIEW, VALIDATION & PUBLICATION GATE ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-integrated-scientific-review-validation-publication-gate-v01590.php >/dev/null
php tests/test-v01590-integrated-scientific-review-publication-gate.php
node --check assets/js/sc-lab-integrated-scientific-review-publication-gate-v01590.js
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node tests/test-v01590-integrated-scientific-review-publication-gate.js
python3 -m py_compile backend/app/integrated_scientific_review_validation_publication_gate_v01590.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ];then PYTHON_BIN="$SC_LAB_TEST_PYTHON";elif command -v python3.12 >/dev/null 2>&1;then PYTHON_BIN="$(command -v python3.12)";else PYTHON_BIN="$(command -v python3)";fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1;then PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')";VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01590-py${PYVER}}";[ -x "$VENV/bin/python" ]||"$PYTHON_BIN" -m venv "$VENV";"$VENV/bin/python" -m pip install -q pytest;PYTHON_BIN="$VENV/bin/python";fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_integrated_scientific_review_validation_publication_gate_v01590.py backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py backend/tests/test_cross_study_replication_meta_experiment_v01570.py backend/tests/test_sqlite_connection_lifecycle_v01590.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text());assert m['releaseVersion']=='0.159.0';assert m['featureVersion']=='0.159.0'
for k in ['v01590IntegratedScientificReviewValidationPublicationGate','v01590ReviewDossiers','v01590ValidationChecklists','v01590FindingsAndRevisionActions','v01590ReviewerSignoffAndDissent','v01590CrossStudyEvidenceSnapshots','v01590ReplicationNetworkEvidenceSnapshots','v01590ProceduralReadinessEvaluation','v01590PublicationPackets','v01590ManifestDigestVerification','v01590HumanPublicationAuthorizationRequired','v01590HumanScientificReviewRequired','v01590V01580ReplicationNetworkRetained','v01590V015701RepairRetained']:assert m.get(k) is True,k
for k in ['v01590AutomaticScientificValidity','v01590AutomaticPublication','v01590AutomaticReplicationJudgment','v01590AutomaticCausalInference','v01590PublicationMeritDetermined','v01590ScientificComputeMethodsChanged']:assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text();assert 'Version: 0.159.0' in plugin;assert 'SC_Lab_Integrated_Scientific_Review_Validation_Publication_Gate_V01590::init();' in plugin
main=(root/'backend/app/main.py').read_text();assert 'integratedScientificReviewValidationPublicationGate' in main and '"version":"0.159.0"' in main
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text();assert 'review-gate/v01590' in repair and 'data-v01590-workspace' in repair
print('PASS - v0.159.0 release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
echo 'PASS - Lab v0.159.0 local validation complete.'
