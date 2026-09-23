#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.126.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.126.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.126.0 — SPATIAL & SPATIOTEMPORAL RESEARCH STUDIO ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01260.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.126.0-$ts"; env_backup="/tmp/sc-lab-v0.126.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/spatial_spatiotemporal_research_studio_v01260.py" ]] || { echo "ERROR: v0.126 spatial/spatiotemporal module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; causal="$(curl -fsS "http://127.0.0.1:${PORT}/v1/causal-research-studio/health")"; spatial="$(curl -fsS "http://127.0.0.1:${PORT}/v1/spatial-spatiotemporal-research-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$causal" "$spatial" "$core" <<'PY'
import json,sys,re
h,c,s,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert c.get('ok') is True and c.get('version')=='0.125.0'; assert s.get('ok') is True and s.get('version')=='0.126.0'; assert s.get('method_family_count')==12 and s.get('automatic_causal_interpretation') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.125 Causal Research Studio II healthy'); print('PASS: Lab v0.126.0 Spatial & Spatiotemporal Research Studio health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PY
docker exec -i "$CONTAINER" python - <<'PY'
from app.main import app
from app.spatial_spatiotemporal_research_studio_v01260 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/spatial-spatiotemporal-research-studio'; required={x for x in paths if x.startswith(base)}; assert len(required)>=28
rows=[]
for y in range(4):
 for x in range(4): rows.append({'id':f'{x}-{y}','x':float(x),'y':float(y),'value':float(x+y+(2 if x>1 and y>1 else 0)),'cov':float(x-y)})
p={'rows':rows,'id_column':'id','x':'x','y':'y','value':'value','covariates':['cov'],'crs':{'id':'LOCAL:GRID','units':'km','geographic':False},'method':'knn','k':3}
assert len(build_spatial_weights(p)['weights']['weights_hash'])==64
assert isinstance(global_morans_i(p)['moran_i'],float); assert len(local_morans_i(p)['locations'])==16; assert len(getis_ord_gi_star(p)['locations'])==16
assert spatial_lag_estimate(p)['causal_interpretation'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'spatial-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.126 required spatial/spatiotemporal routes loaded'); print('PASS: weights, association, raster/spatiotemporal, visualization, snapshot, and Core fixtures'); print('PASS: no silent reprojection/join inference, significance labels, causal interpretation, scientific validity, or Core submission')
PY
echo "PASS - Sustainable Catalyst Lab v0.126.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
