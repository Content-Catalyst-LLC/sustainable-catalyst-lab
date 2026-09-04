#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"; [[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> v0.85.0 WebGL2 Scientific Renderer"
node --check assets/js/modules/webgl2-scientific-renderer-v0850.js
node --check assets/js/modules/graph-studio-v0850.js
node --check assets/js/modules/gpu-renderer-architecture-v0840.js
node --check assets/js/modules/release-console-v0821.js
node tests/test-v0850.js
php tests/test-v0850.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-webgl2-scientific-renderer-v0850.php >/dev/null
php -l includes/class-sc-lab-gpu-renderer-architecture-v0840.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php -l templates/lab-app.php >/dev/null
bash -n scripts/test_release_current.sh
[[ $(wc -l < scripts/test_release_current.sh) -eq 410 ]] || { echo "FAIL - established 410-line current-release harness changed" >&2; exit 1; }

echo "==> governed backend + compatibility"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_webgl2_scientific_renderer_v0850.py \
 backend/tests/test_gpu_renderer_architecture_v0840.py \
 backend/tests/test_provenance_aware_figures_v0830.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_annotation_measurement_markup_v0810.py \
 backend/tests/test_spatial_geospatial_raster_v0800.py \
 backend/tests/test_linked_views_v0790.py \
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
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" - <<'PY2'
from app.main import app
paths={r.path for r in app.routes}
required={
'/v1/visualization/v0850/health','/v1/visualization/v0850/policies','/v1/visualization/v0850/renderers/webgl2','/v1/visualization/v0850/cameras/normalize','/v1/visualization/v0850/draw-calls/normalize','/v1/visualization/v0850/render-plans/build','/v1/visualization/v0850/picking/normalize','/v1/visualization/v0850/workspaces/build',
'/v1/visualization/v0840/health','/v1/visualization/v0830/health','/v1/visualization/v0820/health','/v1/visualization/v0810/health','/v1/visualization/v0800/health','/v1/visualization/v0790/health','/v1/visualization/v0780/health','/v1/visualization/v0770/health','/v1/visualization/v0760/health','/v1/visualization/v0750/health'}
missing=sorted(required-paths)
if missing: raise SystemExit('FAIL - missing FastAPI routes: '+', '.join(missing))
print('PASS - v0.85.0 FastAPI route topology')
PY2

echo "==> contract validation"
"$PYTHON_BIN" - <<'PY2'
from pathlib import Path
import json
names=['webgl2-renderer-v0850.schema.json','webgl2-render-plan-v0850.schema.json','webgl2-picking-v0850.schema.json','webgl2-workspace-v0850.schema.json','webgl2-renderer-policy-v0850.json']
for base in ('contracts','backend/contracts'):
 for name in names: json.loads(Path(base,name).read_text())
print('PASS - v0.85.0 JSON contracts')
PY2

echo "==> canonical release identity + WebGL2 production assertions + manifest integrity"
"$PYTHON_BIN" - <<'PY2'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.85.0' and m['featureVersion']=='0.85.0' and m['platformVersion']=='1.0.0'
main=Path('sustainable-catalyst-lab.php').read_text(); header=re.search(r'^ \* Version: ([0-9.]+)$',main,re.M).group(1); assert header=='0.85.0'
console=Path('assets/js/modules/release-console-v0821.js').read_text(); assert "visualization/v0850/health" in console
browser=Path('assets/js/modules/webgl2-scientific-renderer-v0850.js').read_text(); assert "getContext('webgl2'" in browser and 'drawElementsInstanced' in browser and 'readPixels' in browser
backend=Path('backend/app/webgl2_scientific_renderer_v0850.py').read_text(); assert '"productionRendererReady": True' in backend and '"webgpuProductionRendererReady": False' in backend
config=Path('includes/class-sc-lab-plugin.php').read_text(); assert "'webgl2ProductionRendererReady'=>true" in config and "'webgpuProductionRendererReady'=>false" in config
pat=re.compile(r'(^|/)(?:\.pytest_cache|__pycache__|\.venv[^/]*)($|/)|^backend/data/|^data/')
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  if pat.search(rel): raise SystemExit('FAIL - mutable runtime/cache path in manifest: '+rel)
  p=Path(rel)
  if not p.is_file(): raise SystemExit('FAIL - missing manifest file '+rel)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise SystemExit('FAIL - manifest hash mismatch '+rel)
print(f"PASS - v0.85.0 release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY2

echo "PASS - Lab v0.85.0 WebGL2 Scientific Renderer release gate"
