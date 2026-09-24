#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.8.2 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.8.2.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.8.2 — GRAPH STUDIO RENDERER REPLACEMENT ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v013582.XXXXXX)"; cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.8.2-$ts"; env_backup="/tmp/sc-lab-v0.135.8.2.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; find "$tmp" -type d -exec chmod u+rwx {} +; find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in model_architecture_computational_provenance_graphs_v01352.py multi_view_scientific_analysis_canvas_v01353.py interactive_scientific_scene_drilldown_v01354.py scientific_scene_linking_comparative_context_v01355.py reproducible_visual_analysis_sessions_v01356.py visual_research_narrative_findings_v01357.py research_review_critique_revision_v01358.py graph_studio_canonical_runtime_v013581.py graph_studio_renderer_replacement_v013582.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-renderer/v013582/health")"; legacy="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-canonical-runtime/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$current" "$legacy" "$core" <<'PYHEALTH'
import json,sys,re
cur,nav,core=[json.loads(z) for z in sys.argv[1:]]
assert cur.get('ok') is True and cur.get('version')=='0.135.8.2' and cur.get('api_route_count')==24 and cur.get('primary_renderer_owner')=='graph-studio-renderer-v013582' and cur.get('legacy_graph_studio_execution_allowed') is False and cur.get('single_primary_viewport') is True
assert nav.get('ok') is True and nav.get('version')=='0.135.8.1'
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: v0.135.8.2 advanced renderer owns the primary viewport')
print('PASS: legacy Graph Studio execution disabled; v0.135.8.1 lifecycle retained')
print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app.graph_studio_renderer_replacement_v013582 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; req={p for p in paths if p.startswith('/v1/graph-studio-renderer/v013582')}; assert len(req)==24
assert asset_audit({'active_graph_studio_modules':['graph-studio-renderer-replacement-v013582']})['ok'] is True
assert asset_audit({'active_graph_studio_modules':['graph-studio-v0880']})['ok'] is False
assert dom_audit({'primary_viewports':1,'legacy_primary_canvases_visible':0,'stacked_research_surfaces_visible':0})['ok'] is True
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.8.2 renderer ownership and DOM acceptance fixtures')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.8.2 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
