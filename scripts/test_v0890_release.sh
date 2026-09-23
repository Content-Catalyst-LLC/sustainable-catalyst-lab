#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.89.0 / Carbon & Nature v0.6.0 PHP + browser contracts"
php tests/test-v0890.php
node tests/test-v0890.js
node tests/test-v0880.js
node tests/test-v0880-r1.js
node tests/test-v0880-r2.js
node tests/test-v0870.js
node tests/test-v0860.js
node tests/test-v0830.js
node tests/test-v0820.js
node tests/test-v0800.js
node tests/test-v0750.js

echo "==> v0.89.0 SOC backend + retained scientific compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_soil_organic_carbon_v0890.py \
  backend/tests/test_advanced_scientific_scene_v0880.py \
  backend/tests/test_webgpu_scientific_renderer_v0870.py \
  backend/tests/test_system_dynamics_feedback_v0860.py \
  backend/tests/test_webgl2_scientific_renderer_v0850.py \
  backend/tests/test_gpu_renderer_architecture_v0840.py \
  backend/tests/test_provenance_aware_figures_v0830.py \
  backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
  backend/tests/test_annotation_measurement_markup_v0810.py \
  backend/tests/test_spatial_geospatial_raster_v0800.py \
  backend/tests/test_linked_views_v0790.py \
  backend/tests/test_scientific_data_binding_v0750.py \
  backend/tests/test_dynamic_systems_v0540.py \
  backend/tests/test_equation_builder_v0420.py

echo "==> v0.89.0 FastAPI route topology + formula sanity"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.soil_organic_carbon_v0890 import calculate_layer_stock
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/soc/v0600/health','/v1/carbon-nature/soc/v0600/schema','/v1/carbon-nature/soc/v0600/policies',
'/v1/carbon-nature/soc/v0600/layer-stock','/v1/carbon-nature/soc/v0600/profile-stock','/v1/carbon-nature/soc/v0600/project-packet',
'/v1/visualization/v0880/health','/v1/visualization/v0870/health','/v1/model-studio/dynamic-systems/v0860/health'}
missing=sorted(required-paths); assert not missing, missing
r=calculate_layer_stock({'top_depth':0,'bottom_depth':30,'soc_value':2,'soc_unit':'percent','bulk_density_value':1.3,'bulk_density_unit':'g/cm3'})
assert abs(r['soc_stock_Mg_C_ha']-78.0)<1e-12
print('PASS - v0.89.0 route topology + 78 Mg C/ha reference fixture')
PYTEST

echo "==> v0.89.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json, hashlib
names=['soc-layer-input-v0600.schema.json','soc-profile-input-v0600.schema.json','soc-profile-result-v0600.schema.json','soc-project-packet-v0600.schema.json','soc-foundation-policy-v0600.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes()
 json.loads(a); json.loads(b); assert a==b, name
print('PASS - SOC JSON contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.89.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.89.0' and m['featureVersion']=='0.89.0' and m['platformVersion']=='1.0.0'
assert m['carbonNatureDomainVersion']=='0.6.0'
main=Path('sustainable-catalyst-lab.php').read_text(); assert re.search(r'^ \* Version: 0\.89\.0$',main,re.M)
backend=Path('backend/app/soil_organic_carbon_v0890.py').read_text()
for boundary in ('stock_change_not_inferred','sequestration_rate_not_inferred','co2e_not_inferred','equivalent_soil_mass_not_implemented','credit_eligibility_not_determined'):
 assert boundary in backend, boundary
pat=re.compile(r'(^|/)(?:\.pytest_cache|__pycache__|\.venv[^/]*)($|/)|^backend/data/|^data/')
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  if pat.search(rel): raise SystemExit('FAIL - mutable runtime/cache path in manifest: '+rel)
  p=Path(rel)
  if not p.is_file(): raise SystemExit('FAIL - missing manifest file '+rel)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise SystemExit('FAIL - manifest hash mismatch '+rel)
print(f"PASS - v0.89.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.89.0 / Carbon & Nature v0.6.0 Soil Organic Carbon Lab Foundation release gate"
