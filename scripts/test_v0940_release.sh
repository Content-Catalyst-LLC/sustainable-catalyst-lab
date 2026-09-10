#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.94.0 / Carbon & Nature v0.11.0 PHP + browser contracts"
php tests/test-v0940.php
node tests/test-v0940.js
node tests/test-v0930.js
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.94.0 Whole-Farm GHG backend + retained SOC/scientific compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_whole_farm_ghg_v0940.py \
 backend/tests/test_soil_carbon_scenarios_v0930.py \
 backend/tests/test_soil_carbon_uncertainty_v0920.py \
 backend/tests/test_soil_carbon_change_v0910.py \
 backend/tests/test_soil_carbon_sampling_v0900.py \
 backend/tests/test_soil_organic_carbon_v0890.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_scientific_data_binding_v0750.py

echo "==> v0.94.0 routes + Whole-Farm GHG fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.whole_farm_ghg_v0940 import calculate_balance
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/ghg/v1100/balance/schema','/v1/carbon-nature/ghg/v1100/balance/policies','/v1/carbon-nature/ghg/v1100/balance/entry','/v1/carbon-nature/ghg/v1100/balance/calculate','/v1/carbon-nature/ghg/v1100/balance/project-packet',
'/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
r=calculate_balance({
'balance_id':'ghg-balance:reference','area_ha':1,
'gwp_set':{'name':'illustrative-fixture','source_ref':'source:test-gwp','horizon_years':100,'factors':{'CH4':10,'N2O':100}},
'entries':[
 {'entry_id':'co2','category':'energy','direction':'emission','gas':'CO2','mass_kg':1000,'source_refs':['evidence:co2']},
 {'entry_id':'ch4','category':'livestock','direction':'emission','gas':'CH4','mass_kg':10,'source_refs':['evidence:ch4']},
 {'entry_id':'n2o','category':'soil','direction':'emission','gas':'N2O','mass_kg':1,'source_refs':['evidence:n2o']},
],
'soc_stock_change':{'stock_change_Mg_C_ha':0.1,'area_ha':1,'basis':'measured-change','include_in_net':True,'source_refs':['model-run:soc-change']}
})
assert abs(r['gross_emissions_kg_CO2e']-1200)<1e-9
assert abs(r['gross_removals_kg_CO2e']-(0.1*1000*44/12))<1e-9
assert abs(r['net_balance_kg_CO2e']-833.3333333333334)<1e-9
assert r['interpretation']['whole_farm_balance_is_verification'] is False
assert r['guardrails']['no_default_non_co2_gwp_factors'] is True
print('PASS - v0.94.0 routes + 1200 / 366.667 / 833.333 kg CO2e reference fixture')
PYTEST

echo "==> v0.94.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['whole-farm-ghg-entry-v1100.schema.json','whole-farm-ghg-balance-v1100.schema.json','whole-farm-ghg-policy-v1100.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a);json.loads(b);assert a==b,name
print('PASS - v0.11.0 Whole-Farm GHG contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118, len(data) if isinstance(data,list) else type(data)
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.94.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.94.0' and m['carbonNatureDomainVersion']=='0.11.0'; assert re.search(r'^ \* Version: 0\.94\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel);assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.94.0 manifest integrity ({len(m['wordpressCriticalFiles'])} source + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.94.0 / Carbon & Nature v0.11.0 Whole-Farm GHG Balance release gate"
