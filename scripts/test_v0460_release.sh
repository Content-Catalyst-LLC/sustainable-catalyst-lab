#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> Response Surfaces + Optimization + Design-Space Exploration + modeling regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_response_surfaces_v0460.py \
  backend/tests/test_model_studio_v0460.py \
  backend/tests/test_dynamic_systems_v0450.py \
  backend/tests/test_model_studio_v0450.py \
  backend/tests/test_model_studio_v0440.py \
  backend/tests/test_model_diagnostics_v0430.py \
  backend/tests/test_model_studio_v0430.py \
  backend/tests/test_model_studio_v0420.py \
  backend/tests/test_equation_builder_v0420.py \
  backend/tests/test_model_studio_v0410.py \
  backend/tests/test_model_calibration_v0302.py \
  backend/tests/test_scientific_visualization_v0274.py \
  backend/tests/test_design_studies_v0301.py \
  backend/tests/test_model_registry_v0340.py \
  backend/tests/test_ensemble_uncertainty_v0341.py \
  backend/tests/test_surrogate_reduced_order_v0342.py

node tests/test-v0460.js
php tests/test-v0460.php
php tests/test-v0460-integrity-runtime.php
node --check assets/js/modules/scientific-visualization-engine-v0440.js
node --check assets/js/modules/model-studio-v0460.js
node --check assets/js/modules/numerical-visualization-studio.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-model-studio-v0460.php >/dev/null
php -l includes/class-sc-lab-python-compute-core-v0261.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/response_surfaces.py backend/app/dynamic_systems.py backend/app/model_diagnostics.py backend/app/equation_builder.py backend/app/model_studio.py backend/app/main.py

PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
r=c.get('/v1/model-studio/response-surfaces/health')
assert r.status_code==200 and r.json()['version']=='0.46.0', r.text
study={'title':'Release gate RSM','factors':[{'symbol':'T','low':20,'high':80},{'symbol':'P','low':1,'high':9}],'response':{'symbol':'Yield'}}
rows=[]
for T in (20,50,80):
    for P in (1,5,9):
        x=(T-50)/30; y=(P-5)/4
        rows.append({'T':T,'P':P,'Yield':100-10*x*x-5*y*y+2*x-y+1.5*x*y})
rows += [{'T':50,'P':5,'Yield':100.1},{'T':50,'P':5,'Yield':99.9}]
r=c.post('/v1/model-studio/response-surfaces/fit',json={'study':study,'rows':rows})
assert r.status_code==200, r.text
result=r.json()['result']
assert result['metrics']['r2']>0.999
r=c.post('/v1/model-studio/response-surfaces/explore',json={'result':result,'xFactor':'T','yFactor':'P','gridSize':15,'responseConstraint':{'minimum':90}})
assert r.status_code==200 and r.json()['exploration']['totalCells']==225, r.text
r=c.post('/v1/model-studio/response-surfaces/optimize',json={'result':result,'goal':'maximize','seed':42,'maxIterations':80})
assert r.status_code==200 and r.json()['optimization']['predictedResponse']>99, r.text
print('PASS - FastAPI response-surface routes')
PY

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib, json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.46.0'
assert m['featureVersion']=='0.46.0'
assert m['platformVersion']=='1.0.0'
errors=[]
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
    for rel, expected in m.get(section,{}).items():
        p=Path(rel)
        if not p.is_file(): errors.append(f'missing {rel}'); continue
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected: errors.append(f'hash mismatch {rel}')
if errors:
    raise SystemExit('FAIL - release manifest integrity\n'+'\n'.join(errors[:40]))
print(f"PASS - release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY

echo "PASS - Lab v0.46.0 Response Surfaces, Optimization & Design-Space Exploration release gate"
