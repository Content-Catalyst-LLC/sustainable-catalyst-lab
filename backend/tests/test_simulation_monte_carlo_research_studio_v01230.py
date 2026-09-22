import copy

from app.simulation_monte_carlo_research_studio_v01230 import *


def model():
    return {
        'id':'decay-model','family':'declarative-expression','title':'Exponential decay',
        'definition':{'equation':'y = a * exp(-k*x)'},
        'variables':[{'symbol':'x','label':'Time','unit':'s','role':'input'},{'symbol':'y','label':'Concentration','unit':'mg/L','role':'response'}],
        'parameters':[{'symbol':'a','role':'estimated','value':10},{'symbol':'k','role':'estimated','value':0.3}],
        'constants':[],'datasetBindings':[]
    }


def study(samples=64, seed=42, method='latin-hypercube'):
    return {
        'id':'mc-study','title':'Decay Monte Carlo','model':model(),'values':{'x':5},
        'uncertainInputs':[{'symbol':'a','distribution':'normal','mean':10,'stdDev':0.5},{'symbol':'k','distribution':'normal','mean':0.3,'stdDev':0.02}],
        'design':{'method':method,'samples':samples,'seed':seed},
        'analysis':{'confidence':0.95,'thresholds':[2.0]}
    }


def test_health_catalog_boundaries():
    h=health(); c=catalog(); assert h['ok'] and h['version']=='0.123.0'; assert h['sampling_design_count']==4; assert len(c['figure_families'])==12
    assert h['automatic_evidence_promotion'] is False and h['automatic_convergence_certification'] is False


def test_normalize_sampling_budget_and_run_reproducible():
    n=normalize_study(study()); assert n['study']['simulation_output_semantics']=='modeled-not-observed' and len(n['study']['studio_study_hash'])==64
    sp=build_sampling_plan(study()); assert sp['base_samples']==64 and sp['automatic_execution'] is False
    b=build_compute_budget_plan(study()); assert b['execution_mode']=='direct'
    a=run_simulation(study())['result']; b2=run_simulation(study())['result']; assert a['summary']==b2['summary']; assert a['observational_evidence'] is False


def test_convergence_and_replication_are_descriptive_not_certification():
    c=convergence_report({**study(64),'checkpoints':[16,32,64]}); assert len(c['checkpoints'])==3 and c['convergence_certified'] is False
    r=replication_report({**study(32),'seeds':[1,2,3]}); assert len(r['runs'])==3 and r['replication_stability_certified'] is False


def test_parameter_sweep_plan_and_execution():
    p={'model':model(),'values':{'x':5},'axes':[{'symbol':'a','values':[8,10,12]},{'symbol':'k','start':0.2,'stop':0.4,'points':3}]}
    plan=parameter_sweep_plan(p); assert plan['evaluation_count']==9 and plan['automatic_optimum_selection'] is False
    result=run_parameter_sweep(p); assert len(result['records'])==9 and result['automatic_causal_inference'] is False


def test_scenario_ensemble_has_no_winner():
    p={'study':study(32),'scenarios':[{'id':'base','values':{'x':5}},{'id':'late','values':{'x':7}}]}
    r=run_scenario_ensemble(p); assert len(r['scenarios'])==2 and r['selected_scenario_id'] is None and r['automatic_scenario_ranking'] is False


def test_uncertainty_threshold_visual_snapshot_export_reproduction_core():
    u=run_uncertainty_propagation(study(32)); assert u['automatic_evidence_promotion'] is False
    t=threshold_report(study(32)); assert t['automatic_decision'] is False
    v=build_visualization_plan({}); assert v['automatic_render'] is False and len(v['figures'])>=8
    studio=build_studio(study(32)); assert studio['automatic_causal_inference'] is False
    snap=build_snapshot({'studio':studio}); assert snap['automatic_persistence'] is False and len(snap['snapshot_hash'])==64
    rp=build_reproduction_plan(study(32)); assert rp['automatic_execution'] is False
    ex=build_export_plan({'formats':['json','pdf','svg']}); assert ex['automatic_file_write'] is False
    core=build_core_object_plan({'session_id':'s1','simulation_id':'sim-1'}); assert core['automatic_core_submission'] is False and core['core_executes_simulation'] is False
    lin=build_execution_lineage_plan({'session_id':'s1','simulation_id':'sim-1','seed':42}); assert lin['automatic_execution'] is False and lin['execution']['seed_ref']=='seed:42'
