#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.104.0 PHP contracts"
php tests/test-v01040.php

echo "==> v0.104.0 Platform Core v3 adapter unit tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q backend/tests/test_platform_core_v3_adapter_v01040.py

echo "==> v0.104.0 route topology + adapter invariants"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_adapter_v01040 import manifest, compatibility_report, normalize_runtime_context, validate_handoff
paths={r.path for r in app.routes}
required={
'/v1/platform-core-v3-adapter/health',
'/v1/platform-core-v3-adapter/manifest',
'/v1/platform-core-v3-adapter/registrations/runtime-contract',
'/v1/platform-core-v3-adapter/registrations/session',
'/v1/platform-core-v3-adapter/runtime-context/normalize',
'/v1/platform-core-v3-adapter/handoffs/validate',
'/v1/platform-core-v3-adapter/compatibility/check',
'/v1/typed-cross-product-handoffs/health',
}
missing=sorted(required-paths)
assert not missing, missing
assert len(app.routes)==1008, len(app.routes)
m=manifest(); assert m['lab_release_version']=='0.104.0'; assert m['required_core_release']=='3.0.0'; assert m['boundaries']['lab_calls_core_automatically'] is False
ctx=normalize_runtime_context({'session_id':'1','project_ref':'project:test'}); assert ctx['context']['runtime_contract_ref']=='sc.research.unified-runtime-contract.v1'
h=validate_handoff({'session_id':'1','handoff_ref':'handoff:1','source_product_ref':'product:workspace','target_product_ref':'product:sustainable-catalyst-lab'}); assert h['automatic_execution'] is False
ready={
'release':'3.0.0','contract':'sc.research.unified-research-scientific-investigation-runtime.v1',
'reference_first_runtime_by_core':True,'unified_session_registry_by_core':True,'research_object_binding_by_core':True,'product_context_binding_by_core':True,'computation_execution_binding_by_core':True,'investigation_binding_by_core':True,'visual_reasoning_binding_by_core':True,'validation_challenge_binding_by_core':True,'research_package_binding_by_core':True,'cross_product_handoff_binding_by_core':True,'milestone_registry_by_core':True,'revision_history_by_core':True,'immutable_runtime_snapshots_by_core':True,'underlying_objects_remain_authoritative_in_specialist_layers':True,
'execute_scientific_work_by_core':False,'execute_code_by_core':False,'run_investigation_by_core':False,'infer_findings_by_core':False,'infer_causality_by_core':False,'select_hypothesis_by_core':False,'rank_evidence_by_core':False,'render_visuals_by_core':False,'publish_research_by_core':False,'authorize_access_by_core':False,'certify_scientific_validity_by_core':False,'determine_truth_by_core':False,
}
assert compatibility_report(ready)['status']=='compatible'
print('PASS - Core v3.0.0 compatibility boundary accepted')
print('PASS - existing v0.38.1 typed handoff surface retained')
print('PASS - route count 1008 with seven v0.104.0 adapter endpoints')
PYTEST

echo "==> v0.104.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-runtime-adapter-v01040.schema.json','platform-core-v3-runtime-adapter-policy-v01040.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - Platform Core v3 adapter contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.104.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.104.0' and m['featureVersion']=='0.104.0' and m['routeAssertions']==1008
assert m['platformCoreRequiredVersion']=='3.0.0'
assert re.search(r'^ \* Version: 0\.104\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.104.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.104.0 Platform Core v3 Runtime Adapter & Capability Registration release gate"
