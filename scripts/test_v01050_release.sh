#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYTEST_BIN="${PYTEST_BIN:-pytest}"

echo "==> v0.105.0 PHP contracts"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-object-mapping-v01050.php >/dev/null
php tests/test-v01050.php

echo "==> v0.105.0 canonical object mapping + integration regression tests"
(
 cd backend
 "$PYTEST_BIN" -q \
   tests/test_platform_core_v3_object_mapping_v01050.py \
   tests/test_platform_core_v3_adapter_v01040.py \
   tests/test_typed_cross_product_handoffs_v0381.py \
   tests/test_research_interoperability_v0380.py \
   tests/test_shared_model_handoff_v0490.py \
   tests/test_reproducible_model_package_v0500.py
)

echo "==> v0.105.0 FastAPI route topology + mapping invariants"
(
 cd backend
 "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_object_mapping_v01050 import (
    build_core_object_binding,
    build_core_object_binding_batch,
    catalog,
    map_legacy_typed_handoff,
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]
paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-objects/health',
'/v1/platform-core-v3-objects/catalog',
'/v1/platform-core-v3-objects/schema',
'/v1/platform-core-v3-objects/normalize',
'/v1/platform-core-v3-objects/bind',
'/v1/platform-core-v3-objects/batch',
'/v1/platform-core-v3-objects/legacy-handoff/map',
}
assert not (required-paths), sorted(required-paths)
assert len(path_routes)==1015, len(path_routes)
c=catalog(); assert c['mapping_count']==20 and c['lab_release_version']=='0.105.0'
b=build_core_object_binding({'session_id':'s1','object':{'object_type':'dataset','id':'d1','content_hash':'a'*64}})
assert b['target_path']=='/v1/research/unified-runtime/object-bindings'
assert b['automatic_submission'] is False
assert b['request_body']=={'data':b['data']}
assert b['data']['metadata']['underlying_object_remains_authoritative_in_lab'] is True
batch=build_core_object_binding_batch({'session_id':'s1','objects':[{'object_type':'model','id':'m1'},{'object_type':'scientific-figure','id':'f1'}]})
assert batch['count']==2 and batch['automatic_submission'] is False
legacy=map_legacy_typed_handoff({'session_id':'s1','entityType':'dataset','contractVersion':'sc-research-dataset/1.0','resource':{'id':'d2','sha256':'b'*64}})
assert legacy['core_mapping']['data']['object_ref']=='lab:dataset:d2'
print('PASS - 1015 FastAPI path routes including seven v0.105.0 object-mapping endpoints')
print('PASS - 20 canonical mappings and reference-first Core object-binding envelope')
print('PASS - v0.38.1 typed handoff bridge maps without automatic Core submission or execution')
PYTEST
)

echo "==> v0.105.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-object-mapping-v01050.schema.json','platform-core-v3-object-mapping-policy-v01050.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - Platform Core v3 object mapping contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.105.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.105.0' and m['featureVersion']=='0.105.0' and m['routeAssertions']==1015
assert m['platformCoreRequiredVersion']=='3.0.0'
assert m['canonicalObjectMappingCount']==20
assert re.search(r'^ \* Version: 0\.105\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.105.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.105.0 Canonical Research Object Mapping release gate"
