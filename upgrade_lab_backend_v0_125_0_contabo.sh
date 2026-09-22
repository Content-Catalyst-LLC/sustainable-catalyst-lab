#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.125.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.125.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.125.0 — CAUSAL RESEARCH STUDIO II ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01250.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.125.0-$ts"; env_backup="/tmp/sc-lab-v0.125.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/causal_research_studio_v01250.py" ]] || { echo "ERROR: v0.125 causal module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; sens="$(curl -fsS "http://127.0.0.1:${PORT}/v1/sensitivity-global-uncertainty-analysis-studio/health")"; causal="$(curl -fsS "http://127.0.0.1:${PORT}/v1/causal-research-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$sens" "$causal" "$core" <<'PY'
import json,sys,re
h,s,c,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert s.get('ok') is True and s.get('version')=='0.124.0'; assert c.get('ok') is True and c.get('version')=='0.125.0'; assert c.get('method_family_count')==8 and c.get('automatic_causal_proof') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.124 Sensitivity Studio healthy'); print('PASS: Lab v0.125.0 Causal Research Studio II health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PY
docker exec -i "$CONTAINER" python - <<'PY'
from app.main import app
from app.causal_research_studio_v01250 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/causal-research-studio'; required={x for x in paths if x.startswith(base)}; assert len(required)>=28
rows=[]
for i in range(60):
 x=(i%10)/10; z=((i*7)%13)/13; t=1.0 if i%3 else 0.0; y=2+1.5*t+0.7*x-0.2*z
 rows.append({'t':t,'y':y,'x':x,'z':z,'post':1.0 if i>=30 else 0.0,'time':float(i),'treated_group':1.0 if i%2==0 else 0.0,'running':(i-30)/10})
study={'rows':rows,'treatment':'t','outcome':'y','covariates':['x','z']}
assert len(fit_propensity(study)['scores'])==60; assert estimate_matching(study)['causal_proof'] is False; assert estimate_weighting(study)['causal_proof'] is False
assert estimate_did({'rows':rows,'outcome':'y','treated':'treated_group','post':'post'})['parallel_trends_certified'] is False
assert estimate_its({'rows':rows,'outcome':'y','time':'time','post':'post'})['causal_proof'] is False
assert estimate_rd({'rows':rows,'outcome':'y','running':'running','cutoff':0,'bandwidth':2})['causal_proof'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'causal-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.125 required causal-research routes loaded'); print('PASS: causal estimators, diagnostics, boundaries, and Core fixtures'); print('PASS: no automatic causal proof, assumption satisfaction, scientific validity, or Core submission')
PY
echo "PASS - Sustainable Catalyst Lab v0.125.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
