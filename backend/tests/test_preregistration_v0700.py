import copy
import pytest
from app.preregistration_v0700 import (
    PreregistrationError, health, policies, normalize_question, normalize_hypothesis,
    normalize_preregistration, normalize_deviation, freeze_preregistration, verify_freeze,
    record_review, evaluate, build_packet, verify_packet,
)


def question(**kw):
    d={"id":"rq-1","studyId":"study-1","question":"Does the registered exposure change the primary outcome in the scoped population?","questionType":"causal","rationale":"The question tests the mechanism identified in the scientific theory.","populationBoundary":"Adults represented by the registered study protocol.","exposureOrIntervention":"Registered study exposure.","comparator":"Registered comparison condition.","outcomeBoundary":"Primary outcome measured by the registered instrument.","timeHorizon":"End of the registered observation period.","linkedTheoryIds":["theory-1"],"linkedClaimIds":["claim-1"]}
    d.update(kw); return d


def hypothesis(**kw):
    d={"id":"rh-1","studyId":"study-1","researchQuestionId":"rq-1","linkedArgumentHypothesisId":"hyp-1","linkedTheoryPredictionId":"prediction-1","role":"primary","statement":"The registered exposure will increase the primary outcome relative to comparator.","direction":"positive","outcomeRef":"primary-outcome","exposureRef":"exposure-1","effectOrContrast":"Exposure minus comparator on the registered outcome scale.","falsificationBoundary":"A precise null or reversed estimate under the registered analysis challenges the hypothesis."}
    d.update(kw); return d


def prereg(**kw):
    d={"id":"prereg-1","studyId":"study-1","title":"Primary preregistration","researchQuestionIds":["rq-1"],"hypothesisIds":["rh-1"],"primaryOutcome":"Primary validated outcome score at the registered endpoint.","secondaryOutcomes":["Secondary outcome score"],"analysisPlan":"Estimate the registered contrast using the prespecified model, uncertainty interval, covariates, diagnostics, and sensitivity analysis.","inclusionCriteria":"Include records meeting the registered study eligibility rules.","exclusionCriteria":"Exclude only records meeting the prespecified protocol-defined invalidity criteria.","stoppingRule":"Stop enrollment or evidence accumulation at the prespecified information threshold.","sampleSizeRationale":"Information size is justified by the prespecified precision and power target.","missingDataPlan":"Use the prespecified missingness assessment and sensitivity analysis.","multiplicityPlan":"Primary outcome is confirmatory; secondary outcomes are interpreted with the prespecified multiplicity boundary.","sensitivityPlan":"Repeat the primary analysis under the registered alternate specification and missing-data assumptions.","resultsAccessState":"not-inspected","preResultAttestation":"I attest that outcome results have not been inspected before this registration is frozen.","scopeBoundary":"Applies only to the registered population, measures, design, and analysis plan.","limitations":"Preregistration constrains analytic flexibility but does not prove validity or eliminate all researcher degrees of freedom."}
    d.update(kw); return d


def base_payload(p=None):
    return {"preregistration":p or prereg(),"questions":[question()],"hypotheses":[hypothesis()],"deviations":[]}


def frozen_payload(p=None):
    x=base_payload(p)
    x["freeze"]=freeze_preregistration({**x,"frozenAt":"2026-08-16T01:00:00Z"})
    return x


def reviewed(decision="accept-within-scope", p=None):
    r=record_review({"preregistration":p or prereg(),"review":{"decision":decision,"rationale":"Research questions, hypotheses, outcomes, analysis rules, freeze integrity, deviations, scope and limitations were reviewed.","reviewedAt":"2026-08-16T01:05:00Z"}})
    return r["preregistration"]


def test_health_and_policy_preserve_human_governance():
    assert health()["status"]=="preregistration-ready"
    p=policies(); assert p["preResultFreezeRequired"] is True and p["frozenSnapshotImmutable"] is True and p["automaticPostHocPreregistrationAuthorized"] is False


def test_raw_data_and_credentials_are_rejected():
    with pytest.raises(PreregistrationError): normalize_preregistration({**prereg(),"rawData":[1,2]})
    with pytest.raises(PreregistrationError): normalize_question({**question(),"credentials":{"token":"x"}})


def test_question_hypothesis_and_preregistration_hashes_are_deterministic():
    assert normalize_question(question())["questionHash"]==normalize_question(copy.deepcopy(question()))["questionHash"]
    assert normalize_hypothesis(hypothesis())["hypothesisHash"]==normalize_hypothesis(copy.deepcopy(hypothesis()))["hypothesisHash"]
    assert normalize_preregistration(prereg())["preregistrationHash"]==normalize_preregistration(copy.deepcopy(prereg()))["preregistrationHash"]


def test_research_question_and_hypothesis_registry_are_required():
    p=base_payload(); p["preregistration"]["researchQuestionIds"]=[]; assert evaluate(p)["gate"]=="needs-research-question"
    p=base_payload(); p["preregistration"]["hypothesisIds"]=[]; assert evaluate(p)["gate"]=="needs-hypotheses"


