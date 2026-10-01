#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}";cd "$ROOT"
echo '=== VALIDATE LAB v0.163.0 — INSTITUTIONAL RESEARCH GOVERNANCE & REVIEW FEDERATION ==='
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-institutional-research-governance-review-federation-v01630.php >/dev/null
php tests/test-v01630-institutional-governance-review-federation.php
node --check assets/js/sc-lab-institutional-governance-review-federation-v01630.js
node --check assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js
node tests/test-v01630-institutional-governance-review-federation.js
python3 -m py_compile backend/app/institutional_research_governance_review_federation_v01630.py backend/app/main.py backend/app/config.py
if [ -n "${SC_LAB_TEST_PYTHON:-}" ];then PYTHON_BIN="$SC_LAB_TEST_PYTHON";elif command -v python3.12 >/dev/null 2>&1;then PYTHON_BIN="$(command -v python3.12)";else PYTHON_BIN="$(command -v python3)";fi
if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1;then PYVER="$($PYTHON_BIN -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')";VENV="${SC_LAB_TEST_VENV:-$HOME/.cache/sustainable-catalyst-lab/v01630-py${PYVER}}";[ -x "$VENV/bin/python" ]||"$PYTHON_BIN" -m venv "$VENV";"$VENV/bin/python" -m pip install -q pytest;PYTHON_BIN="$VENV/bin/python";fi
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
 backend/tests/test_institutional_research_governance_review_federation_v01630.py
python3 - <<'PY2'
from pathlib import Path
import json
root=Path('.');m=json.loads((root/'build/sc-lab-release-manifest.json').read_text());assert m['releaseVersion']=='0.163.0';assert m['featureVersion']=='0.163.0'
for k in ['v01630InstitutionalResearchGovernanceReviewFederation','v01630InstitutionRegistry','v01630GovernanceBodyRegistry','v01630FederatedReviewRelationships','v01630ExternalReviewerAssignments','v01630ExplicitIndependenceDeclarations','v01630HumanRecordedDecisions','v01630DissentPreservation','v01630InstitutionalSignoffBoundaries','v01630PolicyAttestations','v01630FederatedGovernanceCommandCenter','v01630ImmutableSnapshots','v01630ManifestDigestVerification','v01630V01620PlanningRetained','v01630V01610ProgramPortfolioRetained','v01630V01600ResearchOSRetained','v01630V01590ReviewGateRetained','v01630V015701RepairRetained','v01630PlatformCoreCanonicalAuthority','v01630WorkspaceExecutionAuthority','v01630ResearchOSProjectLifecycleAuthority','v01630ProgramPortfolioAuthority','v01630ResourcePlanningAuthority']: assert m.get(k) is True,k
for k in ['v01630AutomaticReviewerSelection','v01630AutomaticIndependenceInference','v01630AutomaticEthicsApproval','v01630AutomaticCaseApproval','v01630AutomaticDissentResolution','v01630AutomaticScientificValidity','v01630AutomaticResourceAllocation','v01630AutomaticFundingAllocation','v01630AutomaticExecution','v01630AutomaticPublication','v01630CrossInstitutionCredentialSharing','v01630DirectRemoteCallbacks','v01630ScientificComputeMethodsChanged','v01630CredentialsStored','v01630EmbeddedRestrictedData']: assert m.get(k) is False,k
plugin=(root/'sustainable-catalyst-lab.php').read_text();assert 'Version: 0.163.0' in plugin;assert 'SC_Lab_Institutional_Research_Governance_Review_Federation_V01630::init();' in plugin
main=(root/'backend/app/main.py').read_text();assert 'institutionalResearchGovernanceReviewFederation' in main and 'institutional-research-governance-review-federation/v01630' in main
repair=(root/'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js').read_text();assert 'institutional-governance/v01630' in repair and 'data-v01630-workspace' in repair
backend=(root/'backend/app/institutional_research_governance_review_federation_v01630.py').read_text();assert 'factory=_ClosingConnection' in backend;assert 'automaticReviewerSelection' in backend;assert 'dissentPreservation' in backend
print('PASS - v0.163.0 release contract')
PY2
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
echo 'PASS - Lab v0.163.0 local validation complete.'
