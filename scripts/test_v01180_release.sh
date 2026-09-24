#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"
echo "==> v0.118.0 narrative composer + visualization + Core integration regression suite"
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
 backend/tests/test_visual_research_narrative_figure_composer_v01180.py
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.visual_research_narrative_figure_composer_v01180 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/visual-research-narrative-figure-composer'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/narrative/normalize',f'{base}/section/normalize',f'{base}/figure/normalize',f'{base}/figure-plate/build',f'{base}/caption/build',f'{base}/annotations/build',f'{base}/research-links/build',f'{base}/references/build',f'{base}/provenance/trace',f'{base}/layout/plan',f'{base}/export/plan',f'{base}/publication/package',f'{base}/revision/snapshot',f'{base}/core-visual/plan',f'{base}/accessibility/audit'}
assert not(required-paths),sorted(required-paths)
fig={'id':'f1','figure_ref':'lab:figure:f1','figure_kind':'statistical-figure','title':'Observed response','caption':'Declared response and uncertainty.','alt_text':'A response curve with a shaded uncertainty band.','source_refs':['lab:dataset:d1'],'method_refs':['lab:method:m1'],'finding_refs':['lab:finding:f1']}
narr={'id':'deploy-narrative','title':'Deployment research narrative','format':'research-report','figures':[fig],'sections':[{'id':'results','type':'results','title':'Results','blocks':[{'type':'paragraph','text':'The declared result is shown in the figure.'},{'type':'figure','figure_refs':['lab:figure:f1']}]}],'source_refs':['lab:dataset:d1']}
n=normalize_narrative(narr); assert n['automatic_figure_mutation'] is False and len(n['narrative']['narrative_hash'])==64
assert build_figure_plate({'figures':[fig],'caption':'Declared plate caption.'})['automatic_figure_reordering'] is False
assert build_caption_package({'figure':fig})['automatic_caption_inference'] is False
assert build_annotation_layer({'figure_ref':'lab:figure:f1','annotations':[{'text':'Declared threshold.','evidence_refs':['lab:evidence:e1']}]})['automatic_evidence_weighting'] is False
assert trace_provenance({'narrative':narr})['provenance_trace']['source_refs']==['lab:dataset:d1']
assert build_export_plan({'narrative':narr,'formats':['pdf','html','json']})['automatic_file_write'] is False
assert build_publication_package({'narrative':narr})['automatic_publication'] is False
assert build_revision_snapshot({'narrative':narr})['automatic_persistence'] is False
core=build_core_visual_plan({'narrative':narr,'session_id':'deployment-session'}); assert core['automatic_core_submission'] is False and core['core_renders_narrative'] is False
assert accessibility_audit({'narrative':narr})['accessible'] is True
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: nineteen v0.118 visual research narrative routes loaded')
print('PASS: narrative, figure plate, caption, annotation, provenance, export, revision, accessibility, and Core fixtures')
print('PASS: conclusion/caption/relationship/evidence-weight/scientific-validity inference remains disabled')
PYTEST
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['visual-research-narrative-figure-composer-v01180.schema.json','visual-research-narrative-figure-composer-policy-v01180.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.118 contracts parse and mirror byte-for-byte')
PYTEST
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-visual-research-narrative-figure-composer-v01180.php >/dev/null
php tests/test-v01180.php
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.118.0' and m['featureVersion']=='0.118.0'
assert m['visualResearchNarrativeFigureComposerVersion']=='0.118.0'
assert m['v01180RequiredRouteCount']==19 and m['v01180SectionTypeCount']==11 and m['v01180FigureKindCount']==12
assert re.search(r'^ \* Version: 0\.118\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.118.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST
echo "PASS - Sustainable Catalyst Lab v0.118.0 Visual Research Narrative & Figure Composer release gate"
