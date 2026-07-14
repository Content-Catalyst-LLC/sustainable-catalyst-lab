from __future__ import annotations
import math
from app.genetics_genomics_sequence_analysis import catalog,execute,batch_execute
def test_contract_and_benchmarks():
 c=catalog();assert c["version"]=="0.24.0";assert len(c["methods"])==48;assert len(c["benchmarks"])==48;assert len(c["categories"])==8
 for b in c["benchmarks"]:
  got=execute(b["methodId"],b["inputs"])["value"];exp=b["expected"]
  if isinstance(exp,(int,float)):assert math.isclose(float(got),float(exp),rel_tol=1e-8,abs_tol=float(b["tolerance"]))
  else:assert got==exp
def test_batch_isolation():
 r=batch_execute([{"methodId":"gc-content","inputs":{"sequence":"ACGT"}},{"methodId":"hamming-distance","inputs":{"reference":"AC","query":"A"}}])
 assert r["successCount"]==1 and r["errorCount"]==1
