from __future__ import annotations
import math
from copy import deepcopy
from app.laboratory_data_instrumentation import VERSION,catalog,execute,create_record,create_manifest,create_custody_event,verify_custody,normalize_measurements

def test_contract_benchmarks():
 c=catalog();assert VERSION=='0.25.0';assert len(c['categories'])==8;assert len(c['methods'])==48;assert len(c['benchmarks'])==48
 for b in c['benchmarks']:
  r=execute(b['methodId'],b['inputs']);assert math.isclose(float(r['value']),float(b['expected']),rel_tol=1e-8,abs_tol=float(b['tolerance']))
def test_records_manifest_ingest():
 a=create_record('instrument',{'name':'Balance A'},{'recordId':'instrument-1','createdAt':'2026-07-14T00:00:00+00:00'})
 b=create_record('sample',{'sampleId':'S-1'},{'recordId':'sample-1','createdAt':'2026-07-14T00:01:00+00:00'})
 m=create_manifest([a,b]);assert m['recordCount']==2;assert len(m['manifestHash'])==64
 ing=normalize_measurements([{'value':1000,'unit':'mV','timestamp':'2026-07-14T00:00:00Z'}],{'mV':0.001});assert ing['rows'][0]['normalizedValue']==1;assert len(ing['datasetHash'])==64
def test_custody_tamper():
 a=create_custody_event('S-1','collected','Analyst','Lab A')
 b=create_custody_event('S-1','transferred','Reviewer','Lab B',a['eventHash'])
 assert verify_custody([a,b])['valid'] is True
 t=deepcopy([a,b]);t[1]['location']='Unknown';assert verify_custody(t)['valid'] is False
