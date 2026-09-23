#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.128.0 experimental design + time-series + spatial + causal + sensitivity + simulation + Bayesian + modeling + EDA + visualization + Core regression suite"
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
 backend/tests/test_spatial_spatiotemporal_research_studio_v01260.py \
 backend/tests/test_scientific_time_series_laboratory_v01270.py \
 backend/tests/test_experimental_design_power_analysis_v01280.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.experimental_design_power_analysis_v01280 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/experimental-design-power-analysis'; required={p for p in paths if p.startswith(base)}; assert len(required)>=30,len(required)
a=two_sample_mean_power({'effect_size':.5,'target_power':.8}); assert a['achieved_power']>=.8
b=one_way_anova_power({'groups':4,'effect_size':.25,'target_power':.8}); assert b['achieved_power']>=.79
c=simulation_power({'simulations':2000,'seed':42,'effect_size':.4,'n':50}); assert c['power_is_estimated_not_guaranteed'] is True
d=factorial_design_plan({'factors':[{'name':'A','levels':['0','1']},{'name':'B','levels':['0','1','2']}],'replicates_per_cell':4}); assert d['total_n']==24
assert sequential_design_plan({'looks':4})['automatic_stopping'] is False
assert randomization_schedule({'groups':['A','B'],'n':20,'seed':9})['automatic_enrollment_assignment'] is False
assert build_core_object_plan({'session_id':'sess','analysis_id':'exp1'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: thirty v0.128 Experimental Design & Power Analysis routes loaded')
print('PASS: mean/ANOVA/simulation/factorial/sequential/randomization/Core fixtures')
print('PASS: no automatic design/effect selection, power guarantee, significance claim, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['experimental-design-power-analysis-v01280.schema.json','experimental-design-power-analysis-policy-v01280.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.128 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-experimental-design-power-analysis-v01280.php >/dev/null
php tests/test-v01280.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.128.0' and m['featureVersion']=='0.128.0'
assert m['experimentalDesignPowerAnalysisVersion']=='0.128.0'
assert m['v01280RequiredRouteCount']==30 and m['v01280MethodFamilyCount']==15 and m['v01280FigureFamilyCount']==16
assert re.search(r'^ \* Version: 0\.128\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.128.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.128.0 Experimental Design & Power Analysis release gate"
