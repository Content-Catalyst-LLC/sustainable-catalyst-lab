#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
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
 backend/tests/test_experimental_design_power_analysis_v01280.py \
 backend/tests/test_research_reproduction_replication_studio_v01290.py \
 backend/tests/test_scientific_research_project_studio_v01300.py \
 backend/tests/test_research_question_hypothesis_workspace_v01310.py \
 backend/tests/test_method_selection_intelligence_v01320.py \
 backend/tests/test_statistical_assumption_diagnostic_intelligence_v01330.py \
 backend/tests/test_evidence_synthesis_intelligence_ii_v01340.py \
 backend/tests/test_competing_model_hypothesis_analysis_v01350.py
export PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.competing_model_hypothesis_analysis_v01350 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/competing-model-hypothesis-analysis'; required={x for x in paths if x.startswith(base)}; assert len(required)==49,len(required)
assert catalog()['comparison_family_count']==24 and catalog()['figure_family_count']==17
assert prediction_observation_matrix({'comparisons':[{'prediction_ref':'p','observation_ref':'o','relation':'challenges','hypothesis_refs':['h']}]})['matrix'][0]['relation']=='challenges'
assert contradiction_matrix({'candidates':[{'candidate_ref':'h','supporting_evidence_refs':['e1'],'challenging_evidence_refs':['e2']}]})['contradictions_preserved'] is True
assert diagnostic_bridge({'assumption_refs':['a'],'diagnostic_refs':['d']})['automatic_model_rejection'] is False
assert pairwise_comparison({'candidate_a_ref':'h1','candidate_b_ref':'h2'})['automatic_pairwise_winner'] is None
assert comparison_matrix({'candidate_refs':['h2','h1']})['automatic_ranking'] is False
assert replication_bridge({'replication_refs':['r'],'agreement_state':'disagrees'})['replication_disagreement_preserved'] is True
assert core_object_plan({'hypothesis_refs':['h1'],'model_refs':['m1']})['core_does_not_select_winner'] is True
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: forty-nine v0.135 Competing Model & Hypothesis Analysis routes loaded')
print('PASS: predictions, contradictions, diagnostics, pairwise comparison, replication, and Core fixtures')
print('PASS: no automatic ranking, winner selection, rejection, truth inference, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['competing-model-hypothesis-analysis-v01350.schema.json','competing-model-hypothesis-analysis-policy-v01350.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.135 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-competing-model-hypothesis-analysis-v01350.php >/dev/null
php tests/test-v01350.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.135.0' and m['featureVersion']=='0.135.0'
assert m['competingModelHypothesisAnalysisVersion']=='0.135.0'
assert m['v01350RequiredRouteCount']==49 and m['v01350ComparisonFamilyCount']==24 and m['v01350FigureFamilyCount']==17
assert re.search(r'^ \* Version: 0\.135\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.135.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.135.0 Competing Model & Hypothesis Analysis release gate"
