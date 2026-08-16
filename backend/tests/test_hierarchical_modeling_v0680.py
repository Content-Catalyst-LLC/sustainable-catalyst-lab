import copy
import math

import pytest

from app.hierarchical_modeling_v0680 import (
    HierarchicalModelingError,
    build_packet,
    evaluate,
    fit_model,
    health,
    normalize_model,
    normalize_unit,
    policies,
    record_review,
    verify_packet,
)


def model(model_type="hierarchical-normal", **kw):
    base={
        "id":"hm-1","title":"Cross-group outcome model","modelType":model_type,"levelType":"study",
        "effectMetric":"difference","studyId":"study-1","linkedClaimIds":["claim-1"],
        "outcomeDefinition":"Aggregate outcome contrast","populationBoundary":"Recorded study populations and settings only.",
        "generalizationBoundary":"Do not extrapolate beyond recorded study populations, settings, moderator range, or design assumptions.",
        "modelingAssumptions":"Normal-normal aggregate effect approximation; reported standard errors treated as known sampling uncertainty.",
        "limitations":"Between-study heterogeneity and omitted moderators can limit transportability.",
    }
    base.update(kw); return base


def unit(i, y, se=0.2, **kw):
    base={"id":f"u{i}","modelId":"hm-1","unitId":f"study-{i}","sourceRef":f"source-{i}","estimate":y,"standardError":se,"sampleSize":100+i}
    base.update(kw); return base


def reviewed(m, decision="accept-within-scope"):
    return record_review({"model":m,"review":{"decision":decision,"rationale":"Reviewed modeled variation, shrinkage, heterogeneity, scope, and limitations.","reviewedAt":"2026-08-16T00:00:00Z"}})["model"]


def test_health_and_policy_keep_generalization_human_bounded():
    h=health(); p=policies()
    assert h["ok"] and h["version"]=="0.68.0" and h["platformVersion"]=="1.0.0"
    assert p["aggregateUnitEstimatesOnly"] is True
    assert p["automaticGeneralizabilityAuthorized"] is False
    assert p["participantLevelDataAccepted"] is False
    assert p["arbitraryCodeExecutionAuthorized"] is False


def test_raw_participant_data_and_credentials_are_rejected():
    with pytest.raises(HierarchicalModelingError): normalize_model({**model(),"credentials":{"token":"x"}})
    with pytest.raises(HierarchicalModelingError): normalize_unit({**unit(1,1.0),"participantData":[1,2,3]})


def test_model_and_unit_normalization_are_deterministic():
    a=normalize_model(model()); b=normalize_model(copy.deepcopy(model()))
    assert a["modelHash"]==b["modelHash"]
    u1=normalize_unit(unit(1,1.1)); u2=normalize_unit(copy.deepcopy(unit(1,1.1)))
    assert u1["unitHash"]==u2["unitHash"] and math.isclose(u1["standardError"],0.2)


def test_hierarchical_normal_partial_pooling_reports_tau_i2_and_shrinkage():
    units=[unit(1,0.2,0.12),unit(2,0.9,0.15),unit(3,1.4,0.18),unit(4,0.7,0.16)]
    f=fit_model({"model":model(),"unitEstimates":units})
    assert f["fitKind"]=="hierarchical-normal-partial-pooling"
    assert f["tauSquared"]>=0 and 0<=f["i2Percent"]<=100
    assert len(f["shrinkageRows"])==4
    assert any(abs(r["shrunkenEstimate"]-r["observedEstimate"])>1e-8 for r in f["shrinkageRows"])


def test_random_intercept_pools_clusters_not_raw_participants():
    m=model("random-intercept",levelType="site")
    units=[unit(1,0.2,clusterId="a"),unit(2,0.4,clusterId="a"),unit(3,1.0,clusterId="b"),unit(4,1.2,clusterId="b")]
    f=fit_model({"model":m,"unitEstimates":units})
    assert f["fitKind"]=="random-intercept" and f["clusterCount"]==2 and f["originalUnitCount"]==4
    assert len(f["clusterEstimates"])==2


