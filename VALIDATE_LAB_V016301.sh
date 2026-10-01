#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"; cd "$ROOT"
echo '=== VALIDATE LAB v0.163.0.1 — INSTITUTIONAL GOVERNANCE CONFIGURATION NAMESPACE & BACKEND STARTUP REPAIR ==='
php -l sustainable-catalyst-lab.php >/dev/null
php tests/test-v016301-institutional-governance-config-startup-repair.php
python3 -m py_compile backend/app/config.py backend/app/main.py backend/app/institutional_research_governance_review_federation_v01630.py backend/tests/test_institutional_governance_config_startup_repair_v016301.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ]; then PYTHON_BIN="$SC_LAB_TEST_PYTHON"; elif command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="$(command -v python3)"; fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
  PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v016301-py${PYVER}}"
  [ -x "$VENV/bin/python" ] || "$PYTHON_BIN" -m venv "$VENV"
  "$VENV/bin/python" -m pip install -q pytest
  PYTHON_BIN="$VENV/bin/python"
fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_batch_experiment_sweep_ensemble_v01550.py \
 backend/tests/test_distributed_hpc_accelerated_coordination_v01560.py \
 backend/tests/test_cross_study_replication_meta_experiment_v01570.py \
 backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py \
 backend/tests/test_integrated_scientific_review_validation_publication_gate_v01590.py \
 backend/tests/test_sqlite_connection_lifecycle_v01590.py \
 backend/tests/test_computational_research_operating_system_ii_v01600.py \
 backend/tests/test_research_program_portfolio_orchestration_v01610.py \
 backend/tests/test_cross_project_dependency_research_resource_planning_v01620.py \
 backend/tests/test_institutional_research_governance_review_federation_v01630.py \
 backend/tests/test_institutional_governance_config_startup_repair_v016301.py
python3 - <<'PY2'
from pathlib import Path
import ast,json,re
root=Path('.')
config=(root/'backend/app/config.py').read_text(); main=(root/'backend/app/main.py').read_text(); manifest=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert manifest['releaseVersion']=='0.163.0.1'; assert manifest['featureVersion']=='0.163.0'
assert 'SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_DB_PATH' in config
assert 'SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH' in config
assert 'institutional_governance_max_principals' in config, 'legacy institutional governance namespace must be preserved'
start=main.index('institutional_governance_v01630 = InstitutionalResearchGovernanceReviewFederationManager('); line=main[start:main.index('\n',start)]
assert 'settings.institutional_review_federation_max_bodies' in line
assert 'settings.institutional_governance_max_bodies' not in line
names=set()
for n in ast.parse(config).body:
    if isinstance(n,ast.ClassDef) and n.name=='Settings': names={x.target.id for x in n.body if isinstance(x,ast.AnnAssign) and isinstance(x.target,ast.Name)}
for ref in re.findall(r'settings\.([A-Za-z0-9_]+)',line): assert ref in names,ref
assert '"institutionalGovernanceConfigStartupRepair"' in main
print('PASS - v0.163.0.1 backend startup binding contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ]; then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"; fi
echo 'PASS - Lab v0.163.0.1 local validation complete.'
