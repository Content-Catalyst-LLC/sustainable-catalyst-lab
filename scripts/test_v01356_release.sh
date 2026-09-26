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
 backend/tests/test_competing_model_hypothesis_analysis_v01350.py \
 backend/tests/test_scientific_visualization_experience_v01351.py \
 backend/tests/test_model_architecture_computational_provenance_graphs_v01352.py \
 backend/tests/test_multi_view_scientific_analysis_canvas_v01353.py \
 backend/tests/test_interactive_scientific_scene_drilldown_v01354.py \
 backend/tests/test_scientific_scene_linking_comparative_context_v01355.py \
 backend/tests/test_reproducible_visual_analysis_sessions_v01356.py
export PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.reproducible_visual_analysis_sessions_v01356 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/reproducible-visual-analysis-sessions')}; assert len(required)==52,len(required)
assert catalog()['event_type_count']==12 and catalog()['session_state_count']==4 and catalog()['checkpoint_kind_count']==5 and catalog()['replay_mode_count']==3
assert interpretation_boundaries_report()['interaction_history_is_scientific_evidence'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: fifty-two v0.135.6 Reproducible Visual Analysis Session routes loaded')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-reproducible-visual-analysis-sessions-v01356.php >/dev/null
php tests/test-v01352.php; php tests/test-v01353.php; php tests/test-v01354.php; php tests/test-v01355.php; php tests/test-v01356.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.135.6' and m['featureVersion']=='0.135.6' and m['reproducibleVisualAnalysisSessionsVersion']=='0.135.6'
assert m['v01356RequiredRouteCount']==52 and m['v01356EventTypeCount']==12 and m['v01356SessionStateCount']==4 and m['v01356CheckpointKindCount']==5 and m['v01356ReplayModeCount']==3
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.135.6 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.135.6 Reproducible Visual Analysis Sessions & Interaction Lineage release gate"
