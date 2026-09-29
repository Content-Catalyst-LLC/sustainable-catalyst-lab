#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.10.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.10.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.10.0 — PROVENANCE PATH ANALYSIS / MULTI-OBJECT COMPARISON ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v0135100.XXXXXX)"; cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.10.0-$ts"; env_backup="/tmp/sc-lab-v0.135.10.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; find "$tmp" -type d -exec chmod u+rwx {} +; find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in graph_studio_native_provenance_v013585.py graph_studio_context_relationships_v0135853.py graph_studio_object_explorer_v013590.py graph_studio_provenance_path_analysis_v0135100.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
patch="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-path-analysis/v0135100/health")"; explorer="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-object-explorer/v013590/health")"; native="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-native-provenance/v013585/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$patch" "$explorer" "$native" "$core" <<'PY2'
import json,sys,re
patch,explorer,native,core=[json.loads(z) for z in sys.argv[1:]]
assert patch.get('ok') is True and patch.get('version')=='0.135.10.0' and patch.get('api_route_count')==9
assert patch.get('directed_path_mode') is True and patch.get('structural_path_mode') is True and patch.get('bounded_shortest_path') is True and patch.get('multi_object_comparison') is True and patch.get('research_context_handoff') is True and patch.get('full_graph_redraw_for_path') is False
assert explorer.get('ok') is True and explorer.get('version')=='0.135.9.0'
assert native.get('ok') is True and native.get('api_route_count')==13
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]; assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,0,0)
print('PASS: v0.135.10.0 provenance path-analysis backend healthy'); print(f"PASS: retained object explorer v{explorer.get('version')}"); print(f"PASS: retained native provenance engine v{native.get('version')}"); print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PY2
docker exec -i "$CONTAINER" python - <<'PY2'
from app.main import app
from app import graph_studio_provenance_path_analysis_v0135100 as m
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}; req={x for x in paths if x.startswith('/v1/graph-studio-path-analysis/v0135100')}; assert len(req)==9,len(req)
a=m.acceptance_report(); assert a['directed_path_mode'] and a['structural_path_mode'] and a['bounded_shortest_path'] and a['multi_object_comparison'] and a['research_context_handoff'] and not a['full_graph_redraw_for_path'] and not a['scientific_mutation']
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.135.10.0 backend acceptance contracts')
PY2
echo "PASS - Sustainable Catalyst Lab v0.135.10.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
