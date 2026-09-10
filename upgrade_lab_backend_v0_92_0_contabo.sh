#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.92.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v0920.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.92.0-$ts"
env_backup="/tmp/sc-lab-v0.92.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/soil_carbon_uncertainty_v0920.py" ]] || { echo "ERROR: v0.92.0 SOC uncertainty module missing from package" >&2; exit 1; }

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
python3 - "$health" "$soc" "$sampling" "$change" "$uncertainty" <<'PYVERIFY'
import json,sys
health,soc,sampling,change,uncertainty=(json.loads(x) for x in sys.argv[1:])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
assert soc.get('ok') is True and soc.get('domain_version') == '0.6.0', soc
assert sampling.get('ok') is True and sampling.get('domain_version') == '0.7.0', sampling
assert change.get('ok') is True and change.get('domain_version') == '0.8.0', change
assert uncertainty.get('ok') is True and uncertainty.get('domain_version') == '0.9.0', uncertainty
assert uncertainty.get('lab_release_version') == '0.92.0', uncertainty
assert uncertainty.get('replicate_uncertainty') is True
assert uncertainty.get('stratified_estimation') is True
assert uncertainty.get('geostatistical_interpolation') is False
assert uncertainty.get('guardrails',{}).get('credit_eligibility_not_determined') is True
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0/v0.7.0/v0.8.0 engines retained')
print('PASS: Lab v0.92.0 / Carbon & Nature v0.9.0 uncertainty health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.soil_carbon_uncertainty_v0920 import summarize_replicates, change_uncertainty
obs=[{'observation_id':f'o{i}','stock_Mg_C_ha':v} for i,v in enumerate([76,78,80,82],1)]
r=summarize_replicates({'observations':obs})
assert abs(r['statistics']['mean_Mg_C_ha']-79.0)<1e-12, r
assert abs(r['statistics']['sample_sd_Mg_C_ha']-2.581988897471611)<1e-9, r
pairs=[]
for i,(b,f) in enumerate([(78,86),(77,84),(80,89),(79,87)],1):
    pairs.append({'pair_id':f'p{i}','baseline':{'observation_id':f'b{i}','stock_Mg_C_ha':b},'followup':{'observation_id':f'f{i}','stock_Mg_C_ha':f}})
c=change_uncertainty({'mode':'paired','pairs':pairs,'elapsed_years':2})
assert abs(c['mean_stock_change_Mg_C_ha']-8.0)<1e-12, c
assert abs(c['annualized_mean_stock_change_Mg_C_ha_yr']-4.0)<1e-12, c
assert c['interpretation']['causal_attribution_established'] is False, c
print('PASS: in-container replicate mean = 79.0 Mg C/ha')
print('PASS: in-container paired mean change = +8.0 Mg C/ha; annualized = +4.0 Mg C/ha/yr')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.92.0 / Carbon & Nature Intelligence v0.9.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Persistent Docker volume preserved: sc-lab-data"
