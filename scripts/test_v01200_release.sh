#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.120.0 EDA + visualization + Core integration regression suite"
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
 backend/tests/test_exploratory_data_analysis_studio_v01200.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.exploratory_data_analysis_studio_v01200 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/exploratory-data-analysis-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/dataset/normalize',f'{base}/profile/build',f'{base}/missingness/analyze',f'{base}/distributions/analyze',f'{base}/correlations/analyze',f'{base}/groups/compare',f'{base}/outliers/analyze',f'{base}/relationship/analyze',f'{base}/transformations/plan',f'{base}/transformations/preview',f'{base}/dimensions/pca',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/export/plan',f'{base}/core-object/plan'}
assert not(required-paths),sorted(required-paths)
rows=[{'group':'A','x':1.0,'y':2.0,'z':10.0},{'group':'A','x':2.0,'y':4.1,'z':11.0},{'group':'A','x':3.0,'y':6.2,'z':None},{'group':'B','x':4.0,'y':8.0,'z':13.0},{'group':'B','x':5.0,'y':10.2,'z':14.0},{'group':'B','x':40.0,'y':12.0,'z':15.0}]
base_payload={'id':'deploy-eda','rows':rows}
d=normalize_dataset(base_payload); assert d['source_rows_immutable'] is True and len(d['dataset_hash'])==64
p=profile_dataset(base_payload); assert p['exploratory_not_confirmatory'] is True
m=analyze_missingness(base_payload); assert m['mcar_mar_mnar_not_determined'] is True
c=analyze_correlations({**base_payload,'columns':['x','y','z'],'method':'spearman'}); assert c['p_values_computed'] is False and c['causality_inferred'] is False
g=compare_groups({**base_payload,'group_by':'group','value_columns':['x','y']}); assert g['hypothesis_test_performed'] is False
o=analyze_outliers({**base_payload,'columns':['x'],'method':'iqr'}); assert o['rows_removed'] is False
r=analyze_relationship({**base_payload,'x':'x','y':'y'}); assert r['causality_inferred'] is False
plan=plan_transformations({**base_payload,'operations':[{'column':'x','operation':'standardize'}]}); assert plan['automatic_application'] is False
preview=preview_transformations({**base_payload,'operations':plan['operations']}); assert preview['source_dataset_mutated'] is False
pca=analyze_pca({**base_payload,'columns':['x','y','z'],'components':2}); assert pca['cluster_structure_inferred'] is False
vis=build_visualization_plan(base_payload); assert vis['automatic_render'] is False
snap=build_snapshot(base_payload); assert snap['automatic_persistence'] is False
core=build_core_object_plan({**base_payload,'session_id':'deployment-session','analysis_id':'eda-deploy'}); assert core['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty v0.120 Exploratory Data Analysis Studio routes loaded')
print('PASS: profile, missingness, distributions, correlations, groups, outliers, transformations, PCA, visualization, snapshot, export, and Core fixtures')
print('PASS: EDA remains exploratory/not-confirmatory and source rows remain immutable')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['exploratory-data-analysis-studio-v01200.schema.json','exploratory-data-analysis-studio-policy-v01200.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.120 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-exploratory-data-analysis-studio-v01200.php >/dev/null
php tests/test-v01200.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.120.0' and m['featureVersion']=='0.120.0'
assert m['exploratoryDataAnalysisStudioVersion']=='0.120.0'
assert m['v01200RequiredRouteCount']==20 and m['v01200AnalysisFamilyCount']==9 and m['v01200TransformationCount']==6
assert re.search(r'^ \* Version: 0\.120\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.120.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.120.0 Exploratory Data Analysis Studio release gate"
