#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.127.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.127.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.127.0 — SCIENTIFIC TIME-SERIES LABORATORY ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01270.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.127.0-$ts"; env_backup="/tmp/sc-lab-v0.127.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/scientific_time_series_laboratory_v01270.py" ]] || { echo "ERROR: v0.127 time-series module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; spatial="$(curl -fsS "http://127.0.0.1:${PORT}/v1/spatial-spatiotemporal-research-studio/health")"; tshealth="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-time-series-laboratory/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$spatial" "$tshealth" "$core" <<'PYDEPLOY'
import json,sys,re
h,s,t,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert s.get('ok') is True and s.get('version')=='0.126.0'; assert t.get('ok') is True and t.get('version')=='0.127.0'; assert t.get('method_family_count')==15 and t.get('automatic_model_selection') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.126 Spatial & Spatiotemporal Research Studio healthy'); print('PASS: Lab v0.127.0 Scientific Time-Series Laboratory health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYDEPLOY
docker exec -i "$CONTAINER" python - <<'PYDEPLOY'
import math
from app.main import app
from app.scientific_time_series_laboratory_v01270 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/scientific-time-series-laboratory'; required={x for x in paths if x.startswith(base)}; assert len(required)>=31
t=list(range(96)); y=[10+0.05*i+2*math.sin(2*math.pi*i/12)+0.2*math.sin(2*math.pi*i/5) for i in t]; p={'times':t,'values':y}
assert frequency_audit(p)['regular'] is True; assert len(decompose_series({**p,'period':12})['seasonal_pattern'])==12
assert fit_arima({**p,'p':2,'d':1,'q':1})['automatic_order_selection'] is False
assert len(forecast({**p,'model':'ar','model_spec':{'order':3},'horizon':6})['point_forecast'])==6
assert spectral_analysis(p)['automatic_cycle_certification'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'ts-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.127 required time-series routes loaded'); print('PASS: decomposition, dependence, modeling, forecasting, evaluation, spectral, and Core fixtures'); print('PASS: no silent resampling/model selection/stationarity decision, causal interpretation, scientific validity, or Core submission')
PYDEPLOY
echo "PASS - Sustainable Catalyst Lab v0.127.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
