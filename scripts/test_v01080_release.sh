#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
echo "==> v0.108.0 Python syntax"
"$PYTHON_BIN" -m py_compile backend/app/platform_core_v3_findings_validation_v01080.py backend/app/main.py

echo "==> v0.108.0 Core integration + scientific evidence regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_platform_core_v3_findings_validation_v01080.py \
  backend/tests/test_scientific_claims_traceability_v0620.py \
  backend/tests/test_scientific_evidence_grading_v0650.py \
  backend/tests/test_typed_cross_product_handoffs_v0381.py \
  backend/tests/test_shared_model_handoff_v0490.py \
  backend/tests/test_reproducible_model_package_v0500.py

echo "==> v0.108.0 FastAPI contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_findings_validation_v01080 import (
 build_core_claim_binding,build_core_contradiction_binding,build_core_evidence_link_binding,
 build_core_finding_binding,build_core_replication_binding,build_core_validation_challenge_binding,
 health,manifest,map_legacy_scientific_claim,normalize_claim,normalize_finding
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]
paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-research-intelligence/manifest','/v1/platform-core-v3-research-intelligence/schema',
'/v1/platform-core-v3-research-intelligence/findings/normalize','/v1/platform-core-v3-research-intelligence/findings/bind',
'/v1/platform-core-v3-research-intelligence/claims/normalize','/v1/platform-core-v3-research-intelligence/claims/bind',
'/v1/platform-core-v3-research-intelligence/evidence-links/bind','/v1/platform-core-v3-research-intelligence/contradictions/bind',
'/v1/platform-core-v3-research-intelligence/validation/bind','/v1/platform-core-v3-research-intelligence/replications/bind',
'/v1/platform-core-v3-research-intelligence/legacy-claim/map',
'/v1/platform-core-v3-executions/health','/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'8','session_key':'s1','title':'Study','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:1','researcher_ref':'researcher:r1'}
finding={'id':'f1','title':'Finding','statement':'Declared analysis result.','finding_type':'result','status':'recorded','execution_ref':'lab:execution:r1','source_refs':['lab:artifact:a1']}
claim={'id':'c1','studyId':'s1','statement':'A declared association is present in the modeled scenario.','claimType':'associational','status':'active','evidenceLinks':[{'id':'e1','role':'supports','sourceType':'analysis','ref':'lab:artifact:a1'}]}
nf=normalize_finding({'context':ctx,'finding':finding}); assert nf['finding']['finding_key']=='f1' and len(nf['finding']['finding_hash'])==64
bf=build_core_finding_binding({'context':ctx,'finding':finding}); assert bf['automatic_submission'] is False and bf['data']['analysis_run_ref']=='lab:execution:r1'
nc=normalize_claim({'context':ctx,'claim':claim}); assert nc['claim']['claim_type']=='interpretive' and nc['claim']['status']=='proposed'
bc=build_core_claim_binding({'context':ctx,'claim':claim}); assert bc['automatic_submission'] is False and bc['data']['status']=='proposed'
ev=build_core_evidence_link_binding({'context':ctx,'evidence_link':{'id':'el1','evidence_ref':'lab:artifact:a1','target_type':'claim','target_id':'core-claim-id','relation':'supports','declared_strength':'moderate'}}); assert ev['data']['relation']=='supports'
co=build_core_contradiction_binding({'context':ctx,'contradiction':{'id':'co1','claim_a_id':'a','claim_b_id':'b','status':'unresolved'}}); assert co['data']['status']=='unresolved'
va=build_core_validation_challenge_binding({'context':ctx,'validation':{'id':'v1','challenge_type':'uncertainty_challenge','title':'Uncertainty challenge'}}); assert va['scientific_validity_certified'] is False
rp=build_core_replication_binding({'context':ctx,'replication':{'id':'rp1','challenge_id':'core-challenge-1','target_ref':'lab:claim:c1','execution_ref':'lab:execution:rep1'}}); assert rp['data']['provenance']['replication_result_is_declared_not_core_certified'] is True
legacy=map_legacy_scientific_claim({'context':ctx,'claim':claim}); assert len(legacy['core_evidence_bindings'])==1 and legacy['automatic_claim_inference'] is False
h=health(); m=manifest(); assert h['lab_release_version']=='0.108.0' and h['minimum_core_release']=='3.0.0'; assert m['boundaries']['bridge_determines_truth'] is False
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - twelve v0.108.0 research-intelligence/validation endpoints plus retained v0.104-v0.107 surfaces')
print('PASS - findings/claims/evidence/challenges remain declared and reference-first')
print('PASS - no automatic Core submission, claim/finding inference, evidence judgment, replication certification, or truth determination')
PYTEST

echo "==> v0.108.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-findings-validation-v01080.schema.json','platform-core-v3-findings-validation-policy-v01080.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.108 findings/validation contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.108.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-findings-validation-v01080.php >/dev/null
php tests/test-v01080.php

echo "==> v0.108.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.108.0' and m['featureVersion']=='0.108.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreFindingsClaimsEvidenceValidationVersion']=='0.108.0'
assert m['v01080RequiredRouteCount']==12
assert re.search(r'^ \* Version: 0\.108\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.108.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.108.0 Findings, Claims, Evidence & Validation Bridge release gate"
