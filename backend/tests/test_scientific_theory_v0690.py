import copy
import pytest
from app.scientific_theory_v0690 import (
    ScientificTheoryError, health, policies, normalize_theory, normalize_construct, normalize_relation,
    normalize_prediction, build_graph, record_review, evaluate, build_packet, verify_packet,
)


def theory(**kw):
    d={"id":"theory-1","title":"Mechanism theory","theoryType":"mechanistic-theory","scopeBoundary":"Adults represented by the linked studies.","coreMechanism":"Exposure changes mediator state which changes outcome.","assumptions":"Recorded constructs and links are theoretical commitments.","limitations":"Transportability beyond the represented studies is not established.","linkedClaimIds":["claim-1"],"linkedHypothesisIds":["hyp-1"],"linkedModelIds":["model-1"]}
    d.update(kw); return d


def constructs():
    return [
        {"id":"exposure","theoryId":"theory-1","name":"Exposure","role":"exposure","definition":"Measured exposure intensity.","operationalization":"Study-level standardized exposure measure.","linkedEvidenceRefs":["claim-1"]},
        {"id":"outcome","theoryId":"theory-1","name":"Outcome","role":"outcome","definition":"Measured scientific outcome.","operationalization":"Study-level validated outcome measure."},
    ]


def relations():
    return [{"id":"r1","theoryId":"theory-1","sourceConstructId":"exposure","targetConstructId":"outcome","relationType":"causes","mechanism":"Exposure changes the outcome through the stated biological mechanism.","causalAssumptionRef":"causal-design-1","linkedEvidenceRefs":["claim-1"]}]


def predictions():
    return [{"id":"p1","theoryId":"theory-1","hypothesisId":"hyp-1","statement":"Higher exposure predicts higher outcome within the scoped population.","expectedDirection":"positive","falsificationCondition":"A precise null or reversed estimate across adequately powered scoped replications challenges the prediction.","linkedEvidenceRefs":["claim-1"]}]


def payload(t=None):
    return {"theory": t or theory(), "constructs":constructs(), "relations":relations(), "predictions":predictions()}


def reviewed(decision="accept-within-scope"):
    r=record_review({"theory":theory(),"review":{"decision":decision,"rationale":"Structure, predictions, scope and limitations were reviewed.","reviewedAt":"2026-08-16T00:00:00Z"}})
    return r["theory"]


def test_health_and_policy_keep_theory_human_governed():
    assert health()["status"]=="scientific-theory-ready"
    p=policies(); assert p["humanTheoryReviewRequired"] is True and p["automaticTheoryProofAuthorized"] is False and p["rawScientificDataAccepted"] is False


def test_raw_data_and_credentials_are_rejected():
    with pytest.raises(ScientificTheoryError): normalize_theory({**theory(),"rawData":[1,2]})
    with pytest.raises(ScientificTheoryError): normalize_construct({"theoryId":"theory-1","credentials":{"token":"x"}})


def test_normalization_and_graph_hash_are_deterministic():
    a=normalize_theory(theory()); b=normalize_theory(copy.deepcopy(theory())); assert a["theoryHash"]==b["theoryHash"]
    g1=build_graph(payload())["graph"]; g2=build_graph(payload())["graph"]; assert g1["graphHash"]==g2["graphHash"]


def test_at_least_two_constructs_are_required():
    p=payload(); p["constructs"]=p["constructs"][:1]; assert evaluate(p)["gate"]=="needs-constructs"


def test_construct_definitions_and_operationalization_are_required():
    p=payload(); p["constructs"][0]["definition"]=""; assert evaluate(p)["gate"]=="needs-construct-definitions"
    p=payload(); p["constructs"][0]["operationalization"]=""; assert evaluate(p)["gate"]=="needs-operationalization"


def test_relation_endpoints_must_resolve():
    p=payload(); p["relations"][0]["targetConstructId"]="missing"; assert evaluate(p)["gate"]=="unresolved-construct-reference"


def test_causal_relation_requires_explicit_mechanism():
    p=payload(); p["relations"][0]["mechanism"]=""; assert evaluate(p)["gate"]=="needs-mechanism"


def test_testable_prediction_and_falsification_boundary_are_required():
    p=payload(); p["predictions"]=[]; assert evaluate(p)["gate"]=="needs-predictions"
    p=payload(); p["predictions"][0]["falsificationCondition"]=""; assert evaluate(p)["gate"]=="needs-falsification-boundary"


def test_theory_requires_governed_evidence_linkage():
    p=payload()
    for c in p["constructs"]: c["linkedEvidenceRefs"]=[]
    for r in p["relations"]: r["linkedEvidenceRefs"]=[]
    for x in p["predictions"]: x["linkedEvidenceRefs"]=[]
    assert evaluate(p)["gate"]=="needs-evidence-linkage"


def test_theory_requires_human_review_after_structure_is_complete():
    assert evaluate(payload())["gate"]=="needs-review"


def test_human_review_can_bound_or_qualify_theory_but_not_prove_it():
    r=evaluate(payload(reviewed()))
    assert r["gate"]=="theory-bounded" and r["automaticTheoryProof"] is False
    rq=evaluate(payload(reviewed("accept-with-qualification")))
    assert rq["gate"]=="theory-bounded-with-qualification"


def test_block_review_propagates_to_theory_gate():
    assert evaluate(payload(reviewed("block")))["gate"]=="blocked"


def test_packet_is_metadata_only_and_tamper_evident():
    pkt=build_packet(payload(reviewed()))
    assert pkt["rawScientificDataIncluded"] is False and verify_packet({"packet":pkt})["ok"] is True
    bad=copy.deepcopy(pkt); bad["gate"]="blocked"; assert verify_packet({"packet":bad})["ok"] is False
