#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.100.0 / Carbon & Nature v0.17.0 PHP + browser contracts"
php tests/test-v01000.php
node tests/test-v01000.js
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

echo "==> v0.100.0 MRV Reporting & Audit Packets + retained Carbon & Nature compatibility"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_carbon_mrv_reporting_v01000.py \
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

echo "==> v0.100.0 routes + reporting/audit fixtures"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.carbon_mrv_verification_ledger_v0990 import build_ledger
from app.carbon_mrv_reporting_v01000 import build_report, build_audit_packet, build_project_packet
paths={r.path for r in app.routes}
required={
'/v1/carbon-nature/mrv/v1700/reporting/health','/v1/carbon-nature/mrv/v1700/reporting/schema','/v1/carbon-nature/mrv/v1700/reporting/policies','/v1/carbon-nature/mrv/v1700/reporting/template/{report_type}','/v1/carbon-nature/mrv/v1700/reporting/report/build','/v1/carbon-nature/mrv/v1700/reporting/report/validate','/v1/carbon-nature/mrv/v1700/reporting/audit-packet/build','/v1/carbon-nature/mrv/v1700/reporting/project-packet',
'/v1/carbon-nature/mrv/v1600/verification-ledger/health','/v1/carbon-nature/mrv/v1500/uncertainty/health','/v1/carbon-nature/mrv/v1400/monitoring/health','/v1/carbon-nature/mrv/v1300/protocol/health','/v1/carbon-nature/mrv/v1200/registry/health','/v1/carbon-nature/ghg/v1100/balance/health','/v1/carbon-nature/soc/v1000/scenarios/project','/v1/carbon-nature/soc/v0900/uncertainty/health','/v1/carbon-nature/soc/v0800/change/compare','/v1/carbon-nature/soc/v0700/sampling/profile-handoff','/v1/carbon-nature/soc/v0600/profile-stock'}
assert not sorted(required-paths), sorted(required-paths)
assert len(app.routes)==991, len(app.routes)
ledger=build_ledger({'project_id':'project:fixture','title':'SOC evidence ledger','protocol_ref':'mrv-protocol:fixture','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_assessment_ref':'mrv-uncertainty:fixture','requirements':[{'requirement_key':'sampling','description':'Sampling evidence','accepted_evidence_types':['sample-record']},{'requirement_key':'laboratory','description':'Laboratory evidence','accepted_evidence_types':['laboratory-result']}],'entries':[{'evidence_id':'sample-001','evidence_type':'sample-record','source_ref':'sample:001','requirement_keys':['sampling'],'review_state':'accepted-for-internal-review'},{'evidence_id':'lab-001','evidence_type':'laboratory-result','source_ref':'lab:001','source_sha256':'0'*64,'requirement_keys':['laboratory'],'review_state':'accepted-for-internal-review'}]})['ledger']
sections=[
{'section_key':'project-boundary','title':'Boundary','content':'Parcel and period documented.','source_refs':['project:fixture']},
{'section_key':'methodology','title':'Methodology','content':'Methods linked.','source_refs':['mrv-protocol:fixture']},
{'section_key':'monitoring','title':'Monitoring','content':'Monitoring linked.','source_refs':['monitoring-plan:fixture']},
{'section_key':'quantification','title':'Quantification','content':'Declared metric lineage retained.','source_refs':['model-run:soc-change']},
{'section_key':'uncertainty','title':'Uncertainty','content':'Assessment linked.','source_refs':['mrv-uncertainty:fixture']},
{'section_key':'evidence','title':'Evidence','content':'Ledger linked.','source_refs':[ledger['ledger_id']]},
{'section_key':'deviations','title':'Deviations','content':'No unresolved deviations.','source_refs':[]},
{'section_key':'summary','title':'Summary','content':'Internal review only.','source_refs':[]},]
p={'report_type':'monitoring-report','project_id':'project:fixture','title':'2026 SOC monitoring report','reporting_period':{'start':'2026-01-01','end':'2026-12-31'},'protocol_ref':'mrv-protocol:fixture','monitoring_plan_ref':'monitoring-plan:fixture','uncertainty_assessment_ref':'mrv-uncertainty:fixture','verification_ledger_ref':ledger['ledger_id'],'verification_ledger':ledger,'sections':sections,'reported_metrics':[{'metric_id':'soc-change','name':'SOC stock change','value':7.8,'unit':'Mg C/ha','source_ref':'model-run:soc-change','uncertainty_ref':'mrv-uncertainty:fixture'}],'deviations':[],'source_refs':['model-run:soc-change']}
r=build_report(p); assert r['report']['status']=='ready-for-internal-review'; assert r['report']['reported_metrics'][0]['value']==7.8; assert r['report']['reported_metrics'][0]['calculation_reperformed'] is False
ap=build_audit_packet({'report':r['report'],'artifacts':[{'artifact_id':'lab-result','artifact_type':'laboratory-result','source_ref':'lab:001','sha256':'1'*64}]}); assert ap['audit_packet']['status']=='ready-for-internal-audit-preparation'; assert ap['audit_packet']['external_audit_status'] is None
pp=build_project_packet({'report':r['report'],'artifacts':[]}); obj=pp['packet']['objects'][0]; assert obj['object_type']=='verification-record' and obj['payload']['external_audit_status'] is None
print('PASS - reporting fixture preserves declared 7.8 Mg C/ha metric without recalculation')
print('PASS - supplied v0.16 ledger chain supports internal audit-preparation readiness only')
print('PASS - project handoff is verification-record with external audit/verification unset')
PYTEST

echo "==> v0.100.0 duplicated JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['carbon-mrv-report-v1700.schema.json','carbon-mrv-report-validation-v1700.schema.json','carbon-mrv-audit-packet-v1700.schema.json','carbon-mrv-reporting-policy-v1700.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.17.0 MRV reporting contracts parse and mirror byte-for-byte')
PYTEST

echo "==> retained static scientific assets"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
p=Path('assets/data/elements.json'); assert p.is_file(); data=json.loads(p.read_text()); assert isinstance(data,list) and len(data)==118
print('PASS - retained periodic-table asset contains 118 elements')
PYTEST

echo "==> v0.100.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text()); assert m['releaseVersion']=='0.100.0' and m['carbonNatureDomainVersion']=='0.17.0' and m['routeAssertions']==991; assert re.search(r'^ \* Version: 0\.100\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
assert 'backend/' not in ''.join(m['wordpressCriticalFiles']); assert '.venv/' not in ''.join(m['wordpressCriticalFiles'])
print(f"PASS - v0.100.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.100.0 / Carbon & Nature v0.17.0 MRV Reporting & Audit Packets release gate"
