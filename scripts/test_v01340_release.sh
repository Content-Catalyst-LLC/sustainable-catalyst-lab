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
 backend/tests/test_evidence_synthesis_intelligence_ii_v01340.py
export PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.evidence_synthesis_intelligence_ii_v01340 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/evidence-synthesis-intelligence-ii'; required={x for x in paths if x.startswith(base)}; assert len(required)>=44,len(required)
assert catalog()['synthesis_family_count']>=20 and catalog()['figure_family_count']>=16
assert contradiction_report({'evidence':[{'evidence_ref':'a','claim_refs':['c'],'state':'supports','effect_direction':'positive'},{'evidence_ref':'b','claim_refs':['c'],'state':'challenges','effect_direction':'negative'}]})['contradiction_count']==1
assert quantitative_synthesis({'effects':[{'effect':.1,'standard_error':.1},{'effect':.3,'standard_error':.1}]})['automatic_truth_inference'] is False
assert replication_synthesis({'evidence':[{'evidence_ref':'o','state':'supports'},{'evidence_ref':'r','replication_of_ref':'o','state':'challenges'}]})['automatic_replication_certification'] is False
assert adjudication_record({'claim_ref':'c','decision':'retain-disagreement'})['adjudication']['automatic_adjudication'] is False
assert core_object_plan({'project_ref':'p','claim_refs':['c'],'evidence_refs':['e']})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: forty-four v0.134 Evidence Synthesis Intelligence II routes loaded')
print('PASS: contradictions, meta-analysis, replication, adjudication, and Core fixtures')
print('PASS: no automatic study-quality scoring, evidence weighting, consensus certification, truth inference, scientific validity, or Core submission')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['evidence-synthesis-intelligence-ii-v01340.schema.json','evidence-synthesis-intelligence-ii-policy-v01340.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.134 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-evidence-synthesis-intelligence-ii-v01340.php >/dev/null
php tests/test-v01340.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.134.0' and m['featureVersion']=='0.134.0'
assert m['evidenceSynthesisIntelligenceIIVersion']=='0.134.0'
assert m['v01340RequiredRouteCount']==44 and m['v01340SynthesisFamilyCount']==20 and m['v01340FigureFamilyCount']==16
assert re.search(r'^ \* Version: 0\.134\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.134.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.134.0 Evidence Synthesis Intelligence II release gate"
