#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.106.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.106.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.106.0 — UNIFIED PROJECT & RESEARCH SESSION CONTEXT ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01060.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.106.0-$ts"; env_backup="/tmp/sc-lab-v0.106.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_research_context_v01060.py" ]] || { echo "ERROR: v0.106.0 context module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; adapter="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-adapter/health")"; objects="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-objects/health")"; context="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-context/health")"; core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert adapter.get('ok') is True and adapter.get('lab_release_version')=='0.104.0',adapter
assert objects.get('ok') is True and objects.get('lab_release_version')=='0.105.0' and objects.get('mapping_count')==20,objects
assert context.get('ok') is True and context.get('lab_release_version')=='0.106.0',context
assert context.get('minimum_core_release')=='3.0.0',context
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104 runtime adapter and v0.105 object mapper healthy')
print('PASS: Lab v0.106.0 project/session context health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_research_context_v01060 import build_core_session_registration,build_core_product_context_binding,build_contextual_object_binding,build_contextual_handoff_binding,check_context_continuity,normalize_research_context
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={'/v1/platform-core-v3-context/health','/v1/platform-core-v3-context/manifest','/v1/platform-core-v3-context/schema','/v1/platform-core-v3-context/normalize','/v1/platform-core-v3-context/sessions/build','/v1/platform-core-v3-context/products/bind','/v1/platform-core-v3-context/objects/bind','/v1/platform-core-v3-context/handoffs/bind','/v1/platform-core-v3-context/continuity/check'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'7','session_key':'deploy-session','title':'Deployment Fixture','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy'}
n=normalize_research_context(ctx)['context']; s=build_core_session_registration(ctx); p=build_core_product_context_binding(ctx); o=build_contextual_object_binding({'context':ctx,'object':{'object_type':'dataset','id':'d1'}}); h=build_contextual_handoff_binding({'context':ctx,'handoff':{'id':'h1','targetProduct':'knowledge-library'}}); c=check_context_continuity({'context':ctx,'entries':[{'project_ref':'project:deploy','session_id':'7','context_ref':n['context_ref']}]})
assert s['automatic_submission'] is False and p['automatic_submission'] is False
assert o['core_mapping']['data']['metadata']['lab_metadata']['context_ref']==n['context_ref']
assert h['automatic_execution'] is False and h['automatic_core_mutation'] is False
assert c['ok'] is True
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: nine v0.106 project/session context routes loaded')
print('PASS: one context_ref flows through session, product, object, and handoff envelopes')
print('PASS: no automatic Core submission, mutation, or scientific execution')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.106.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
