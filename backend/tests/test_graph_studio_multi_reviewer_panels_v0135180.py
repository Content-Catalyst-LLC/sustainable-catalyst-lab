from app import graph_studio_multi_reviewer_panels_v0135180 as m

BASE={
 "id":"panel-1","threadId":"thread-1","resolutionRecordId":"res-1","auditRecordId":"audit-1","reviewVersionRef":"revision-4",
 "subjectRefs":["claim-1","figure-2"],
 "reviewers":[
   {"reviewerId":"alice","displayName":"Alice","role":"method-reviewer","independenceAttested":True},
   {"reviewerId":"bob","displayName":"Bob","role":"reproduction-reviewer","independenceAttested":True,"conflictDisclosure":"Prior collaboration disclosed."},
 ]
}
def payload(**kw):
 x={**BASE}; x.update(kw); return x

def test_normalize_and_validate_panel():
 n=m.normalize_panel(payload()); assert n["ok"] and n["record"]["collection"]=="graphStudioMultiReviewerPanels" and len(n["record"]["fingerprint"])==64
 v=m.validate_panel(payload()); assert v["ok"] and not v["errors"]

def test_requires_multiple_distinct_reviewers():
 v=m.validate_panel(payload(reviewers=[{"reviewerId":"alice"}])); assert not v["ok"] and any("two distinct" in x for x in v["errors"])
 d=m.normalize_panel(payload(reviewers=[{"reviewerId":"alice"},{"reviewerId":"alice"}])); assert not d["ok"] and any("duplicate" in x for x in d["errors"])

def test_independent_assessment_and_signoff():
 a=m.record_assessment({**payload(),"reviewerId":"alice","assessmentState":"further-revision","rationale":"Method specification remains incomplete."}); assert a["ok"] and a["record"]["independent_record"] and not a["majority_calculated"]
 p=a["panel"]
 s=m.record_signoff({"panel":p,"reviewerId":"alice","signoffState":"withheld","assessmentRef":a["record"]["id"]}); assert s["ok"] and s["record"]["signs_for_self_only"] and not s["automatic_resolution"]

def test_dissent_is_preserved():
 d=m.record_dissent({**payload(),"reviewerId":"bob","dissentKind":"interpretive","statement":"The same result admits an alternative interpretation.","alternativeInterpretation":"Treat as unresolved."}); assert d["ok"] and d["record"]["preserved_even_if_minority"]

def test_matrix_has_no_consensus_or_winner():
 a=m.record_assessment({**payload(),"reviewerId":"alice","assessmentState":"addressed"})
 b=m.record_assessment({"panel":a["panel"],"reviewerId":"bob","assessmentState":"further-revision"})
 mx=m.panel_matrix({"panel":b["panel"]}); assert mx["ok"] and mx["majority_calculated"] is False and mx["consensus_score"] is None and mx["winner"] is None

def test_administrative_completion_is_not_scientific_resolution():
 p=payload();
 for rid,state in (("alice","addressed"),("bob","accept-with-reservation")):
  r=m.record_assessment({"panel":p,"reviewerId":rid,"assessmentState":state}); p=r["panel"]
  r=m.record_signoff({"panel":p,"reviewerId":rid,"signoffState":"signed"}); p=r["panel"]
 c=m.completion_status({"panel":p}); assert c["administratively_complete"] and c["scientifically_resolved"] is None and not c["automatic_resolution"]

def test_independence_disclosure_not_auto_disqualifying():
 i=m.independence_check(payload()); assert i["ok"] and "bob" in i["conflict_disclosures_present"] and i["automatic_disqualification"] is False

def test_audit_packet_and_contract_boundaries():
 e=m.audit_event_draft({**payload(),"eventType":"dissent-recorded","reviewerId":"bob","recordRef":"dissent-1"}); assert e["ok"] and e["automatic_append"] is False and e["automatic_resolution"] is False
 p=m.panel_packet(payload()); assert p["ok"] and p["packet"]["automatic_consensus"] is False and p["packet"]["truth_ranking"] is False
 h=m.health(); assert h["api_route_count"]==18 and h["backward_compatible_v0135170"]
 c=m.contract(); assert c["majority_voting"] is False and c["consensus_scoring"] is False
 a=m.acceptance_report(); assert a["dissent_preserved"] and not a["reviewer_ranking"] and not a["automatic_scientific_validity"]
