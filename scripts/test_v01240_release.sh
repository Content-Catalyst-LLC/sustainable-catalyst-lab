#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.124.0 sensitivity + simulation + Bayesian + modeling + EDA + visualization + Core regression suite"
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
 backend/tests/test_bayesian_analysis_workbench_v01220.py \
 backend/tests/test_probabilistic_analysis_v0480.py \
 backend/tests/test_ensemble_uncertainty_v0341.py \
 backend/tests/test_simulation_monte_carlo_research_studio_v01230.py \
 backend/tests/test_sensitivity_global_uncertainty_analysis_studio_v01240.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.sensitivity_global_uncertainty_analysis_studio_v01240 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/sensitivity-global-uncertainty-analysis-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/study/normalize',f'{base}/sobol/report',f'{base}/morris/report',f'{base}/correlation-screening/report',f'{base}/variance-decomposition/report',f'{base}/interaction-screening/report',f'{base}/response-surface/plan',f'{base}/response-surface/run',f'{base}/convergence/report',f'{base}/replication/report',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan',f'{base}/execution-lineage/plan',f'{base}/interpretation-boundaries/report'}
assert not(required-paths),sorted(required-paths)
model={'id':'deploy-sensitivity','family':'declarative-expression','title':'Sensitivity','definition':{'equation':'y = a*x + b*x*x + a*b'},'variables':[{'symbol':'x','role':'input'},{'symbol':'y','role':'response'}],'parameters':[{'symbol':'a','role':'estimated','value':2},{'symbol':'b','role':'estimated','value':.5}],'constants':[],'datasetBindings':[]}
study={'id':'deploy-sens','title':'Deploy Sensitivity','model':model,'values':{'x':3},'uncertainInputs':[{'symbol':'a','distribution':'uniform','low':1,'high':3},{'symbol':'b','distribution':'uniform','low':.1,'high':1}],'design':{'method':'latin-hypercube','samples':32,'seed':11},'analysis':{'confidence':.95}}
s=sobol_report({**study,'base_samples':32}); assert len(s['indices'])==2 and s['automatic_parameter_ranking'] is False
m=morris_report({**study,'trajectories':6}); assert len(m['effects'])==2 and m['automatic_significance_inference'] is False
v=variance_decomposition_report({**study,'base_samples':32}); assert v['automatic_interaction_proof'] is False
i=interaction_screening_report({**study,'samples':64}); assert len(i['pairs'])==1 and i['formal_second_order_sobol'] is False
surf=response_surface_run({'model':model,'values':{'x':3},'axes':[{'symbol':'a','values':[1,2,3]},{'symbol':'b','values':[.1,.5,1]}]}); assert surf['diagnostics']['record_count']==9 and surf['automatic_optimum_selection'] is False
assert sensitivity_convergence_report({**study,'checkpoints':[16,32]})['convergence_certified'] is False
assert sensitivity_replication_report({**study,'seeds':[1,2],'base_samples':16})['stability_certified'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'sensitivity-deploy'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty-two v0.124 Sensitivity & Global Uncertainty Analysis Studio routes loaded')
print('PASS: Sobol, Morris, variance, interaction, response-surface, convergence, replication, and Core fixtures')
print('PASS: no automatic parameter ranking, significance inference, causal claims, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['sensitivity-global-uncertainty-analysis-studio-v01240.schema.json','sensitivity-global-uncertainty-analysis-policy-v01240.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.124 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-sensitivity-global-uncertainty-analysis-studio-v01240.php >/dev/null
php tests/test-v01240.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.124.0' and m['featureVersion']=='0.124.0'
assert m['sensitivityGlobalUncertaintyAnalysisStudioVersion']=='0.124.0'
assert m['v01240RequiredRouteCount']==22 and m['v01240MethodFamilyCount']==6 and m['v01240FigureFamilyCount']==12
assert re.search(r'^ \* Version: 0\.124\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.124.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.124.0 Sensitivity & Global Uncertainty Analysis Studio release gate"
