#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.128.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.128.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.128.0 — EXPERIMENTAL DESIGN & POWER ANALYSIS ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01280.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.128.0-$ts"; env_backup="/tmp/sc-lab-v0.128.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/experimental_design_power_analysis_v01280.py" ]] || { echo "ERROR: v0.128 experimental-design module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-time-series-laboratory/health")"; exp="$(curl -fsS "http://127.0.0.1:${PORT}/v1/experimental-design-power-analysis/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$exp" "$core" <<'PYDEPLOY'
import json,sys,re
h,p,e,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert p.get('ok') is True and p.get('version')=='0.127.0'; assert e.get('ok') is True and e.get('version')=='0.128.0'; assert e.get('method_family_count')==15 and e.get('automatic_design_selection') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.127 Scientific Time-Series Laboratory healthy'); print('PASS: Lab v0.128.0 Experimental Design & Power Analysis health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYDEPLOY
docker exec -i "$CONTAINER" python - <<'PYDEPLOY'
from app.main import app
from app.experimental_design_power_analysis_v01280 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/experimental-design-power-analysis'; required={x for x in paths if x.startswith(base)}; assert len(required)>=30
assert two_sample_mean_power({'effect_size':.5,'target_power':.8})['achieved_power']>=.8
assert one_way_anova_power({'groups':4,'effect_size':.25,'target_power':.8})['achieved_power']>=.79
assert simulation_power({'simulations':1000,'seed':7,'effect_size':.4,'n':50})['power_is_estimated_not_guaranteed'] is True
assert sequential_design_plan({'looks':4})['automatic_stopping'] is False
assert randomization_schedule({'groups':['A','B'],'n':20,'seed':9})['automatic_enrollment_assignment'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'exp-deploy'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.128 required experimental-design routes loaded'); print('PASS: analytical power, ANOVA, simulation, sequential, randomization, and Core fixtures'); print('PASS: no automatic design/effect selection, power guarantee, significance claim, scientific validity, or Core submission')
PYDEPLOY
echo "PASS - Sustainable Catalyst Lab v0.128.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
