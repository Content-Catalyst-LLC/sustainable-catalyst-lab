#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.8.4.1 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.8.4.1.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.8.4.1 — PROVENANCE INTERACTION LIFECYCLE + GRAPH CONTROL RECOVERY ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v0135841.XXXXXX)"; cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.8.4.1-$ts"; env_backup="/tmp/sc-lab-v0.135.8.4.1.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; find "$tmp" -type d -exec chmod u+rwx {} +; find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in graph_studio_recovery_v013583.py graph_studio_bootstrap_finalization_v0135831.py graph_studio_live_binding_v013584.py graph_studio_provenance_interaction_recovery_v0135841.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
patch="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-provenance-interaction/v0135841/health")"; live="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-live-binding/v013584/health")"; final="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-bootstrap-finalization/v0135831/health")"; recovery="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-recovery/v013583/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$patch" "$live" "$final" "$recovery" "$core" <<'PYHEALTH'
import json,sys,re
patch,live,final,recovery,core=[json.loads(z) for z in sys.argv[1:]]
assert patch.get('ok') is True and patch.get('version')=='0.135.8.4.1' and patch.get('api_route_count')==8 and patch.get('delegated_interaction') is True and patch.get('programmatic_layout_click') is False
assert live.get('ok') is True and live.get('version')=='0.135.8.4'
assert final.get('ok') is True and final.get('version')=='0.135.8.3.1'
assert recovery.get('ok') is True and recovery.get('single_renderer_root') is True and recovery.get('single_primary_viewport') is True
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]; assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,0,0)
print('PASS: v0.135.8.4.1 provenance interaction backend contract healthy')
print('PASS: v0.135.8.4 live project binding retained')
print('PASS: v0.135.8.3.1 bootstrap and v0.135.8.3 recovery retained')
print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app import graph_studio_provenance_interaction_recovery_v0135841 as p
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}; req={x for x in paths if x.startswith('/v1/graph-studio-provenance-interaction/v0135841')}; assert len(req)==8,len(req)
a=p.acceptance_report(); assert a['renderer_31_hosts']==1 and a['primary_viewports']==1 and a['provenance_explorers']==1 and a['layout_control_count']==3 and a['programmatic_layout_clicks']==0
assert p.lifecycle_contract()['programmatic_button_click_restore'] is False
assert p.selection_contract()['changes_claim_status'] is False
assert p.exploration_contract()['structural_paths_are_causal'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.8.4.1 interaction lifecycle acceptance fixtures')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.8.4.1 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
