#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> v0.73.0 Scientific Visualization Engine 2 & Unified Graph Contract"
node --check assets/js/modules/scientific-visualization-engine-v0730.js
node --check assets/js/modules/graph-studio-v0730.js
node --check assets/js/modules/scientific-visualization-engine-v0440.js
node --check assets/js/modules/advanced-visualization-front-door-v0710.js
node tests/test-v0730.js
php tests/test-v0730.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-scientific-visualization-engine-v0730.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l templates/lab-app.php >/dev/null

echo "==> governed backend + compatibility"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_visualization_engine_v0730.py \
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
    '/v1/visualization/v0730/health',
    '/v1/visualization/v0730/policies',
    '/v1/visualization/v0730/specs/normalize',
    '/v1/visualization/v0730/figures/normalize',
    '/v1/visualization/v0730/workspaces/build',
    '/v1/graph-studio/health',
}
missing=sorted(required-paths)
if missing: raise SystemExit('FAIL - missing FastAPI routes: '+', '.join(missing))
print('PASS - v0.73.0 FastAPI route topology')
PY

echo "==> release manifest integrity"
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.73.0'
assert m['featureVersion']=='0.73.0'
assert m['platformVersion']=='1.0.0'
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
    for rel,expected in m[section].items():
        p=Path(rel)
        if not p.is_file(): raise SystemExit(f'FAIL - missing manifest file {rel}')
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=expected: raise SystemExit(f'FAIL - manifest hash mismatch {rel}')
print(f"PASS - v0.73.0 release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY

echo "PASS - Lab v0.73.0 Scientific Visualization Engine 2, Unified Graph Contract & Graph Studio Renderer Architecture release gate"
