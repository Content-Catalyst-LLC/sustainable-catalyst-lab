#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.117.0 3D/4D + visualization + Core integration regression suite"
"$PYTHON_BIN" -m pytest -q \
 backend/tests/test_platform_core_v3_*.py \
 backend/tests/test_visualization_engine_v0730.py \
 backend/tests/test_visualization_engine_v0740.py \
 backend/tests/test_large_data_visualization_v0760.py \
 backend/tests/test_scientific_scene_v0770.py \
 backend/tests/test_linked_views_v0790.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_provenance_aware_figures_v0830.py \
 backend/tests/test_gpu_renderer_architecture_v0840.py \
 backend/tests/test_webgl2_scientific_renderer_v0850.py \
 backend/tests/test_webgpu_scientific_renderer_v0870.py \
 backend/tests/test_advanced_scientific_scene_v0880.py \
 backend/tests/test_scientific_visualization_design_system_v01140.py \
 backend/tests/test_advanced_statistical_uncertainty_graphics_v01150.py \
 backend/tests/test_interactive_scientific_dashboards_v01160.py \
 backend/tests/test_advanced_3d_4d_scientific_visualization_v01170.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.advanced_3d_4d_scientific_visualization_v01170 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/advanced-3d-4d-scientific-visualization'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/scene/normalize',f'{base}/surface/figure',f'{base}/mesh/figure',f'{base}/vector-field/figure',f'{base}/scalar-field/figure',f'{base}/volume/plan',f'{base}/trajectory/figure',f'{base}/time/frames',f'{base}/slice/plan',f'{base}/isosurface/plan',f'{base}/camera/state',f'{base}/uncertainty/geometry',f'{base}/renderer/plan',f'{base}/publication/export',f'{base}/dashboard/panel',f'{base}/core-visual/plan',f'{base}/accessibility/audit'}
assert not(required-paths),sorted(required-paths)
scene={'id':'deploy-scene','title':'Deployment 4D scene','source_refs':['lab:dataset:d1'],'objects':[{'id':'mesh','type':'triangle-mesh','vertices':[[0,0,0],[1,0,0],[0,1,0]],'triangles':[[0,1,2]],'semantic_role':'observed','source_refs':['lab:dataset:d1']}],'time_axis':{'values':[0,1,2],'unit':'s'}}
n=normalize_scene(scene)['scene']; assert n['time_axis']['frame_count']==3
assert build_vector_field({'positions':[[0,0,0]],'vectors':[[1,0,0]]})['automatic_vector_inference'] is False
assert build_volume({'dimensions':[2,2,2],'data_ref':'lab:volume:v1','transfer_function':{'opacity_stops':[[0,0],[1,1]]}})['automatic_transfer_function'] is False
assert build_slice_plan({'source_field_ref':'lab:volume:v1','planes':[{'origin':[0,0,0],'normal':[0,0,1]}]})['automatic_slice_selection'] is False
assert build_isosurface_plan({'source_field_ref':'lab:volume:v1','iso_values':[0.5]})['automatic_threshold_selection'] is False
assert build_uncertainty_geometry({'kind':'uncertainty-envelope','level':0.95,'geometry_ref':'lab:geometry:u1'})['automatic_uncertainty_inference'] is False
assert build_renderer_plan({'scene':scene,'renderer':'webgpu'})['automatic_renderer_execution'] is False
assert build_publication_export({'scene':scene,'formats':['png','pdf','gltf','json']})['automatic_file_write'] is False
assert build_dashboard_panel({'scene':scene,'panel_id':'p1'})['automatic_dashboard_mutation'] is False
core=build_core_visual_plan({'scene':scene,'session_id':'deployment-session'}); assert core['automatic_core_submission'] is False and core['core_renders_scene'] is False
m=manifest(); assert m['features']['temporal_4d_scenes'] is True and m['boundaries']['automatic_geometry_inference'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty-one v0.117 advanced 3D/4D scientific visualization routes loaded')
print('PASS: mesh, field, volume, time, slice, isosurface, uncertainty, renderer, dashboard, publication, and Core fixtures')
print('PASS: geometry/topology/time/uncertainty/scientific-validity inference remains disabled')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['advanced-3d-4d-scientific-visualization-v01170.schema.json','advanced-3d-4d-scientific-visualization-policy-v01170.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.117 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-advanced-3d-4d-scientific-visualization-v01170.php >/dev/null
php tests/test-v01170.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.117.0' and m['featureVersion']=='0.117.0'
assert m['advanced3D4DScientificVisualizationVersion']=='0.117.0'
assert m['v01170RequiredRouteCount']==21 and m['v01170ObjectTypeCount']==12 and m['v01170RendererCount']==4
assert re.search(r'^ \* Version: 0\.117\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.117.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.117.0 Advanced 3D/4D Scientific Visualization release gate"
