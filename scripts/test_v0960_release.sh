#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.96.0 / Carbon & Nature v0.13.0 PHP + browser contracts"
php tests/test-v0960.php
node tests/test-v0960.js
node tests/test-v0950.js
node tests/test-v0940.js
node tests/test-v0930.js
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.96.0 MRV Protocol Builder + retained Carbon & Nature compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
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

echo "==> v0.96.0 routes + protocol fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.carbon_mrv_protocol_v0960 import build_protocol, validate_protocol, build_project_packet, protocol_template
from app.carbon_mrv_registry_v0950 import METHODS
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/mrv/v1300/protocol/health','/v1/carbon-nature/mrv/v1300/protocol/schema','/v1/carbon-nature/mrv/v1300/protocol/policies','/v1/carbon-nature/mrv/v1300/protocol/template/{method_key}','/v1/carbon-nature/mrv/v1300/protocol/build','/v1/carbon-nature/mrv/v1300/protocol/validate','/v1/carbon-nature/mrv/v1300/protocol/project-packet',
'/v1/carbon-nature/mrv/v1200/registry/health','/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
assert len(app.routes)==957, len(app.routes)
m=METHODS['soc-direct-measurement']
assert protocol_template('soc-direct-measurement')['method_title']=='SOC Direct Measurement'
payload={
 'project_id':'project:fixture','title':'SOC monitoring protocol','objective':'Repeated fixed-depth SOC monitoring for the named parcel.',
 'method_key':'soc-direct-measurement','spatial_boundary_ref':'parcel:fixture',
 'monitoring_period':{'start_date':'2026-01-01','end_date':'2030-12-31'},'monitoring_frequency':'Baseline and repeat campaign; deviations recorded.',
 'responsible_roles':[{'role':'field lead','actor_ref':'actor:field-team','responsibility':'sampling and custody'}],
 'available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],
 'methodology_refs':['library-methodology:soc-direct-measurement'],'source_refs':['evidence:fixture'],
 'sections':{
  'objective_and_scope':'Parcel, 0-30 cm SOC pool; exclusions explicit.',
  'measurement_and_sampling_plan':'Explicit sample IDs, depths, SOC, bulk density, coarse fragments and custody.',
  'calculation_plan':'Governed fixed-depth SOC stock calculation with versioned inputs.',
  'uncertainty_plan':'Replicate and analytical uncertainty documented; unresolved components explicit.',
  'quality_control_plan':'Identity, depth, custody, replicate and laboratory-method checks.',
  'data_management_plan':'Stable IDs, source refs, immutable observations and versioned derived records.',
  'monitoring_schedule':'Baseline 2026 and repeat 2030; actual dates recorded.',
  'reporting_plan':'Monitoring record with results, evidence, uncertainty and limitations.',
  'change_control_plan':'Version revisions and preserve superseded protocols with reasons.'}}
r=build_protocol(payload); v=validate_protocol({'protocol':r['protocol']})
assert r['protocol']['status']=='ready-for-internal-review' and v['ready_for_internal_review'] is True
assert v['external_methodology_compliance'] is None and v['verification_status'] is None and v['credit_eligibility'] is None
packet=build_project_packet({'protocol':r['protocol']})
assert packet['packet']['objects'][0]['object_type']=='monitoring-record'
assert packet['packet']['objects'][0]['payload']['record_type']=='mrv-protocol'
print('PASS - v0.96.0 protocol fixture = ready-for-internal-review; external compliance/verification/credit eligibility remain unset')
PYTEST

echo "==> v0.96.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['carbon-mrv-protocol-v1300.schema.json','carbon-mrv-protocol-validation-v1300.schema.json','carbon-mrv-protocol-policy-v1300.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a);json.loads(b);assert a==b,name
print('PASS - v0.13.0 MRV Protocol Builder contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.96.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.96.0' and m['carbonNatureDomainVersion']=='0.13.0' and m['routeAssertions']==957; assert re.search(r'^ \* Version: 0\.96\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel);assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles'])
assert '.venv/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.96.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.96.0 / Carbon & Nature v0.13.0 MRV Protocol Builder release gate"
