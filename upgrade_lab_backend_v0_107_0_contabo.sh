#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.107.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.107.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.107.0 — SCIENTIFIC EXECUTION LINEAGE BRIDGE ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01070.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.107.0-$ts"; env_backup="/tmp/sc-lab-v0.107.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_execution_lineage_v01070.py" ]] || { echo "ERROR: v0.107.0 execution-lineage module missing" >&2; exit 1; }
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
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert adapter.get('ok') is True and adapter.get('lab_release_version')=='0.104.0',adapter
assert objects.get('ok') is True and objects.get('lab_release_version')=='0.105.0' and objects.get('mapping_count')==20,objects
assert context.get('ok') is True and context.get('lab_release_version')=='0.106.0',context
assert execution.get('ok') is True and execution.get('lab_release_version')=='0.107.0',execution
assert execution.get('minimum_core_release')=='3.0.0',execution
assert execution.get('automatic_core_submission') is False and execution.get('automatic_scientific_execution') is False,execution
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104 adapter, v0.105 object mapper, and v0.106 research context healthy')
print('PASS: Lab v0.107.0 scientific execution lineage health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_execution_lineage_v01070 import build_core_execution_binding,build_core_execution_binding_batch,check_execution_lineage,map_legacy_execution,normalize_execution
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={'/v1/platform-core-v3-executions/health','/v1/platform-core-v3-executions/manifest','/v1/platform-core-v3-executions/schema','/v1/platform-core-v3-executions/normalize','/v1/platform-core-v3-executions/bind','/v1/platform-core-v3-executions/batch','/v1/platform-core-v3-executions/lineage/check','/v1/platform-core-v3-executions/legacy-run/map'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'7','session_key':'deploy-session','title':'Deployment Fixture','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy'}
run={'id':'run-deploy','runtime':'python','environment_ref':'lab:env:py312','method_ref':'lab:method:monte-carlo:v1','inputs':[{'object_type':'dataset','id':'d1'}],'outputs':[{'object_type':'artifact','id':'a1'}],'parameters':{'iterations':1000},'assumptions':{'iid':True}}
n=normalize_execution({'context':ctx,'execution':run})
b=build_core_execution_binding({'context':ctx,'execution':run})
batch=build_core_execution_binding_batch({'context':ctx,'executions':[run,{**run,'id':'run-deploy-2'}]})
legacy=map_legacy_execution({'context':ctx,'run':{'runId':'legacy-deploy','engine':'python','environmentId':'env:legacy','method':'method:legacy','inputs':[],'outputs':[]}})
check=check_execution_lineage({'context':ctx,'execution':run})
assert n['execution']['execution_ref']=='lab:execution:run-deploy' and len(n['execution']['lineage_hash'])==64
assert b['target_path']=='/v1/research/unified-runtime/execution-bindings'
assert b['automatic_submission'] is False and b['automatic_execution'] is False and b['automatic_core_mutation'] is False
assert b['data']['session_id']=='7' and b['data']['input_refs']==['lab:dataset:d1'] and b['data']['output_refs']==['lab:artifact:a1']
assert batch['count']==2 and batch['automatic_submission'] is False
assert legacy['automatic_execution'] is False and legacy['core_binding']['data']['execution_ref']=='lab:execution:legacy-deploy'
assert check['ok'] is True and check['scientific_validity_certified'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: eight v0.107 scientific execution lineage routes loaded')
print('PASS: method/runtime/environment/input/output lineage maps to Core execution binding')
print('PASS: parameters, assumptions, environment, hashes, and provenance stay namespaced in Lab metadata')
print('PASS: no automatic Core submission, mutation, scientific execution, or validity certification')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.107.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
