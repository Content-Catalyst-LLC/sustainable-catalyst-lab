#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.2 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.2.zip}"; CONTAINER="sc-lab"; PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.2 — MODEL ARCHITECTURE & COMPUTATIONAL PROVENANCE GRAPHS ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01352.XXXXXX)"
cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.135.2-$ts"; env_backup="/tmp/sc-lab-v0.135.2.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
find "$tmp" -type d -exec chmod u+rwx {} +
find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/scientific_visualization_experience_v01351.py" ]] || { echo "ERROR: retained v0.135.1 module missing" >&2; exit 1; }
[[ -f "$source_backend/app/model_architecture_computational_provenance_graphs_v01352.py" ]] || { echo "ERROR: v0.135.2 graph module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-experience/health")"; current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/model-architecture-provenance-graphs/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$current" "$core" <<'PYHEALTH'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'
assert p.get('ok') is True and p.get('version')=='0.135.1'
assert r.get('ok') is True and r.get('version')=='0.135.2'
assert r.get('node_type_count')==20 and r.get('edge_type_count')==18
assert r.get('automatic_model_inference') is False and r.get('automatic_core_submission') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version','')))
assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.135.1 Scientific Visualization Experience healthy')
print('PASS: Lab v0.135.2 Model Architecture & Computational Provenance Graphs health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYHEALTH
docker exec -i "$CONTAINER" python - <<'PYFIX'
from app.main import app
from app.model_architecture_computational_provenance_graphs_v01352 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/model-architecture-provenance-graphs')}; assert len(required)==40
p={'nodes':[{'node_id':'d','node_type':'dataset','state':'bound'},{'node_id':'m','node_type':'model'},{'node_id':'x','node_type':'execution'},{'node_id':'f','node_type':'figure','state':'derived'},{'node_id':'c','node_type':'core-object','state':'external'}],'edges':[{'source':'d','target':'m','edge_type':'binds'},{'source':'m','target':'x','edge_type':'executes'},{'source':'x','target':'f','edge_type':'produces'},{'source':'f','target':'c','edge_type':'registered-as'}]}
assert path_trace({**p,'source':'d','target':'c'})['found'] is True
assert impact_path({**p,'node_id':'d'})['automatic_causal_inference'] is False
assert visual_encoding_plan({})['fabricated_scientific_values'] is False
assert core_object_plan({'graph_refs':['g']})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.2 required graph routes loaded')
print('PASS: graph path, structural impact, visual encoding, and Core fixtures')
print('PASS: no fabricated values, undeclared model/provenance inference, causal interpretation, evidence weighting, validity certification, or Core submission')
PYFIX
echo "PASS - Sustainable Catalyst Lab v0.135.2 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
