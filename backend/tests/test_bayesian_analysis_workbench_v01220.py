import copy
import math
import pytest
from app.bayesian_analysis_workbench_v01220 import *


def rows():
    return [{'x':i/4.0,'y':1.2+1.8*(i/4.0)+((i%4)-1.5)*0.08} for i in range(20)]

def payload():
    return {'dataset':{'id':'bayes-data','rows':rows()},'study':{'id':'bayes-1','title':'Bayesian regression','family':'gaussian','modelType':'linear','features':['x'],'response':'y','chains':2,'draws':60,'warmup':30,'posteriorPredictiveDraws':30,'seed':11,'coefficientPriorSD':3.0}}

def test_health_catalog_boundaries():
    h=health(); c=catalog(); assert h['ok'] and h['version']=='0.122.0'; assert h['automatic_prior_selection'] is False and h['automatic_convergence_certification'] is False; assert len(c['figure_families'])==12

def test_normalize_and_fit():
    n=normalize_analysis(payload()); assert n['source_rows_immutable'] is True and len(n['analysis_spec_hash'])==64
    f=fit_posterior(payload())['result']; assert f['dataset_id']=='bayes-data'; assert f['automatic_model_selection'] is False and f['scientific_validity_certified'] is False

def test_prior_posterior_and_diagnostics():
    f=fit_posterior(payload())['result']; pp=prior_posterior_report({'result':f}); assert pp['automatic_prior_selection'] is False and len(pp['terms'])>=2
    d=sampler_diagnostics({'result':f}); assert d['automatic_convergence_certification'] is False and d['terms'][0]['automatic_pass_fail'] is False
    a=convergence_audit({'result':f}); assert a['convergence_certified'] is False

def test_posterior_predictive_and_probability_report():
    f=fit_posterior(payload())['result']; p=posterior_predictive_report({'result':f}); assert p['automatic_model_approval'] is False and p['posterior_predictive']['checks']['statistics']
    q=probability_report({'result':f,'queries':[{'term':'z(x)','direction':'greater-than','threshold':0}]}); assert 0<=q['queries'][0]['posterior_probability']<=1 and q['automatic_decision'] is False

def test_hierarchical_normal_random_effects():
    p={'hierarchical':{'id':'h1','mu_prior_mean':0,'mu_prior_sd':5,'tau_prior_scale':1,'draws':500,'seed':7},'units':[{'id':'a','estimate':0.2,'standard_error':0.15},{'id':'b','estimate':0.7,'standard_error':0.2},{'id':'c','estimate':1.1,'standard_error':0.18},{'id':'d','estimate':0.6,'standard_error':0.22}]}
    r=fit_hierarchical_normal(p); assert r['unit_count']==4 and r['posterior']['tau']['mean']>=0 and r['automatic_generalization'] is False
    s=hierarchical_summary({'hierarchical_result':r}); assert s['automatic_heterogeneity_judgment'] is False and len(s['group_posteriors'])==4

def test_comparison_has_no_winner():
    a=fit_posterior(payload())['result']; b=copy.deepcopy(a); b['study']['id']='bayes-2'; c=compare_models({'results':[a,b]}); assert c['selected_model_id'] is None and c['automatic_model_selection'] is False

def test_visual_snapshot_export_reproduction_core():
    f=fit_posterior(payload())['result']; v=build_visualization_plan({'result':f}); assert v['automatic_render'] is False
    w=build_workbench(payload()); assert w['automatic_causal_inference'] is False
    s=build_snapshot({'workbench':w}); assert s['automatic_persistence'] is False and len(s['snapshot_hash'])==64
    rp=build_reproduction_plan({'result':f}); assert rp['automatic_execution'] is False
    ex=build_export_plan({'formats':['json','pdf','svg']}); assert ex['automatic_file_write'] is False
    core=build_core_object_plan({'session_id':'s1','model_id':'bayes-1'}); assert core['automatic_core_submission'] is False and core['core_selects_priors'] is False
