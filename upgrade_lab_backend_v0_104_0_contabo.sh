#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.104.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.104.0.zip}"
CONTAINER="sc-lab"
PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"

[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" ]] || { echo "ERROR: Lab root not found: $BASE" >&2; exit 1; }
[[ -f "$BASE/.env.production" ]] || { echo "ERROR: $BASE/.env.production is required" >&2; exit 1; }
[[ -f "$BASE/compose.yml" ]] || { echo "ERROR: $BASE/compose.yml is required" >&2; exit 1; }
[[ -d "$LIVE_BACKEND" ]] || { echo "ERROR: live backend not found: $LIVE_BACKEND" >&2; exit 1; }
for cmd in docker unzip rsync curl python3; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.104.0 — PLATFORM CORE v3 RUNTIME ADAPTER ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v01040.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.104.0-$ts"
env_backup="/tmp/sc-lab-v0.104.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_backend="$(find "$tmp" -type f -path '*/backend/Dockerfile' -printf '%h\n' | head -1)"
[[ -n "$source_backend" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
[[ -f "$source_backend/app/platform_core_v3_adapter_v01040.py" ]] || { echo "ERROR: v0.104.0 Platform Core v3 adapter module missing from package" >&2; exit 1; }
[[ -f "$source_backend/contracts/platform-core-v3-runtime-adapter-policy-v01040.json" ]] || { echo "ERROR: v0.104.0 adapter policy missing from package" >&2; exit 1; }

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
adapter="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-adapter/health")"
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$core_health" <<'PYVERIFY'
import json,sys
health=json.loads(sys.argv[1]); adapter=json.loads(sys.argv[2]); core=json.loads(sys.argv[3])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
assert adapter.get('ok') is True and adapter.get('lab_release_version') == '0.104.0', adapter
assert adapter.get('required_core_release') == '3.0.0', adapter
assert adapter.get('runtime_contract') == 'sc.research.unified-runtime-contract.v1', adapter
assert adapter.get('unified_runtime_contract') == 'sc.research.unified-research-scientific-investigation-runtime.v1', adapter
assert adapter.get('boundaries',{}).get('lab_is_scientific_execution_authority') is True, adapter
assert adapter.get('boundaries',{}).get('lab_calls_core_automatically') is False, adapter
assert core.get('ok') is True and core.get('version') == '3.0.0', core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: Lab v0.104.0 Platform Core v3 adapter health contract')
print('PASS: Platform Core public health reports v3.0.0')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_adapter_v01040 import (
    build_contract_product_registration,
    build_session_product_binding,
    compatibility_report,
    normalize_runtime_context,
    validate_handoff,
)
paths={r.path for r in app.routes}
required={
'/v1/platform-core-v3-adapter/health',
'/v1/platform-core-v3-adapter/manifest',
'/v1/platform-core-v3-adapter/registrations/runtime-contract',
'/v1/platform-core-v3-adapter/registrations/session',
'/v1/platform-core-v3-adapter/runtime-context/normalize',
'/v1/platform-core-v3-adapter/handoffs/validate',
'/v1/platform-core-v3-adapter/compatibility/check',
}
assert not (required-paths), sorted(required-paths)
assert len(app.routes) == 1008, len(app.routes)
reg=build_contract_product_registration({'contract_id':'contract:runtime:v1','supported_object_types':['dataset','model']})
assert reg['automatic_submission'] is False and reg['data']['product_ref']=='product:sustainable-catalyst-lab'
session=build_session_product_binding({'session_id':'1','context_ref':'context:deployment-fixture'})
assert session['automatic_submission'] is False and session['data']['runtime_binding_ref']=='lab:runtime:scientific-compute:0.104.0'
ctx=normalize_runtime_context({'session_id':'1','project_ref':'project:deployment-fixture'})
assert ctx['context']['runtime_contract_ref']=='sc.research.unified-runtime-contract.v1'
handoff=validate_handoff({'session_id':'1','handoff_ref':'handoff:deployment-fixture','source_product_ref':'product:platform-core','target_product_ref':'product:sustainable-catalyst-lab'})
assert handoff['automatic_execution'] is False and handoff['automatic_core_mutation'] is False
readiness={
'release':'3.0.0','contract':'sc.research.unified-research-scientific-investigation-runtime.v1',
'reference_first_runtime_by_core':True,'unified_session_registry_by_core':True,'research_object_binding_by_core':True,'product_context_binding_by_core':True,'computation_execution_binding_by_core':True,'investigation_binding_by_core':True,'visual_reasoning_binding_by_core':True,'validation_challenge_binding_by_core':True,'research_package_binding_by_core':True,'cross_product_handoff_binding_by_core':True,'milestone_registry_by_core':True,'revision_history_by_core':True,'immutable_runtime_snapshots_by_core':True,'underlying_objects_remain_authoritative_in_specialist_layers':True,
'execute_scientific_work_by_core':False,'execute_code_by_core':False,'run_investigation_by_core':False,'infer_findings_by_core':False,'infer_causality_by_core':False,'select_hypothesis_by_core':False,'rank_evidence_by_core':False,'render_visuals_by_core':False,'publish_research_by_core':False,'authorize_access_by_core':False,'certify_scientific_validity_by_core':False,'determine_truth_by_core':False,
}
assert compatibility_report(readiness)['status']=='compatible'
print('PASS: seven Platform Core v3 adapter routes loaded (1008 total FastAPI routes)')
print('PASS: contract/session registration payloads remain explicit and non-submitting')
print('PASS: Core-to-Lab handoff validation does not auto-execute or auto-mutate Core')
print('PASS: Core v3 readiness/boundary fixture is compatible')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.104.0 backend deployment complete."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volume declarations were left unchanged."
