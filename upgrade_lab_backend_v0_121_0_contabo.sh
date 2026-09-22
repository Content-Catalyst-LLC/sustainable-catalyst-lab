#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.121.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.121.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.121.0 — STATISTICAL MODELING & MODEL DIAGNOSTICS STUDIO ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01210.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.121.0-$ts"; env_backup="/tmp/sc-lab-v0.121.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/statistical_modeling_diagnostics_studio_v01210.py" ]] || { echo "ERROR: v0.121.0 modeling module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; eda="$(curl -fsS "http://127.0.0.1:${PORT}/v1/exploratory-data-analysis-studio/health")"; model="$(curl -fsS "http://127.0.0.1:${PORT}/v1/statistical-modeling-diagnostics-studio/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$eda" "$model" "$design" "$core" <<'PYVERIFY'
import json,sys,re
h,e,m,d,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert e.get('ok') is True and e.get('version')=='0.120.0',e
assert m.get('ok') is True and m.get('version')=='0.121.0',m
assert m.get('family_count')==3 and m.get('automatic_model_selection') is False and m.get('automatic_significance_labels') is False,m
assert d.get('ok') is True and d.get('version')=='0.114.0',d
assert c.get('ok') is True,c
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert mm,c; assert tuple(map(int,mm.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.120 Exploratory Data Analysis Studio healthy')
print('PASS: Lab v0.121.0 Statistical Modeling & Model Diagnostics Studio health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.statistical_modeling_diagnostics_studio_v01210 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/statistical-modeling-diagnostics-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/model/normalize',f'{base}/model/fit',f'{base}/coefficients/report',f'{base}/diagnostics/analyze',f'{base}/assumptions/audit',f'{base}/effects/report',f'{base}/predictions/evaluate',f'{base}/cross-validation/run',f'{base}/models/compare',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/export/plan',f'{base}/core-object/plan'}
assert not(required-paths),sorted(required-paths)
rows=[{'x1':1.,'x2':2.,'y':3.1},{'x1':2.,'x2':1.,'y':4.8},{'x1':3.,'x2':4.,'y':8.2},{'x1':4.,'x2':3.,'y':9.9},{'x1':5.,'x2':6.,'y':13.1},{'x1':6.,'x2':5.,'y':14.8},{'x1':7.,'x2':8.,'y':18.2},{'x1':8.,'x2':7.,'y':19.9}]
p={'dataset':{'id':'deploy-model','rows':rows},'model':{'id':'ols-deploy','family':'gaussian','estimator':'ols','features':['x1','x2'],'response':'y'}}
f=fit_model(p)['result']; assert f['automatic_model_selection'] is False and f['automatic_significance_labels'] is False
assert diagnose_model({**p,'result':f})['automatic_model_rejection'] is False
assert assumption_audit({**p,'result':f})['automatic_assumption_pass_fail'] is False
assert effect_report({'result':f})['automatic_significance_labels'] is False
assert cross_validate_model({**p,'folds':4})['validation']['automatic_model_selection'] is False
assert build_core_object_plan({'session_id':'deployment-session','model_id':'ols-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.121 required modeling/diagnostics routes loaded')
print('PASS: fit, diagnostics, effects, assumptions, CV, and Core fixtures')
print('PASS: no automatic model selection, significance labels, causal claims, scientific validity, or Core submission')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.121.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
