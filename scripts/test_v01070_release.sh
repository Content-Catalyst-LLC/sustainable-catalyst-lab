#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
echo "==> v0.107.0 Python syntax"
"$PYTHON_BIN" -m py_compile backend/app/platform_core_v3_execution_lineage_v01070.py backend/app/main.py

echo "==> v0.107.0 Core integration regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_typed_cross_product_handoffs_v0381.py \
  backend/tests/test_shared_model_handoff_v0490.py \
  backend/tests/test_reproducible_model_package_v0500.py

echo "==> v0.107.0 FastAPI contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_execution_lineage_v01070 import (
    build_core_execution_binding,build_core_execution_binding_batch,check_execution_lineage,
    map_legacy_execution,normalize_execution,manifest
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]
paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-executions/health','/v1/platform-core-v3-executions/manifest','/v1/platform-core-v3-executions/schema',
'/v1/platform-core-v3-executions/normalize','/v1/platform-core-v3-executions/bind','/v1/platform-core-v3-executions/batch',
'/v1/platform-core-v3-executions/lineage/check','/v1/platform-core-v3-executions/legacy-run/map',
'/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths), sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'7','session_key':'s1','title':'Study','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:1'}
run={'id':'run-1','runtime':'python','environment_ref':'lab:env:py312','method_ref':'lab:method:mc:v1','inputs':[{'object_type':'dataset','id':'d1'}],'outputs':[{'object_type':'artifact','id':'a1'}],'parameters':{'n':1000},'assumptions':{'iid':True}}
n=normalize_execution({'context':ctx,'execution':run}); assert n['execution']['execution_ref']=='lab:execution:run-1' and len(n['execution']['lineage_hash'])==64
b=build_core_execution_binding({'context':ctx,'execution':run}); assert b['target_path']=='/v1/research/unified-runtime/execution-bindings'; assert b['automatic_submission'] is False and b['automatic_execution'] is False
assert b['data']['session_id']=='7' and b['data']['input_refs']==['lab:dataset:d1'] and b['data']['output_refs']==['lab:artifact:a1']
batch=build_core_execution_binding_batch({'context':ctx,'executions':[run,{**run,'id':'run-2','method_ref':'lab:method:sobol:v1'}]}); assert batch['count']==2
legacy=map_legacy_execution({'context':ctx,'run':{'runId':'legacy','engine':'python','environmentId':'env:1','method':'method:1','inputs':[],'outputs':[]}}); assert legacy['automatic_execution'] is False
check=check_execution_lineage({'context':ctx,'execution':run}); assert check['ok'] is True and check['scientific_validity_certified'] is False
m=manifest(); assert m['lab_release_version']=='0.107.0' and m['minimum_core_release']=='3.0.0'
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - eight v0.107.0 execution-lineage endpoints plus retained v0.104-v0.106 integration surfaces')
print('PASS - execution bindings preserve Lab authority and never auto-submit/execute')
PYTEST

echo "==> v0.107.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-execution-lineage-v01070.schema.json','platform-core-v3-execution-lineage-policy-v01070.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.107 execution-lineage contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.107.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-execution-lineage-v01070.php >/dev/null
php tests/test-v01070.php

echo "==> v0.107.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.107.0' and m['featureVersion']=='0.107.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreScientificExecutionLineageVersion']=='0.107.0'
assert m['v01070RequiredRouteCount']==8
assert re.search(r'^ \* Version: 0\.107\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.107.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.107.0 Scientific Execution Lineage Bridge release gate"
