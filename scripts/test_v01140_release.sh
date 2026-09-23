#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"

echo "==> v0.114.0 visualization + Core integration regression suite"
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
 backend/tests/test_scientific_visualization_design_system_v01140.py

echo "==> v0.114.0 required FastAPI routes + behavior fixtures"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.scientific_visualization_design_system_v01140 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/scientific-visualization-design-system'
required={f'{base}/health',f'{base}/manifest',f'{base}/tokens',f'{base}/catalog',f'{base}/figures/normalize',f'{base}/figures/profile',f'{base}/annotations/plan',f'{base}/uncertainty/style',f'{base}/small-multiples/compose',f'{base}/accessibility/build',f'{base}/renderers/plan',f'{base}/exports/plan',f'{base}/audit',f'{base}/publication-figure/build',f'{base}/core-visual/plan'}
assert not(required-paths),sorted(required-paths)
spec={'kind':'confidence-band','title':'Publication fixture','axes':{'x':{'label':'Time','unit':'day'},'y':{'label':'Response','unit':'mg/L'}},'series':[{'id':'obs','semantic_role':'observed','points':[{'x':0,'y':1,'yLow':.8,'yHigh':1.2},{'x':1,'y':2,'yLow':1.7,'yHigh':2.3}]},{'id':'model','semantic_role':'model','points':[{'x':0,'y':1.1},{'x':1,'y':1.9}]}],'publication':{'caption':'Fixture caption.','source':'Fixture source.','method':'Fixture method.'},'provenance':{'dataset':'fixture'}}
result=build_publication_figure({'spec':spec,'profile':'journal-double','alt_text':'Confidence-band figure comparing observations and model.','annotations':[{'type':'finding','text':'Peak response','x':1,'y':2,'evidence_ref':'e:1'}],'uncertainty_layers':[{'kind':'confidence','level':.95,'label':'95% CI'}]})
fig=result['figure']; assert fig['profile']=='journal-double' and fig['rendering']['vector_first'] is True
assert [x['role'] for x in fig['semantic_series']]==['observed','model']
assert result['audit']['publication_ready'] is True and result['audit']['scientific_validity_certified'] is False
assert result['export_plan']['vector_formats']==['svg','pdf'] and result['export_plan']['automatic_file_write'] is False
assert fig['accessibility']['color_only_encoding'] is False and fig['annotations'][0]['evidence_ref']=='e:1'
sm=compose_small_multiples({'panels':[{'id':'a'},{'id':'b'},{'id':'c'},{'id':'d'}],'columns':2}); assert sm['layout']['rows']==2 and sm['responsive']['mobile_columns']==1
rp=renderer_plan({'figure':fig,'publication':True}); assert rp['preferred_renderer']=='svg2d' and rp['vector_first'] is True
m=manifest(); assert m['publication_grade_rendering'] is True and m['boundaries']['automatic_scientific_validity_certification'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: fifteen v0.114 scientific-visualization design-system routes loaded')
print('PASS: publication profiles, semantic roles, annotations, uncertainty, small multiples, accessibility, renderer planning, export planning, and audit behavior')
print('PASS: publication readiness remains separate from scientific validity/truth certification')
PYTEST

echo "==> v0.114.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['scientific-visualization-design-system-v01140.schema.json','scientific-visualization-design-system-policy-v01140.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.114 design-system contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.114.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-scientific-visualization-design-system-v01140.php >/dev/null
php tests/test-v01140.php

echo "==> v0.114.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.114.0' and m['featureVersion']=='0.114.0'
assert m['scientificVisualizationDesignSystemVersion']=='0.114.0'
assert m['v01140RequiredRouteCount']==15 and m['v01140PublicationProfileCount']==6 and m['v01140SemanticRoleCount']==10
assert re.search(r'^ \* Version: 0\.114\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.114.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.114.0 Scientific Visualization Design System & Publication-Grade Rendering release gate"
