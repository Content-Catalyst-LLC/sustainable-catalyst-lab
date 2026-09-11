#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.98.0 / Carbon & Nature v0.15.0 PHP + browser contracts"
php tests/test-v0980.php
node tests/test-v0980.js
node tests/test-v0970.js
node tests/test-v0960.js
node tests/test-v0950.js
node tests/test-v0940.js
node tests/test-v0930.js
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.98.0 MRV Uncertainty & Detection Engine + retained Carbon & Nature compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_carbon_mrv_uncertainty_v0980.py \
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

echo "==> v0.98.0 routes + uncertainty/detection fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.carbon_mrv_uncertainty_v0980 import uncertainty_budget, change_detection, required_sample_size, build_assessment, build_project_packet
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/mrv/v1500/uncertainty/health','/v1/carbon-nature/mrv/v1500/uncertainty/schema','/v1/carbon-nature/mrv/v1500/uncertainty/policies','/v1/carbon-nature/mrv/v1500/uncertainty/budget','/v1/carbon-nature/mrv/v1500/uncertainty/change-detection','/v1/carbon-nature/mrv/v1500/uncertainty/detection-sample-size','/v1/carbon-nature/mrv/v1500/uncertainty/build','/v1/carbon-nature/mrv/v1500/uncertainty/validate','/v1/carbon-nature/mrv/v1500/uncertainty/project-packet',
'/v1/carbon-nature/mrv/v1400/monitoring/health','/v1/carbon-nature/mrv/v1300/protocol/health','/v1/carbon-nature/mrv/v1200/registry/health','/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
assert len(app.routes)==975, len(app.routes)
b=uncertainty_budget({'estimate':100,'unit':'Mg C/ha','coverage_factor':2,'components':[{'component_key':'sampling','standard_uncertainty':3},{'component_key':'laboratory','standard_uncertainty':4}]})
assert b['combined_standard_uncertainty']==5 and b['expanded_uncertainty']==10 and b['expanded_interval']==[90,110]
c=change_detection({'design':'paired','observed_change':4,'critical_value':1.96,'sd_change':8,'n_pairs':16})
assert c['standard_error_change']==2 and abs(c['detection_threshold']-3.92)<1e-12 and c['change_detected_at_supplied_threshold'] is True
n=required_sample_size({'design':'paired','minimum_detectable_change':4,'z_alpha':1.96,'z_power':0.84,'expected_sd_change':8})
assert n['recommended_pairs']==32
p={'project_id':'project:fixture','title':'MRV uncertainty fixture','metric':'SOC stock change','unit':'Mg C/ha','monitoring_plan_ref':'monitoring-plan:fixture','protocol_ref':'mrv-protocol:fixture','uncertainty_budget':{'estimate':100,'unit':'Mg C/ha','components':[{'component_key':'sampling','standard_uncertainty':3}]},'change_detection':{'design':'paired','observed_change':4,'critical_value':1.96,'sd_change':8,'n_pairs':16},'source_refs':['evidence:fixture']}
r=build_assessment(p)
assert r['assessment']['status']=='ready-for-internal-review'
assert r['validation']['verification_status'] is None and r['validation']['credit_eligibility'] is None
packet=build_project_packet({'assessment':r['assessment']})
assert packet['packet']['objects'][0]['object_type']=='model-run'
assert packet['packet']['provenance'][0]['event_type']=='modeled'
print('PASS - combined u=5, expanded U=10, paired threshold=3.92, planning n=32, internal-review-only assessment')
PYTEST

echo "==> v0.98.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['carbon-mrv-uncertainty-budget-v1500.schema.json','carbon-mrv-change-detection-v1500.schema.json','carbon-mrv-detection-sample-size-v1500.schema.json','carbon-mrv-uncertainty-assessment-v1500.schema.json','carbon-mrv-uncertainty-assessment-validation-v1500.schema.json','carbon-mrv-uncertainty-policy-v1500.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.15.0 uncertainty/detection contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.98.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.98.0' and m['carbonNatureDomainVersion']=='0.15.0' and m['routeAssertions']==975; assert re.search(r'^ \* Version: 0\.98\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles'])
assert '.venv/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.98.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.98.0 / Carbon & Nature v0.15.0 MRV Uncertainty & Detection Engine release gate"
