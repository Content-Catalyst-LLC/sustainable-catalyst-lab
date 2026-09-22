#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.122.0 Bayesian + modeling + EDA + visualization + Core regression suite"
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
 backend/tests/test_statistical_modeling_diagnostics_studio_v01210.py \
 backend/tests/test_bayesian_inference_v0520.py \
 backend/tests/test_hierarchical_modeling_v0680.py \
 backend/tests/test_bayesian_analysis_workbench_v01220.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.bayesian_analysis_workbench_v01220 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/bayesian-analysis-workbench'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/analysis/normalize',f'{base}/posterior/fit',f'{base}/prior-posterior/report',f'{base}/diagnostics/sampler',f'{base}/convergence/audit',f'{base}/posterior-predictive/report',f'{base}/probability/report',f'{base}/hierarchical/fit',f'{base}/hierarchical/summary',f'{base}/models/compare',f'{base}/visualization/plan',f'{base}/workbench/build',f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan'}
assert not(required-paths),sorted(required-paths)
rows=[{'x':i/4.0,'y':1.2+1.8*(i/4.0)+((i%4)-1.5)*0.08} for i in range(20)]
p={'dataset':{'id':'deploy-bayes','rows':rows},'study':{'id':'bayes-deploy','family':'gaussian','features':['x'],'response':'y','chains':2,'draws':60,'warmup':30,'posteriorPredictiveDraws':30,'seed':11}}
f=fit_posterior(p)['result']; assert f['automatic_prior_selection'] is False and f['automatic_convergence_certification'] is False
assert prior_posterior_report({'result':f})['automatic_prior_selection'] is False
assert sampler_diagnostics({'result':f})['automatic_convergence_certification'] is False
assert convergence_audit({'result':f})['convergence_certified'] is False
assert posterior_predictive_report({'result':f})['automatic_model_approval'] is False
assert probability_report({'result':f,'queries':[{'term':'z(x)','threshold':0,'direction':'greater-than'}]})['automatic_decision'] is False
h=fit_hierarchical_normal({'hierarchical':{'id':'h','draws':400,'seed':3},'units':[{'id':'a','estimate':.2,'standard_error':.15},{'id':'b','estimate':.7,'standard_error':.2},{'id':'c','estimate':1.1,'standard_error':.18}]}); assert h['automatic_generalization'] is False
assert hierarchical_summary({'hierarchical_result':h})['automatic_heterogeneity_judgment'] is False
assert build_visualization_plan({'result':f,'hierarchical_result':h})['automatic_render'] is False
assert build_snapshot({'workbench':build_workbench(p)})['automatic_persistence'] is False
assert build_reproduction_plan({'result':f})['automatic_execution'] is False
assert build_export_plan({'formats':['json','pdf']})['automatic_file_write'] is False
assert build_core_object_plan({'session_id':'deploy-session','model_id':'bayes-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty v0.122 Bayesian Analysis Workbench II routes loaded')
print('PASS: posterior, diagnostics, PPC, probability, hierarchical, visualization, snapshot, reproduction, export, and Core fixtures')
print('PASS: no automatic prior/model selection, convergence certification, causal inference, generalization, validity certification, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['bayesian-analysis-workbench-v01220.schema.json','bayesian-analysis-workbench-policy-v01220.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.122 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-bayesian-analysis-workbench-v01220.php >/dev/null
php tests/test-v01220.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.122.0' and m['featureVersion']=='0.122.0'
assert m['bayesianAnalysisWorkbenchVersion']=='0.122.0'
assert m['v01220RequiredRouteCount']==20 and m['v01220FamilyCount']==3 and m['v01220DiagnosticCount']==7 and m['v01220FigureFamilyCount']==12
assert re.search(r'^ \* Version: 0\.122\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.122.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.122.0 Bayesian Analysis Workbench II release gate"
