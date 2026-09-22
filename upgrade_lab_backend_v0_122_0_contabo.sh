#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.122.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.122.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.122.0 — BAYESIAN ANALYSIS WORKBENCH II ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01220.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.122.0-$ts"; env_backup="/tmp/sc-lab-v0.122.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/bayesian_analysis_workbench_v01220.py" ]] || { echo "ERROR: v0.122.0 Bayesian Workbench module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; model="$(curl -fsS "http://127.0.0.1:${PORT}/v1/statistical-modeling-diagnostics-studio/health")"; bayes="$(curl -fsS "http://127.0.0.1:${PORT}/v1/bayesian-analysis-workbench/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$model" "$bayes" "$core" <<'PYVERIFY'
import json,sys,re
h,m,b,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert m.get('ok') is True and m.get('version')=='0.121.0',m
assert b.get('ok') is True and b.get('version')=='0.122.0',b
assert b.get('family_count')==3 and b.get('automatic_prior_selection') is False and b.get('automatic_convergence_certification') is False,b
assert c.get('ok') is True,c
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert mm,c; assert tuple(map(int,mm.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.121 Statistical Modeling & Model Diagnostics Studio healthy')
print('PASS: Lab v0.122.0 Bayesian Analysis Workbench II health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.bayesian_analysis_workbench_v01220 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/bayesian-analysis-workbench'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/analysis/normalize',f'{base}/posterior/fit',f'{base}/prior-posterior/report',f'{base}/diagnostics/sampler',f'{base}/convergence/audit',f'{base}/posterior-predictive/report',f'{base}/probability/report',f'{base}/hierarchical/fit',f'{base}/hierarchical/summary',f'{base}/models/compare',f'{base}/visualization/plan',f'{base}/workbench/build',f'{base}/snapshot/build',f'{base}/reproduction/plan',f'{base}/export/plan',f'{base}/core-object/plan'}
assert not(required-paths),sorted(required-paths)
rows=[{'x':i/4.0,'y':1.2+1.8*(i/4.0)+((i%4)-1.5)*0.08} for i in range(20)]
p={'dataset':{'id':'deploy-bayes','rows':rows},'study':{'id':'bayes-deploy','family':'gaussian','features':['x'],'response':'y','chains':2,'draws':60,'warmup':30,'posteriorPredictiveDraws':30,'seed':11}}
f=fit_posterior(p)['result']; assert f['automatic_prior_selection'] is False and f['automatic_convergence_certification'] is False
assert prior_posterior_report({'result':f})['automatic_prior_selection'] is False
assert convergence_audit({'result':f})['convergence_certified'] is False
assert probability_report({'result':f,'queries':[{'term':'z(x)','threshold':0,'direction':'greater-than'}]})['automatic_decision'] is False
h=fit_hierarchical_normal({'hierarchical':{'id':'h','draws':400,'seed':3},'units':[{'id':'a','estimate':.2,'standard_error':.15},{'id':'b','estimate':.7,'standard_error':.2},{'id':'c','estimate':1.1,'standard_error':.18}]}); assert h['automatic_generalization'] is False
assert build_core_object_plan({'session_id':'deployment-session','model_id':'bayes-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.122 required Bayesian Workbench routes loaded')
print('PASS: posterior, convergence, probability, hierarchical, and Core fixtures')
print('PASS: no automatic prior/model selection, convergence certification, causal claims, generalization, scientific validity, or Core submission')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.122.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
