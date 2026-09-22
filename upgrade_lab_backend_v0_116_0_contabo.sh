#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.116.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.116.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.116.0 — INTERACTIVE SCIENTIFIC DASHBOARDS & SMALL MULTIPLES ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01160.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.116.0-$ts"; env_backup="/tmp/sc-lab-v0.116.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/interactive_scientific_dashboards_v01160.py" ]] || { echo "ERROR: v0.116.0 dashboard module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-statistical-uncertainty-graphics/health")"; dashboards="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-dashboards/health")"; production="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-production-runtime/health")"; core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$stats" "$dashboards" "$production" "$core_health" <<'PYVERIFY'
import json,sys,re
health,design,stats,dashboards,production,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert design.get('ok') is True and design.get('version')=='0.114.0',design
assert stats.get('ok') is True and stats.get('version')=='0.115.0',stats
assert dashboards.get('ok') is True and dashboards.get('version')=='0.116.0',dashboards
assert dashboards.get('interaction_channel_count')==7 and dashboards.get('boundaries',{}).get('automatic_cross_dataset_join') is False,dashboards
assert production.get('ok') is True and production.get('lab_release_version')=='0.113.0',production
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core; assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.114 publication-grade visualization design system healthy')
print('PASS: retained v0.115 advanced statistical & uncertainty graphics healthy')
print('PASS: Lab v0.116.0 interactive scientific dashboards health contract')
print('PASS: retained v0.113 production runtime healthy')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.interactive_scientific_dashboards_v01160 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/interactive-scientific-dashboards'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/dashboard/normalize',f'{base}/controls/normalize',f'{base}/links/normalize',f'{base}/small-multiples/compose',f'{base}/interactions/propagate',f'{base}/filters/state',f'{base}/scales/synchronize',f'{base}/state/snapshot',f'{base}/state/restore-plan',f'{base}/provenance/trace',f'{base}/accessibility/audit',f'{base}/export/plan',f'{base}/publication/build',f'{base}/core-visual/plan'}
assert not(required-paths),sorted(required-paths)
a={'id':'a','title':'Observed','renderer':'svg2d','figure_kind':'scatter','figure_ref':'lab:figure:a','source_refs':['lab:dataset:d1'],'spec':{'kind':'scatter','title':'Observed','axes':{'x':{'label':'X','unit':'unitless'},'y':{'label':'Y','unit':'unitless'}},'series':[{'id':'s1','points':[{'x':1,'y':2}]}],'publication':{'caption':'Observed.','source':'Fixture.'},'accessibility':{'alt_text':'Observed scatter plot.'}}}
b={'id':'b','title':'Model','renderer':'svg2d','figure_kind':'line','figure_ref':'lab:figure:b','source_refs':['lab:model:m1'],'spec':{'kind':'line','title':'Model','axes':{'x':{'label':'X','unit':'unitless'},'y':{'label':'Y','unit':'unitless'}},'series':[{'id':'s2','points':[{'x':1,'y':2}]}],'publication':{'caption':'Model.','source':'Fixture.'},'accessibility':{'alt_text':'Model line plot.'}}}
dash={'id':'deploy','title':'Deployment dashboard','panels':[a,b],'links':[{'source_panel_id':'a','target_panel_ids':['b'],'channel':'brush','key':'sample','direction':'bidirectional'}],'layout':{'type':'grid','columns':2}}
d=normalize_dashboard(dash)['dashboard']; assert len(d['panels'])==2
brush=propagate_interaction({'dashboard':dash,'event':{'source_panel_id':'a','channel':'brush','value':{'x':[0,1]}}}); assert brush['propagation_count']==1 and brush['automatic_cross_dataset_join'] is False
scales=synchronize_scales({'groups':[{'axis':'x','panel_ids':['a','b'],'declared_domains':[[0,1],[-1,2]]}]}); assert scales['groups'][0]['synchronized_domain']==[-1.0,2.0]
snap=snapshot_state({'dashboard':dash,'selections':{'a':[1]}}); assert restore_plan({'dashboard':dash,'state':snap['state']})['compatible'] is True
core=core_visual_plan({'dashboard':dash,'session_id':'deployment-session'}); assert core['binding_count']==2 and core['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: eighteen v0.116 interactive dashboard routes loaded')
print('PASS: dashboard, linked brush, declared scales, state continuity, and Core visual plan fixtures')
print('PASS: dashboard runtime does not infer joins, statistics, scientific validity, or truth')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.116.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
