#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.91.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v0910.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.91.0-$ts"
env_backup="/tmp/sc-lab-v0.91.0.env.production.$ts"

cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/soil_carbon_change_v0910.py" ]] || { echo "ERROR: v0.91.0 SOC change module missing from package" >&2; exit 1; }

# Replace source only. Preserve secrets, compose topology, and Docker-volume data.
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
    unhealthy|exited|dead)
      echo "ERROR: $CONTAINER entered state: $state" >&2
      docker logs --tail=200 "$CONTAINER" >&2 || true
      exit 1 ;;
  esac
  sleep 2
done
[[ "$healthy" == "1" ]] || { echo "ERROR: $CONTAINER did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
soc="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0600/health")"
sampling="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0700/sampling/health")"
change="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0800/change/health")"
python3 - "$health" "$soc" "$sampling" "$change" <<'PYVERIFY'
import json,sys
health,soc,sampling,change=(json.loads(x) for x in sys.argv[1:])
assert health.get('ok') is True, health
assert health.get('version') == '1.0.0', health.get('version')
assert soc.get('ok') is True and soc.get('domain_version') == '0.6.0', soc
assert sampling.get('ok') is True and sampling.get('domain_version') == '0.7.0', sampling
assert change.get('ok') is True, change
assert change.get('domain_version') == '0.8.0', change
assert change.get('lab_release_version') == '0.91.0', change
assert change.get('matched_fixed_depth_comparison') is True, change
assert change.get('annualized_stock_change') is True, change
assert change.get('attributed_sequestration_claim') is False, change
assert change.get('guardrails',{}).get('uncertainty_not_inferred') is True, change
assert change.get('guardrails',{}).get('credit_eligibility_not_determined') is True, change
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 SOC stock engine retained')
print('PASS: Carbon & Nature v0.7.0 SOC sampling engine retained')
print('PASS: Lab v0.91.0 / Carbon & Nature v0.8.0 SOC change health contract')
PYVERIFY

# Execute a deterministic fixture inside the deployed container. -i is required
# so the Python program is actually delivered over stdin.
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.soil_carbon_change_v0910 import compare_profiles
base={'layers':[{'layer_id':'baseline','top_depth':0,'bottom_depth':30,'soc_value':2,'soc_unit':'percent','bulk_density_value':1.3,'bulk_density_unit':'g/cm3'}]}
follow={'layers':[{'layer_id':'followup','top_depth':0,'bottom_depth':30,'soc_value':2.2,'soc_unit':'percent','bulk_density_value':1.3,'bulk_density_unit':'g/cm3'}]}
r=compare_profiles({'comparison_id':'comparison:deploy-validation','spatial_unit_id':'parcel:deploy-validation','baseline_at':'2025-01-01','followup_at':'2026-01-01','baseline_profile':base,'followup_profile':follow})
assert abs(r['baseline']['soc_stock_Mg_C_ha']-78.0)<1e-12, r
assert abs(r['followup']['soc_stock_Mg_C_ha']-85.8)<1e-12, r
assert abs(r['stock_change_Mg_C_ha']-7.8)<1e-12, r
assert r['interpretation']['intervention_attribution_established'] is False, r
print('PASS: in-container baseline SOC stock = 78.0 Mg C/ha')
print('PASS: in-container follow-up SOC stock = 85.8 Mg C/ha')
print('PASS: in-container matched SOC stock change = +7.8 Mg C/ha')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.91.0 / Carbon & Nature Intelligence v0.8.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Persistent Docker volume preserved: sc-lab-data"