def test_question_and_hypothesis_boundaries_must_be_complete():
    p=base_payload(); p["questions"][0]["populationBoundary"]=""; assert evaluate(p)["gate"]=="research-question-incomplete"
    p=base_payload(); p["hypotheses"][0]["falsificationBoundary"]=""; assert evaluate(p)["gate"]=="hypothesis-registry-incomplete"


def test_primary_outcome_analysis_exclusions_and_stopping_rule_are_required():
    p=base_payload(prereg(primaryOutcome="")); assert evaluate(p)["gate"]=="needs-primary-outcome"
    p=base_payload(prereg(analysisPlan="")); assert evaluate(p)["gate"]=="needs-analysis-plan"
    p=base_payload(prereg(exclusionCriteria="")); assert evaluate(p)["gate"]=="needs-exclusion-rules"
    p=base_payload(prereg(stoppingRule="")); assert evaluate(p)["gate"]=="needs-stopping-rule"


def test_sample_size_rationale_and_pre_result_attestation_are_required():
    p=base_payload(prereg(sampleSizeRationale="")); assert evaluate(p)["gate"]=="needs-sample-size-rationale"
    p=base_payload(prereg(resultsAccessState="unknown")); assert evaluate(p)["gate"]=="pre-result-attestation-required"


def test_freeze_requires_not_inspected_state_and_attestation():
    with pytest.raises(PreregistrationError): freeze_preregistration(base_payload(prereg(resultsAccessState="inspected")))
    with pytest.raises(PreregistrationError): freeze_preregistration(base_payload(prereg(preResultAttestation="")))


def test_freeze_is_deterministic_for_fixed_time_and_tamper_evident():
    a=freeze_preregistration({**base_payload(),"frozenAt":"2026-08-16T01:00:00Z"})
    b=freeze_preregistration({**base_payload(),"frozenAt":"2026-08-16T01:00:00Z"})
    assert a["freezeHash"]==b["freezeHash"]
    p={**base_payload(),"freeze":a}; assert verify_freeze(p)["ok"] is True
    p["preregistration"]["analysisPlan"]="Changed after freeze"; assert evaluate(p)["gate"]=="freeze-integrity-failure"


def test_complete_registration_needs_freeze_then_human_review():
    assert evaluate(base_payload())["gate"]=="needs-freeze"
    assert evaluate(frozen_payload())["gate"]=="needs-review"


def test_post_freeze_deviation_requires_rationale_and_timestamp():
    p=frozen_payload(); p["deviations"]=[{"id":"d1","preregistrationId":"prereg-1","freezeHash":p["freeze"]["freezeHash"],"deviationType":"analysis","description":"Changed robust variance estimator.","rationale":"","declaredAt":""}]
    assert evaluate(p)["gate"]=="needs-deviation-rationale"
    d=normalize_deviation({"id":"d1","preregistrationId":"prereg-1","freezeHash":p["freeze"]["freezeHash"],"deviationType":"analysis","description":"Changed robust variance estimator after a documented software incompatibility.","rationale":"The prespecified estimator was unavailable in the certified runtime; the substitute is reported as a deviation.","impactOnInterpretation":"Treat inferential uncertainty as qualified relative to the original plan.","discoveredAt":"2026-08-16T01:10:00Z","declaredAt":"2026-08-16T01:12:00Z"})
    assert d["deviationHash"]


def test_human_review_can_bound_clean_or_deviated_registration_without_proving_hypothesis():
    p=frozen_payload(); p["preregistration"]=reviewed()
    r=evaluate(p); assert r["gate"]=="preregistration-bounded" and r["automaticHypothesisValidation"] is False
    p=frozen_payload(); p["preregistration"]=reviewed(); p["deviations"]=[{"id":"d1","preregistrationId":"prereg-1","freezeHash":p["freeze"]["freezeHash"],"deviationType":"analysis","description":"Changed a prespecified implementation detail after freeze.","rationale":"The original implementation was unavailable and the change is explicitly disclosed.","impactOnInterpretation":"Result remains bounded by this deviation.","declaredAt":"2026-08-16T01:12:00Z"}]
    assert evaluate(p)["gate"]=="preregistration-bounded-with-deviations"


def test_block_and_qualified_reviews_propagate_to_gate_and_packet_is_tamper_evident():
    p=frozen_payload(); p["preregistration"]=reviewed("block"); assert evaluate(p)["gate"]=="blocked"
    p=frozen_payload(); p["preregistration"]=reviewed("accept-with-qualification"); assert evaluate(p)["gate"]=="preregistration-bounded-with-qualification"
    p=frozen_payload(); p["preregistration"]=reviewed(); pkt=build_packet(p); assert pkt["rawScientificDataIncluded"] is False and verify_packet({"packet":pkt})["ok"] is True
    bad=copy.deepcopy(pkt); bad["gate"]="blocked"; assert verify_packet({"packet":bad})["ok"] is False
