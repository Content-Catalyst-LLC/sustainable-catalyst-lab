#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.95.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v0950.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.95.0-$ts"
env_backup="/tmp/sc-lab-v0.95.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/carbon_mrv_registry_v0950.py" ]] || { echo "ERROR: v0.95.0 Carbon MRV Registry module missing from package" >&2; exit 1; }

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
h12="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/mrv/v1200/registry/health")"
python3 - "$health" "$h6" "$h7" "$h8" "$h9" "$h10" "$h11" "$h12" <<'PYVERIFY'
import json,sys
health,h6,h7,h8,h9,h10,h11,h12=(json.loads(x) for x in sys.argv[1:])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
for obj,version in zip((h6,h7,h8,h9,h10,h11,h12),('0.6.0','0.7.0','0.8.0','0.9.0','0.10.0','0.11.0','0.12.0')):
    assert obj.get('ok') is True and obj.get('domain_version') == version, (version,obj)
assert h12.get('lab_release_version') == '0.95.0', h12
assert h12.get('method_count') == 7, h12
assert h12.get('guardrails',{}).get('no_automatic_method_selection') is True, h12
assert h12.get('guardrails',{}).get('no_methodology_eligibility_determination') is True, h12
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 through v0.11.0 engines retained')
print('PASS: Lab v0.95.0 / Carbon & Nature v0.12.0 Carbon MRV Method Registry health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.carbon_mrv_registry_v0950 import METHODS, list_methods, compare_methods, assess_readiness, build_project_packet
assert len(METHODS) == 7
assert list_methods(gas='CH4')['count'] == 2
comparison=compare_methods({'method_keys':['soc-direct-measurement','hybrid-measurement-modeling','modeled-carbon-stock-change']})
assert comparison['ranking_performed'] is False and comparison['recommendation_generated'] is False
m=METHODS['soc-direct-measurement']
readiness=assess_readiness({'method_key':'soc-direct-measurement','available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],'source_refs':['evidence:fixture']})
assert readiness['documentation_ready'] is True
assert readiness['external_methodology_eligibility'] is None
packet=build_project_packet({'project_id':'project:fixture','readiness':{'method_key':'soc-direct-measurement','available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],'source_refs':['evidence:fixture']}})
assert packet['packet']['objects'][0]['object_type']=='monitoring-record'
assert packet['packet']['objects'][0]['payload']['guardrails']['no_verification_determination'] is True
print('PASS: in-container MRV registry fixture = 7 methods; CH4 filter = 2; complete SOC documentation profile = ready')
print('PASS: no method ranking, external eligibility, verification, or credit eligibility inferred')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.95.0 / Carbon & Nature Intelligence v0.12.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Persistent Docker volume preserved: sc-lab-data"
