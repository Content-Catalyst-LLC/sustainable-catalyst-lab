#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"
echo "==> v0.90.0 / Carbon & Nature v0.7.0 PHP + browser contracts"
php tests/test-v0900.php
node tests/test-v0900.js
node tests/test-v0890.js
node tests/test-v0880.js
node tests/test-v0880-r1.js
node tests/test-v0880-r2.js
node tests/test-v0870.js
node tests/test-v0860.js

echo "==> v0.90.0 SOC sampling backend + retained SOC/scientific compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_soil_carbon_sampling_v0900.py \
  backend/tests/test_soil_organic_carbon_v0890.py \
  backend/tests/test_advanced_scientific_scene_v0880.py \
  backend/tests/test_webgpu_scientific_renderer_v0870.py \
  backend/tests/test_system_dynamics_feedback_v0860.py \
  backend/tests/test_webgl2_scientific_renderer_v0850.py \
  backend/tests/test_provenance_aware_figures_v0830.py \
  backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
  backend/tests/test_spatial_geospatial_raster_v0800.py \
  backend/tests/test_scientific_data_binding_v0750.py

echo "==> v0.90.0 route topology + field fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.soil_carbon_sampling_v0900 import calculate_bulk_density, build_profile_handoff
paths={r.path for r in app.routes}
required={'/v1/carbon-nature/soc/v0600/profile-stock','/v1/carbon-nature/soc/v0700/sampling/health','/v1/carbon-nature/soc/v0700/sampling/sample/normalize','/v1/carbon-nature/soc/v0700/sampling/samples/normalize','/v1/carbon-nature/soc/v0700/sampling/bulk-density','/v1/carbon-nature/soc/v0700/sampling/design','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0700/sampling/field-packet'}
assert not sorted(required-paths), sorted(required-paths)
assert abs(calculate_bulk_density({'dry_mass_g':130,'core_volume_cm3':100})['bulk_density_g_cm3']-1.3)<1e-12
h=build_profile_handoff({'samples':[{'sample_id':'S1','profile_id':'profile:test','top_depth':0,'bottom_depth':30,'soc_value':2,'soc_unit':'percent','dry_mass_g':130,'core_volume_cm3':100}]})
assert abs(h['compatibility_validation']['calculated_stock_Mg_C_ha']-78.0)<1e-12
print('PASS - v0.90.0 routes + 1.3 g/cm3 bulk density + 78 Mg C/ha profile handoff')
PYTEST

echo "==> v0.90.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['soc-field-sample-v0700.schema.json','soc-sampling-design-v0700.schema.json','soc-field-packet-v0700.schema.json','soc-profile-handoff-v0700.schema.json','soc-sampling-policy-v0700.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.7.0 sampling contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.90.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.90.0' and m['featureVersion']=='0.90.0' and m['carbonNatureDomainVersion']=='0.7.0'
assert re.search(r'^ \* Version: 0\.90\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.90.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.90.0 / Carbon & Nature v0.7.0 SOC Sampling & Field Measurement Studio release gate"
