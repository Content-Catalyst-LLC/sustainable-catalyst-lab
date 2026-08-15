import copy
import pytest
from app.systematic_evidence_synthesis_v0640 import (
    SystematicEvidenceSynthesisError, health, policies, normalize_protocol, normalize_effect,
    record_synthesis_review, meta_analyze, build_synthesis_packet, verify_synthesis_packet,
)

def source(sid, decision="include", status="active"):
    return {"id":sid,"sourceType":"journal-article","title":sid,"status":status,"peerReviewStatus":"peer-reviewed","reviewHistory":[{"decision":decision,"rationale":"reviewed for synthesis","reviewerRole":"researcher"}]}

def protocol(**kw):
    p={"id":"syn-1","title":"Synthesis","researchQuestion":"Does X affect Y?","claimIds":["claim-1"],"effectMetric":"generic","modelChoice":"random-effects","minStudies":2,"inclusionCriteria":["eligible studies"]}
    p.update(kw); return p

def effect(eid,sid,val,se=.2,**kw):
    e={"id":eid,"sourceId":sid,"claimIds":["claim-1"],"effectMetric":"generic","effect":val,"standardError":se};e.update(kw);return e

def payload(**kw):
    p={"protocol":protocol(),"sources":[source("s1"),source("s2"),source("s3")],"effects":[effect("e1","s1",.2),effect("e2","s2",.4),effect("e3","s3",.3)]};p.update(kw);return p

def test_health_and_policy_boundaries():
    h=health();pol=policies();assert h["ok"] and h["version"]=="0.64.0";assert pol["rawParticipantDataAccepted"] is False;assert pol["automaticTruthInferenceAuthorized"] is False

def test_protocol_is_bounded_and_hashed():
    p=normalize_protocol(protocol());assert len(p["protocolHash"])==64 and p["heterogeneityEstimator"]=="dersimonian-laird" and p["minStudies"]==2

def test_effect_accepts_se_variance_or_ci():
    a=normalize_effect(effect("a","s1",.1,standardError=.1));b=normalize_effect({"id":"b","sourceId":"s1","effectMetric":"generic","effect":.1,"variance":.04});c=normalize_effect({"id":"c","sourceId":"s1","effectMetric":"generic","effect":.1,"ciLow":-.1,"ciHigh":.3});assert a["standardError"]==.1 and b["standardError"]==.2 and c["standardError"]>0

def test_raw_data_and_credentials_rejected():
    with pytest.raises(SystematicEvidenceSynthesisError): normalize_effect({**effect("a","s1",.1),"rows":[1,2]})
    with pytest.raises(SystematicEvidenceSynthesisError): normalize_protocol({**protocol(),"api_key":"x"})

def test_random_effects_meta_analysis_and_heterogeneity():
    r=meta_analyze(payload());m=r["metaAnalysis"];assert m["k"]==3 and .19 < m["pooledEffect"] < .41 and m["tauSquared"]>=0 and m["iSquaredPercent"]>=0;assert r["gate"]=="needs-review"

def test_fixed_effect_mode():
    p=payload(protocol=protocol(modelChoice="fixed-effect"));r=meta_analyze(p);assert r["metaAnalysis"]["model"]=="fixed-effect" and r["metaAnalysis"]["tauSquared"]>=0

def test_unreviewed_and_retracted_sources_not_silently_pooled():
    p=payload(sources=[source("s1"),source("s2",decision="reopen"),source("s3",status="retracted")]);r=meta_analyze(p);assert "s2" in r["unreviewedSourceIds"] and "s3" in r["excludedSourceIds"] and r["eligibleEffectCount"]==1 and r["gate"]=="needs-source-review"

def test_metric_mismatch_blocks_harmonization():
    p=payload(effects=[effect("e1","s1",.2),effect("e2","s2",.3,effectMetric="mean-difference")]);r=meta_analyze(p);assert r["gate"]=="needs-effect-harmonization" and r["metricMismatchEffectIds"]==["e2"]

def test_replication_assessment_preserves_disagreement():
    p=payload(effects=[effect("orig","s1",.4,.1),effect("rep","s2",-.3,.1,replicationOfSourceId="s1")]);r=meta_analyze(p);assert r["replicationRows"][0]["gate"]=="discordant-direction"

def test_high_heterogeneity_requires_qualified_review():
    p=payload(effects=[effect("e1","s1",-2,.1),effect("e2","s2",2,.1),effect("e3","s3",0,.1)]);r=meta_analyze(p);assert r["gate"]=="heterogeneous" and r["metaAnalysis"]["iSquaredPercent"]>=75
    reviewed=record_synthesis_review({"protocol":p["protocol"],"review":{"decision":"accept-with-qualification","rationale":"High heterogeneity is material and retained."}})["protocol"]
    p["protocol"]=reviewed;assert meta_analyze(p)["gate"]=="synthesis-reviewed"

def test_block_review_propagates():
    reviewed=record_synthesis_review({"protocol":protocol(),"review":{"decision":"block","rationale":"Protocol scope is not defensible."}})["protocol"]
    assert meta_analyze(payload(protocol=reviewed))["gate"]=="blocked"

def test_leave_one_out_is_reported_for_three_or_more_studies():
    r=meta_analyze(payload());assert len(r["leaveOneOut"])==3 and all("omittedEffectId" in x for x in r["leaveOneOut"])

def test_packet_is_metadata_only_and_tamper_evident():
    reviewed=record_synthesis_review({"protocol":protocol(),"review":{"decision":"accept","rationale":"Evidence synthesis reviewed."}})["protocol"]
    p=payload(protocol=reviewed);packet=build_synthesis_packet(p);assert packet["gate"]=="synthesis-reviewed"; assert all(k not in packet for k in ("rawData","rows","credentials","inputs")); assert verify_synthesis_packet({"packet":packet})["ok"]
    bad=copy.deepcopy(packet);bad["metaAnalysis"]["pooledEffect"]+=1;assert not verify_synthesis_packet({"packet":bad})["ok"]
