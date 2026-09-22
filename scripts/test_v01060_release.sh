#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYTEST_BIN="${PYTEST_BIN:-pytest}"

echo "==> v0.106.0 PHP contracts"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-research-context-v01060.php >/dev/null
php tests/test-v01060.php

echo "==> v0.106.0 project/session context + integration regressions"
(
 cd backend
 "$PYTEST_BIN" -q \
   tests/test_platform_core_v3_research_context_v01060.py \
   tests/test_platform_core_v3_object_mapping_v01050.py \
   tests/test_platform_core_v3_adapter_v01040.py \
   tests/test_typed_cross_product_handoffs_v0381.py \
   tests/test_research_interoperability_v0380.py \
   tests/test_shared_model_handoff_v0490.py \
   tests/test_reproducible_model_package_v0500.py
)

echo "==> v0.106.0 FastAPI required-route topology + context invariants"
(
 cd backend
 "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_research_context_v01060 import (
    build_contextual_handoff_binding, build_contextual_object_binding,
    build_core_product_context_binding, build_core_session_registration,
    check_context_continuity, normalize_research_context,
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]
paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-context/health','/v1/platform-core-v3-context/manifest','/v1/platform-core-v3-context/schema',
'/v1/platform-core-v3-context/normalize','/v1/platform-core-v3-context/sessions/build','/v1/platform-core-v3-context/products/bind',
'/v1/platform-core-v3-context/objects/bind','/v1/platform-core-v3-context/handoffs/bind','/v1/platform-core-v3-context/continuity/check',
'/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health',
}
assert not (required-paths), sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'7','session_key':'s1','title':'Study','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:1'}
n=normalize_research_context(ctx)['context']; assert n['context_ref'].startswith('lab:research-context:')
s=build_core_session_registration(ctx); assert s['target_path']=='/v1/research/unified-runtime/sessions' and s['automatic_submission'] is False
p=build_core_product_context_binding(ctx); assert p['data']['context_ref']==n['context_ref']
o=build_contextual_object_binding({'context':ctx,'object':{'object_type':'dataset','id':'d1'}}); assert o['core_mapping']['data']['metadata']['lab_metadata']['project_ref']=='project:p1'
h=build_contextual_handoff_binding({'context':ctx,'handoff':{'id':'h1','targetProduct':'knowledge-library'}}); assert h['automatic_execution'] is False and h['data']['context_ref']==n['context_ref']
c=check_context_continuity({'context':ctx,'entries':[{'project_ref':'project:p1','session_id':'7','context_ref':n['context_ref']} ]}); assert c['ok'] is True
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - nine v0.106.0 context endpoints plus retained v0.104/v0.105 integration surfaces')
print('PASS - session/product/object/handoff envelopes preserve one project/session context without automatic submission/execution')
PYTEST
)

echo "==> v0.106.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-research-context-v01060.schema.json','platform-core-v3-research-context-policy-v01060.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.106 research-context contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.106.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.106.0' and m['featureVersion']=='0.106.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreProjectSessionContextVersion']=='0.106.0'
assert m['canonicalObjectMappingCount']==20
assert m['v01060RequiredRouteCount']==9
assert re.search(r'^ \* Version: 0\.106\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.106.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.106.0 Unified Project & Research Session Context release gate"
