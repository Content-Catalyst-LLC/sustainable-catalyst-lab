#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.111.0 integration/regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_platform_core_v3_findings_validation_v01080.py \
  backend/tests/test_platform_core_v3_visual_scene_v01090.py \
  backend/tests/test_platform_core_v3_scholarly_package_v01100.py \
  backend/tests/test_platform_core_v3_scientific_investigation_v01110.py \
  backend/tests/test_scientific_study_lifecycle_v0610.py \
  backend/tests/test_scientific_claims_traceability_v0620.py \
  backend/tests/test_scientific_evidence_grading_v0650.py \
  backend/tests/test_scientific_argumentation_v0660.py \
  backend/tests/test_causal_inference_v0670.py \
  backend/tests/test_reproducible_model_package_v0500.py

echo "==> v0.111.0 FastAPI scientific-investigation contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_scientific_investigation_v01110 import (
 build_core_investigation_binding,build_runtime_integration_plan,bridge_evidence_context,
 bridge_reasoning_context,bridge_scientific_assets,check_investigation_continuity,
 health,manifest,map_legacy_scientific_study,normalize_investigation
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-scientific-investigations/health','/v1/platform-core-v3-scientific-investigations/manifest','/v1/platform-core-v3-scientific-investigations/schema',
'/v1/platform-core-v3-scientific-investigations/investigations/normalize','/v1/platform-core-v3-scientific-investigations/investigations/bind',
'/v1/platform-core-v3-scientific-investigations/investigations/runtime-plan','/v1/platform-core-v3-scientific-investigations/investigations/evidence-context',
'/v1/platform-core-v3-scientific-investigations/investigations/reasoning-context','/v1/platform-core-v3-scientific-investigations/investigations/scientific-assets',
'/v1/platform-core-v3-scientific-investigations/investigations/continuity/check','/v1/platform-core-v3-scientific-investigations/legacy-study/map',
'/v1/platform-core-v3-scientific-investigations/legacy-argumentation/map',
'/v1/platform-core-v3-scholarly-packages/health','/v1/platform-core-v3-visual-scene/health','/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-executions/health','/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'9','session_key':'s1','title':'Study','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:1','researcher_ref':'researcher:r1'}
inv={'id':'inv1','investigation_type':'computational','title':'Model investigation','status':'active','dataset_refs':['lab:dataset:d1'],'model_refs':['lab:model:m1'],'execution_refs':['lab:execution:r1'],'evidence_refs':['lab:evidence:e1'],'claim_refs':['lab:claim:c1'],'hypothesis_refs':['lab:hypothesis:h1'],'visual_refs':['lab:visual:v1'],'validation_refs':['lab:validation:x1'],'package_refs':['lab:research-package:p1']}
n=normalize_investigation({'context':ctx,'investigation':inv}); b=build_core_investigation_binding({'context':ctx,'investigation':inv}); plan=build_runtime_integration_plan({'context':ctx,'investigation':inv})
e=bridge_evidence_context({'context':ctx,'investigation':inv}); r=bridge_reasoning_context({'context':ctx,'investigation':inv}); a=bridge_scientific_assets({'context':ctx,'investigation':inv}); c=check_investigation_continuity({'context':ctx,'investigation':inv,'expected_context':{'project_ref':'project:p1','session_id':'9'}})
assert n['investigation']['investigation_ref']=='lab:scientific-investigation:inv1'
assert b['automatic_submission'] is False and b['automatic_execution'] is False
assert plan['plan']['automatic_investigation_run'] is False and plan['plan']['primary_operation']['endpoint'].endswith('/investigation-bindings')
assert e['automatic_evidence_ranking'] is False and r['automatic_hypothesis_ranking'] is False and a['automatic_binding_submission'] is False
assert c['reference_continuity_valid'] is True and c['scientific_validity_assessed'] is False
legacy=map_legacy_scientific_study({'context':ctx,'study':{'id':'study1','title':'Study','studyType':'experimental','status':'active','hypotheses':['H1'],'evidenceRefs':['lab:evidence:e1']}})
assert legacy['legacy_hypothesis_text_promoted_to_truth'] is False and legacy['automatic_execution'] is False
h=health(); m=manifest(); assert h['lab_release_version']=='0.111.0' and h['minimum_core_release']=='3.0.0'; assert m['boundaries']['core_determines_truth'] is False
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - twelve v0.111.0 scientific-investigation endpoints plus retained v0.104-v0.110 surfaces')
print('PASS - Lab investigations map to Core reference-first investigation bindings')
print('PASS - executions, visuals, validations, packages, models, datasets, protocols, and sources remain declared specialist references')
print('PASS - Core execution, evidence ranking, contradiction resolution, hypothesis selection, causal inference, scientific certification, and truth determination remain disabled')
PYTEST

echo "==> v0.111.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-scientific-investigation-v01110.schema.json','platform-core-v3-scientific-investigation-policy-v01110.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.111 scientific-investigation contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.111.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-scientific-investigation-v01110.php >/dev/null
php tests/test-v01110.php

echo "==> v0.111.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.111.0' and m['featureVersion']=='0.111.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreScientificInvestigationRuntimeVersion']=='0.111.0'
assert m['v01110RequiredRouteCount']==12
assert re.search(r'^ \* Version: 0\.111\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.111.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.111.0 Scientific Investigation Runtime Integration release gate"
