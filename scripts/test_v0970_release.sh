#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.97.0 / Carbon & Nature v0.14.0 PHP + browser contracts"
php tests/test-v0970.php
node tests/test-v0970.js
node tests/test-v0960.js
node tests/test-v0950.js
node tests/test-v0940.js
node tests/test-v0930.js
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.97.0 Monitoring Plan & Sampling Designer + retained Carbon & Nature compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_carbon_mrv_monitoring_v0970.py \
 backend/tests/test_carbon_mrv_protocol_v0960.py \
 backend/tests/test_carbon_mrv_registry_v0950.py \
 backend/tests/test_whole_farm_ghg_v0940.py \
 backend/tests/test_soil_carbon_scenarios_v0930.py \
 backend/tests/test_soil_carbon_uncertainty_v0920.py \
 backend/tests/test_soil_carbon_change_v0910.py \
 backend/tests/test_soil_carbon_sampling_v0900.py \
 backend/tests/test_soil_organic_carbon_v0890.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_scientific_data_binding_v0750.py

echo "==> v0.97.0 routes + statistical planning fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.carbon_mrv_monitoring_v0970 import sample_size_plan, allocate_strata, build_plan, build_project_packet, plan_template
from app.carbon_mrv_registry_v0950 import METHODS
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/mrv/v1400/monitoring/health','/v1/carbon-nature/mrv/v1400/monitoring/schema','/v1/carbon-nature/mrv/v1400/monitoring/policies','/v1/carbon-nature/mrv/v1400/monitoring/template/{method_key}','/v1/carbon-nature/mrv/v1400/monitoring/sample-size','/v1/carbon-nature/mrv/v1400/monitoring/strata-allocation','/v1/carbon-nature/mrv/v1400/monitoring/build','/v1/carbon-nature/mrv/v1400/monitoring/validate','/v1/carbon-nature/mrv/v1400/monitoring/project-packet',
'/v1/carbon-nature/mrv/v1300/protocol/health','/v1/carbon-nature/mrv/v1200/registry/health','/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
assert len(app.routes)>=966, len(app.routes)
assert len(plan_template('soc-direct-measurement')['strategy_options'])==5
ss=sample_size_plan({'expected_sd':12,'z_value':1.96,'target_half_width':4})
assert ss['unadjusted_sample_size']==35 and ss['recommended_planning_sample_size']==35
fpc=sample_size_plan({'expected_sd':10,'z_value':1.96,'target_half_width':5,'population_size':100})
assert fpc['unadjusted_sample_size']==16 and fpc['recommended_planning_sample_size']==14
alloc=allocate_strata({'allocation_method':'proportional','total_sample_size':36,'strata':[{'stratum_key':'A','size':60},{'stratum_key':'B','size':40}]})
assert [x['allocated_sample_size'] for x in alloc['strata']]==[22,14]
m=METHODS['soc-direct-measurement']
payload={
 'project_id':'project:fixture','protocol_id':'mrv-protocol:fixture','title':'SOC monitoring plan','objective':'Repeatable fixed-depth SOC sampling for the named parcel.',
 'method_key':'soc-direct-measurement','spatial_boundary_ref':'parcel:fixture',
 'campaigns':[{'campaign_id':'campaign:baseline','purpose':'baseline','planned_start_date':'2026-04-01','planned_end_date':'2026-04-15'}],
 'sampling_frame_ref':'sampling-frame:fixture','sample_unit':'field core',
 'sampling_design':{'strategy':'stratified-random','target_population':'Mineral soil within parcel','depth_intervals_cm':[{'top_cm':0,'bottom_cm':30}],
   'strata':[{'stratum_key':'A','size':60,'expected_sd':10},{'stratum_key':'B','size':40,'expected_sd':20}],
   'field_qc_steps':['stable sample IDs'],'laboratory_qc_steps':['laboratory method record']},
 'available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],
 'methodology_refs':['library-methodology:soc-direct-measurement'],'source_refs':['evidence:sampling-frame']}
r=build_plan(payload)
assert r['plan']['status']=='ready-for-internal-review'
assert r['validation']['sampling_representativeness'] is None
packet=build_project_packet({'plan':r['plan']})
assert packet['packet']['objects'][0]['payload']['record_type']=='monitoring-plan'
assert packet['packet']['links'][0]['relationship']=='monitoring-for'
print('PASS - planning n=35; FPC n=14; proportional allocation=22/14; complete plan ready-for-internal-review only')
PYTEST

echo "==> v0.97.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['carbon-mrv-monitoring-plan-v1400.schema.json','carbon-mrv-monitoring-plan-validation-v1400.schema.json','carbon-mrv-sample-size-v1400.schema.json','carbon-mrv-stratified-allocation-v1400.schema.json','carbon-mrv-monitoring-plan-policy-v1400.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a);json.loads(b);assert a==b,name
print('PASS - v0.14.0 monitoring/sampling contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.97.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.97.0' and m['carbonNatureDomainVersion']=='0.14.0' and m['routeAssertions']==966; assert re.search(r'^ \* Version: 0\.97\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel);assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles'])
assert '.venv/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.97.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.97.0 / Carbon & Nature v0.14.0 Monitoring Plan & Sampling Designer release gate"
