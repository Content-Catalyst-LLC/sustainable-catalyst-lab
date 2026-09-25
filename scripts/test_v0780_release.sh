#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }
echo "==> v0.78.0 4D, Time & Parameter-Space Visualization"
node --check assets/js/modules/time-parameter-space-v0780.js
node --check assets/js/modules/graph-studio-v0780.js
node tests/test-v0780.js
php tests/test-v0780.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-time-parameter-space-v0780.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l templates/lab-app.php >/dev/null
bash -n scripts/test_release_current.sh
[[ $(wc -l < scripts/test_release_current.sh) -eq 410 ]] || { echo "FAIL - established 410-line current-release harness changed" >&2; exit 1; }
echo "==> governed backend + compatibility"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_time_parameter_space_v0780.py \
  backend/tests/test_scientific_scene_v0770.py \
  backend/tests/test_large_data_visualization_v0760.py \
  backend/tests/test_scientific_data_binding_v0750.py \
  backend/tests/test_visualization_engine_v0740.py \
  backend/tests/test_visualization_engine_v0730.py \
  backend/tests/test_data_transformations_v0550.py \
  backend/tests/test_graph_studio_v0470.py \
  backend/tests/test_reproducible_model_package_v0500.py \
  backend/tests/test_scientific_workflow_composer_v0570.py \
  backend/tests/test_model_studio_v0460.py \
  backend/tests/test_preregistration_v0700.py
echo "==> FastAPI visualization route registration"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PY'
from app.main import app
paths={route.path for route in app.routes}
required={
 '/v1/visualization/v0780/health','/v1/visualization/v0780/policies','/v1/visualization/v0780/axes/normalize','/v1/visualization/v0780/projections/normalize','/v1/visualization/v0780/state-spaces/normalize','/v1/visualization/v0780/state-spaces/from-dataset','/v1/visualization/v0780/state-spaces/slice','/v1/visualization/v0780/figures/build','/v1/visualization/v0780/workspaces/build',
 '/v1/visualization/v0770/health','/v1/visualization/v0760/health','/v1/visualization/v0750/health','/v1/visualization/v0740/health','/v1/visualization/v0730/health','/v1/graph-studio/health'
}
missing=sorted(required-paths)
if missing: raise SystemExit('FAIL - missing FastAPI routes: '+', '.join(missing))
print('PASS - v0.78.0 FastAPI route topology')
PY
echo "==> contract validation"
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import json
names=['4d-state-space-v0780.schema.json','state-axis-v0780.schema.json','4d-projection-v0780.schema.json','scientific-visualization-v0780.schema.json','scientific-figure-v0780.schema.json','figure-workspace-v0780.schema.json','4d-time-parameter-policy-v0780.json']
for base in ('contracts','backend/contracts'):
 for name in names: json.loads(Path(base,name).read_text())
print('PASS - v0.78.0 JSON contracts')
PY
echo "==> release manifest integrity"
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.78.0' and m['featureVersion']=='0.78.0' and m['platformVersion']=='1.0.0'
pattern=re.compile(r'(^|/)(?:\.pytest_cache|__pycache__|\.venv[^/]*)($|/)|^backend/data/|^data/')
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel in m[section]:
  if pattern.search(rel): raise SystemExit('FAIL - mutable runtime/cache path present in release manifest: '+rel)
  p=Path(rel)
  if not p.is_file(): raise SystemExit('FAIL - missing manifest file '+rel)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=m[section][rel]: raise SystemExit('FAIL - manifest hash mismatch '+rel)
print(f"PASS - v0.78.0 release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY
echo "PASS - Lab v0.78.0 4D, Time & Parameter-Space Visualization release gate"
