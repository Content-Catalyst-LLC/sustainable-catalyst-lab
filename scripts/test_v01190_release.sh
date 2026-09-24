#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.119.0 figure intelligence + visualization + Core integration regression suite"
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
 backend/tests/test_scientific_figure_intelligence_automatic_layout_v01190.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.scientific_figure_intelligence_automatic_layout_v01190 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/scientific-figure-intelligence-automatic-layout'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/figure/normalize',f'{base}/figure/analyze',f'{base}/figure/intelligence',f'{base}/layout/plan',f'{base}/axes/plan',f'{base}/legend/plan',f'{base}/panels/plan',f'{base}/annotations/plan',f'{base}/collisions/audit',f'{base}/responsive/plan',f'{base}/print/plan',f'{base}/quality/audit',f'{base}/accessibility/audit',f'{base}/layout/explain',f'{base}/export/plan',f'{base}/snapshot/build',f'{base}/core-visual/plan'}
assert not(required-paths),sorted(required-paths)
fig={'id':'deploy-figure','figure_ref':'lab:figure:deploy','title':'Deployment figure','caption':'Declared caption.','alt_text':'Declared description.','publication_profile':'web-responsive','width_px':1200,'height_px':760,'axes':{'x':{'title':'Time','labels':[str(x) for x in range(20)],'domain':[0,19],'scale':'linear'},'y':{'title':'Response','labels':['0','20','40','60','80','100'],'domain':[0,100],'scale':'linear'}},'legend':{'entries':[{'label':'Observed'},{'label':'Model'}]},'panels':[{'id':'a'},{'id':'b'},{'id':'c'},{'id':'d'}],'annotations':[{'id':'a1','x':0.5,'y':0.4},{'id':'a2','x':0.51,'y':0.41}]}
f=normalize_figure_context(fig); assert f['scientific_encoding_locked'] is True and len(f['context_hash'])==64
a=analyze_figure(fig); assert a['automatic_data_inspection'] is False
axes=plan_axes(fig); assert axes['automatic_domain_changes'] is False and axes['automatic_scale_changes'] is False
legend=plan_legend(fig); assert legend['automatic_series_reordering'] is False and legend['automatic_legend_entry_dropping'] is False
panels=plan_panels(fig); assert panels['automatic_panel_reordering'] is False and panels['panels']['count']==4
anns=plan_annotations(fig); assert len(anns['annotations'])==2 and anns['automatic_annotation_deletion'] is False
layout=plan_layout(fig); assert layout['layout']['scientific_encoding_locked'] is True and layout['automatic_scientific_encoding_changes'] is False
assert build_export_plan({**fig,'formats':['svg','pdf','json']})['automatic_file_write'] is False
assert build_snapshot(fig)['automatic_persistence'] is False
core=build_core_visual_plan({**fig,'session_id':'deployment-session'}); assert core['automatic_core_submission'] is False and core['core_changes_scientific_encoding'] is False
assert quality_audit(fig)['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: twenty-one v0.119 scientific figure intelligence routes loaded')
print('PASS: axes, legend, panels, annotations, responsive, print, quality, snapshot, export, and Core fixtures')
print('PASS: scientific encodings/domains/scales/evidence semantics remain explicit and locked')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['scientific-figure-intelligence-automatic-layout-v01190.schema.json','scientific-figure-intelligence-automatic-layout-policy-v01190.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.119 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-scientific-figure-intelligence-automatic-layout-v01190.php >/dev/null
php tests/test-v01190.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.119.0' and m['featureVersion']=='0.119.0'
assert m['scientificFigureIntelligenceAutomaticLayoutVersion']=='0.119.0'
assert m['v01190RequiredRouteCount']==21 and m['v01190LayoutModeCount']==7 and m['v01190LegendPositionCount']==6 and m['v01190LabelStrategyCount']==7
assert re.search(r'^ \* Version: 0\.119\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.119.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.119.0 Scientific Figure Intelligence & Automatic Layout release gate"
