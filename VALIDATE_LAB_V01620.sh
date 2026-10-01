#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}";cd "$ROOT"
echo '=== VALIDATE LAB v0.162.0 — CROSS-PROJECT DEPENDENCY & RESEARCH RESOURCE PLANNING ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-cross-project-dependency-resource-planning-v01620.php >/dev/null
php tests/test-v01620-cross-project-resource-planning.php
node --check assets/js/sc-lab-cross-project-resource-planning-v01620.js
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node tests/test-v01620-cross-project-resource-planning.js
python3 -m py_compile backend/app/cross_project_dependency_research_resource_planning_v01620.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ];then PYTHON_BIN="$SC_LAB_TEST_PYTHON";elif command -v python3.12 >/dev/null 2>&1;then PYTHON_BIN="$(command -v python3.12)";else PYTHON_BIN="$(command -v python3)";fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1;then PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')";VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01620-py${PYVER}}";[ -x "$VENV/bin/python" ]||"$PYTHON_BIN" -m venv "$VENV";"$VENV/bin/python" -m pip install -q pytest;PYTHON_BIN="$VENV/bin/python";fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_batch_experiment_sweep_ensemble_v01550.py \
 backend/tests/test_distributed_hpc_accelerated_coordination_v01560.py \
 backend/tests/test_cross_study_replication_meta_experiment_v01570.py \
 backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py \
 backend/tests/test_integrated_scientific_review_validation_publication_gate_v01590.py \
 backend/tests/test_sqlite_connection_lifecycle_v01590.py \
 backend/tests/test_computational_research_operating_system_ii_v01600.py \
 backend/tests/test_research_program_portfolio_orchestration_v01610.py \
 backend/tests/test_cross_project_dependency_research_resource_planning_v01620.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text());assert m['releaseVersion']=='0.162.0';assert m['featureVersion']=='0.162.0'
for k in ['v01620CrossProjectDependencyResourcePlanning','v01620ExplicitDependencyGraph','v01620SharedResourceRegistry','v01620ProjectResourceRequirements','v01620DescriptiveCapacityConflictDetection','v01620DependencyBlockerAnalysis','v01620HumanApprovedPlanningScenarios','v01620ProgramPlanningCommandCenter','v01620ImmutableSnapshots','v01620ManifestDigestVerification','v01620V01610ProgramPortfolioRetained','v01620V01600ResearchOSRetained','v01620V01590ReviewGateRetained','v01620V015701RepairRetained','v01620PlatformCoreCanonicalAuthority','v01620WorkspaceExecutionAuthority','v01620ResearchOSProjectLifecycleAuthority','v01620ProgramPortfolioAuthority']:assert m.get(k) is True,k
for k in ['v01620AutomaticDependencyInference','v01620AutomaticScheduling','v01620AutomaticResourceAllocation','v01620AutomaticFundingAllocation','v01620AutomaticProjectRanking','v01620AutomaticScientificValidity','v01620AutomaticExecution','v01620AutomaticPublication','v01620ScientificComputeMethodsChanged','v01620CredentialsStored','v01620EmbeddedRestrictedData']:assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text();assert 'Version: 0.162.0' in plugin;assert 'SC_Lab_Cross_Project_Dependency_Resource_Planning_V01620::init();' in plugin
main=(root/'backend/app/main.py').read_text();assert 'crossProjectDependencyResearchResourcePlanning' in main and 'cross-project-dependency-resource-planning/v01620' in main
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text();assert 'cross-project-resource-planning/v01620' in repair and 'data-v01620-workspace' in repair
backend=(root/'backend/app/cross_project_dependency_research_resource_planning_v01620.py').read_text();assert 'factory=_ClosingConnection' in backend;assert 'automaticResourceAllocation' in backend;assert 'programAuthorityVersion' in backend
print('PASS - v0.162.0 release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
echo 'PASS - Lab v0.162.0 local validation complete.'
