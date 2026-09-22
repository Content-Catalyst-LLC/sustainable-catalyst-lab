#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"

echo "==> v0.116.0 dashboards + statistical visualization + Core integration regression suite"
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
 backend/tests/test_interactive_scientific_dashboards_v01160.py

echo "==> v0.116.0 required FastAPI routes + behavior fixtures"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.interactive_scientific_dashboards_v01160 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/interactive-scientific-dashboards'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/dashboard/normalize',f'{base}/controls/normalize',f'{base}/links/normalize',f'{base}/small-multiples/compose',f'{base}/interactions/propagate',f'{base}/filters/state',f'{base}/scales/synchronize',f'{base}/state/snapshot',f'{base}/state/restore-plan',f'{base}/provenance/trace',f'{base}/accessibility/audit',f'{base}/export/plan',f'{base}/publication/build',f'{base}/core-visual/plan'}
assert not(required-paths),sorted(required-paths)
panel_a={'id':'observed','title':'Observed','renderer':'svg2d','figure_kind':'scatter','figure_ref':'lab:figure:observed','source_refs':['lab:dataset:d1'],'spec':{'kind':'scatter','title':'Observed','axes':{'x':{'label':'X','unit':'unitless'},'y':{'label':'Y','unit':'unitless'}},'series':[{'id':'s1','points':[{'x':1,'y':2}]}],'publication':{'caption':'Observed.','source':'Deployment fixture.'},'accessibility':{'alt_text':'Observed scatter plot.'}}}
panel_b={'id':'model','title':'Model','renderer':'svg2d','figure_kind':'line','figure_ref':'lab:figure:model','source_refs':['lab:model:m1'],'spec':{'kind':'line','title':'Model','axes':{'x':{'label':'X','unit':'unitless'},'y':{'label':'Y','unit':'unitless'}},'series':[{'id':'s2','points':[{'x':1,'y':2}]}],'publication':{'caption':'Model.','source':'Deployment fixture.'},'accessibility':{'alt_text':'Model line plot.'}}}
dash={'id':'deployment-dashboard','title':'Deployment dashboard','panels':[panel_a,panel_b],'controls':[{'type':'category-filter','key':'group','target_panel_ids':['observed','model']}],'links':[{'source_panel_id':'observed','target_panel_ids':['model'],'channel':'selection','key':'sample','direction':'bidirectional'}],'layout':{'type':'grid','columns':2}}
d=normalize_dashboard(dash)['dashboard']; assert len(d['panels'])==2 and d['layout']['responsive']['mobile_columns']==1
interaction=propagate_interaction({'dashboard':dash,'event':{'source_panel_id':'observed','channel':'selection','value':[1,2]}}); assert interaction['propagation_count']==1 and interaction['automatic_data_mutation'] is False
scales=synchronize_scales({'groups':[{'id':'x','axis':'x','panel_ids':['observed','model'],'declared_domains':[[0,10],[-2,8]]}]}); assert scales['groups'][0]['synchronized_domain']==[-2.0,10.0] and scales['automatic_domain_inference'] is False
snap=snapshot_state({'dashboard':dash,'selections':{'observed':[1,2]}}); restore=restore_plan({'dashboard':dash,'state':snap['state']}); assert restore['compatible'] is True and restore['automatic_restore'] is False
pub=build_publication_dashboard({'dashboard':dash,'formats':['svg','pdf','json']}); assert pub['publication_ready'] is True and pub['scientific_validity_certified'] is False
core=core_visual_plan({'dashboard':dash,'session_id':'deployment-session'}); assert core['binding_count']==2 and core['automatic_core_submission'] is False
m=manifest(); assert m['interaction_channel_count']==7 and m['boundaries']['automatic_truth_determination'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: eighteen v0.116 interactive scientific dashboard routes loaded')
print('PASS: linked interaction, declared scale synchronization, snapshot/restore, publication, and Core visual fixtures')
print('PASS: dashboard composition remains separate from joins, statistical inference, scientific validity, and truth judgments')
PYTEST

echo "==> v0.116.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['interactive-scientific-dashboards-v01160.schema.json','interactive-scientific-dashboards-policy-v01160.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.116 dashboard contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.116.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-interactive-scientific-dashboards-v01160.php >/dev/null
php tests/test-v01160.php

echo "==> v0.116.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.116.0' and m['featureVersion']=='0.116.0'
assert m['interactiveScientificDashboardsVersion']=='0.116.0'
assert m['v01160RequiredRouteCount']==18 and m['v01160InteractionChannelCount']==7 and m['v01160PanelLimit']==48
assert re.search(r'^ \* Version: 0\.116\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.116.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.116.0 Interactive Scientific Dashboards & Small Multiples release gate"
