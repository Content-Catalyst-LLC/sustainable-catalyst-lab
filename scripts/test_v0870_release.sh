#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.87.0 PHP + browser contracts"
php tests/test-v0870.php
node tests/test-v0870.js
node tests/test-v0860.js
node tests/test-v0850.js

echo "==> v0.87.0 backend + compatibility tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_webgpu_scientific_renderer_v0870.py \
  backend/tests/test_system_dynamics_feedback_v0860.py \
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
  backend/tests/test_dynamic_systems_v0540.py \
  backend/tests/test_equation_builder_v0420.py

echo "==> v0.87.0 FastAPI route topology"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PY'
from app.main import app
paths={r.path for r in app.routes}
required={
'/v1/visualization/v0870/health','/v1/visualization/v0870/policies','/v1/visualization/v0870/renderers/webgpu',
'/v1/visualization/v0870/render-passes/normalize','/v1/visualization/v0870/render-plans/build',
'/v1/visualization/v0870/compute/dispatches/normalize','/v1/visualization/v0870/compute/plans/build','/v1/visualization/v0870/workspaces/build',
'/v1/model-studio/dynamic-systems/v0860/health','/v1/visualization/v0850/health'}
missing=sorted(required-paths); assert not missing, missing
print('PASS - v0.87.0 FastAPI route topology')
PY

echo "==> v0.87.0 JSON contracts"
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import json
names=['webgpu-renderer-v0870.schema.json','webgpu-render-plan-v0870.schema.json','webgpu-compute-plan-v0870.schema.json','webgpu-workspace-v0870.schema.json','webgpu-renderer-policy-v0870.json']
for base in ('contracts','backend/contracts'):
 for name in names: json.loads(Path(base,name).read_text())
print('PASS - v0.87.0 JSON contracts')
PY

echo "==> v0.87.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.87.0' and m['featureVersion']=='0.87.0' and m['platformVersion']=='1.0.0'
main=Path('sustainable-catalyst-lab.php').read_text(); assert re.search(r'^ \* Version: 0\.87\.0$',main,re.M)
console=Path('assets/js/modules/release-console-v0821.js').read_text(); assert 'visualization/v0870/health' in console and 'modeling/v0860/health' in console
backend=Path('backend/app/webgpu_scientific_renderer_v0870.py').read_text(); assert '"arbitraryWGSLSource": False' in backend and '"computeResultCreatesObservation": False' in backend
pat=re.compile(r'(^|/)(?:\.pytest_cache|__pycache__|\.venv[^/]*)($|/)|^backend/data/|^data/')
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  if pat.search(rel): raise SystemExit('FAIL - mutable runtime/cache path in manifest: '+rel)
  p=Path(rel)
  if not p.is_file(): raise SystemExit('FAIL - missing manifest file '+rel)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise SystemExit('FAIL - manifest hash mismatch '+rel)
print(f"PASS - v0.87.0 release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY

echo "PASS - Lab v0.87.0 WebGPU Scientific Renderer & GPU Compute release gate"
