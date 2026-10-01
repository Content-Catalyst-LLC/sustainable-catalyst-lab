#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.157.0.1 — CANONICAL RELEASE IDENTITY, FRONT-DOOR SYNCHRONIZATION & WORKSPACE AUTHORIZATION REPAIR ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-canonical-release-front-door-auth-repair-v015701.php >/dev/null
php tests/test-v015701-canonical-release-front-door-auth-repair.php
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node --check assets/js/sc-lab-cross-study-replication-meta-experiment-v01570.js
node tests/test-v015701-canonical-release-front-door-auth-repair.js
python3 -m py_compile backend/app/cross_study_replication_meta_experiment_v01570.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"; VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v015701-py${PYVER}}"; [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"; "$VENV/bin/python" -m pip install -q pytest; PYTHON_BIN="$VENV/bin/python"
fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_cross_study_replication_meta_experiment_v01570.py
python3 - <<'PY'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.157.0.1'; assert m['featureVersion']=='0.157.0'
true_keys=['v015701CanonicalReleaseIdentityRepair','v015701FrontDoorSynchronizationRepair','v015701WorkspaceAuthorizationPresentationRepair','v015701CachedGlobalVersionCorrection','v015701CanonicalRuntimeLabelCorrection','v015701LabAppCardVersionCorrection','v015701SubsystemIntroductionVersionsPreserved','v015701ServerBackedWorkspaceRequiresLogin','v015701LoggedOutRawAuthorizationErrorsSuppressed','v015701RestNonceCredentialPathRetained','v015701V01570CrossStudyWorkspaceRetained','v015701V01560DistributedCoordinationRetained','v015701V01550CampaignLayerRetained','v015701V01540ProtocolNotebookRetained','v015701V01530FourDWorkspaceRetained']
for k in true_keys: assert m.get(k) is True,k
for k in ['v015701PublicProjectDataExposure','v015701PermissionCallbacksRelaxed','v015701BackendBehaviorChanged','v015701ScientificBehaviorChanged']: assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text(); assert 'Version: 0.157.0.1' in plugin; assert 'SC_Lab_Canonical_Release_Front_Door_Auth_Repair_V015701::init();' in plugin
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text(); assert 'MutationObserver' in repair; assert 'syntheticUnauthorized' in repair; assert "public project" not in repair.lower()
v157=(root/'assets/js/sc-lab-cross-study-replication-meta-experiment-v01570.js').read_text(); assert "credentials=opt.credentials||'same-origin'" in v157
if (root/'templates/lab-app.php').is_file(): assert 'data-canonical-release=' in (root/'templates/lab-app.php').read_text()
main=(root/'backend/app/main.py').read_text(); assert 'crossStudyReplicationMetaExperiment' in main and '"version":"0.157.0"' in main
print('PASS - v0.157.0.1 release repair contract')
PY
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ]; then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"; fi
echo 'PASS - Lab v0.157.0.1 local validation complete.'
