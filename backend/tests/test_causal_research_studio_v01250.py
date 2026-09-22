import numpy as np
from app.causal_research_studio_v01250 import *


def rows():
    out=[]
    for i in range(80):
        x=(i%10)/10
        z=((i*7)%13)/13
        p=1/(1+np.exp(-(-0.5+1.2*x-0.8*z)))
        t=1.0 if ((i*37)%100)/100 < p else 0.0
        y=3+2*t+1.5*x-0.7*z+(i%3)*0.05
        out.append({'t':t,'y':y,'x':x,'z':z,'post':1.0 if i>=40 else 0.0,'time':float(i),'treated_group':1.0 if i%2==0 else 0.0,'running':(i-40)/10})
    return out


def study(): return {'id':'c1','title':'Causal study','rows':rows(),'treatment':'t','outcome':'y','covariates':['x','z'],'estimand':'ATE'}


def test_health_catalog_boundaries():
    h=health(); c=catalog(); assert h['version']=='0.125.0' and h['method_family_count']==8 and h['figure_family_count']==12
    assert h['automatic_causal_proof'] is False and h['human_causal_review_required'] is True
    assert 'synthetic-control' in c['method_families']


def test_dag_and_adjustment_plan():
    dag={'nodes':[{'id':'x'},{'id':'t'},{'id':'y'}],'edges':[{'source':'x','target':'t'},{'source':'x','target':'y'},{'source':'t','target':'y'}]}
    d=normalize_dag(dag); assert d['dag']['acyclic'] and len(d['dag']['dag_hash'])==64
    p=dag_adjustment_plan({'dag':dag,'treatment':'t','outcome':'y','adjustment_set':['x']}); assert p['declared_adjustment_set']==['x'] and p['backdoor_sufficiency_certified'] is False


def test_propensity_matching_weighting_balance_overlap():
    p=fit_propensity(study()); assert len(p['scores'])==80 and p['propensity_model_correctness_certified'] is False
    m=estimate_matching({**study(),'replacement':False}); assert m['pair_count']>5 and m['causal_proof'] is False
    w=estimate_weighting(study()); assert w['effective_sample_size']>0 and w['causal_proof'] is False
    b=balance_report({**study(),'weights':w['weights']}); assert len(b['covariates'])==2 and b['automatic_balance_pass_fail'] is False
    o=overlap_report(study()); assert 0<=o['common_support']['row_fraction']<=1 and o['overlap_sufficient_certified'] is False


def test_did_its_rd():
    r=rows()
    did=estimate_did({'rows':r,'outcome':'y','treated':'treated_group','post':'post'}); assert did['parallel_trends_certified'] is False
    its=estimate_its({'rows':r,'outcome':'y','time':'time','post':'post'}); assert its['no_concurrent_intervention_certified'] is False
    rd=estimate_rd({'rows':r,'outcome':'y','running':'running','cutoff':0,'bandwidth':2.5}); assert rd['rows_in_bandwidth']>=8 and rd['causal_proof'] is False


def test_synthetic_control_and_counterfactual():
    tp=[1,1.2,1.4,1.6]; post=[2.5,2.8]
    dp=[[.8,1.2],[1.0,1.4],[1.2,1.6],[1.4,1.8]]; dpost=[[1.6,2.0],[1.8,2.2]]
    s=estimate_synthetic_control({'treated_pre':tp,'treated_post':post,'donors_pre':dp,'donors_post':dpost}); assert len(s['donor_weights'])==2 and s['causal_proof'] is False
    c=counterfactual_report({'observed':[3,4],'counterfactual':[2,2.5]}); assert c['counterfactual_observed'] is False and c['average_gap']>0


def test_plans_studio_snapshot_core_and_boundaries():
    assert robustness_plan({})['automatic_execution'] is False
    assert placebo_plan({})['placebo_pass_fail_certified'] is False
    assert len(build_visualization_plan({})['figures'])==12
    st=build_studio({'study_id':'c1','method':'difference-in-differences'}); assert st['automatic_causal_proof'] is False
    snap=build_snapshot({'studio':st}); assert len(snap['snapshot_hash'])==64 and snap['automatic_persistence'] is False
    assert build_reproduction_plan({'study_hash':'abc'})['automatic_execution'] is False
    assert build_export_plan({})['automatic_publication'] is False
    assert build_core_object_plan({'session_id':'s1','analysis_id':'c1'})['automatic_core_submission'] is False
    assert build_execution_lineage_plan({'session_id':'s1','analysis_id':'c1'})['automatic_execution'] is False
    b=interpretation_boundaries_report(); assert b['scientific_validity_certified'] is False and len(b['boundaries'])>=7
