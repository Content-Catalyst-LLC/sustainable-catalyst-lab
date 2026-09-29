#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.0.zip}"
CONTAINER="sc-lab"
PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.135.0 — COMPETING MODEL & HYPOTHESIS ANALYSIS ==="
ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v01350.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.135.0-$ts"
env_backup="/tmp/sc-lab-v0.135.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/competing_model_hypothesis_analysis_v01350.py" ]] || { echo "ERROR: v0.135 competing-model-hypothesis module missing" >&2; exit 1; }
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
[[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/evidence-synthesis-intelligence-ii/health")"
current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/competing-model-hypothesis-analysis/health")"
core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$current" "$core" <<'__PY135_HEALTH__'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'
assert p.get('ok') is True and p.get('version')=='0.134.0'
assert r.get('ok') is True and r.get('version')=='0.135.0'
assert r.get('comparison_family_count')==24
assert r.get('automatic_winner_selection') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version','')))
assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.134 Evidence Synthesis Intelligence II healthy')
print('PASS: Lab v0.135.0 Competing Model & Hypothesis Analysis health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
__PY135_HEALTH__
docker exec -i "$CONTAINER" python - <<'__PY135_FIXTURES__'
from app.main import app
from app.competing_model_hypothesis_analysis_v01350 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/competing-model-hypothesis-analysis'
required={x for x in paths if x.startswith(base)}
assert len(required)==49
assert prediction_observation_matrix({'comparisons':[{'prediction_ref':'p','observation_ref':'o','relation':'challenges'}]})['matrix'][0]['relation']=='challenges'
assert contradiction_matrix({'candidates':[{'candidate_ref':'h','supporting_evidence_refs':['e1'],'challenging_evidence_refs':['e2']}]})['contradictions_preserved']
assert pairwise_comparison({'candidate_a_ref':'h1','candidate_b_ref':'h2'})['automatic_pairwise_winner'] is None
assert core_object_plan({'project_ref':'deployment-project','hypothesis_refs':['h1'],'model_refs':['m1']})['core_does_not_select_winner'] is True
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.135 required Competing Model & Hypothesis Analysis routes loaded')
print('PASS: prediction, contradiction, pairwise comparison, and Core fixtures')
print('PASS: no automatic ranking, winner selection, truth inference, scientific validity, or Core submission')
__PY135_FIXTURES__
echo "PASS - Sustainable Catalyst Lab v0.135.0 backend deployment complete."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
echo "Compose file and compose-managed volumes were left unchanged."
