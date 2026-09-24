#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> Integrated uncertainty + sensitivity + probabilistic visualization regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_probabilistic_analysis_v0480.py \
  backend/tests/test_graph_studio_v0470.py \
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

node tests/test-v0480.js
php tests/test-v0480.php
php tests/test-v0480-integrity-runtime.php
node --check assets/js/modules/probabilistic-analysis-v0480.js
node --check assets/js/modules/model-studio-v0460.js
node --check assets/js/modules/graph-studio-v0470.js
node --check assets/js/modules/scientific-visualization-engine-v0440.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-probabilistic-analysis-v0480.php >/dev/null
php -l includes/class-sc-lab-python-compute-core-v0261.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/probabilistic_analysis.py backend/app/model_studio.py backend/app/graph_studio.py backend/app/response_surfaces.py backend/app/dynamic_systems.py backend/app/model_diagnostics.py backend/app/equation_builder.py backend/app/main.py

PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
r=c.get('/v1/model-studio/probabilistic/health')
assert r.status_code==200 and r.json()['version']=='0.48.0', r.text
assert r.json()['saltelliSobolSensitivity'] is True and r.json()['arbitraryCode'] is False
r=c.get('/v1/model-studio/probabilistic/policies')
assert r.status_code==200 and r.json()['studySchema']=='sc-lab-probabilistic-study/0.48.0', r.text
model={'family':'declarative-expression','title':'Release gate model','definition':{'equation':'y = a*exp(-k*x)'},'variables':[{'symbol':'x','role':'input','unit':'s'},{'symbol':'y','role':'response','unit':'mg/L'}],'parameters':[{'symbol':'a','role':'estimated','value':10},{'symbol':'k','role':'estimated','value':0.3}],'constants':[],'datasetBindings':[]}
study={'title':'Release gate uncertainty','model':model,'values':{'x':5},'uncertainInputs':[{'symbol':'a','distribution':'normal','mean':10,'stdDev':0.5},{'symbol':'k','distribution':'normal','mean':0.3,'stdDev':0.02}],'design':{'method':'latin-hypercube','samples':128,'seed':42},'analysis':{'confidence':0.95,'thresholds':[2]},'curve':{'xSymbol':'x','start':0,'stop':8,'points':11}}
r=c.post('/v1/model-studio/probabilistic/normalize',json=study)
assert r.status_code==200 and r.json()['study']['schema']=='sc-lab-probabilistic-study/0.48.0', r.text
r=c.post('/v1/model-studio/probabilistic/analyze',json=study)
assert r.status_code==200, r.text
j=r.json()['result']
assert j['schema']=='sc-lab-probabilistic-analysis/0.48.0'
assert set(j['graphs'])=={'distribution','cdf','sensitivity','uncertaintyBand'}
assert len(j['graphs']['uncertaintyBand']['series'][0]['points'])==11
assert j['summary']['count']==128
print('PASS - FastAPI v0.48 probabilistic routes')
PY

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib, json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.48.0'
assert m['featureVersion']=='0.48.0'
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

echo "PASS - Lab v0.48.0 Integrated Uncertainty, Sensitivity & Probabilistic Visualization release gate"
