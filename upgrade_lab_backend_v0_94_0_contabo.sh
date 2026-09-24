#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.94.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v0940.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.94.0-$ts"
env_backup="/tmp/sc-lab-v0.94.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/whole_farm_ghg_v0940.py" ]] || { echo "ERROR: v0.94.0 Whole-Farm GHG module missing from package" >&2; exit 1; }

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
h6="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0600/health")"
h7="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0700/sampling/health")"
h8="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0800/change/health")"
h9="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0900/uncertainty/health")"
h10="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v1000/scenarios/health")"
h11="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/ghg/v1100/balance/health")"
python3 - "$health" "$h6" "$h7" "$h8" "$h9" "$h10" "$h11" <<'PYVERIFY'
import json,sys
health,h6,h7,h8,h9,h10,h11=(json.loads(x) for x in sys.argv[1:])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
for obj,version in zip((h6,h7,h8,h9,h10,h11),('0.6.0','0.7.0','0.8.0','0.9.0','0.10.0','0.11.0')):
    assert obj.get('ok') is True and obj.get('domain_version') == version, (version,obj)
assert h11.get('lab_release_version') == '0.94.0', h11
assert h11.get('guardrails',{}).get('whole_farm_balance_is_not_verification') is True, h11
assert h11.get('guardrails',{}).get('no_default_non_co2_gwp_factors') is True, h11
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 through v0.10.0 engines retained')
print('PASS: Lab v0.94.0 / Carbon & Nature v0.11.0 Whole-Farm GHG health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.whole_farm_ghg_v0940 import calculate_balance
r=calculate_balance({
'balance_id':'ghg-balance:reference','area_ha':1,
'gwp_set':{'name':'illustrative-fixture','source_ref':'source:test-gwp','horizon_years':100,'factors':{'CH4':10,'N2O':100}},
'entries':[
 {'entry_id':'co2','category':'energy','direction':'emission','gas':'CO2','mass_kg':1000,'source_refs':['evidence:co2']},
 {'entry_id':'ch4','category':'livestock','direction':'emission','gas':'CH4','mass_kg':10,'source_refs':['evidence:ch4']},
 {'entry_id':'n2o','category':'soil','direction':'emission','gas':'N2O','mass_kg':1,'source_refs':['evidence:n2o']},
],
'soc_stock_change':{'stock_change_Mg_C_ha':0.1,'area_ha':1,'basis':'measured-change','include_in_net':True,'source_refs':['model-run:soc-change']}
})
assert abs(r['gross_emissions_kg_CO2e']-1200)<1e-9, r
assert abs(r['gross_removals_kg_CO2e']-366.6666666666667)<1e-9, r
assert abs(r['net_balance_kg_CO2e']-833.3333333333334)<1e-9, r
assert r['interpretation']['whole_farm_balance_is_verification'] is False, r
print('PASS: in-container Whole-Farm GHG fixture = 1200 emissions - 366.667 removals = 833.333 kg CO2e net emissions')
print('PASS: illustrative GWP factors are explicit and sourced; no defaults inferred')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.94.0 / Carbon & Nature Intelligence v0.11.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Persistent Docker volume preserved: sc-lab-data"
