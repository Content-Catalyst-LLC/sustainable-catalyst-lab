#!/usr/bin/env bash
set -euo pipefail

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.100.0.zip}"
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
tmp="$(mktemp -d /tmp/sc-lab-v01000.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.100.0-$ts"
env_backup="/tmp/sc-lab-v0.100.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/carbon_mrv_reporting_v01000.py" ]] || { echo "ERROR: v0.100.0 MRV Reporting & Audit Packets module missing from package" >&2; exit 1; }

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
h17="$(curl -fsS "http://127.0.0.1:${PORT}/v1/carbon-nature/mrv/v1700/reporting/health")"
python3 - "$health" "$h6" "$h7" "$h8" "$h9" "$h10" "$h11" "$h12" "$h13" "$h14" "$h15" "$h16" "$h17" <<'PYVERIFY'
import json,sys
objs=[json.loads(x) for x in sys.argv[1:]]
health=objs[0]; versions=objs[1:]
assert health.get('ok') is True and health.get('version') == '1.0.0', health
for obj,version in zip(versions,('0.6.0','0.7.0','0.8.0','0.9.0','0.10.0','0.11.0','0.12.0','0.13.0','0.14.0','0.15.0','0.16.0','0.17.0')):
    assert obj.get('ok') is True and obj.get('domain_version') == version, (version,obj)
h17=versions[-1]
assert h17.get('lab_release_version') == '0.100.0', h17
assert h17.get('status') == 'mrv-reporting-audit-packets-ready', h17
print('PASS: Compute Core 1.0.0 healthy')
print('PASS: Carbon & Nature v0.6.0 through v0.16.0 engines retained')
print('PASS: Lab v0.100.0 / Carbon & Nature v0.17.0 reporting health contract')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.carbon_mrv_verification_ledger_v0990 import build_ledger
from app.carbon_mrv_reporting_v01000 import build_report, build_audit_packet, build_project_packet
ledger=build_ledger({
 'project_id':'project:fixture','title':'SOC evidence ledger','protocol_ref':'mrv-protocol:fixture','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_assessment_ref':'mrv-uncertainty:fixture',
 'requirements':[{'requirement_key':'sampling','description':'Sampling evidence','accepted_evidence_types':['sample-record']},{'requirement_key':'laboratory','description':'Laboratory evidence','accepted_evidence_types':['laboratory-result']}],
 'entries':[{'evidence_id':'sample-001','evidence_type':'sample-record','source_ref':'sample:001','requirement_keys':['sampling'],'review_state':'accepted-for-internal-review'},{'evidence_id':'lab-001','evidence_type':'laboratory-result','source_ref':'lab:001','source_sha256':'0'*64,'requirement_keys':['laboratory'],'review_state':'accepted-for-internal-review'}]
})['ledger']
sections=[
 {'section_key':'project-boundary','title':'Boundary','content':'Parcel and period documented.','source_refs':['project:fixture']},
 {'section_key':'methodology','title':'Methodology','content':'Methods linked.','source_refs':['mrv-protocol:fixture']},
 {'section_key':'monitoring','title':'Monitoring','content':'Monitoring linked.','source_refs':['monitoring-plan:fixture']},
 {'section_key':'quantification','title':'Quantification','content':'Declared metric lineage retained.','source_refs':['model-run:soc-change']},
 {'section_key':'uncertainty','title':'Uncertainty','content':'Assessment linked.','source_refs':['mrv-uncertainty:fixture']},
 {'section_key':'evidence','title':'Evidence','content':'Ledger linked.','source_refs':[ledger['ledger_id']]},
 {'section_key':'deviations','title':'Deviations','content':'No unresolved deviations.','source_refs':[]},
 {'section_key':'summary','title':'Summary','content':'Internal review only.','source_refs':[]},
]
p={'report_type':'monitoring-report','project_id':'project:fixture','title':'2026 SOC monitoring report','reporting_period':{'start':'2026-01-01','end':'2026-12-31'},'protocol_ref':'mrv-protocol:fixture','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_assessment_ref':'mrv-uncertainty:fixture','verification_ledger_ref':ledger['ledger_id'],'verification_ledger':ledger,'sections':sections,'reported_metrics':[{'metric_id':'soc-change','name':'SOC stock change','value':7.8,'unit':'Mg C/ha','source_ref':'model-run:soc-change','uncertainty_ref':'mrv-uncertainty:fixture'}],'deviations':[]}
r=build_report(p); assert r['report']['status']=='ready-for-internal-review'; assert r['validation']['external_verification_status'] is None
ap=build_audit_packet({'report':r['report'],'artifacts':[{'artifact_id':'lab-result','artifact_type':'laboratory-result','source_ref':'lab:001','sha256':'1'*64}]}); assert ap['audit_packet']['status']=='ready-for-internal-audit-preparation'; assert ap['audit_packet']['external_audit_status'] is None
pp=build_project_packet({'report':r['report'],'artifacts':[]}); assert pp['packet']['objects'][0]['object_type']=='verification-record'; assert pp['packet']['objects'][0]['payload']['external_audit_status'] is None
print('PASS: internally review-ready report built with explicit 7.8 Mg C/ha declared metric')
print('PASS: valid v0.16 ledger chain supports internal audit-preparation readiness only')
print('PASS: Carbon Project handoff remains a draft verification-record with external audit/verification unset')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.100.0 / Carbon & Nature Intelligence v0.17.0 is active."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volume declarations were left unchanged."
