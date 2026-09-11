#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.96.0.zip}"
CONTAINER="sc-lab"
PORT="8092"

[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" ]] || { echo "ERROR: Lab root not found: $BASE" >&2; exit 1; }
[[ -f "$BASE/.env.production" ]] || { echo "ERROR: $BASE/.env.production is required" >&2; exit 1; }
[[ -f "$BASE/compose.yml" ]] || { echo "ERROR: $BASE/compose.yml is required" >&2; exit 1; }
[[ -d "$LIVE_BACKEND" ]] || { echo "ERROR: live backend not found: $LIVE_BACKEND" >&2; exit 1; }
for cmd in docker unzip rsync curl python3; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v0960.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.96.0-$ts"
env_backup="/tmp/sc-lab-v0.96.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/carbon_mrv_protocol_v0960.py" ]] || { echo "ERROR: v0.96.0 MRV Protocol Builder module missing from package" >&2; exit 1; }

rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
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
h13="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/mrv/v1300/protocol/health")"
python3 - "$health" "$h6" "$h7" "$h8" "$h9" "$h10" "$h11" "$h12" "$h13" <<'PYVERIFY'
import json,sys
health,h6,h7,h8,h9,h10,h11,h12,h13=(json.loads(x) for x in sys.argv[1:])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
for obj,version in zip((h6,h7,h8,h9,h10,h11,h12,h13),('0.6.0','0.7.0','0.8.0','0.9.0','0.10.0','0.11.0','0.12.0','0.13.0')):
    assert obj.get('ok') is True and obj.get('domain_version') == version, (version,obj)
assert h12.get('method_count') == 7, h12
assert h13.get('lab_release_version') == '0.96.0', h13
assert h13.get('status') == 'mrv-protocol-builder-ready', h13
assert h13.get('section_count') == 9, h13
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 through v0.12.0 engines retained')
print('PASS: Lab v0.96.0 / Carbon & Nature v0.13.0 MRV Protocol Builder health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.carbon_mrv_protocol_v0960 import build_protocol, build_project_packet
from app.carbon_mrv_registry_v0950 import METHODS
m=METHODS['soc-direct-measurement']
payload={
 'project_id':'project:fixture','title':'SOC monitoring protocol','objective':'Repeated fixed-depth SOC monitoring for the named parcel.',
 'method_key':'soc-direct-measurement','spatial_boundary_ref':'parcel:fixture',
 'monitoring_period':{'start_date':'2026-01-01','end_date':'2030-12-31'},
 'monitoring_frequency':'Baseline and repeat campaign; deviations recorded.',
 'responsible_roles':[{'role':'field lead','actor_ref':'actor:field-team','responsibility':'sampling and custody'}],
 'available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],
 'methodology_refs':['library-methodology:soc-direct-measurement'],'source_refs':['evidence:fixture'],
 'sections':{
  'objective_and_scope':'Parcel, 0-30 cm SOC pool; exclusions explicit.',
  'measurement_and_sampling_plan':'Explicit sample IDs, depths, SOC, bulk density, coarse fragments, custody.',
  'calculation_plan':'Governed fixed-depth SOC stock calculation with versioned inputs.',
  'uncertainty_plan':'Replicate and analytical uncertainty documented; unresolved components explicit.',
  'quality_control_plan':'Identity, depth, custody, replicate and laboratory-method checks.',
  'data_management_plan':'Stable IDs, source refs, immutable observations, versioned derived records.',
  'monitoring_schedule':'Baseline 2026 and repeat 2030; actual dates recorded.',
  'reporting_plan':'Monitoring record with results, evidence, uncertainty and limitations.',
  'change_control_plan':'Version revisions and preserve superseded protocols with reasons.'}}
r=build_protocol(payload)
assert r['protocol']['status']=='ready-for-internal-review'
assert r['validation']['ready_for_internal_review'] is True
assert r['validation']['external_methodology_compliance'] is None
packet=build_project_packet({'protocol':r['protocol']})
obj=packet['packet']['objects'][0]
assert obj['object_type']=='monitoring-record' and obj['payload']['record_type']=='mrv-protocol'
assert obj['payload']['guardrails']['no_verification_determination'] is True
print('PASS: in-container complete SOC protocol = ready-for-internal-review')
print('PASS: external methodology compliance, verification, certification, and credit eligibility remain unset')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.96.0 / Carbon & Nature Intelligence v0.13.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volume declarations were left unchanged."
