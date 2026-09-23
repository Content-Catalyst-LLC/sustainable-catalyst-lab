#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.1 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.1.zip}"
CONTAINER="sc-lab"
PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo "=== LAB v0.135.1 — SCIENTIFIC VISUALIZATION EXPERIENCE OVERHAUL ==="
ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v01351.XXXXXX)"
cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }
trap cleanup EXIT
backup="$BASE/backend.before-v0.135.1-$ts"
env_backup="/tmp/sc-lab-v0.135.1.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
# Defensive normalization for ZIP permission metadata on Linux/macOS-produced archives.
find "$tmp" -type d -exec chmod u+rwx {} +
find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found in archive" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/scientific_visualization_experience_v01351.py" ]] || { echo "ERROR: v0.135.1 visualization-experience module missing" >&2; exit 1; }
[[ -f "$source_backend/app/competing_model_hypothesis_analysis_v01350.py" ]] || { echo "ERROR: retained v0.135.0 comparison module missing" >&2; exit 1; }
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
  [[ "$state" == healthy ]] && { healthy=1; break; }
  [[ "$state" =~ unhealthy|exited|dead ]] && exit 1
  sleep 2
done
[[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/competing-model-hypothesis-analysis/health")"
current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-experience/health")"
core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$current" "$core" <<'__PY1351_HEALTH__'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'
assert p.get('ok') is True and p.get('version')=='0.135.0'
assert r.get('ok') is True and r.get('version')=='0.135.1'
assert r.get('panel_family_count')==12
assert r.get('capability_family_count')==12
assert r.get('fabricated_scientific_values') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version','')))
assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.135.0 Competing Model & Hypothesis Analysis healthy')
print('PASS: Lab v0.135.1 Scientific Visualization Experience health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
__PY1351_HEALTH__
docker exec -i "$CONTAINER" python - <<'__PY1351_FIXTURES__'
from app.main import app
from app.scientific_visualization_experience_v01351 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
required={x for x in paths if x.startswith('/v1/scientific-visualization-experience')}
assert len(required)==32
assert compose_workspace({})['workspace']['panel_count']==12
assert analytical_panels_plan({'bindings':{}})['fabricate_missing_scientific_values'] is False
assert model_architecture_graph({})['graph']['automatic_model_inference'] is False
assert linked_view_plan({})['automatic_join_inference'] is False
assert core_visual_object_plan({'figure_refs':['figure:deployment']})['lab_owns_scientific_rendering'] is True
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135.1 required Scientific Visualization Experience routes loaded')
print('PASS: workspace, missing-state, architecture, linked-view, and Core fixtures')
print('PASS: no fabricated scientific values, automatic interpretation, evidence promotion, scientific validity, or Core submission')
__PY1351_FIXTURES__
echo "PASS - Sustainable Catalyst Lab v0.135.1 backend deployment complete."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volumes were left unchanged."
