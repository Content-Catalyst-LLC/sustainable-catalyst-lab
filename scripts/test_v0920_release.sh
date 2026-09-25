#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"
echo "==> v0.92.0 / Carbon & Nature v0.9.0 PHP + browser contracts"
php tests/test-v0920.php
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.92.0 uncertainty backend + retained SOC/scientific compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_soil_carbon_uncertainty_v0920.py \
 backend/tests/test_soil_carbon_change_v0910.py \
 backend/tests/test_soil_carbon_sampling_v0900.py \
 backend/tests/test_soil_organic_carbon_v0890.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_spatial_geospatial_raster_v0800.py \
 backend/tests/test_scientific_data_binding_v0750.py

echo "==> v0.92.0 routes + statistical fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.soil_carbon_uncertainty_v0920 import summarize_replicates, change_uncertainty
paths={r.path for r in app.routes}
required={'/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0900/uncertainty/schema','/v1/carbon-nature/soc/v0900/uncertainty/policies','/v1/carbon-nature/soc/v0900/uncertainty/replicates','/v1/carbon-nature/soc/v0900/uncertainty/stratified','/v1/carbon-nature/soc/v0900/uncertainty/change','/v1/carbon-nature/soc/v0900/uncertainty/layer-propagation','/v1/carbon-nature/soc/v0900/uncertainty/project-packet','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
obs=[{'observation_id':f'o{i}','stock_Mg_C_ha':v} for i,v in enumerate([76,78,80,82],1)]
r=summarize_replicates({'observations':obs}); assert abs(r['statistics']['mean_Mg_C_ha']-79)<1e-12; assert r['statistics']['standard_error_Mg_C_ha']>1
pairs=[]
for i,(b,f) in enumerate([(78,86),(77,84),(80,89),(79,87)],1): pairs.append({'pair_id':f'p{i}','baseline':{'observation_id':f'b{i}','stock_Mg_C_ha':b},'followup':{'observation_id':f'f{i}','stock_Mg_C_ha':f}})
c=change_uncertainty({'pairs':pairs,'elapsed_years':2}); assert abs(c['mean_stock_change_Mg_C_ha']-8)<1e-12; assert abs(c['annualized_mean_stock_change_Mg_C_ha_yr']-4)<1e-12; assert c['interpretation']['causal_attribution_established'] is False
print('PASS - v0.92.0 routes + replicate mean 79 + paired delta 8 Mg C/ha fixtures')
PYTEST

echo "==> v0.92.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['soc-spatial-uncertainty-v0900.schema.json','soc-stratified-estimate-v0900.schema.json','soc-change-uncertainty-v0900.schema.json','soc-input-uncertainty-v0900.schema.json','soc-uncertainty-policy-v0900.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a);json.loads(b);assert a==b,name
print('PASS - v0.9.0 uncertainty contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118, len(data) if isinstance(data,list) else type(data)
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.92.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.92.0' and m['carbonNatureDomainVersion']=='0.9.0'; assert re.search(r'^ \* Version: 0\.92\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel);assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.92.0 manifest integrity ({len(m['wordpressCriticalFiles'])} source + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.92.0 / Carbon & Nature v0.9.0 SOC Spatial Variability & Uncertainty release gate"
