#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.93.0 / Carbon & Nature v0.10.0 PHP + browser contracts"
php tests/test-v0930.php
node tests/test-v0930.js
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.93.0 scenario backend + retained SOC/scientific compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_soil_carbon_scenarios_v0930.py \
 backend/tests/test_soil_carbon_uncertainty_v0920.py \
 backend/tests/test_soil_carbon_change_v0910.py \
 backend/tests/test_soil_carbon_sampling_v0900.py \
 backend/tests/test_soil_organic_carbon_v0890.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_scientific_data_binding_v0750.py

echo "==> v0.93.0 routes + scenario fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.soil_carbon_scenarios_v0930 import project_scenario, compare_scenarios, sensitivity_sweep
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/soc/v1000/scenarios/health','/v1/carbon-nature/soc/v1000/scenarios/schema','/v1/carbon-nature/soc/v1000/scenarios/policies',
'/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v1000/scenarios/compare','/v1/carbon-nature/soc/v1000/scenarios/sensitivity','/v1/carbon-nature/soc/v1000/scenarios/project-packet',
'/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
r=project_scenario({'scenario_id':'reference','baseline_stock_Mg_C_ha':78,'horizon_years':10,'model_type':'constant-annual-change','annual_change_Mg_C_ha_yr':2})
assert abs(r['final_stock_Mg_C_ha']-98)<1e-12
assert abs(r['cumulative_stock_change_Mg_C_ha']-20)<1e-12
assert r['interpretation']['scenario_projection_is_forecast'] is False
c=compare_scenarios({'baseline_stock_Mg_C_ha':78,'scenarios':[{'scenario_id':'low','horizon_years':10,'model_type':'constant-annual-change','annual_change_Mg_C_ha_yr':1},{'scenario_id':'high','horizon_years':10,'model_type':'constant-annual-change','annual_change_Mg_C_ha_yr':3}]})
assert [x['final_stock_Mg_C_ha'] for x in c['comparison_table']]==[88.0,108.0]
assert c['automatic_ranking_performed'] is False
s=sensitivity_sweep({'baseline_stock_Mg_C_ha':78,'horizon_years':10,'model_type':'constant-annual-change','values':[0,1,2,3]})
assert [x['final_stock_Mg_C_ha'] for x in s['rows']]==[78.0,88.0,98.0,108.0]
print('PASS - v0.93.0 routes + 78 -> 98 Mg C/ha 10-year scenario fixture')
PYTEST

echo "==> v0.93.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['soc-management-scenario-v1000.schema.json','soc-management-scenario-comparison-v1000.schema.json','soc-management-sensitivity-v1000.schema.json','soc-management-scenario-policy-v1000.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a);json.loads(b);assert a==b,name
print('PASS - v0.10.0 management scenario contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118, len(data) if isinstance(data,list) else type(data)
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.93.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.93.0' and m['carbonNatureDomainVersion']=='0.10.0'; assert re.search(r'^ \* Version: 0\.93\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel);assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.93.0 manifest integrity ({len(m['wordpressCriticalFiles'])} source + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.93.0 / Carbon & Nature v0.10.0 SOC Management Scenario Studio release gate"
