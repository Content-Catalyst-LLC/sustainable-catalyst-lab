#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.125.0 causal + sensitivity + simulation + Bayesian + modeling + EDA + visualization + Core regression suite"
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
 backend/tests/test_sensitivity_global_uncertainty_analysis_studio_v01240.py \
 backend/tests/test_causal_inference_v0670.py \
 backend/tests/test_causal_research_studio_v01250.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.causal_research_studio_v01250 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/causal-research-studio'
required={
 f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/study/normalize',
 f'{base}/dag/normalize',f'{base}/dag/adjustment-plan',f'{base}/propensity/fit',f'{base}/matching/estimate',
 f'{base}/weighting/estimate',f'{base}/balance/report',f'{base}/overlap/report',f'{base}/did/estimate',
 f'{base}/its/estimate',f'{base}/rd/estimate',f'{base}/synthetic-control/estimate',f'{base}/robustness/plan',
 f'{base}/placebo/plan',f'{base}/counterfactual/report',f'{base}/visualization/plan',f'{base}/studio/build',
 f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan',
 f'{base}/execution-lineage/plan',f'{base}/governance/review',f'{base}/interpretation-boundaries/report'}
assert not(required-paths),sorted(required-paths)
rows=[]
for i in range(60):
 x=(i%10)/10; z=((i*7)%13)/13; t=1.0 if (i%3) else 0.0; y=2+1.5*t+0.7*x-0.2*z
 rows.append({'t':t,'y':y,'x':x,'z':z,'post':1.0 if i>=30 else 0.0,'time':float(i),'treated_group':1.0 if i%2==0 else 0.0,'running':(i-30)/10})
study={'id':'deploy-causal','rows':rows,'treatment':'t','outcome':'y','covariates':['x','z']}
assert len(fit_propensity(study)['scores'])==60
m=estimate_matching(study); assert m['pair_count']>0 and m['causal_proof'] is False
w=estimate_weighting(study); assert w['effective_sample_size']>0
assert balance_report({**study,'weights':w['weights']})['automatic_balance_pass_fail'] is False
assert overlap_report(study)['overlap_sufficient_certified'] is False
assert estimate_did({'rows':rows,'outcome':'y','treated':'treated_group','post':'post'})['parallel_trends_certified'] is False
assert estimate_its({'rows':rows,'outcome':'y','time':'time','post':'post'})['causal_proof'] is False
assert estimate_rd({'rows':rows,'outcome':'y','running':'running','cutoff':0,'bandwidth':2})['causal_proof'] is False
sc=estimate_synthetic_control({'treated_pre':[1,1.2,1.4],'treated_post':[2,2.4],'donors_pre':[[.8,1.1],[1,1.3],[1.2,1.5]],'donors_post':[[1.4,1.8],[1.6,2.0]]}); assert sc['causal_proof'] is False
assert robustness_plan({})['automatic_execution'] is False
assert placebo_plan({})['placebo_pass_fail_certified'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'causal-deploy'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty-eight v0.125 Causal Research Studio II routes loaded')
print('PASS: propensity, matching, weighting, DiD, ITS, RD, synthetic control, diagnostics, and Core fixtures')
print('PASS: no automatic causal proof, assumption satisfaction, method selection, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['causal-research-studio-v01250.schema.json','causal-research-studio-policy-v01250.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.125 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-causal-research-studio-v01250.php >/dev/null
php tests/test-v01250.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.125.0' and m['featureVersion']=='0.125.0'
assert m['causalResearchStudioVersion']=='0.125.0'
assert m['v01250RequiredRouteCount']==28 and m['v01250MethodFamilyCount']==8 and m['v01250FigureFamilyCount']==12
assert re.search(r'^ \* Version: 0\.125\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.125.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.125.0 Causal Research Studio II release gate"
