#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.109.0 integration/regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_platform_core_v3_findings_validation_v01080.py \
  backend/tests/test_platform_core_v3_visual_scene_v01090.py \
  backend/tests/test_scientific_scene_v0770.py \
  backend/tests/test_advanced_scientific_scene_v0880.py \
  backend/tests/test_linked_views_v0790.py \
  backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
  backend/tests/test_gpu_renderer_architecture_v0840.py \
  backend/tests/test_webgl2_scientific_renderer_v0850.py \
  backend/tests/test_webgpu_scientific_renderer_v0870.py

echo "==> v0.109.0 FastAPI visual-scene contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_visual_scene_v01090 import (
 build_core_scene_contract,build_core_visual_binding,bridge_linked_views,bridge_uncertainty_visual,
 health,manifest,map_legacy_scene,negotiate_renderer,normalize_scene,normalize_visual,renderer_catalog
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-visual-scene/health','/v1/platform-core-v3-visual-scene/manifest','/v1/platform-core-v3-visual-scene/schema',
'/v1/platform-core-v3-visual-scene/visuals/normalize','/v1/platform-core-v3-visual-scene/visuals/bind',
'/v1/platform-core-v3-visual-scene/scenes/normalize','/v1/platform-core-v3-visual-scene/scenes/bridge',
'/v1/platform-core-v3-visual-scene/linked-views/bridge','/v1/platform-core-v3-visual-scene/uncertainty/bridge',
'/v1/platform-core-v3-visual-scene/renderers/catalog','/v1/platform-core-v3-visual-scene/renderers/negotiate',
'/v1/platform-core-v3-visual-scene/legacy-scene/map',
'/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-executions/health','/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'9','session_key':'s1','title':'Study','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:1','researcher_ref':'researcher:r1'}
scene={'id':'scene-1','title':'Test scene','rendererPreference':'native-webgpu','cameras':[{'id':'cam-1','type':'perspective'}],'nodes':[{'id':'points','type':'point-cloud','name':'Points','sourceObjectId':'lab:dataset:d1','vertexCount':3,'children':[]}]}
nv=normalize_visual({'context':ctx,'visual':{'id':'v1','visual_type':'scientific-figure','title':'Figure','source_refs':['lab:dataset:d1'],'renderer':'svg2d'}}); assert nv['visual']['visual_ref']=='lab:visual:v1'
bv=build_core_visual_binding({'context':ctx,'visual':nv['visual']}); assert bv['automatic_submission'] is False and bv['data']['source_refs']==['lab:dataset:d1']
ns=normalize_scene({'context':ctx,'scene':scene}); assert ns['scene']['scene_kind']=='advanced-scene'
cs=build_core_scene_contract({'context':ctx,'scene':scene}); assert cs['core_scene']['contract']=='sc.visual-runtime.scene.v1' and cs['automatic_rendering'] is False
legacy=map_legacy_scene({'context':ctx,'scene':scene}); assert legacy['core_visual_binding']['data']['visual_type']=='scientific-scene' and legacy['automatic_submission'] is False
linked=bridge_linked_views({'context':ctx,'composition':{'title':'Linked','views':[{'id':'a','renderer':'svg2d','datasetId':'d1'},{'id':'b','renderer':'canvas3d','datasetId':'d1'}],'links':[{'sourceViewId':'a','targetViewIds':['b'],'channel':'selection','key':'id'}]},'source_refs':['lab:dataset:d1']}); assert linked['automatic_link_inference'] is False
unc=bridge_uncertainty_visual({'context':ctx,'layer':{'id':'u1','uncertaintySeries':[{'id':'s1','type':'interval','semantics':'custom','records':[{'x':0,'center':2,'lower':1.5,'upper':2.5}]}]},'source_refs':['lab:result:r1']}); assert unc['automatic_uncertainty_inference'] is False
cat=renderer_catalog(); assert len(cat['registry']['renderers'])>=4 and cat['core_renders_visuals'] is False
neg=negotiate_renderer({'browserCapabilities':{'detected':{'svg':True,'canvas2d':True,'webgl2':True,'webgpu':False}},'requiredFeatures':['3d'],'preferredRenderers':['webgpu','webgl2','canvas3d'],'allowFallback':True}); assert neg['core_renderer_selection'] is False
h=health(); m=manifest(); assert h['lab_release_version']=='0.109.0' and h['minimum_core_release']=='3.0.0'; assert m['boundaries']['core_renders_visuals'] is False
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - twelve v0.109.0 visual reasoning/scientific scene endpoints plus retained v0.104-v0.108 surfaces')
print('PASS - Lab scenes/figures map to reference-first Core visual/scene contracts')
print('PASS - Core rendering/GPU/truth inference remains disabled; Lab remains rendering authority')
PYTEST

echo "==> v0.109.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-visual-scene-v01090.schema.json','platform-core-v3-visual-scene-policy-v01090.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.109 visual-scene contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.109.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-visual-scene-v01090.php >/dev/null
php tests/test-v01090.php

echo "==> v0.109.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.109.0' and m['featureVersion']=='0.109.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreVisualReasoningScientificSceneVersion']=='0.109.0'
assert m['v01090RequiredRouteCount']==12
assert re.search(r'^ \* Version: 0\.109\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.109.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.109.0 Visual Reasoning & Scientific Scene Bridge release gate"
