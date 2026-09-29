#!/usr/bin/env bash
set -euo pipefail
BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.89.0.zip}"
CONTAINER="sc-lab"

[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" ]] || { echo "ERROR: Lab root not found: $BASE" >&2; exit 1; }
[[ -f "$BASE/.env.production" ]] || { echo "ERROR: $BASE/.env.production is required" >&2; exit 1; }
[[ -f "$BASE/compose.yml" ]] || { echo "ERROR: $BASE/compose.yml is required" >&2; exit 1; }
[[ -d "$LIVE_BACKEND" ]] || { echo "ERROR: live backend not found: $LIVE_BACKEND" >&2; exit 1; }

ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v0890.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.89.0-$ts"
env_backup="/tmp/sc-lab-v0.89.0.env.production.$ts"

cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }

# Preserve Docker-volume runtime state and all production secrets. Only source is replaced.
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

health="$(curl -fsS http://127.0.0.1:8092/health)"
soc="$(curl -fsS http://127.0.0.1:8092/v1/carbon-nature/soc/v0600/health)"
python3 - "$health" "$soc" <<'PYVERIFY'
import json,sys
health=json.loads(sys.argv[1]); soc=json.loads(sys.argv[2])
assert health.get('ok') is True
assert health.get('version') == '1.0.0', health.get('version')
assert soc.get('ok') is True
assert soc.get('domain_version') == '0.6.0', soc
assert soc.get('lab_release_version') == '0.89.0', soc
assert soc.get('fixed_depth_soc_stock') is True
assert soc.get('project_packet_handoff') is True
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Lab v0.89.0 / Carbon & Nature v0.6.0 SOC health contract')
PYVERIFY

docker exec "$CONTAINER" python - <<'PYFIXTURE'
from app.soil_organic_carbon_v0890 import calculate_layer_stock
r=calculate_layer_stock({
    'top_depth':0,
    'bottom_depth':30,
    'soc_value':2,
    'soc_unit':'percent',
    'bulk_density_value':1.3,
    'bulk_density_unit':'g/cm3',
    'coarse_fragments_percent':0,
})
assert abs(r['soc_stock_Mg_C_ha']-78.0) < 1e-12, r
print('PASS: in-container SOC reference fixture = 78.0 Mg C/ha')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.89.0 / Carbon & Nature Intelligence v0.6.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
