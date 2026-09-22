#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.121.0 statistical modeling + EDA + visualization + Core regression suite"
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
 backend/tests/test_advanced_3d_4d_scientific_visualization_v01170.py \
 backend/tests/test_visual_research_narrative_figure_composer_v01180.py \
 backend/tests/test_scientific_figure_intelligence_automatic_layout_v01190.py \
 backend/tests/test_exploratory_data_analysis_studio_v01200.py \
 backend/tests/test_statistical_modeling_diagnostics_studio_v01210.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.statistical_modeling_diagnostics_studio_v01210 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/statistical-modeling-diagnostics-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/model/normalize',f'{base}/model/fit',f'{base}/coefficients/report',f'{base}/diagnostics/analyze',f'{base}/assumptions/audit',f'{base}/effects/report',f'{base}/predictions/evaluate',f'{base}/cross-validation/run',f'{base}/models/compare',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/export/plan',f'{base}/core-object/plan'}
assert not(required-paths),sorted(required-paths)
rows=[{'x1':1.,'x2':2.,'y':3.1,'bin':0,'count':1},{'x1':2.,'x2':1.,'y':4.8,'bin':0,'count':2},{'x1':3.,'x2':4.,'y':8.2,'bin':0,'count':3},{'x1':4.,'x2':3.,'y':9.9,'bin':1,'count':4},{'x1':5.,'x2':6.,'y':13.1,'bin':1,'count':6},{'x1':6.,'x2':5.,'y':14.8,'bin':1,'count':7},{'x1':7.,'x2':8.,'y':18.2,'bin':1,'count':9},{'x1':8.,'x2':7.,'y':19.9,'bin':1,'count':11}]
p={'dataset':{'id':'deploy-model','rows':rows},'model':{'id':'ols-deploy','family':'gaussian','estimator':'ols','features':['x1','x2'],'response':'y'}}
n=normalize_model_spec(p); assert n['source_rows_immutable'] is True
f=fit_model(p)['result']; assert f['automatic_model_selection'] is False and f['automatic_significance_labels'] is False
c=coefficient_report({'result':f}); assert all(x['significance_label'] is None for x in c['coefficients'])
d=diagnose_model({**p,'result':f,'row_order_meaningful':True}); assert d['automatic_model_rejection'] is False and 'influence' in d
assert assumption_audit({**p,'result':f})['automatic_assumption_pass_fail'] is False
assert effect_report({'result':f})['automatic_significance_labels'] is False
assert evaluate_predictions({'result':f,'evaluation_rows':rows})['automatic_model_approval'] is False
assert cross_validate_model({**p,'folds':4})['validation']['automatic_model_selection'] is False
comp=compare_models({'dataset':{'id':'deploy-model','rows':rows},'candidates':[p['model'],{**p['model'],'id':'ridge','estimator':'ridge','alpha':1.0}],'folds':4}); assert comp['automatic_model_selection'] is False and comp['selected_model_id'] is None
assert build_visualization_plan({'result':f})['automatic_render'] is False
studio=build_studio(p); assert studio['automatic_causal_inference'] is False
assert build_snapshot({'studio':studio})['automatic_persistence'] is False
assert build_export_plan({'formats':['json','pdf']})['automatic_file_write'] is False
assert build_core_object_plan({'session_id':'deploy-session','model_id':'ols-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: eighteen v0.121 Statistical Modeling & Model Diagnostics Studio routes loaded')
print('PASS: fit, coefficients/effects, assumptions, diagnostics, prediction, CV, comparison, visual, snapshot, export, and Core fixtures')
print('PASS: no automatic feature/model selection, significance labels, causal claims, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['statistical-modeling-diagnostics-studio-v01210.schema.json','statistical-modeling-diagnostics-studio-policy-v01210.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.121 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-statistical-modeling-diagnostics-studio-v01210.php >/dev/null
php tests/test-v01210.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.121.0' and m['featureVersion']=='0.121.0'
assert m['statisticalModelingDiagnosticsStudioVersion']=='0.121.0'
assert m['v01210RequiredRouteCount']==18 and m['v01210FamilyCount']==3 and m['v01210EstimatorCount']==7 and m['v01210DiagnosticFamilyCount']==11
assert re.search(r'^ \* Version: 0\.121\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.121.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.121.0 Statistical Modeling & Model Diagnostics Studio release gate"
