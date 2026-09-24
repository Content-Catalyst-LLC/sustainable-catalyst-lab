#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }
echo "==> v0.80.0 Spatial, Geospatial & Raster Visualization"
node --check assets/js/modules/spatial-geospatial-raster-v0800.js
node --check assets/js/modules/graph-studio-v0800.js
node tests/test-v0800.js
php tests/test-v0800.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-spatial-geospatial-raster-v0800.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l templates/lab-app.php >/dev/null
bash -n scripts/test_release_current.sh
[[ $(wc -l < scripts/test_release_current.sh) -eq 410 ]] || { echo "FAIL - established 410-line current-release harness changed" >&2; exit 1; }
echo "==> governed backend + compatibility"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_spatial_geospatial_raster_v0800.py backend/tests/test_linked_views_v0790.py backend/tests/test_time_parameter_space_v0780.py backend/tests/test_scientific_scene_v0770.py backend/tests/test_large_data_visualization_v0760.py backend/tests/test_scientific_data_binding_v0750.py backend/tests/test_visualization_engine_v0740.py backend/tests/test_visualization_engine_v0730.py backend/tests/test_data_transformations_v0550.py backend/tests/test_graph_studio_v0470.py backend/tests/test_reproducible_model_package_v0500.py backend/tests/test_scientific_workflow_composer_v0570.py backend/tests/test_model_studio_v0460.py backend/tests/test_preregistration_v0700.py
echo "==> FastAPI visualization route registration"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PY2'
from app.main import app
paths={r.path for r in app.routes}
required={'/v1/visualization/v0800/health','/v1/visualization/v0800/policies','/v1/visualization/v0800/crs/normalize','/v1/visualization/v0800/viewports/normalize','/v1/visualization/v0800/vectors/normalize','/v1/visualization/v0800/rasters/normalize','/v1/visualization/v0800/selections/bbox','/v1/visualization/v0800/figures/build','/v1/visualization/v0800/workspaces/build','/v1/visualization/v0790/health','/v1/visualization/v0780/health','/v1/visualization/v0770/health','/v1/visualization/v0760/health','/v1/visualization/v0750/health'}
missing=sorted(required-paths)
if missing: raise SystemExit('FAIL - missing FastAPI routes: '+', '.join(missing))
print('PASS - v0.80.0 FastAPI route topology')
PY2
echo "==> contract validation"
"$PYTHON_BIN" - <<'PY2'
from pathlib import Path
import json
names=['spatial-crs-v0800.schema.json','spatial-vector-layer-v0800.schema.json','spatial-raster-v0800.schema.json','spatial-viewport-v0800.schema.json','spatial-figure-v0800.schema.json','figure-workspace-v0800.schema.json','spatial-visualization-policy-v0800.json']
for base in ('contracts','backend/contracts'):
 for name in names: json.loads(Path(base,name).read_text())
print('PASS - v0.80.0 JSON contracts')
PY2
echo "==> release manifest integrity"
"$PYTHON_BIN" - <<'PY2'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.80.0' and m['featureVersion']=='0.80.0' and m['platformVersion']=='1.0.0'
pat=re.compile(r'(^|/)(?:\.pytest_cache|__pycache__|\.venv[^/]*)($|/)|^backend/data/|^data/')
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  if pat.search(rel): raise SystemExit('FAIL - mutable runtime/cache path in manifest: '+rel)
  p=Path(rel)
  if not p.is_file(): raise SystemExit('FAIL - missing manifest file '+rel)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise SystemExit('FAIL - manifest hash mismatch '+rel)
print(f"PASS - v0.80.0 release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY2
echo "PASS - Lab v0.80.0 Spatial, Geospatial & Raster Visualization release gate"
