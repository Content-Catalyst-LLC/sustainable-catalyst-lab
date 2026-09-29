#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.123.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.123.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.123.0 — SIMULATION & MONTE CARLO RESEARCH STUDIO ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01230.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.123.0-$ts"; env_backup="/tmp/sc-lab-v0.123.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/simulation_monte_carlo_research_studio_v01230.py" ]] || { echo "ERROR: v0.123.0 Simulation Studio module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; bayes="$(curl -fsS "http://127.0.0.1:${PORT}/v1/bayesian-analysis-workbench/health")"; sim="$(curl -fsS "http://127.0.0.1:${PORT}/v1/simulation-monte-carlo-research-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$bayes" "$sim" "$core" <<'PYVERIFY'
import json,sys,re
h,b,s,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert b.get('ok') is True and b.get('version')=='0.122.0',b
assert s.get('ok') is True and s.get('version')=='0.123.0',s
assert s.get('sampling_design_count')==4 and s.get('automatic_convergence_certification') is False and s.get('automatic_evidence_promotion') is False,s
assert c.get('ok') is True,c
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert mm,c; assert tuple(map(int,mm.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.122 Bayesian Analysis Workbench II healthy')
print('PASS: Lab v0.123.0 Simulation & Monte Carlo Research Studio health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.simulation_monte_carlo_research_studio_v01230 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/simulation-monte-carlo-research-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/study/normalize',f'{base}/sampling/plan',f'{base}/compute-budget/plan',f'{base}/simulation/run',f'{base}/convergence/report',f'{base}/replication/report',f'{base}/parameter-sweep/plan',f'{base}/parameter-sweep/run',f'{base}/scenario-ensemble/run',f'{base}/uncertainty-propagation/run',f'{base}/threshold/report',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan',f'{base}/execution-lineage/plan'}
assert not(required-paths),sorted(required-paths)
model={'id':'deploy-decay','family':'declarative-expression','title':'Decay','definition':{'equation':'y = a * exp(-k*x)'},'variables':[{'symbol':'x','role':'input'},{'symbol':'y','role':'response'}],'parameters':[{'symbol':'a','role':'estimated','value':10},{'symbol':'k','role':'estimated','value':.3}],'constants':[],'datasetBindings':[]}
study={'id':'deploy-mc','title':'Deploy MC','model':model,'values':{'x':5},'uncertainInputs':[{'symbol':'a','distribution':'normal','mean':10,'stdDev':.5},{'symbol':'k','distribution':'normal','mean':.3,'stdDev':.02}],'design':{'method':'latin-hypercube','samples':32,'seed':11},'analysis':{'confidence':.95,'thresholds':[2.0]}}
r=run_simulation(study)['result']; assert r['observational_evidence'] is False and r['automatic_evidence_promotion'] is False
assert convergence_report({**study,'checkpoints':[16,32]})['convergence_certified'] is False
assert replication_report({**study,'seeds':[1,2]})['replication_stability_certified'] is False
assert run_parameter_sweep({'model':model,'values':{'x':5},'axes':[{'symbol':'a','values':[9,10]},{'symbol':'k','values':[.25,.35]}]})['summary']['count']==4
assert run_scenario_ensemble({'study':study,'scenarios':[{'id':'base','values':{'x':5}},{'id':'later','values':{'x':7}}]})['selected_scenario_id'] is None
assert build_core_object_plan({'session_id':'deployment-session','simulation_id':'sim-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.123 required Simulation & Monte Carlo Research Studio routes loaded')
print('PASS: Monte Carlo, convergence, replication, parameter-sweep, scenario, and Core fixtures')
print('PASS: no automatic convergence certification, scenario selection, evidence promotion, causal claims, scientific validity, or Core submission')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.123.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
