from app.sensitivity_global_uncertainty_analysis_studio_v01240 import *


def model():
    return {'id':'sensitivity-model','family':'declarative-expression','title':'Sensitivity model','definition':{'equation':'y = a*x + b*x*x + a*b'},'variables':[{'symbol':'x','label':'X','role':'input'},{'symbol':'y','label':'Y','role':'response'}],'parameters':[{'symbol':'a','role':'estimated','value':2},{'symbol':'b','role':'estimated','value':0.5}],'constants':[],'datasetBindings':[]}


def study(samples=64,seed=42):
    return {'id':'sens-study','title':'Sensitivity study','model':model(),'values':{'x':3},'uncertainInputs':[{'symbol':'a','label':'A','distribution':'uniform','low':1,'high':3},{'symbol':'b','label':'B','distribution':'uniform','low':0.1,'high':1.0}],'design':{'method':'latin-hypercube','samples':samples,'seed':seed},'analysis':{'confidence':0.95}}


def test_health_catalog_boundaries():
    h=health(); c=catalog(); assert h['version']=='0.124.0' and h['method_family_count']==6 and h['figure_family_count']==12
    assert h['automatic_parameter_ranking'] is False and h['automatic_causal_inference'] is False
    assert 'morris-elementary-effects' in c['method_families']


def test_normalize_and_sobol():
    n=normalize_analysis(study()); assert n['study']['simulation_output_semantics']=='modeled-not-observed' and len(n['study']['sensitivity_study_hash'])==64
    s=sobol_report({**study(), 'base_samples':32}); assert len(s['indices'])==2 and s['automatic_parameter_ranking'] is False and s['output_variance']>=0


def test_morris_and_screening():
    m=morris_report({**study(), 'trajectories':8}); assert len(m['effects'])==2 and all(x['elementary_effect_count']==8 for x in m['effects'])
    c=correlation_screening_report({**study(), 'samples':64}); assert len(c['variables'])==2 and c['automatic_significance_inference'] is False


def test_variance_interactions_and_response_surface():
    v=variance_decomposition_report({**study(), 'base_samples':32}); assert len(v['indices'])==2 and v['automatic_interaction_proof'] is False
    i=interaction_screening_report({**study(), 'samples':96}); assert len(i['pairs'])==1 and i['formal_second_order_sobol'] is False
    p={'model':model(),'values':{'x':3},'axes':[{'symbol':'a','values':[1,2,3]},{'symbol':'b','values':[.1,.5,1.0]}]}
    plan=response_surface_plan(p); assert plan['sweep_plan']['evaluation_count']==9
    r=response_surface_run(p); assert r['diagnostics']['record_count']==9 and r['automatic_optimum_selection'] is False


def test_convergence_replication_visual_snapshot_core():
    c=sensitivity_convergence_report({**study(), 'checkpoints':[16,32]}); assert len(c['checkpoints'])==2 and c['convergence_certified'] is False
    r=sensitivity_replication_report({**study(32), 'seeds':[1,2]}); assert len(r['runs'])==2 and r['stability_certified'] is False
    v=build_visualization_plan({}); assert len(v['figures'])>=8 and v['automatic_render'] is False
    studio=build_studio({**study(), 'base_samples':32}); assert studio['automatic_parameter_ranking'] is False
    snap=build_snapshot({'studio':studio}); assert len(snap['snapshot_hash'])==64 and snap['automatic_persistence'] is False
    assert build_reproduction_plan(study())['automatic_execution'] is False
    assert build_export_plan({'formats':['json','pdf']})['automatic_file_write'] is False
    core=build_core_object_plan({'session_id':'s1','analysis_id':'sa1'}); assert core['automatic_core_submission'] is False
    lin=build_execution_lineage_plan({'session_id':'s1','analysis_id':'sa1','seed':42}); assert lin['automatic_execution'] is False
    b=interpretation_boundaries_report(); assert b['scientific_validity_certified'] is False and len(b['boundaries'])>=5
