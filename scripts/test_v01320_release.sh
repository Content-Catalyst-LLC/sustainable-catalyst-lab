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
 backend/tests/test_method_selection_intelligence_v01320.py
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.method_selection_intelligence_v01320 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/method-selection-intelligence'; required={p for p in paths if p.startswith(base)}; assert len(required)>=37,len(required)
assert catalog()['method_catalog_count']>=20
assert method_candidates({'method_refs':['linear-regression','bayesian-regression'],'research_goal':'association','outcome_type':'continuous','design_type':'observational'})['automatic_method_ranking'] is False
assert eligibility_matrix({'method_refs':['bayesian-regression'],'outcome_type':'continuous','design_type':'observational','satisfied_requirements':[]})['eligibility'][0]['status']=='needs-information'
assert method_comparison({'methods':[{'method_ref':'a'},{'method_ref':'b'}]})['automatic_winner'] is None
assert method_decision_record({'selected_method_ref':'a'})['decision']['automatic_decision'] is False
assert core_object_plan({'project_ref':'p:1','candidate_method_refs':['a']})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: thirty-seven v0.132 Method Selection Intelligence routes loaded')
print('PASS: candidates, eligibility, comparison, decision, and Core fixtures')
print('PASS: researcher selection retained; no automatic ranking/selection/validity/truth/Core decisions')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['method-selection-intelligence-v01320.schema.json','method-selection-intelligence-policy-v01320.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.132 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-method-selection-intelligence-v01320.php >/dev/null
php tests/test-v01320.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.132.0' and m['featureVersion']=='0.132.0'
assert m['methodSelectionIntelligenceVersion']=='0.132.0'
assert m['v01320RequiredRouteCount']==37 and m['v01320MethodFamilyCount']==22 and m['v01320FigureFamilyCount']==12
assert re.search(r'^ \* Version: 0\.132\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.132.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.132.0 Method Selection Intelligence release gate"
