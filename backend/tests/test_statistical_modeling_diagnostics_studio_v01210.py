import math
import pytest
from app.statistical_modeling_diagnostics_studio_v01210 import *

ROWS=[
 {'x1':1.0,'x2':2.0,'y':3.1,'bin':0,'count':1},
 {'x1':2.0,'x2':1.0,'y':4.8,'bin':0,'count':2},
 {'x1':3.0,'x2':4.0,'y':8.2,'bin':0,'count':3},
 {'x1':4.0,'x2':3.0,'y':9.9,'bin':1,'count':4},
 {'x1':5.0,'x2':6.0,'y':13.1,'bin':1,'count':6},
 {'x1':6.0,'x2':5.0,'y':14.8,'bin':1,'count':7},
 {'x1':7.0,'x2':8.0,'y':18.2,'bin':1,'count':9},
 {'x1':8.0,'x2':7.0,'y':19.9,'bin':1,'count':11},
]

def payload(family='gaussian'):
 response={'gaussian':'y','binomial-logit':'bin','poisson-log':'count'}[family]
 estimator='ols' if family=='gaussian' else 'glm'
 return {'dataset':{'id':'fixture','rows':ROWS},'model':{'id':f'm-{family}','title':family,'family':family,'estimator':estimator,'features':['x1','x2'],'response':response}}

def test_health_catalog_boundaries():
 h=health(); assert h['version']=='0.121.0' and h['family_count']==3 and h['automatic_model_selection'] is False and h['determine_truth'] is False
 assert 'influence' in catalog()['diagnostic_families']

def test_normalize_and_fit_gaussian():
 n=normalize_model_spec(payload()); assert n['source_rows_immutable'] is True and len(n['model_spec_hash'])==64
 f=fit_model(payload())['result']; assert f['automatic_significance_labels'] is False and f['automatic_causal_inference'] is False and len(f['studio_result_hash'])==64
 assert f['metrics']['rmse']>=0

def test_coefficients_no_significance_labels():
 f=fit_model(payload())['result']; c=coefficient_report({'result':f}); assert all(r['significance_label'] is None for r in c['coefficients'])

def test_gaussian_diagnostics():
 f=fit_model(payload())['result']; d=diagnose_model({**payload(),'result':f,'row_order_meaningful':True}); assert d['family']=='gaussian'; assert 'normality' in d and 'heteroskedasticity' in d and 'influence' in d and d['automatic_model_rejection'] is False
 assert len(d['multicollinearity']['vif'])==2

def test_binomial_diagnostics():
 f=fit_model(payload('binomial-logit'))['result']; d=diagnose_model({**payload('binomial-logit'),'result':f,'calibration_bins':4}); assert 'classification' in d and 'calibration' in d; assert d['classification']['automatic_threshold_optimization'] is False

def test_poisson_diagnostics():
 f=fit_model(payload('poisson-log'))['result']; d=diagnose_model({**payload('poisson-log'),'result':f}); assert 'deviance' in d and d['deviance']['automatic_overdispersion_conclusion'] is False

def test_prediction_evaluation():
 f=fit_model(payload())['result']; e=evaluate_predictions({'result':f,'evaluation_rows':ROWS}); assert e['metrics']['count']==8 and e['automatic_model_approval'] is False

def test_cross_validation():
 cv=cross_validate_model({**payload(),'folds':4,'repeats':1})['validation']; assert cv['automatic_model_selection'] is False and cv['mean']>=0

def test_comparison_preserves_candidate_order_and_no_winner():
 p={'dataset':{'id':'fixture','rows':ROWS},'candidates':[payload()['model'],{**payload()['model'],'id':'ridge','estimator':'ridge','alpha':1.0}],'folds':4}
 c=compare_models(p); assert [x['model_id'] for x in c['candidates']]==['m-gaussian','ridge']; assert c['automatic_model_selection'] is False and c['selected_model_id'] is None
 c2=compare_models({**p,'selected_model_id':'ridge'}); assert c2['selected_model_id']=='ridge' and c2['selection_declared_by_user'] is True

def test_visual_studio_snapshot_export_core():
 s=build_studio(payload()); assert s['automatic_model_selection'] is False and s['source_rows_immutable'] is True
 v=build_visualization_plan({'result':s['model']}); assert v['automatic_render'] is False and len(v['figures'])>=4
 snap=build_snapshot({'studio':s}); assert snap['automatic_persistence'] is False and len(snap['snapshot_hash'])==64
 ex=build_export_plan({'formats':['json','pdf','svg']}); assert ex['automatic_file_write'] is False
 core=build_core_object_plan({'session_id':'s1','model_id':'m1'}); assert core['automatic_core_submission'] is False and core['core_executes_model'] is False


def test_assumption_and_effect_reports():
    f=fit_model(payload())['result']
    a=assumption_audit({**payload(),'result':f}); assert a['automatic_assumption_pass_fail'] is False and 'normality' in a['diagnostics']
    e=effect_report({'result':f}); assert e['automatic_significance_labels'] is False and all(x['significance_label'] is None for x in e['effects'])
