#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.93.0.zip}"
CONTAINER="sc-lab"
PORT="8092"

[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" ]] || { echo "ERROR: Lab root not found: $BASE" >&2; exit 1; }
[[ -f "$BASE/.env.production" ]] || { echo "ERROR: $BASE/.env.production is required" >&2; exit 1; }
[[ -f "$BASE/compose.yml" ]] || { echo "ERROR: $BASE/compose.yml is required" >&2; exit 1; }
[[ -d "$LIVE_BACKEND" ]] || { echo "ERROR: live backend not found: $LIVE_BACKEND" >&2; exit 1; }
for cmd in docker unzip rsync curl python3; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

if ! docker volume inspect sc-lab-data >/dev/null 2>&1; then
  echo "WARNING: Docker volume sc-lab-data is not currently present; compose may create it on startup." >&2
fi

ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v0930.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.93.0-$ts"
env_backup="/tmp/sc-lab-v0.93.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/soil_carbon_scenarios_v0930.py" ]] || { echo "ERROR: v0.93.0 SOC scenario module missing from package" >&2; exit 1; }

rsync -a --delete --exclude='data/' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"
chmod 600 "$BASE/.env.production"

cd "$BASE"
docker compose config --quiet
docker compose build lab
docker compose up -d --force-recreate lab

healthy=0
for _ in $(seq 1 60); do
  state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"
  case "$state" in
    healthy) healthy=1; break ;;
    unhealthy|exited|dead) echo "ERROR: $CONTAINER entered state: $state" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1 ;;
  esac
  sleep 2
done
[[ "$healthy" == "1" ]] || { echo "ERROR: $CONTAINER did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
soc="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0600/health")"
sampling="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0700/sampling/health")"
change="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0800/change/health")"
uncertainty="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0900/uncertainty/health")"
scenarios="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v1000/scenarios/health")"
python3 - "$health" "$soc" "$sampling" "$change" "$uncertainty" "$scenarios" <<'PYVERIFY'
import json,sys
health,soc,sampling,change,uncertainty,scenarios=(json.loads(x) for x in sys.argv[1:])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
assert soc.get('ok') is True and soc.get('domain_version') == '0.6.0', soc
assert sampling.get('ok') is True and sampling.get('domain_version') == '0.7.0', sampling
assert change.get('ok') is True and change.get('domain_version') == '0.8.0', change
assert uncertainty.get('ok') is True and uncertainty.get('domain_version') == '0.9.0', uncertainty
assert scenarios.get('ok') is True and scenarios.get('domain_version') == '0.10.0', scenarios
assert scenarios.get('lab_release_version') == '0.93.0', scenarios
assert scenarios.get('scenario_projection') is True
assert scenarios.get('automatic_recommendation') is False
assert scenarios.get('whole_farm_ghg_balance') is False
assert scenarios.get('guardrails',{}).get('credit_eligibility_not_determined') is True
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0/v0.7.0/v0.8.0/v0.9.0 engines retained')
print('PASS: Lab v0.93.0 / Carbon & Nature v0.10.0 scenario health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.soil_carbon_scenarios_v0930 import project_scenario, compare_scenarios
r=project_scenario({'scenario_id':'reference','baseline_stock_Mg_C_ha':78,'horizon_years':10,'model_type':'constant-annual-change','annual_change_Mg_C_ha_yr':2})
assert abs(r['final_stock_Mg_C_ha']-98.0)<1e-12, r
assert abs(r['cumulative_stock_change_Mg_C_ha']-20.0)<1e-12, r
assert r['interpretation']['scenario_projection_is_forecast'] is False, r
c=compare_scenarios({'baseline_stock_Mg_C_ha':78,'scenarios':[{'scenario_id':'low','horizon_years':10,'model_type':'constant-annual-change','annual_change_Mg_C_ha_yr':1},{'scenario_id':'high','horizon_years':10,'model_type':'constant-annual-change','annual_change_Mg_C_ha_yr':3}]})
assert [x['final_stock_Mg_C_ha'] for x in c['comparison_table']]==[88.0,108.0], c
assert c['automatic_ranking_performed'] is False, c
print('PASS: in-container scenario baseline 78 + 2 Mg C/ha/yr x 10 years = 98 Mg C/ha')
print('PASS: scenario comparison does not rank or recommend alternatives')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.93.0 / Carbon & Nature Intelligence v0.10.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Persistent Docker volume preserved: sc-lab-data"
