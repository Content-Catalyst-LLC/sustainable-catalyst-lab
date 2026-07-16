from app.experiment_framework import build_report, build_run, compare_runs, health, normalize_protocol, validate_protocol, verify

BASE={
 "title":"Light response experiment","domain":"plant physiology","designType":"controlled",
 "objective":"Measure the effect of light intensity on growth.",
 "hypothesis":"Increasing light intensity increases growth within the tested range.",
 "variables":[{"name":"light","role":"independent","unit":"umol m-2 s-1"},{"name":"growth","role":"dependent","unit":"mm"}],
 "controls":[{"name":"dark control"}],"procedure":["Assign treatments","Measure growth"],
 "analysisPlan":"Compare group means and confidence intervals.","sourceIds":["source-1"]
}
def test_health(): assert health()["ok"] and health()["version"]=="0.30.0"
def test_protocol_normalization_and_validation():
 p=normalize_protocol(BASE); assert p["schema"].endswith("0.30.0") and len(p["variables"])==2
 v=validate_protocol(BASE); assert v["ready"] and v["score"]>=90
 assert verify({"record":p})["ok"]
def test_incomplete_protocol_blocks():
 v=validate_protocol({"title":"x"}); assert not v["ready"] and v["blockingIssues"]
def test_run_hash_and_comparison():
 r1=build_run({"protocol":BASE,"run":{"replicate":1,"results":{"growth":10.0}}})
 r2=build_run({"protocol":BASE,"run":{"replicate":2,"results":{"growth":10.2}}})
 assert verify({"record":r1})["ok"]
 c=compare_runs({"protocol":BASE,"runs":[r1,r2],"relativeTolerance":0.05})
 assert c["replicationStatus"]=="consistent" and c["metrics"][0]["withinTolerance"]
def test_report():
 report=build_report({"protocol":BASE,"runs":[{"results":{"growth":10}},{"results":{"growth":10.1}}]})
 assert report["reportHash"] and "# Light response experiment" in report["markdown"]
