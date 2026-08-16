import copy
import pytest
from app.causal_inference_v0670 import (
    CausalInferenceError, health, policies, normalize_design, normalize_estimate,
    normalize_diagnostic, record_review, evaluate, build_packet, verify_packet,
)


def design(method='difference-in-differences', review=None):
    req = {
        'matching': [('conditional-exchangeability','asserted'),('overlap','asserted'),('consistency','asserted')],
        'weighting': [('conditional-exchangeability','asserted'),('overlap','asserted'),('consistency','asserted')],
        'difference-in-differences': [('parallel-trends','asserted'),('no-anticipation','asserted'),('stable-composition','asserted')],
        'interrupted-time-series': [('stable-pretrend','asserted'),('no-concurrent-intervention','asserted'),('stable-measurement','asserted')],
        'regression-discontinuity': [('continuity-at-cutoff','asserted'),('no-precise-manipulation','asserted'),('local-comparability','asserted')],
    }[method]
    return {
        'id':'causal-1','title':'Causal design','method':method,'studyId':'study-1','linkedClaimIds':['claim-1'],
        'estimand':'Average treatment effect within the governed study boundary.',
        'treatmentDefinition':'Exposure to intervention','comparisonDefinition':'Comparison condition','outcomeDefinition':'Governed outcome',
        'timeBoundary':'Study observation window','assignmentMechanism':'Non-random assignment documented by researcher',
        'identificationAssumptions':[{'kind':k,'status':s,'statement':k.replace('-',' ')} for k,s in req],
        'limitations':'Residual confounding and design assumptions remain review boundaries.',
        'reviewHistory': review or [],
    }


def diagnostics(method='difference-in-differences', state='pass'):
    kinds={
        'matching':['balance','overlap','sensitivity'],
        'weighting':['balance','overlap','sensitivity'],
        'difference-in-differences':['parallel-trends','placebo','sensitivity'],
        'interrupted-time-series':['pretrend','placebo','sensitivity'],
        'regression-discontinuity':['bandwidth','continuity','manipulation','sensitivity'],
    }[method]
    return [{'id':f'd-{k}','designId':'causal-1','kind':k,'state':state,'note':'Governed aggregate diagnostic.'} for k in kinds]


def estimate():
    return {'id':'e-1','designId':'causal-1','effectMetric':'difference','estimate':1.25,'standardError':0.2,'sampleSizeTreated':120,'sampleSizeComparison':120}


def reviewed(method='difference-in-differences', decision='accept-assumptions'):
    d=normalize_design(design(method))
    return record_review({'design':d,'review':{'decision':decision,'rationale':'Assumptions and diagnostics reviewed explicitly.','reviewedAt':'2026-08-15T20:00:00-05:00'}})['design']


def test_health_policy_boundaries():
    h=health(); p=policies()
    assert h['ok'] and p['explicitIdentificationAssumptionsRequired']
    assert not h['automaticCausalProof'] and not p['participantLevelDataAccepted']
    assert {'matching','weighting','difference-in-differences','interrupted-time-series','regression-discontinuity'} <= set(h['methods'])


def test_raw_data_credentials_and_code_rejected():
    for bad in ({'rows':[1]}, {'credentials':{'x':'y'}}, {'python':'print(1)'}, {'participantData':[1,2]}):
        payload=design(); payload.update(bad)
        with pytest.raises(CausalInferenceError): normalize_design(payload)


def test_design_hash_deterministic_and_method_registered():
    a=normalize_design(design()); b=normalize_design(design())
    assert a['designHash']==b['designHash']
    bad=design(); bad['method']='magic-causality'
    with pytest.raises(CausalInferenceError): normalize_design(bad)


def test_estimate_requires_uncertainty_and_aggregate_only():
    assert normalize_estimate(estimate())['estimate']==1.25
    e=estimate(); e.pop('standardError')
    with pytest.raises(CausalInferenceError): normalize_estimate(e)
    e=estimate(); e['rows']=[{'y':1}]
    with pytest.raises(CausalInferenceError): normalize_estimate(e)


def test_matching_requires_balance_overlap_and_sensitivity():
    r=evaluate({'design':design('matching'),'estimates':[estimate() | {'designId':'causal-1'}],'diagnostics':diagnostics('matching')[:-1]})
    assert r['gate']=='needs-diagnostics'
    assert 'sensitivity' in r['missingDiagnosticKinds']


def test_did_requires_parallel_trends_assumption():
    d=design(); d['identificationAssumptions']=[x for x in d['identificationAssumptions'] if x['kind']!='parallel-trends']
    r=evaluate({'design':d,'estimates':[estimate()],'diagnostics':diagnostics()})
    assert r['gate']=='needs-identification-assumptions'
    assert 'parallel-trends' in r['missingAssumptionKinds']


def test_challenged_assumption_blocks_progression():
    d=design(); d['identificationAssumptions'][0]['status']='challenged'
    r=evaluate({'design':d,'estimates':[estimate()],'diagnostics':diagnostics()})
    assert r['gate']=='assumption-challenge'


def test_failed_diagnostic_is_not_overridden_by_review():
    d=reviewed()
    ds=diagnostics(); ds[0]['state']='fail'
    r=evaluate({'design':d,'estimates':[estimate()],'diagnostics':ds})
    assert r['gate']=='diagnostic-failure'
    assert r['automaticCausalProof'] is False


def test_caution_requires_qualified_review():
    ds=diagnostics(); ds[0]['state']='caution'
    r=evaluate({'design':reviewed(decision='accept-assumptions'),'estimates':[estimate()],'diagnostics':ds})
    assert r['gate']=='sensitivity-or-qualification-needed'
    rq=evaluate({'design':reviewed(decision='accept-with-qualification'),'estimates':[estimate()],'diagnostics':ds})
    assert rq['gate']=='causal-estimate-bounded-with-qualification'


def test_clean_reviewed_did_reaches_bounded_estimate_not_proof():
    r=evaluate({'design':reviewed(),'estimates':[estimate()],'diagnostics':diagnostics()})
    assert r['gate']=='causal-estimate-bounded'
    assert r['automaticCausalProof'] is False
    assert 'not automatic proof' in r['causalLanguageBoundary']


def test_rdd_has_method_specific_diagnostics():
    d=reviewed('regression-discontinuity')
    e=estimate(); e['designId']='causal-1'
    r=evaluate({'design':d,'estimates':[e],'diagnostics':diagnostics('regression-discontinuity')})
    assert r['gate']=='causal-estimate-bounded'
    assert {'bandwidth','continuity','manipulation','sensitivity'} <= set(r['requiredDiagnosticKinds'])


def test_packet_is_metadata_only_and_deterministic():
    payload={'design':reviewed(),'estimates':[estimate()],'diagnostics':diagnostics()}
    a=build_packet(payload); b=build_packet(payload)
    assert a['packetHash']==b['packetHash']
    assert a['rawScientificDataIncluded'] is False and a['participantLevelDataIncluded'] is False
    assert 'rows' not in str(a).lower()


def test_packet_verification_detects_tampering():
    p=build_packet({'design':reviewed(),'estimates':[estimate()],'diagnostics':diagnostics()})
    assert verify_packet({'packet':p})['ok']
    q=copy.deepcopy(p); q['gate']='causal-proof'
    assert not verify_packet({'packet':q})['ok']
