#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}";cd "$ROOT"
echo '=== VALIDATE LAB v0.161.0 — RESEARCH PROGRAM & PORTFOLIO ORCHESTRATION ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-research-program-portfolio-orchestration-v01610.php >/dev/null
php tests/test-v01610-research-program-portfolio.php
node --check assets/js/sc-lab-research-program-portfolio-v01610.js
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node tests/test-v01610-research-program-portfolio.js
python3 -m py_compile backend/app/research_program_portfolio_orchestration_v01610.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ];then PYTHON_BIN="$SC_LAB_TEST_PYTHON";elif command -v python3.12 >/dev/null 2>&1;then PYTHON_BIN="$(command -v python3.12)";else PYTHON_BIN="$(command -v python3)";fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1;then PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')";VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01610-py${PYVER}}";[ -x "$VENV/bin/python" ]||"$PYTHON_BIN" -m venv "$VENV";"$VENV/bin/python" -m pip install -q pytest;PYTHON_BIN="$VENV/bin/python";fi
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_batch_experiment_sweep_ensemble_v01550.py \
 backend/tests/test_distributed_hpc_accelerated_coordination_v01560.py \
 backend/tests/test_cross_study_replication_meta_experiment_v01570.py \
 backend/tests/test_scientific_reproduction_independent_replication_network_v01580.py \
 backend/tests/test_integrated_scientific_review_validation_publication_gate_v01590.py \
 backend/tests/test_sqlite_connection_lifecycle_v01590.py \
 backend/tests/test_computational_research_operating_system_ii_v01600.py \
 backend/tests/test_research_program_portfolio_orchestration_v01610.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text());assert m['releaseVersion']=='0.161.0';assert m['featureVersion']=='0.161.0'
for k in ['v01610ResearchProgramPortfolioOrchestration','v01610ProgramRegistry','v01610PortfolioRegistry','v01610ResearchOSProjectMembership','v01610ProgramObjectives','v01610ProgramMilestones','v01610ObjectiveProjectAllocation','v01610HumanControlledProgramLifecycle','v01610HumanControlledPortfolioLifecycle','v01610ProgramCommandCenter','v01610PortfolioCommandCenter','v01610ImmutableSnapshots','v01610ManifestDigestVerification','v01610ResearchOSProjectReferences','v01610DescriptiveAggregationOnly','v01610PlatformCoreCanonicalAuthority','v01610WorkspaceExecutionAuthority','v01610ResearchOSProjectLifecycleAuthority','v01610HumanAuthorizationRequired','v01610V01600ResearchOSRetained','v01610V01590ReviewGateRetained','v01610V015701RepairRetained']:assert m.get(k) is True,k
for k in ['v01610AutomaticProjectCreation','v01610AutomaticStageAdvancement','v01610AutomaticScientificValidity','v01610AutomaticProgramPrioritization','v01610AutomaticFundingAllocation','v01610AutomaticResourceAllocation','v01610AutomaticPublication','v01610ScientificComputeMethodsChanged','v01610CredentialsStored','v01610EmbeddedRestrictedData']:assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text();assert 'Version: 0.161.0' in plugin;assert 'SC_Lab_Research_Program_Portfolio_Orchestration_V01610::init();' in plugin
main=(root/'backend/app/main.py').read_text();assert 'researchProgramPortfolioOrchestration' in main and 'research-program-portfolio-orchestration/v01610' in main
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text();assert 'program-portfolio/v01610' in repair and 'data-v01610-workspace' in repair
backend=(root/'backend/app/research_program_portfolio_orchestration_v01610.py').read_text();assert 'factory=_ClosingConnection' in backend;assert 'automaticFundingAllocation' in backend;assert 'researchOSProjectLifecycleAuthority' in backend
print('PASS - v0.161.0 release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
echo 'PASS - Lab v0.161.0 local validation complete.'
