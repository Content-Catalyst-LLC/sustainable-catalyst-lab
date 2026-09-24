#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.98.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v0980.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.98.0-$ts"
env_backup="/tmp/sc-lab-v0.98.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/carbon_mrv_uncertainty_v0980.py" ]] || { echo "ERROR: v0.98.0 MRV Uncertainty & Detection Engine module missing from package" >&2; exit 1; }

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
h14="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/mrv/v1400/monitoring/health")"
h15="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/mrv/v1500/uncertainty/health")"
python3 - "$health" "$h6" "$h7" "$h8" "$h9" "$h10" "$h11" "$h12" "$h13" "$h14" "$h15" <<'PYVERIFY'
import json,sys
objs=[json.loads(x) for x in sys.argv[1:]]
health=objs[0]; versions=objs[1:]
assert health.get('ok') is True and health.get('version') == '1.0.0', health
for obj,version in zip(versions,('0.6.0','0.7.0','0.8.0','0.9.0','0.10.0','0.11.0','0.12.0','0.13.0','0.14.0','0.15.0')):
    assert obj.get('ok') is True and obj.get('domain_version') == version, (version,obj)
h15=versions[-1]
assert h15.get('lab_release_version') == '0.98.0', h15
assert h15.get('status') == 'mrv-uncertainty-detection-engine-ready', h15
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 through v0.14.0 engines retained')
print('PASS: Lab v0.98.0 / Carbon & Nature v0.15.0 uncertainty health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.carbon_mrv_uncertainty_v0980 import uncertainty_budget, change_detection, required_sample_size, build_assessment
b=uncertainty_budget({'estimate':100,'unit':'Mg C/ha','coverage_factor':2,'components':[{'component_key':'sampling','standard_uncertainty':3},{'component_key':'lab','standard_uncertainty':4}]})
assert b['combined_standard_uncertainty']==5 and b['expanded_uncertainty']==10
c=change_detection({'design':'paired','observed_change':4,'critical_value':1.96,'sd_change':8,'n_pairs':16})
assert c['standard_error_change']==2 and abs(c['detection_threshold']-3.92)<1e-12 and c['change_detected_at_supplied_threshold'] is True
n=required_sample_size({'design':'paired','minimum_detectable_change':4,'z_alpha':1.96,'z_power':0.84,'expected_sd_change':8})
assert n['recommended_pairs']==32
r=build_assessment({'project_id':'project:fixture','title':'MRV uncertainty fixture','metric':'SOC stock change','unit':'Mg C/ha','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_budget':{'estimate':100,'unit':'Mg C/ha','components':[{'component_key':'sampling','standard_uncertainty':3}]},'change_detection':{'design':'paired','observed_change':4,'critical_value':1.96,'sd_change':8,'n_pairs':16},'source_refs':['evidence:fixture']})
assert r['assessment']['status']=='ready-for-internal-review'
assert r['validation']['verification_status'] is None
print('PASS: uncertainty budget fixture = combined 5, expanded 10 at k=2')
print('PASS: paired detection fixture = SE 2, threshold 3.92; paired planning n = 32')
print('PASS: MRV uncertainty assessment = ready-for-internal-review only')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.98.0 / Carbon & Nature Intelligence v0.15.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volume declarations were left unchanged."
