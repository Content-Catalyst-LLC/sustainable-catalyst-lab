#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> Graph Studio + Scientific Figure Workspace + modeling regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
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

node tests/test-v0470.js
php tests/test-v0470.php
php tests/test-v0470-integrity-runtime.php
node --check assets/js/modules/scientific-visualization-engine-v0440.js
node --check assets/js/modules/model-studio-v0460.js
node --check assets/js/modules/graph-studio-v0470.js
node --check assets/js/modules/interface-reorganization-v0470.js
node --check assets/js/modules/numerical-visualization-studio.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-model-studio-v0460.php >/dev/null
php -l includes/class-sc-lab-graph-studio-v0470.php >/dev/null
php -l includes/class-sc-lab-python-compute-core-v0261.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/graph_studio.py backend/app/response_surfaces.py backend/app/dynamic_systems.py backend/app/model_diagnostics.py backend/app/equation_builder.py backend/app/model_studio.py backend/app/main.py

PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
r=c.get('/v1/graph-studio/health')
assert r.status_code==200 and r.json()['version']=='0.47.0', r.text
assert r.json()['figureWorkspace'] is True and r.json()['arbitraryCode'] is False
r=c.get('/v1/graph-studio/policies')
assert r.status_code==200 and r.json()['figureSchema']=='sc-lab-scientific-figure/0.47.0', r.text
graph={
  'schema':'sc-lab-scientific-graph/0.46.0',
  'kind':'line-scatter',
  'title':'Release gate figure',
  'xLabel':'Input (s)',
  'yLabel':'Response (K)',
  'series':[{'id':'observed','label':'Observed','mode':'scatter','points':[{'x':0,'y':2},{'x':1,'y':3.5},{'x':2,'y':5}]}],
  'publication':{'caption':'Graph Studio release gate','source':'Synthetic release-gate data','method':'Deterministic fixture'}
}
r=c.post('/v1/graph-studio/graphs/normalize',json={'graph':graph})
assert r.status_code==200 and r.json()['graph']['title']=='Release gate figure', r.text
r=c.post('/v1/graph-studio/figures/normalize',json={'figure':{'title':'Figure 1','graph':graph,'sourceContext':'release-gate'}})
assert r.status_code==200 and r.json()['figure']['schema']=='sc-lab-scientific-figure/0.47.0', r.text
fig=r.json()['figure']
r=c.post('/v1/graph-studio/workspaces/build',json={'title':'Release gate workspace','figures':[fig]})
assert r.status_code==200 and r.json()['workspace']['schema']=='sc-lab-figure-workspace/0.47.0', r.text
assert len(r.json()['workspace']['figures'])==1
print('PASS - FastAPI Graph Studio routes')
PY

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib, json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.47.0'
assert m['featureVersion']=='0.47.0'
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

echo "PASS - Lab v0.47.0 Graph Studio, Scientific Figure Workspace & Interface Reorganization release gate"
