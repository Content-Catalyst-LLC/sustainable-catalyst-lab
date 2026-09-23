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
 backend/tests/test_scientific_scene_linking_comparative_context_v01355.py
export PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.scientific_scene_linking_comparative_context_v01355 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/scientific-scene-linking-comparative-context')}
assert len(required)==48,len(required)
assert catalog()['link_type_count']==10 and catalog()['compare_mode_count']==6
assert catalog()['context_family_count']==12 and catalog()['pin_state_count']==3
assert catalog()['automatic_equivalence_inference'] is False and catalog()['automatic_join_inference'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: forty-eight v0.135.5 Scientific Scene Linking / Comparative Context routes loaded')
print('PASS: explicit links, pinning, comparison guards, context capsules, snapshots, handoffs, and Core fixtures')
print('PASS: no scientific-record mutation, equivalence/join/causal inference, evidence weighting, truth determination, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['interactive-scientific-scene-drilldown-v01354.schema.json','interactive-scientific-scene-drilldown-policy-v01354.json','scientific-scene-linking-comparative-context-v01355.schema.json','scientific-scene-linking-comparative-context-policy-v01355.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.135.4/v0.135.5 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-model-architecture-provenance-graphs-v01352.php >/dev/null
php -l includes/class-sc-lab-multi-view-scientific-analysis-canvas-v01353.php >/dev/null
php -l includes/class-sc-lab-interactive-scientific-scene-drilldown-v01354.php >/dev/null
php -l includes/class-sc-lab-scientific-scene-linking-comparative-context-v01355.php >/dev/null
php tests/test-v01352.php
php tests/test-v01353.php
php tests/test-v01354.php
php tests/test-v01355.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.135.5' and m['featureVersion']=='0.135.5'
assert m['scientificSceneLinkingComparativeContextVersion']=='0.135.5'
assert m['v01355RequiredRouteCount']==48 and m['v01355LinkTypeCount']==10 and m['v01355CompareModeCount']==6
assert m['v01355ContextFamilyCount']==12 and m['v01355PinStateCount']==3
assert re.search(r'^ \* Version: 0\.135\.5$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.135.5 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.135.5 Scientific Scene Linking, Comparative Inspection & Context Preservation release gate"
