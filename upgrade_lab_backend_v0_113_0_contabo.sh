#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.113.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.113.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.113.0 — UNIFIED RESEARCH SESSION PRODUCTION RUNTIME ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01130.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.113.0-$ts"; env_backup="/tmp/sc-lab-v0.113.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_production_runtime_v01130.py" ]] || { echo "ERROR: v0.113.0 production-runtime module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do
 state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"
 case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac
 sleep 2
done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
adapter="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-adapter/health")"
objects="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-objects/health")"
context="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-context/health")"
execution="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-executions/health")"
research="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-research-intelligence/health")"
visual="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-visual-scene/health")"
packages="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-scholarly-packages/health")"
investigation="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-scientific-investigations/health")"
cert="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-integration-certification/health")"
production="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-production-runtime/health")"
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$research" "$visual" "$packages" "$investigation" "$cert" "$production" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,research,visual,packages,investigation,cert,production,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
checks=[(adapter,'0.104.0'),(objects,'0.105.0'),(context,'0.106.0'),(execution,'0.107.0'),(research,'0.108.0'),(visual,'0.109.0'),(packages,'0.110.0'),(investigation,'0.111.0'),(cert,'0.112.0'),(production,'0.113.0')]
for obj,v in checks: assert obj.get('ok') is True and obj.get('lab_release_version')==v,(v,obj)
assert production.get('component_count')==9 and production.get('operation_type_count')==14,production
for k in ('automatic_core_submission','automatic_retry','automatic_recovery','automatic_scientific_execution','automatic_scientific_certification','automatic_truth_determination'): assert production.get(k) is False,(k,production)
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104-v0.112 Platform Core integration surfaces healthy')
print('PASS: Lab v0.113.0 production-runtime health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - "$adapter" "$objects" "$context" "$execution" "$research" "$visual" "$packages" "$investigation" "$cert" "$core_health" <<'PYFIXTURE'
import json,sys
from app.main import app
from app.platform_core_v3_production_runtime_v01130 import COMPONENTS,assess_diagnostics,assess_roundtrip,build_checkpoint,build_receipt,build_recovery_plan,build_retry_plan,build_roundtrip_plan,build_submission_plan,catalog,check_continuity,check_idempotency,check_readiness,manifest,normalize_operation
adapter,objects,context_h,execution,research,visual,packages,investigation,cert,core=[json.loads(x) for x in sys.argv[1:]]
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}; base='/v1/platform-core-v3-production-runtime'
required={f'{base}/health',f'{base}/manifest',f'{base}/schema',f'{base}/catalog',f'{base}/operations/normalize',f'{base}/submissions/plan',f'{base}/idempotency/check',f'{base}/receipts/build',f'{base}/retries/plan',f'{base}/recovery/plan',f'{base}/checkpoints/build',f'{base}/continuity/check',f'{base}/diagnostics/assess',f'{base}/readiness/check',f'{base}/roundtrip/plan',f'{base}/roundtrip/assess'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'12','session_key':'deploy-session','title':'Deployment Production Runtime','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy','researcher_ref':'researcher:deploy'}
request={'context':ctx,'operation_type':'object-binding','payload':{'object':{'object_type':'dataset','id':'d1','content_hash':'a'*64}}}
op=normalize_operation(request)['operation']; submission=build_submission_plan(request); assert submission['automatic_submission'] is False and submission['authorization_material_included'] is False
idem=check_idempotency({**request,'prior_records':[{'idempotency_key':op['idempotency_key'],'request_hash':op['request_hash']}]}); assert idem['state']=='replay-safe' and idem['automatic_replay'] is False
receipt=build_receipt({'operation':op,'declared_outcome':'uncertain','status_code':200,'response':{'ok':True}})['receipt']; assert receipt['success_inferred_from_status_code'] is False
retry=build_retry_plan({'receipt':{**receipt,'declared_outcome':'failed','status_code':503}}); assert retry['eligible_for_explicit_retry'] is True and retry['automatic_retry'] is False
recovery=build_recovery_plan({'receipts':[{**receipt,'declared_outcome':'failed'}]}); assert recovery['recovery_required'] is True and recovery['automatic_recovery'] is False
checkpoint=build_checkpoint({'context':ctx,'operations':[op],'receipts':[receipt]}); assert checkpoint['automatic_persistence'] is False
assert check_continuity({'context':ctx,'operations':[op]})['continuous'] is True
components={'runtime-adapter':adapter,'object-mapping':objects,'research-context':context_h,'execution-lineage':execution,'research-intelligence':research,'visual-scene':visual,'scholarly-package':packages,'scientific-investigation':investigation,'integration-certification':cert}
diagnostics=assess_diagnostics({'components':components}); assert diagnostics['ready'] is True,diagnostics
results=[{'case_key':k,'status':'pass'} for k in __import__('app.platform_core_v3_integration_certification_v01120',fromlist=['CASE_CATALOG']).CASE_CATALOG]
cert_assessment=__import__('app.platform_core_v3_integration_certification_v01120',fromlist=['assess_roundtrip']).assess_roundtrip({'results':results})
readiness=check_readiness({'core_health':core,'components':components,'certification':cert_assessment}); assert readiness['production_ready'] is True,readiness
plan=build_roundtrip_plan({'context':ctx,'operations':[request]}); assert len(plan['stages'])==7 and plan['automatic_recovery'] is False
assessment=assess_roundtrip({'receipts':[{'declared_outcome':'succeeded'},{'declared_outcome':'duplicate'}]}); assert assessment['declared_roundtrip_complete'] is True and assessment['scientific_validity_certified'] is False
assert catalog()['component_count']==9 and catalog()['operation_type_count']==14 and manifest()['boundaries']['automatic_retry'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: sixteen v0.113 production-runtime routes loaded')
print('PASS: deterministic operation/idempotency identity and explicit non-authorized submission planning')
print('PASS: declared receipts do not infer success from HTTP status')
print('PASS: advisory retry/recovery, checkpoints, continuity, diagnostics, readiness, and roundtrip controls')
print('PASS: production readiness is operational only and does not certify science, product quality, or truth')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.113.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
