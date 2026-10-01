#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}";cd "$ROOT"
echo '=== VALIDATE LAB v0.160.0 — COMPUTATIONAL RESEARCH OPERATING SYSTEM II ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-computational-research-operating-system-ii-v01600.php >/dev/null
php tests/test-v01600-computational-research-os-ii.php
node --check assets/js/sc-lab-computational-research-os-ii-v01600.js
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node tests/test-v01600-computational-research-os-ii.js
python3 -m py_compile backend/app/computational_research_operating_system_ii_v01600.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ];then PYTHON_BIN="$SC_LAB_TEST_PYTHON";elif command -v python3.12 >/dev/null 2>&1;then PYTHON_BIN="$(command -v python3.12)";else PYTHON_BIN="$(command -v python3)";fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1;then PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')";VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01600-py${PYVER}}";[ -x "$VENV/bin/python" ]||"$PYTHON_BIN" -m venv "$VENV";"$VENV/bin/python" -m pip install -q pytest;PYTHON_BIN="$VENV/bin/python";fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_batch_experiment_sweep_ensemble_v01550.py \
 backend/tests/test_distributed_hpc_accelerated_coordination_v01560.py \
 backend/tests/test_cross_study_replication_meta_experiment_v01570.py \
 backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py \
 backend/tests/test_integrated_scientific_review_validation_publication_gate_v01590.py \
 backend/tests/test_sqlite_connection_lifecycle_v01590.py \
 backend/tests/test_computational_research_operating_system_ii_v01600.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text());assert m['releaseVersion']=='0.160.0';assert m['featureVersion']=='0.160.0'
for k in ['v01600ComputationalResearchOperatingSystemII','v01600UnifiedResearchProjectGraph','v01600LifecycleStateMachine','v01600ResearchCommandCenter','v01600CrossModuleObjectResolution','v01600ResearchPackageComposer','v01600DependencyIntegrityValidation','v01600HumanAuthorizationLayer','v01600OperatingSystemHealthContract','v01600ReferenceFirst','v01600PlatformCoreCanonicalAuthority','v01600WorkspaceExecutionAuthority','v01600HumanAuthorizationRequired','v01600ManifestDigestVerification','v01600ImmutableResearchPackages','v01600ExplicitDownstreamHandoffs','v01600StaleDependencyDetection','v01600V01590ReviewGateRetained','v01600V015701RepairRetained']:assert m.get(k) is True,k
for k in ['v01600AutomaticStageAdvancement','v01600AutomaticExecution','v01600AutomaticScientificValidity','v01600AutomaticCausalInference','v01600AutomaticReplicationJudgment','v01600AutomaticPublication','v01600ScientificComputeMethodsChanged','v01600CredentialsStored','v01600EmbeddedRestrictedData']:assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text();assert 'Version: 0.160.0' in plugin;assert 'SC_Lab_Computational_Research_Operating_System_II_V01600::init();' in plugin
main=(root/'backend/app/main.py').read_text();assert 'computationalResearchOperatingSystemII' in main and 'computational-research-operating-system-ii/v01600' in main
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text();assert 'research-os/v01600' in repair and 'data-v01600-workspace' in repair
backend=(root/'backend/app/computational_research_operating_system_ii_v01600.py').read_text();assert 'factory=_ClosingConnection' in backend;assert 'automaticStageAdvancement' in backend;assert 'workspaceExecutionAuthority' in backend
print('PASS - v0.160.0 release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
echo 'PASS - Lab v0.160.0 local validation complete.'
