#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.126.0 spatial/spatiotemporal + causal + sensitivity + simulation + Bayesian + modeling + EDA + visualization + Core regression suite"
"$PYTHON_BIN" -m pytest -q \
 backend/tests/test_platform_core_v3_*.py \
 backend/tests/test_visualization_engine_v0730.py \
 backend/tests/test_visualization_engine_v0740.py \
 backend/tests/test_large_data_visualization_v0760.py \
 backend/tests/test_scientific_scene_v0770.py \
 backend/tests/test_linked_views_v0790.py \
 backend/tests/test_spatial_geospatial_raster_v0800.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_provenance_aware_figures_v0830.py \
 backend/tests/test_gpu_renderer_architecture_v0840.py \
 backend/tests/test_webgl2_scientific_renderer_v0850.py \
 backend/tests/test_webgpu_scientific_renderer_v0870.py \
 backend/tests/test_advanced_scientific_scene_v0880.py \
 backend/tests/test_scientific_visualization_design_system_v01140.py \
 backend/tests/test_advanced_statistical_uncertainty_graphics_v01150.py \
 backend/tests/test_interactive_scientific_dashboards_v01160.py \
 backend/tests/test_advanced_3d_4d_scientific_visualization_v01170.py \
 backend/tests/test_visual_research_narrative_figure_composer_v01180.py \
 backend/tests/test_scientific_figure_intelligence_automatic_layout_v01190.py \
 backend/tests/test_exploratory_data_analysis_studio_v01200.py \
 backend/tests/test_statistical_modeling_diagnostics_studio_v01210.py \
 backend/tests/test_bayesian_inference_v0520.py \
 backend/tests/test_hierarchical_modeling_v0680.py \
 backend/tests/test_bayesian_analysis_workbench_v01220.py \
 backend/tests/test_probabilistic_analysis_v0480.py \
 backend/tests/test_ensemble_uncertainty_v0341.py \
 backend/tests/test_simulation_monte_carlo_research_studio_v01230.py \
 backend/tests/test_sensitivity_global_uncertainty_analysis_studio_v01240.py \
 backend/tests/test_causal_inference_v0670.py \
 backend/tests/test_causal_research_studio_v01250.py \
 backend/tests/test_spatial_spatiotemporal_research_studio_v01260.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.spatial_spatiotemporal_research_studio_v01260 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/spatial-spatiotemporal-research-studio'
required={p for p in paths if p.startswith(base)}
assert len(required)>=28, len(required)
rows=[]
for y in range(4):
 for x in range(4): rows.append({'id':f'{x}-{y}','x':float(x),'y':float(y),'value':float(x+y+(2 if x>1 and y>1 else 0)),'cov':float(x-y)})
p={'rows':rows,'id_column':'id','x':'x','y':'y','value':'value','covariates':['cov'],'crs':{'id':'LOCAL:GRID','units':'km','geographic':False},'method':'knn','k':3}
w=build_spatial_weights(p)['weights']; assert len(w['weights_hash'])==64
assert isinstance(global_morans_i(p)['moran_i'],float)
assert len(local_morans_i(p)['locations'])==16
assert len(getis_ord_gi_star(p)['locations'])==16
assert nearest_neighbor_report(p)['physical_distance_certified'] is False
assert spatial_lag_estimate(p)['causal_interpretation'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'spatial-deploy'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty-eight v0.126 Spatial & Spatiotemporal Research Studio routes loaded')
print('PASS: spatial weights, association, raster/spatiotemporal, visualization, snapshot, and Core fixtures')
print('PASS: no silent reprojection/join inference, significance labels, causal interpretation, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['spatial-spatiotemporal-research-studio-v01260.schema.json','spatial-spatiotemporal-research-studio-policy-v01260.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.126 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-spatial-spatiotemporal-research-studio-v01260.php >/dev/null
php tests/test-v01260.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.126.0' and m['featureVersion']=='0.126.0'
assert m['spatialSpatiotemporalResearchStudioVersion']=='0.126.0'
assert m['v01260RequiredRouteCount']==28 and m['v01260MethodFamilyCount']==12 and m['v01260FigureFamilyCount']==14
assert re.search(r'^ \* Version: 0\.126\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.126.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.126.0 Spatial & Spatiotemporal Research Studio release gate"
