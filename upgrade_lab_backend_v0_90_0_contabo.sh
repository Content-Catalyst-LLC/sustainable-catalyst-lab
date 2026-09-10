#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.90.0.zip}"
CONTAINER="sc-lab"
PORT="8092"

[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" ]] || { echo "ERROR: Lab root not found: $BASE" >&2; exit 1; }
[[ -f "$BASE/.env.production" ]] || { echo "ERROR: $BASE/.env.production is required" >&2; exit 1; }
[[ -f "$BASE/compose.yml" ]] || { echo "ERROR: $BASE/compose.yml is required" >&2; exit 1; }
[[ -d "$LIVE_BACKEND" ]] || { echo "ERROR: live backend not found: $LIVE_BACKEND" >&2; exit 1; }
command -v docker >/dev/null || { echo "ERROR: docker is required" >&2; exit 1; }
command -v unzip >/dev/null || { echo "ERROR: unzip is required" >&2; exit 1; }
command -v rsync >/dev/null || { echo "ERROR: rsync is required" >&2; exit 1; }
command -v curl >/dev/null || { echo "ERROR: curl is required" >&2; exit 1; }

# Never remove the named sc-lab-data volume. Runtime state remains outside the
# source tree at /app/data; backend/data is additionally excluded from rsync.
if ! docker volume inspect sc-lab-data >/dev/null 2>&1; then
  echo "WARNING: Docker volume sc-lab-data is not currently present; compose may create it on startup." >&2
fi

ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v0900.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.90.0-$ts"
env_backup="/tmp/sc-lab-v0.90.0.env.production.$ts"

cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/soil_carbon_sampling_v0900.py" ]] || { echo "ERROR: v0.90.0 SOC sampling module missing from package" >&2; exit 1; }

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
soc_v0600="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0600/health")"
sampling="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/soc/v0700/sampling/health")"
python3 - "$health" "$soc_v0600" "$sampling" <<'PYVERIFY'
import json,sys
health=json.loads(sys.argv[1]); soc=json.loads(sys.argv[2]); sampling=json.loads(sys.argv[3])
assert health.get('ok') is True, health
assert health.get('version') == '1.0.0', health.get('version')
assert soc.get('ok') is True, soc
assert soc.get('domain_version') == '0.6.0', soc
assert soc.get('lab_release_version') in {'0.89.0','0.90.0'}, soc
assert sampling.get('ok') is True, sampling
assert sampling.get('domain_version') == '0.7.0', sampling
assert sampling.get('lab_release_version') == '0.90.0', sampling
assert sampling.get('bulk_density_core_calculation') is True, sampling
assert sampling.get('soc_v0600_profile_handoff') is True, sampling
assert sampling.get('guardrails',{}).get('sequestration_rate_not_inferred') is True, sampling
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 fixed-depth SOC engine retained')
print('PASS: Lab v0.90.0 / Carbon & Nature v0.7.0 sampling health contract')
PYVERIFY

# Validate scientific fixtures inside the deployed container without exposing
# production API keys or signing secrets.
docker exec "$CONTAINER" python - <<'PYFIXTURE'
from app.soil_carbon_sampling_v0900 import calculate_bulk_density, build_profile_handoff
bd=calculate_bulk_density({'dry_mass_g':130,'core_volume_cm3':100,'mass_basis':'whole-dry-soil'})
assert abs(bd['bulk_density_g_cm3'] - 1.3) < 1e-12, bd
handoff=build_profile_handoff({
    'batch_id':'batch:deploy-validation',
    'profile_id':'profile:deploy-validation',
    'samples':[{
        'sample_id':'sample:deploy-validation:0001',
        'profile_id':'profile:deploy-validation',
        'top_depth':0,
        'bottom_depth':30,
        'soc_value':2,
        'soc_unit':'percent',
        'dry_mass_g':130,
        'core_volume_cm3':100,
        'coarse_fragments_percent':0,
    }],
})
assert abs(handoff['compatibility_validation']['calculated_stock_Mg_C_ha'] - 78.0) < 1e-12, handoff
print('PASS: in-container bulk-density fixture = 1.300 g/cm3')
print('PASS: in-container v0.6 profile handoff fixture = 78.0 Mg C/ha')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.90.0 / Carbon & Nature Intelligence v0.7.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Persistent Docker volume preserved: sc-lab-data"
