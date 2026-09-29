#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.124.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.124.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.124.0 — SENSITIVITY & GLOBAL UNCERTAINTY ANALYSIS STUDIO ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01240.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.124.0-$ts"; env_backup="/tmp/sc-lab-v0.124.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/sensitivity_global_uncertainty_analysis_studio_v01240.py" ]] || { echo "ERROR: v0.124.0 sensitivity module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; sim="$(curl -fsS "http://127.0.0.1:${PORT}/v1/simulation-monte-carlo-research-studio/health")"; sens="$(curl -fsS "http://127.0.0.1:${PORT}/v1/sensitivity-global-uncertainty-analysis-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$sim" "$sens" "$core" <<'PYVERIFY'
import json,sys,re
h,s,sa,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert s.get('ok') is True and s.get('version')=='0.123.0',s
assert sa.get('ok') is True and sa.get('version')=='0.124.0',sa
assert sa.get('method_family_count')==6 and sa.get('automatic_parameter_ranking') is False and sa.get('automatic_causal_inference') is False,sa
assert c.get('ok') is True,c
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert mm,c; assert tuple(map(int,mm.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.123 Simulation & Monte Carlo Research Studio healthy')
print('PASS: Lab v0.124.0 Sensitivity & Global Uncertainty Analysis Studio health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.sensitivity_global_uncertainty_analysis_studio_v01240 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/sensitivity-global-uncertainty-analysis-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/study/normalize',f'{base}/sobol/report',f'{base}/morris/report',f'{base}/correlation-screening/report',f'{base}/variance-decomposition/report',f'{base}/interaction-screening/report',f'{base}/response-surface/plan',f'{base}/response-surface/run',f'{base}/convergence/report',f'{base}/replication/report',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan',f'{base}/execution-lineage/plan',f'{base}/interpretation-boundaries/report'}
assert not(required-paths),sorted(required-paths)
model={'id':'deploy-sensitivity','family':'declarative-expression','title':'Sensitivity','definition':{'equation':'y = a*x + b*x*x + a*b'},'variables':[{'symbol':'x','role':'input'},{'symbol':'y','role':'response'}],'parameters':[{'symbol':'a','role':'estimated','value':2},{'symbol':'b','role':'estimated','value':.5}],'constants':[],'datasetBindings':[]}
study={'id':'deploy-sens','title':'Deploy Sensitivity','model':model,'values':{'x':3},'uncertainInputs':[{'symbol':'a','distribution':'uniform','low':1,'high':3},{'symbol':'b','distribution':'uniform','low':.1,'high':1}],'design':{'method':'latin-hypercube','samples':32,'seed':11},'analysis':{'confidence':.95}}
assert len(sobol_report({**study,'base_samples':32})['indices'])==2
assert len(morris_report({**study,'trajectories':6})['effects'])==2
assert variance_decomposition_report({**study,'base_samples':32})['automatic_interaction_proof'] is False
assert len(interaction_screening_report({**study,'samples':64})['pairs'])==1
assert response_surface_run({'model':model,'values':{'x':3},'axes':[{'symbol':'a','values':[1,2,3]},{'symbol':'b','values':[.1,.5,1]}]})['automatic_optimum_selection'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'sensitivity-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.124 required sensitivity/global-uncertainty routes loaded')
print('PASS: Sobol, Morris, variance, interaction, response-surface, and Core fixtures')
print('PASS: no automatic parameter ranking, significance inference, causal claims, scientific validity, or Core submission')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.124.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
