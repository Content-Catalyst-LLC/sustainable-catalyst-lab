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
 backend/tests/test_reproducible_visual_analysis_sessions_v01356.py \
 backend/tests/test_visual_research_narrative_findings_v01357.py \
 backend/tests/test_research_review_critique_revision_v01358.py \
 backend/tests/test_graph_studio_canonical_runtime_v013581.py
export PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.research_review_critique_revision_v01358 import health as review_health
from app.graph_studio_canonical_runtime_v013581 import health,catalog,boundaries_report
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/graph-studio-canonical-runtime')}; assert len(required)==16,len(required)
assert review_health()['version']=='0.135.8' and review_health()['api_route_count']==60
h=health(); assert h['version']=='0.135.8.1' and h['api_route_count']==16 and h['canonical_view_count']==8 and h['isolated_capability_panel_count']==13
c=catalog(); assert c['view_count']==8 and c['capability_panel_count']==13
b=boundaries_report(); assert b['presentation_state_is_scientific_record'] is False and b['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: sixteen v0.135.8.1 Graph Studio canonical runtime routes loaded')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-research-review-critique-revision-v01358.php >/dev/null
php -l includes/class-sc-lab-graph-studio-canonical-runtime-v013581.php >/dev/null
php -l includes/class-sc-lab-runtime-repair-v02631.php >/dev/null
node --check assets/js/modules/graph-studio-canonical-runtime-v013581.js >/dev/null
php tests/test-v01352.php; php tests/test-v01353.php; php tests/test-v01354.php; php tests/test-v01355.php; php tests/test-v01356.php; php tests/test-v01357.php; php tests/test-v01358.php; php tests/test-v013581.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.135.8.1' and m['featureVersion']=='0.135.8.1' and m['researchReviewCritiqueRevisionVersion']=='0.135.8' and m['graphStudioCanonicalRuntimeVersion']=='0.135.8.1'
assert m['v01358RequiredRouteCount']==60 and m['v013581RequiredRouteCount']==16 and m['v013581CanonicalViewCount']==8 and m['v013581IsolatedCapabilityPanelCount']==13
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.135.8.1 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.135.8.1 Graph Studio Canonical Runtime & Interface Recovery release gate"
