#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.117.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.117.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.117.0 — ADVANCED 3D/4D SCIENTIFIC VISUALIZATION ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01170.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.117.0-$ts"; env_backup="/tmp/sc-lab-v0.117.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/advanced_3d_4d_scientific_visualization_v01170.py" ]] || { echo "ERROR: v0.117.0 module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-statistical-uncertainty-graphics/health")"; dash="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-dashboards/health")"; advanced="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-3d-4d-scientific-visualization/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$stats" "$dash" "$advanced" "$core" <<'PYVERIFY'
import json,sys,re
h,d,s,db,a,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert d.get('ok') is True and d.get('version')=='0.114.0',d
assert s.get('ok') is True and s.get('version')=='0.115.0',s
assert db.get('ok') is True and db.get('version')=='0.116.0',db
assert a.get('ok') is True and a.get('version')=='0.117.0',a
assert a.get('object_type_count')==12 and a.get('automatic_core_submission') is False,a
assert c.get('ok') is True,c
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert m,c; assert tuple(map(int,m.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.114 publication design system healthy')
print('PASS: retained v0.115 statistical graphics healthy')
print('PASS: retained v0.116 dashboards healthy')
print('PASS: Lab v0.117.0 advanced 3D/4D visualization health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.advanced_3d_4d_scientific_visualization_v01170 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/advanced-3d-4d-scientific-visualization'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/scene/normalize',f'{base}/surface/figure',f'{base}/mesh/figure',f'{base}/vector-field/figure',f'{base}/scalar-field/figure',f'{base}/volume/plan',f'{base}/trajectory/figure',f'{base}/time/frames',f'{base}/slice/plan',f'{base}/isosurface/plan',f'{base}/camera/state',f'{base}/uncertainty/geometry',f'{base}/renderer/plan',f'{base}/publication/export',f'{base}/dashboard/panel',f'{base}/core-visual/plan',f'{base}/accessibility/audit'}
assert not(required-paths), sorted(required-paths)
scene={'id':'deploy','title':'Deployment 4D scene','source_refs':['lab:dataset:d1'],'objects':[{'id':'m','type':'triangle-mesh','vertices':[[0,0,0],[1,0,0],[0,1,0]],'triangles':[[0,1,2]],'semantic_role':'observed','source_refs':['lab:dataset:d1']}],'time_axis':{'values':[0,1,2],'unit':'s'}}
n=normalize_scene(scene)['scene']; assert n['time_axis']['frame_count']==3
assert build_volume({'dimensions':[2,2,2],'data_ref':'lab:volume:v','transfer_function':{'opacity_stops':[[0,0],[1,1]]}})['automatic_transfer_function'] is False
assert build_slice_plan({'source_field_ref':'lab:volume:v','planes':[{'origin':[0,0,0],'normal':[0,0,1]}]})['automatic_slice_selection'] is False
assert build_isosurface_plan({'source_field_ref':'lab:volume:v','iso_values':[.5]})['automatic_threshold_selection'] is False
assert build_renderer_plan({'scene':scene,'renderer':'webgpu'})['automatic_renderer_execution'] is False
assert build_core_visual_plan({'scene':scene,'session_id':'deployment-session'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.117 required 3D/4D visualization routes loaded')
print('PASS: temporal scene, volume, slice, isosurface, renderer, and Core bridge fixtures')
print('PASS: no automatic geometry/topology/time/uncertainty/truth inference')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.117.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
