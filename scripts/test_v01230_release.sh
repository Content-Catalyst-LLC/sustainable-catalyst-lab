#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.123.0 simulation + Bayesian + modeling + EDA + visualization + Core regression suite"
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
 backend/tests/test_simulation_monte_carlo_research_studio_v01230.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.simulation_monte_carlo_research_studio_v01230 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/simulation-monte-carlo-research-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/study/normalize',f'{base}/sampling/plan',f'{base}/compute-budget/plan',f'{base}/simulation/run',f'{base}/convergence/report',f'{base}/replication/report',f'{base}/parameter-sweep/plan',f'{base}/parameter-sweep/run',f'{base}/scenario-ensemble/run',f'{base}/uncertainty-propagation/run',f'{base}/threshold/report',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan',f'{base}/execution-lineage/plan'}
assert not(required-paths),sorted(required-paths)
model={'id':'deploy-decay','family':'declarative-expression','title':'Decay','definition':{'equation':'y = a * exp(-k*x)'},'variables':[{'symbol':'x','role':'input'},{'symbol':'y','role':'response'}],'parameters':[{'symbol':'a','role':'estimated','value':10},{'symbol':'k','role':'estimated','value':.3}],'constants':[],'datasetBindings':[]}
study={'id':'deploy-mc','title':'Deploy MC','model':model,'values':{'x':5},'uncertainInputs':[{'symbol':'a','distribution':'normal','mean':10,'stdDev':.5},{'symbol':'k','distribution':'normal','mean':.3,'stdDev':.02}],'design':{'method':'latin-hypercube','samples':32,'seed':11},'analysis':{'confidence':.95,'thresholds':[2.0]}}
r=run_simulation(study)['result']; assert r['observational_evidence'] is False and r['automatic_evidence_promotion'] is False
assert convergence_report({**study,'checkpoints':[16,32]})['convergence_certified'] is False
assert replication_report({**study,'seeds':[1,2]})['replication_stability_certified'] is False
sweep={'model':model,'values':{'x':5},'axes':[{'symbol':'a','values':[9,10,11]},{'symbol':'k','values':[.25,.3,.35]}]}
assert run_parameter_sweep(sweep)['summary']['count']==9
assert run_scenario_ensemble({'study':study,'scenarios':[{'id':'base','values':{'x':5}},{'id':'later','values':{'x':7}}]})['selected_scenario_id'] is None
assert build_core_object_plan({'session_id':'deployment-session','simulation_id':'sim-deploy'})['automatic_core_submission'] is False
assert build_execution_lineage_plan({'session_id':'deployment-session','simulation_id':'sim-deploy','seed':11})['automatic_execution'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty-two v0.123 Simulation & Monte Carlo Research Studio routes loaded')
print('PASS: simulation, convergence, replication, sweep, scenarios, visualization, snapshot, export, and Core fixtures')
print('PASS: no automatic convergence certification, scenario selection, evidence promotion, causal claims, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['simulation-monte-carlo-research-studio-v01230.schema.json','simulation-monte-carlo-research-studio-policy-v01230.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.123 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-simulation-monte-carlo-research-studio-v01230.php >/dev/null
php tests/test-v01230.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.123.0' and m['featureVersion']=='0.123.0'
assert m['simulationMonteCarloResearchStudioVersion']=='0.123.0'
assert m['v01230RequiredRouteCount']==22 and m['v01230SamplingDesignCount']==4 and m['v01230FigureFamilyCount']==12 and m['v01230StudyFamilyCount']==5
assert re.search(r'^ \* Version: 0\.123\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.123.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.123.0 Simulation & Monte Carlo Research Studio release gate"
