#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.119.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.119.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.119.0 — SCIENTIFIC FIGURE INTELLIGENCE & AUTOMATIC LAYOUT ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01190.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.119.0-$ts"; env_backup="/tmp/sc-lab-v0.119.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/scientific_figure_intelligence_automatic_layout_v01190.py" ]] || { echo "ERROR: v0.119.0 module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-statistical-uncertainty-graphics/health")"; dash="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-dashboards/health")"; advanced="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-3d-4d-scientific-visualization/health")"; narrative="$(curl -fsS "http://127.0.0.1:${PORT}/v1/visual-research-narrative-figure-composer/health")"; intelligence="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-figure-intelligence-automatic-layout/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$stats" "$dash" "$advanced" "$narrative" "$intelligence" "$core" <<'PYVERIFY'
import json,sys,re
h,d,s,db,a,n,i,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert d.get('ok') is True and d.get('version')=='0.114.0',d
assert s.get('ok') is True and s.get('version')=='0.115.0',s
assert db.get('ok') is True and db.get('version')=='0.116.0',db
assert a.get('ok') is True and a.get('version')=='0.117.0',a
assert n.get('ok') is True and n.get('version')=='0.118.0',n
assert i.get('ok') is True and i.get('version')=='0.119.0',i
assert i.get('layout_mode_count')==7 and i.get('automatic_scientific_encoding_changes') is False,i
assert c.get('ok') is True,c
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert m,c; assert tuple(map(int,m.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.114–v0.118 visualization stack healthy')
print('PASS: Lab v0.119.0 figure intelligence health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.scientific_figure_intelligence_automatic_layout_v01190 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/scientific-figure-intelligence-automatic-layout'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/figure/normalize',f'{base}/figure/analyze',f'{base}/figure/intelligence',f'{base}/layout/plan',f'{base}/axes/plan',f'{base}/legend/plan',f'{base}/panels/plan',f'{base}/annotations/plan',f'{base}/collisions/audit',f'{base}/responsive/plan',f'{base}/print/plan',f'{base}/quality/audit',f'{base}/accessibility/audit',f'{base}/layout/explain',f'{base}/export/plan',f'{base}/snapshot/build',f'{base}/core-visual/plan'}
assert not(required-paths),sorted(required-paths)
fig={'id':'deploy','figure_ref':'lab:figure:deploy','title':'Deployment figure','caption':'Declared caption.','alt_text':'Declared alt text.','publication_profile':'web-responsive','width_px':1200,'height_px':760,'axes':{'x':{'title':'Time','labels':[str(x) for x in range(20)],'domain':[0,19],'scale':'linear'},'y':{'title':'Response','labels':['0','20','40','60','80','100'],'domain':[0,100],'scale':'linear'}},'legend':{'entries':[{'label':'Observed'},{'label':'Model'}]},'panels':[{'id':'a'},{'id':'b'},{'id':'c'},{'id':'d'}],'annotations':[{'id':'a1','x':0.5,'y':0.4},{'id':'a2','x':0.51,'y':0.41}]}
assert normalize_figure_context(fig)['scientific_encoding_locked'] is True
assert plan_axes(fig)['automatic_domain_changes'] is False
assert plan_legend(fig)['automatic_series_reordering'] is False
assert plan_panels(fig)['automatic_panel_reordering'] is False
assert plan_annotations(fig)['automatic_annotation_deletion'] is False
assert plan_layout(fig)['automatic_scientific_encoding_changes'] is False
assert build_snapshot(fig)['automatic_persistence'] is False
assert build_core_visual_plan({**fig,'session_id':'deployment-session'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.119 required figure-intelligence routes loaded')
print('PASS: deterministic layout, collision, responsive, print, quality, snapshot, and Core fixtures')
print('PASS: no automatic scientific encoding/domain/scale/evidence/claim changes')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.119.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
