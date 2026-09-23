#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.6 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.6.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.6 — REPRODUCIBLE VISUAL ANALYSIS SESSIONS & INTERACTION LINEAGE ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01356.XXXXXX)"; cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.6-$ts"; env_backup="/tmp/sc-lab-v0.135.6.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; find "$tmp" -type d -exec chmod u+rwx {} +; find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in model_architecture_computational_provenance_graphs_v01352.py multi_view_scientific_analysis_canvas_v01353.py interactive_scientific_scene_drilldown_v01354.py scientific_scene_linking_comparative_context_v01355.py reproducible_visual_analysis_sessions_v01356.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; graph="$(curl -fsS "http://127.0.0.1:${PORT}/v1/model-architecture-provenance-graphs/health")"; canvas="$(curl -fsS "http://127.0.0.1:${PORT}/v1/multi-view-scientific-analysis-canvas/health")"; scene="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-scene-drilldown/health")"; context="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-scene-linking-comparative-context/health")"; current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/reproducible-visual-analysis-sessions/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$graph" "$canvas" "$scene" "$context" "$current" "$core" <<'PYHEALTH'
import json,sys,re
h,g,c,s,x,r,core=[json.loads(v) for v in sys.argv[1:]]
assert h.get('ok') is True; assert g.get('version')=='0.135.2'; assert c.get('version')=='0.135.3'; assert s.get('version')=='0.135.4'; assert x.get('version')=='0.135.5'
assert r.get('ok') is True and r.get('version')=='0.135.6' and r.get('event_type_count')==12 and r.get('session_state_count')==4 and r.get('checkpoint_kind_count')==5 and r.get('replay_mode_count')==3 and r.get('api_route_count')==52
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: retained Lab v0.135.2-v0.135.5 visual reasoning stack healthy'); print('PASS: Lab v0.135.6 session/interaction-lineage health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app.reproducible_visual_analysis_sessions_v01356 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; required={x for x in paths if x.startswith('/v1/reproducible-visual-analysis-sessions')}; assert len(required)==52
p={'events':[{'event_type':'focus','sequence':0,'target_ref':'figure:1'},{'event_type':'drill','sequence':1,'target_ref':'model:1'}]}; assert build_lineage(p)['lineage']['scientific_causality'] is False; assert replay_plan(p)['replay_mutates_science'] is False; assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.135.6 required routes and boundary fixtures')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.6 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