def test_cross_study_pooling_requires_source_provenance():
    m=model("cross-study-pooling")
    units=[unit(1,0.2),unit(2,0.4,sourceRef="")]
    r=evaluate({"model":m,"unitEstimates":units})
    assert r["gate"]=="needs-study-provenance"


def test_random_slope_requires_moderator_variation_and_fits_when_present():
    m=model("random-slope",moderatorName="baseline-risk")
    flat=[unit(i,y,moderatorValue=1.0) for i,y in enumerate([.1,.2,.3,.4],1)]
    assert evaluate({"model":m,"unitEstimates":flat})["gate"]=="needs-moderator-variation"
    varied=[unit(1,.2,moderatorValue=0),unit(2,.5,moderatorValue=1),unit(3,.9,moderatorValue=2),unit(4,1.1,moderatorValue=3)]
    f=fit_model({"model":m,"unitEstimates":varied})
    assert f["fitKind"]=="random-slope-meta-regression" and f["slope"]>0
    assert f["moderatorMin"]==0 and f["moderatorMax"]==3


def test_cross_study_meta_regression_requires_source_refs_and_reports_residual_heterogeneity():
    m=model("cross-study-meta-regression",moderatorName="mean-age")
    units=[unit(1,.1,moderatorValue=30),unit(2,.4,moderatorValue=40),unit(3,.8,moderatorValue=50),unit(4,1.0,moderatorValue=60)]
    f=fit_model({"model":m,"unitEstimates":units})
    assert f["unitCount"]==4 and "qResidual" in f and "tauSquared" in f
    assert len(f["residualRows"])==4


def test_generalization_boundary_is_required_before_human_completion():
    m=model(generalizationBoundary="")
    units=[unit(1,.2),unit(2,.25),unit(3,.3)]
    r=evaluate({"model":reviewed(m),"unitEstimates":units})
    assert r["gate"]=="needs-generalization-boundary"


def test_high_heterogeneity_requires_qualified_review():
    units=[unit(1,-2,.1),unit(2,0,.1),unit(3,2,.1),unit(4,4,.1)]
    m1=reviewed(model(),"accept-within-scope")
    r1=evaluate({"model":m1,"unitEstimates":units})
    assert r1["highHeterogeneity"] is True and r1["gate"]=="heterogeneity-caution"
    m2=reviewed(model(),"accept-with-qualification")
    r2=evaluate({"model":m2,"unitEstimates":units})
    assert r2["gate"]=="multilevel-estimate-bounded-with-qualification"


def test_low_heterogeneity_still_requires_explicit_human_review():
    units=[unit(1,.20,.2),unit(2,.22,.2),unit(3,.18,.2)]
    r=evaluate({"model":model(),"unitEstimates":units})
    assert r["gate"]=="needs-review"
    r2=evaluate({"model":reviewed(model()),"unitEstimates":units})
    assert r2["gate"]=="multilevel-estimate-bounded"
    assert r2["automaticGeneralizability"] is False


def test_blocked_human_review_blocks_model_interpretation():
    units=[unit(1,.2),unit(2,.25),unit(3,.3)]
    r=evaluate({"model":reviewed(model(),"block"),"unitEstimates":units})
    assert r["gate"]=="blocked"


def test_packet_is_metadata_only_deterministic_and_tamper_evident():
    units=[unit(1,.2,.2),unit(2,.22,.2),unit(3,.18,.2)]
    payload={"model":reviewed(model()),"unitEstimates":units}
    p1=build_packet(payload); p2=build_packet(copy.deepcopy(payload))
    assert p1["packetHash"]==p2["packetHash"]
    assert p1["rawScientificDataIncluded"] is False and p1["participantLevelDataIncluded"] is False
    assert verify_packet({"packet":p1})["ok"] is True
    tampered=copy.deepcopy(p1); tampered["generalizationBoundary"]="Universal"
    assert verify_packet({"packet":tampered})["ok"] is False
