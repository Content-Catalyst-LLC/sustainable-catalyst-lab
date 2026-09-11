#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.99.0 / Carbon & Nature v0.16.0 PHP + browser contracts"
php tests/test-v0990.php
node tests/test-v0990.js
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

echo "==> v0.99.0 Verification Evidence Ledger + retained Carbon & Nature compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_carbon_mrv_verification_ledger_v0990.py \
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

echo "==> v0.99.0 routes + verification-ledger fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from copy import deepcopy
from app.main import app
from app.carbon_mrv_verification_ledger_v0990 import build_ledger, verify_chain, build_project_packet
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/mrv/v1600/verification-ledger/health','/v1/carbon-nature/mrv/v1600/verification-ledger/schema','/v1/carbon-nature/mrv/v1600/verification-ledger/policies','/v1/carbon-nature/mrv/v1600/verification-ledger/evidence-entry','/v1/carbon-nature/mrv/v1600/verification-ledger/build','/v1/carbon-nature/mrv/v1600/verification-ledger/validate','/v1/carbon-nature/mrv/v1600/verification-ledger/chain-check','/v1/carbon-nature/mrv/v1600/verification-ledger/project-packet',
'/v1/carbon-nature/mrv/v1500/uncertainty/health','/v1/carbon-nature/mrv/v1400/monitoring/health','/v1/carbon-nature/mrv/v1300/protocol/health','/v1/carbon-nature/mrv/v1200/registry/health','/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
assert len(app.routes)==983, len(app.routes)
p={'project_id':'project:fixture','title':'SOC verification evidence ledger','protocol_ref':'mrv-protocol:fixture','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_assessment_ref':'mrv-uncertainty:fixture','requirements':[{'requirement_key':'sampling','description':'Sampling evidence','accepted_evidence_types':['sample-record']},{'requirement_key':'laboratory','description':'Laboratory evidence','accepted_evidence_types':['laboratory-result']},{'requirement_key':'uncertainty','description':'Uncertainty evidence','accepted_evidence_types':['model-run']}],'entries':[{'evidence_id':'sample-001','evidence_type':'sample-record','source_ref':'sample:001','requirement_keys':['sampling'],'review_state':'accepted-for-internal-review'},{'evidence_id':'lab-001','evidence_type':'laboratory-result','source_ref':'lab:001','source_sha256':'0'*64,'requirement_keys':['laboratory'],'review_state':'accepted-for-internal-review'},{'evidence_id':'unc-001','evidence_type':'model-run','source_ref':'mrv-uncertainty:fixture','requirement_keys':['uncertainty'],'review_state':'accepted-for-internal-review'}],'source_refs':['mrv-protocol:fixture']}
r=build_ledger(p); l=r['ledger']; assert l['status']=='ready-for-internal-review'; assert r['validation']['external_verification_status'] is None
c=verify_chain({'ledger':l}); assert c['chain_valid'] is True and c['tamper_detected'] is False
t=deepcopy(l); t['entries'][1]['source_ref']='lab:tampered'; tc=verify_chain({'ledger':t}); assert tc['tamper_detected'] is True and tc['chain_valid'] is False
packet=build_project_packet({'ledger':l}); assert packet['packet']['objects'][0]['object_type']=='verification-record'; assert packet['packet']['provenance'][0]['event_type']=='created'
print('PASS - 3-entry required-evidence fixture is internally review-ready; chain validates; tamper mutation is detected; packet uses verification-record')
PYTEST

echo "==> v0.99.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['carbon-mrv-verification-evidence-entry-v1600.schema.json','carbon-mrv-verification-evidence-ledger-v1600.schema.json','carbon-mrv-verification-evidence-validation-v1600.schema.json','carbon-mrv-verification-evidence-chain-v1600.schema.json','carbon-mrv-verification-evidence-policy-v1600.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.16.0 verification-evidence contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(); data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.99.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.99.0' and m['carbonNatureDomainVersion']=='0.16.0' and m['routeAssertions']==983; assert re.search(r'^ \* Version: 0\.99\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles']); assert '.venv/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.99.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.99.0 / Carbon & Nature v0.16.0 Verification Evidence Ledger release gate"
