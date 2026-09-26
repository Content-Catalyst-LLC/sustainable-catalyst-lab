#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.91.0 / Carbon & Nature v0.8.0 PHP + browser contracts"
php tests/test-v0910.php
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js
node tests/test-v0880.js
node tests/test-v0880-r1.js
node tests/test-v0880-r2.js
node tests/test-v0870.js
node tests/test-v0860.js

echo "==> v0.91.0 SOC change backend + retained SOC/scientific compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_soil_carbon_change_v0910.py \
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

echo "==> v0.91.0 route topology + stock-change fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.soil_carbon_change_v0910 import compare_profiles
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/soc/v0600/profile-stock',
'/v1/carbon-nature/soc/v0700/sampling/profile-handoff',
'/v1/carbon-nature/soc/v0800/change/health',
'/v1/carbon-nature/soc/v0800/change/schema',
'/v1/carbon-nature/soc/v0800/change/policies',
'/v1/carbon-nature/soc/v0800/change/compare',
'/v1/carbon-nature/soc/v0800/change/series',
'/v1/carbon-nature/soc/v0800/change/project-packet',
}
assert not sorted(required-paths), sorted(required-paths)
base={'layers':[{'layer_id':'b','top_depth':0,'bottom_depth':30,'soc_value':2,'soc_unit':'percent','bulk_density_value':1.3,'bulk_density_unit':'g/cm3'}]}
follow={'layers':[{'layer_id':'f','top_depth':0,'bottom_depth':30,'soc_value':2.2,'soc_unit':'percent','bulk_density_value':1.3,'bulk_density_unit':'g/cm3'}]}
r=compare_profiles({'comparison_id':'comparison:gate','spatial_unit_id':'parcel:gate','baseline_at':'2025-01-01','followup_at':'2026-01-01','baseline_profile':base,'followup_profile':follow})
assert abs(r['baseline']['soc_stock_Mg_C_ha']-78.0)<1e-12
assert abs(r['followup']['soc_stock_Mg_C_ha']-85.8)<1e-12
assert abs(r['stock_change_Mg_C_ha']-7.8)<1e-12
assert r['interpretation']['intervention_attribution_established'] is False
print('PASS - v0.91.0 routes + 78.0 -> 85.8 Mg C/ha + delta 7.8 Mg C/ha fixture')
PYTEST

echo "==> v0.91.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['soc-stock-change-v0800.schema.json','soc-change-series-v0800.schema.json','soc-change-policy-v0800.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.8.0 SOC change contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.91.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.91.0' and m['featureVersion']=='0.91.0' and m['carbonNatureDomainVersion']=='0.8.0'
assert re.search(r'^ \* Version: 0\.91\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.91.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.91.0 / Carbon & Nature v0.8.0 SOC Change & Sequestration Model release gate"
