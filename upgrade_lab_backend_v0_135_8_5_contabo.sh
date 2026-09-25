#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.8.5 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.8.5.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.8.5 — NATIVE PROVENANCE STATE ENGINE + BROWSER HARDENING ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v013585.XXXXXX)"; cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.8.5-$ts"; env_backup="/tmp/sc-lab-v0.135.8.5.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; find "$tmp" -type d -exec chmod u+rwx {} +; find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in graph_studio_recovery_v013583.py graph_studio_live_binding_v013584.py graph_studio_provenance_interaction_recovery_v0135841.py graph_studio_native_provenance_v013585.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
native="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-native-provenance/v013585/health")"; patch="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-provenance-interaction/v0135841/health")"; recovery="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-recovery/v013583/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$native" "$patch" "$recovery" "$core" <<'PYHEALTH'
import json,sys,re
native,patch,recovery,core=[json.loads(z) for z in sys.argv[1:]]
assert native.get('ok') is True and native.get('version')=='0.135.8.5' and native.get('api_route_count')==13
assert native.get('native_graph_state_engine') is True and native.get('mutation_observer_owns_interaction') is False and native.get('project_state_persistence') is True
assert patch.get('ok') is True and patch.get('version')=='0.135.8.4.1'
assert recovery.get('ok') is True and recovery.get('single_renderer_root') is True and recovery.get('single_primary_viewport') is True
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]; assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,0,0)
print('PASS: v0.135.8.5 native provenance backend contract healthy')
print('PASS: v0.135.8.4.1 interaction repair retained beneath native controller')
print('PASS: Renderer 3.1 recovery remains single-root / single-viewport')
print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app import graph_studio_native_provenance_v013585 as p
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}; req={x for x in paths if x.startswith('/v1/graph-studio-native-provenance/v013585')}; assert len(req)==13,len(req)
a=p.acceptance_report(); assert a['graph_controller_count']==1 and a['observer_driven_renders']==0 and a['mutation_observer_interaction_owner'] is False and a['project_state_persistence'] is True
assert p.layout_contract()['synthetic_clicks'] is False
assert p.traversal_contract()['opacity_only_traversal'] is False
assert p.graph_contract()['edge_order_drives_semantics'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.8.5 native graph-state acceptance fixtures')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.8.5 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
