#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.5 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.5.zip}"; CONTAINER="sc-lab"; PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.5 — SCIENTIFIC SCENE LINKING, COMPARATIVE INSPECTION & CONTEXT PRESERVATION ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01355.XXXXXX)"
cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.5-$ts"; env_backup="/tmp/sc-lab-v0.135.5.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
find "$tmp" -type d -exec chmod u+rwx {} +
find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/model_architecture_computational_provenance_graphs_v01352.py" ]] || { echo "ERROR: retained v0.135.2 graph module missing" >&2; exit 1; }
[[ -f "$source_backend/app/multi_view_scientific_analysis_canvas_v01353.py" ]] || { echo "ERROR: retained v0.135.3 multi-view canvas module missing" >&2; exit 1; }
[[ -f "$source_backend/app/interactive_scientific_scene_drilldown_v01354.py" ]] || { echo "ERROR: retained v0.135.4 interactive scene/drill-down module missing" >&2; exit 1; }
[[ -f "$source_backend/app/scientific_scene_linking_comparative_context_v01355.py" ]] || { echo "ERROR: v0.135.5 scene-linking/comparative-context module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
graph="$(curl -fsS "http://127.0.0.1:${PORT}/v1/model-architecture-provenance-graphs/health")"
canvas="$(curl -fsS "http://127.0.0.1:${PORT}/v1/multi-view-scientific-analysis-canvas/health")"
scene="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-scene-drilldown/health")"
current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-scene-linking-comparative-context/health")"
core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$graph" "$canvas" "$scene" "$current" "$core" <<'PYHEALTH'
import json,sys,re
h,g,c,s,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'
assert g.get('ok') is True and g.get('version')=='0.135.2'
assert c.get('ok') is True and c.get('version')=='0.135.3'
assert s.get('ok') is True and s.get('version')=='0.135.4'
assert r.get('ok') is True and r.get('version')=='0.135.5'
assert r.get('link_type_count')==10 and r.get('compare_mode_count')==6 and r.get('context_family_count')==12 and r.get('pin_state_count')==3 and r.get('api_route_count')==48
assert r.get('presentation_state_mutates_scientific_record') is False and r.get('automatic_equivalence_inference') is False and r.get('automatic_join_inference') is False and r.get('automatic_core_submission') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version','')))
assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.135.2 computational provenance graph healthy')
print('PASS: retained v0.135.3 multi-view scientific analysis canvas healthy')
print('PASS: retained v0.135.4 interactive scientific scene/drill-down healthy')
print('PASS: Lab v0.135.5 scene-linking/comparative-context health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app.scientific_scene_linking_comparative_context_v01355 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/scientific-scene-linking-comparative-context')}; assert len(required)==48
l=normalize_link({'link_type':'derived-from','source_ref':'figure:1','target_ref':'model:1'})['link']; assert l['declared'] is True
c=comparison_plan({'object_refs':['model:a','model:b'],'compare_mode':'side-by-side'}); assert c['automatic_equivalence_inference'] is False
ctx=preserve_context({'source_ref':'model:a','context':{'focus':{'ref':'model:a'},'provenance':{'refs':['p:1']}}}); assert ctx['scientific_record_mutated'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
assert core_object_plan({})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.5 required scene-linking/comparative-context routes loaded')
print('PASS: explicit links, comparison guards, context preservation, snapshots, handoffs, and Core fixtures')
print('PASS: no source mutation, equivalence/join/causal inference, evidence weighting, truth determination, or Core submission')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.5 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
