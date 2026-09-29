#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.105.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR

BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.105.0.zip}"
CONTAINER="sc-lab"
PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"

[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" ]] || { echo "ERROR: Lab root not found: $BASE" >&2; exit 1; }
[[ -f "$BASE/.env.production" ]] || { echo "ERROR: $BASE/.env.production is required" >&2; exit 1; }
[[ -f "$BASE/compose.yml" ]] || { echo "ERROR: $BASE/compose.yml is required" >&2; exit 1; }
[[ -d "$LIVE_BACKEND" ]] || { echo "ERROR: live backend not found: $LIVE_BACKEND" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.105.0 — CANONICAL RESEARCH OBJECT MAPPING ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v01050.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.105.0-$ts"
env_backup="/tmp/sc-lab-v0.105.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"

unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found in package" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_object_mapping_v01050.py" ]] || { echo "ERROR: v0.105.0 object mapping module missing from package" >&2; exit 1; }
[[ -f "$source_backend/contracts/platform-core-v3-object-mapping-policy-v01050.json" ]] || { echo "ERROR: v0.105.0 object mapping policy missing from package" >&2; exit 1; }

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
objects="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-objects/health")"
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$core_health" <<'PYVERIFY'
import json,sys
health=json.loads(sys.argv[1]); adapter=json.loads(sys.argv[2]); objects=json.loads(sys.argv[3]); core=json.loads(sys.argv[4])
assert health.get('ok') is True and health.get('version') == '1.0.0', health
assert adapter.get('ok') is True and adapter.get('lab_release_version') == '0.104.0', adapter
assert adapter.get('required_core_release') == '3.0.0', adapter
assert objects.get('ok') is True and objects.get('lab_release_version') == '0.105.0', objects
assert objects.get('mapping_count') == 20, objects
assert objects.get('reference_first') is True, objects
assert objects.get('automatic_core_submission') is False, objects
assert core.get('ok') is True and core.get('version') == '3.0.0', core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained Lab v0.104.0 Platform Core v3 runtime adapter healthy')
print('PASS: Lab v0.105.0 canonical research object mapping health contract')
print('PASS: Platform Core public health reports v3.0.0')
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_object_mapping_v01050 import (
    build_core_object_binding,
    build_core_object_binding_batch,
    catalog,
    map_legacy_typed_handoff,
    normalize_object,
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]
paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-objects/health',
'/v1/platform-core-v3-objects/catalog',
'/v1/platform-core-v3-objects/schema',
'/v1/platform-core-v3-objects/normalize',
'/v1/platform-core-v3-objects/bind',
'/v1/platform-core-v3-objects/batch',
'/v1/platform-core-v3-objects/legacy-handoff/map',
}
assert not (required-paths), sorted(required-paths)
assert len(path_routes)==1015, len(path_routes)
assert catalog()['mapping_count']==20
obj=normalize_object({'object_type':'evidence','id':'ev-deploy','content':{'value':1}})['object']
assert obj['lab_object_type']=='evidence-record' and obj['core_object_type']=='evidence'
assert len(obj['content_hash'])==64 and 'content' not in obj
binding=build_core_object_binding({'session_id':'deployment-session','object':{'object_type':'dataset','id':'dataset-deploy','content_hash':'a'*64}})
assert binding['automatic_submission'] is False
assert binding['request_body']=={'data':binding['data']}
assert binding['data']['object_ref']=='lab:dataset:dataset-deploy'
assert binding['data']['metadata']['underlying_object_remains_authoritative_in_lab'] is True
batch=build_core_object_binding_batch({'session_id':'deployment-session','objects':[{'object_type':'model','id':'m1'},{'object_type':'scientific-figure','id':'f1'}]})
assert batch['count']==2 and batch['automatic_submission'] is False
legacy=map_legacy_typed_handoff({'session_id':'deployment-session','entityType':'reproducibility-package','contractVersion':'sc-research-reproducibility-package/1.0','resource':{'id':'pkg1','sha256':'b'*64}})
assert legacy['core_mapping']['data']['object_ref']=='lab:reproducibility-package:pkg1'
assert legacy['automatic_execution'] is False
print('PASS: seven v0.105.0 object-mapping routes loaded (1015 path routes total)')
print('PASS: 20 canonical Lab-to-Core object mappings')
print('PASS: reference-first object bindings preserve Lab authority and do not copy payloads')
print('PASS: v0.38.1 typed handoff bridge maps to Core v3 object references')
print('PASS: no automatic Core submission or scientific execution introduced')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.105.0 backend deployment complete."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volume declarations were left unchanged."
