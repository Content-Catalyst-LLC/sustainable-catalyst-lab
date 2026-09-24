#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.99.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v0990.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.99.0-$ts"
env_backup="/tmp/sc-lab-v0.99.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/carbon_mrv_verification_ledger_v0990.py" ]] || { echo "ERROR: v0.99.0 Verification Evidence Ledger module missing from package" >&2; exit 1; }

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
h16="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/mrv/v1600/verification-ledger/health")"
python3 - "$health" "$h6" "$h7" "$h8" "$h9" "$h10" "$h11" "$h12" "$h13" "$h14" "$h15" "$h16" <<'PYVERIFY'
import json,sys
objs=[json.loads(x) for x in sys.argv[1:]]
health=objs[0]; versions=objs[1:]
assert health.get('ok') is True and health.get('version') == '1.0.0', health
for obj,version in zip(versions,('0.6.0','0.7.0','0.8.0','0.9.0','0.10.0','0.11.0','0.12.0','0.13.0','0.14.0','0.15.0','0.16.0')):
    assert obj.get('ok') is True and obj.get('domain_version') == version, (version,obj)
h16=versions[-1]
assert h16.get('lab_release_version') == '0.99.0', h16
assert h16.get('status') == 'verification-evidence-ledger-ready', h16
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 through v0.15.0 engines retained')
print('PASS: Lab v0.99.0 / Carbon & Nature v0.16.0 verification-ledger health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from copy import deepcopy
from app.carbon_mrv_verification_ledger_v0990 import build_ledger, verify_chain, build_project_packet
p={'project_id':'project:fixture','title':'SOC verification evidence ledger','protocol_ref':'mrv-protocol:fixture','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_assessment_ref':'mrv-uncertainty:fixture','requirements':[{'requirement_key':'sampling','description':'Sampling evidence','accepted_evidence_types':['sample-record']},{'requirement_key':'laboratory','description':'Laboratory evidence','accepted_evidence_types':['laboratory-result']},{'requirement_key':'uncertainty','description':'Uncertainty evidence','accepted_evidence_types':['model-run']}],'entries':[{'evidence_id':'sample-001','evidence_type':'sample-record','source_ref':'sample:001','requirement_keys':['sampling'],'review_state':'accepted-for-internal-review'},{'evidence_id':'lab-001','evidence_type':'laboratory-result','source_ref':'lab:001','source_sha256':'0'*64,'requirement_keys':['laboratory'],'review_state':'accepted-for-internal-review'},{'evidence_id':'unc-001','evidence_type':'model-run','source_ref':'mrv-uncertainty:fixture','requirement_keys':['uncertainty'],'review_state':'accepted-for-internal-review'}],'source_refs':['mrv-protocol:fixture']}
r=build_ledger(p); l=r['ledger']
assert l['status']=='ready-for-internal-review' and r['validation']['external_verification_status'] is None
c=verify_chain({'ledger':l}); assert c['chain_valid'] is True and c['tamper_detected'] is False
t=deepcopy(l); t['entries'][1]['source_ref']='lab:tampered'; tc=verify_chain({'ledger':t}); assert tc['tamper_detected'] is True
packet=build_project_packet({'ledger':l}); assert packet['packet']['objects'][0]['object_type']=='verification-record'
print('PASS: three-entry evidence ledger is ready for internal review only')
print('PASS: deterministic hash chain validates and detects a source-reference mutation')
print('PASS: Carbon Project packet uses verification-record without asserting external verification')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.99.0 / Carbon & Nature Intelligence v0.16.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volume declarations were left unchanged."
