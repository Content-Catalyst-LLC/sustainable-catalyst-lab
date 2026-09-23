#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.113.0 integration/regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_platform_core_v3_findings_validation_v01080.py \
  backend/tests/test_platform_core_v3_visual_scene_v01090.py \
  backend/tests/test_platform_core_v3_scholarly_package_v01100.py \
  backend/tests/test_platform_core_v3_scientific_investigation_v01110.py \
  backend/tests/test_platform_core_v3_integration_certification_v01120.py \
  backend/tests/test_platform_core_v3_production_runtime_v01130.py \
  backend/tests/test_scientific_study_lifecycle_v0610.py \
  backend/tests/test_scientific_claims_traceability_v0620.py \
  backend/tests/test_scientific_evidence_grading_v0650.py \
  backend/tests/test_scientific_argumentation_v0660.py \
  backend/tests/test_causal_inference_v0670.py \
  backend/tests/test_reproducible_model_package_v0500.py

echo "==> v0.113.0 FastAPI production-runtime contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_production_runtime_v01130 import (
 COMPONENTS,OPERATION_CATALOG,assess_diagnostics,assess_roundtrip,build_checkpoint,
 build_receipt,build_recovery_plan,build_retry_plan,build_roundtrip_plan,build_submission_plan,
 catalog,check_continuity,check_idempotency,check_readiness,health,manifest,normalize_operation
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
base='/v1/platform-core-v3-production-runtime'
required={
 f'{base}/health',f'{base}/manifest',f'{base}/schema',f'{base}/catalog',
 f'{base}/operations/normalize',f'{base}/submissions/plan',f'{base}/idempotency/check',f'{base}/receipts/build',
 f'{base}/retries/plan',f'{base}/recovery/plan',f'{base}/checkpoints/build',f'{base}/continuity/check',
 f'{base}/diagnostics/assess',f'{base}/readiness/check',f'{base}/roundtrip/plan',f'{base}/roundtrip/assess',
 '/v1/platform-core-v3-integration-certification/health','/v1/platform-core-v3-scientific-investigations/health',
 '/v1/platform-core-v3-scholarly-packages/health','/v1/platform-core-v3-visual-scene/health',
 '/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-executions/health',
 '/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'12','session_key':'s12','title':'Production','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:12','researcher_ref':'researcher:r1'}
request={'context':ctx,'operation_type':'object-binding','payload':{'object':{'object_type':'dataset','id':'d1','content_hash':'a'*64}}}
a=normalize_operation(request); b=normalize_operation(request)
assert a['operation']['request_hash']==b['operation']['request_hash'] and a['operation']['idempotency_key']==b['operation']['idempotency_key']
submission=build_submission_plan(request); assert submission['automatic_submission'] is False and submission['authorization_material_included'] is False
idem=check_idempotency({**request,'prior_records':[{'idempotency_key':a['operation']['idempotency_key'],'request_hash':a['operation']['request_hash']}]}); assert idem['state']=='replay-safe' and idem['automatic_replay'] is False
receipt=build_receipt({'operation':a['operation'],'declared_outcome':'uncertain','status_code':200,'response':{'ok':True}})['receipt']; assert receipt['success_inferred_from_status_code'] is False
retry=build_retry_plan({'receipt':{**receipt,'declared_outcome':'failed','status_code':503}}); assert retry['eligible_for_explicit_retry'] is True and retry['automatic_retry'] is False
recovery=build_recovery_plan({'receipts':[{**receipt,'declared_outcome':'failed'}]}); assert recovery['recovery_required'] is True and recovery['automatic_recovery'] is False
checkpoint=build_checkpoint({'context':ctx,'operations':[a['operation']],'receipts':[receipt]}); assert checkpoint['automatic_persistence'] is False
continuity=check_continuity({'context':ctx,'operations':[a['operation']]}); assert continuity['continuous'] is True
components={name:{'ok':True,'lab_release_version':spec['version']} for name,spec in COMPONENTS.items()}; diagnostics=assess_diagnostics({'components':components}); assert diagnostics['ready'] is True and diagnostics['live_calls_performed'] is False
readiness=check_readiness({'core_health':{'ok':True,'version':'3.1.0'},'components':components,'certification':{'declared_conformance':True}}); assert readiness['production_ready'] is True and readiness['scientific_validity_certified'] is False
roundtrip=build_roundtrip_plan({'context':ctx,'operations':[request]}); assert len(roundtrip['stages'])==7 and roundtrip['automatic_recovery'] is False
assessment=assess_roundtrip({'receipts':[{'declared_outcome':'succeeded'},{'declared_outcome':'duplicate'}]}); assert assessment['declared_roundtrip_complete'] is True and assessment['truth_determined'] is False
h=health(); m=manifest(); c=catalog(); assert h['lab_release_version']=='0.113.0' and h['component_count']==9 and c['operation_type_count']==14; assert m['boundaries']['automatic_retry'] is False
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - sixteen v0.113.0 production-runtime endpoints plus retained v0.104-v0.112 surfaces')
print('PASS - nine retained integration components and fourteen governed operation types')
print('PASS - deterministic operation/idempotency identity, explicit receipts, advisory retry/recovery, checkpoints, continuity, diagnostics, readiness, and roundtrip controls')
print('PASS - automatic submission, retry, recovery, execution, certification, success inference, and truth determination remain disabled')
PYTEST

echo "==> v0.113.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-production-runtime-v01130.schema.json','platform-core-v3-production-runtime-policy-v01130.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.113 production-runtime contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.113.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-production-runtime-v01130.php >/dev/null
php tests/test-v01130.php

echo "==> v0.113.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.113.0' and m['featureVersion']=='0.113.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreProductionRuntimeVersion']=='0.113.0'
assert m['platformCoreProductionRuntimeContract']=='sc.research.unified-research-scientific-investigation-runtime.v1'
assert m['v01130RequiredRouteCount']==16 and m['v01130IntegrationComponentCount']==9 and m['v01130OperationTypeCount']==14
assert re.search(r'^ \* Version: 0\.113\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.113.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.113.0 Unified Research Session Production Runtime release gate"
