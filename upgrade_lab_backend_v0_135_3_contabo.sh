#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.3 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.3.zip}"; CONTAINER="sc-lab"; PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.3 — MULTI-VIEW SCIENTIFIC ANALYSIS CANVAS ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01353.XXXXXX)"
cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.3-$ts"; env_backup="/tmp/sc-lab-v0.135.3.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
find "$tmp" -type d -exec chmod u+rwx {} +
find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/model_architecture_computational_provenance_graphs_v01352.py" ]] || { echo "ERROR: retained v0.135.2 graph module missing" >&2; exit 1; }
[[ -f "$source_backend/app/multi_view_scientific_analysis_canvas_v01353.py" ]] || { echo "ERROR: v0.135.3 multi-view canvas module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/model-architecture-provenance-graphs/health")"; current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/multi-view-scientific-analysis-canvas/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$current" "$core" <<'PYHEALTH'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'
assert p.get('ok') is True and p.get('version')=='0.135.2'
assert r.get('ok') is True and r.get('version')=='0.135.3'
assert r.get('panel_type_count')==10 and r.get('layout_mode_count')==5 and r.get('interaction_channel_count')==8
assert r.get('selection_mutates_scientific_record') is False and r.get('automatic_join_inference') is False and r.get('automatic_core_submission') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version','')))
assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.135.2 Model Architecture & Computational Provenance Graphs healthy')
print('PASS: Lab v0.135.3 Multi-View Scientific Analysis Canvas health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app.multi_view_scientific_analysis_canvas_v01353 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/multi-view-scientific-analysis-canvas')}; assert len(required)==41
p={'panels':[{'panel_id':'fig','panel_type':'primary-figure','object_refs':['figure:1']},{'panel_id':'diag','panel_type':'diagnostics','object_refs':['diagnostic:1']}],'links':[{'source_panel':'fig','target_panel':'diag','channel':'select','mapping_ref':'map:1'}]}
assert compose_canvas(p)['linked_selection_enabled'] is True
assert selection_link({'selection':{'items':[{'row_ref':'r1'}]},'target_panel_ids':['diag']})['automatic_join_inference'] is False
assert filter_apply({'filter':{'field':'x','operator':'gte','value':2},'rows':[{'x':1},{'x':2}]})['matched_row_indices']==[1]
assert core_object_plan({'canvas_refs':['c']})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.3 required multi-view canvas routes loaded')
print('PASS: composition, linked selection, non-mutating filters, and Core fixtures')
print('PASS: no source mutation, inferred joins, automatic validity/evidence/probability interpretation, truth determination, or Core submission')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.3 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
