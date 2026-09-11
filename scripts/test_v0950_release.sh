#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.95.0 / Carbon & Nature v0.12.0 PHP + browser contracts"
php tests/test-v0950.php
node tests/test-v0950.js
node tests/test-v0940.js
node tests/test-v0930.js
node tests/test-v0920.js
node tests/test-v0910.js
node tests/test-v0900.js
node tests/test-v0890.js

echo "==> v0.95.0 Carbon MRV registry + retained Carbon & Nature compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_carbon_mrv_registry_v0950.py \
 backend/tests/test_whole_farm_ghg_v0940.py \
 backend/tests/test_soil_carbon_scenarios_v0930.py \
 backend/tests/test_soil_carbon_uncertainty_v0920.py \
 backend/tests/test_soil_carbon_change_v0910.py \
 backend/tests/test_soil_carbon_sampling_v0900.py \
 backend/tests/test_soil_organic_carbon_v0890.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_scientific_data_binding_v0750.py

echo "==> v0.95.0 routes + registry fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.carbon_mrv_registry_v0950 import METHODS, list_methods, compare_methods, assess_readiness, build_project_packet
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/mrv/v1200/registry/health','/v1/carbon-nature/mrv/v1200/registry/schema','/v1/carbon-nature/mrv/v1200/registry/policies','/v1/carbon-nature/mrv/v1200/registry/methods','/v1/carbon-nature/mrv/v1200/registry/methods/{method_key}','/v1/carbon-nature/mrv/v1200/registry/compare','/v1/carbon-nature/mrv/v1200/registry/readiness','/v1/carbon-nature/mrv/v1200/registry/project-packet',
'/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
assert list_methods()['count']==7
assert list_methods(gas='CH4')['count']==2
comp=compare_methods({'method_keys':['soc-direct-measurement','hybrid-measurement-modeling','modeled-carbon-stock-change']})
assert comp['ranking_performed'] is False and comp['recommendation_generated'] is False
m=METHODS['soc-direct-measurement']
ready=assess_readiness({'method_key':'soc-direct-measurement','available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],'source_refs':['evidence:fixture']})
assert ready['documentation_ready'] is True and ready['external_methodology_eligibility'] is None
packet=build_project_packet({'project_id':'project:fixture','readiness':{'method_key':'soc-direct-measurement','available_inputs':m['required_inputs'],'available_evidence':m['required_evidence'],'source_refs':['evidence:fixture']}})
assert packet['packet']['objects'][0]['object_type']=='monitoring-record'
assert packet['packet']['objects'][0]['payload']['guardrails']['no_verification_determination'] is True
print('PASS - v0.95.0 registry = 7 profiles; CH4 filter = 2; readiness and project handoff guardrails preserved')
PYTEST

echo "==> v0.95.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['carbon-mrv-method-v1200.schema.json','carbon-mrv-readiness-v1200.schema.json','carbon-mrv-registry-policy-v1200.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a);json.loads(b);assert a==b,name
print('PASS - v0.12.0 Carbon MRV contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(), 'assets/data/elements.json missing'
data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.95.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.95.0' and m['carbonNatureDomainVersion']=='0.12.0'; assert re.search(r'^ \* Version: 0\.95\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel);assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.95.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.95.0 / Carbon & Nature v0.12.0 Carbon MRV Method Registry release gate"
