import math
import pytest
from app.experimental_design_power_analysis_v01280 import *


def test_health_catalog_schema():
    assert health()['version']=='0.128.0'; assert len(METHOD_FAMILIES)==15; assert len(FIGURE_FAMILIES)==16
    assert catalog()['automatic_design_selection'] is False


def test_normalize_and_effect_sizes():
    d=normalize_design({'alpha':.05,'target_power':.8})['design']; assert len(d['design_hash'])==64
    r=standardized_effect_report({'kind':'mean-difference','difference':5,'sd':10}); assert r['effect_size']==.5
    h=standardized_effect_report({'kind':'proportion-difference','p0':.2,'p1':.4}); assert h['metric']=='cohen_h'


def test_mean_power_plans():
    a=one_sample_mean_power({'effect_size':.5,'target_power':.8}); assert a['n']>10 and a['achieved_power']>=.8
    b=two_sample_mean_power({'effect_size':.5,'target_power':.8}); assert b['n_per_group']>20 and b['achieved_power']>=.8
    c=paired_mean_power({'effect_size':.6,'target_power':.8}); assert c['pairs']>5


def test_proportion_power_plans():
    a=one_proportion_power({'p0':.3,'p1':.45}); assert a['total_n']>0
    b=two_proportion_power({'p1':.3,'p2':.45}); assert b['total_n']==2*b['n_per_group']


def test_anova_and_factorial():
    a=one_way_anova_power({'groups':4,'effect_size':.25,'target_power':.8}); assert a['total_n']>=4 and a['achieved_power']>=.79
    f=factorial_design_plan({'factors':[{'name':'A','levels':['a0','a1']},{'name':'B','levels':['b0','b1','b2']}],'replicates_per_cell':5})
    assert f['cell_count']==6 and f['total_n']==30


def test_block_cluster_precision():
    b=blocked_randomization_plan({'groups':['c','t'],'block_size':4,'blocks':5}); assert b['total_n']==20
    c=cluster_design_effect({'mean_cluster_size':20,'icc':.05,'individual_level_n':100}); assert c['design_effect']>1
    p=precision_sample_size({'kind':'mean','sd':10,'half_width':2}); assert p['sample_size']>2


def test_seeded_simulation_power_reproducible():
    p={'simulations':3000,'seed':42,'effect_size':.4,'n':50,'noise_sd':1}
    a=simulation_power(p); b=simulation_power(p); assert a['estimated_power']==b['estimated_power']; assert a['monte_carlo_se']>0


def test_sequential_adaptive_multiplicity():
    s=sequential_design_plan({'looks':4,'alpha':.05}); assert len(s['cumulative_alpha'])==4 and s['automatic_stopping'] is False
    a=adaptive_reestimation_plan({'initial_n':100,'review_n':50,'max_n':180}); assert a['automatic_sample_size_change'] is False
    m=multiple_testing_plan({'hypotheses':['h1','h2','h3'],'method':'bonferroni'}); assert math.isclose(sum(m['nominal_alpha_sequence']),.05)


def test_randomization_schedule_deterministic():
    a=randomization_schedule({'groups':['A','B'],'n':20,'seed':9}); b=randomization_schedule({'groups':['A','B'],'n':20,'seed':9})
    assert a['assignments']==b['assignments']; assert a['schedule_hash']==b['schedule_hash']


def test_design_diagnostics_boundaries():
    d=design_diagnostics({'effect_size_source':'pilot','variance_source':'pilot','target_power':.9}); assert d['ready_for_review'] is True and d['scientific_validity_certified'] is False
    b=interpretation_boundaries_report(); assert b['power_guaranteed'] is False and len(b['boundaries'])>=10


def test_visual_studio_snapshot_core():
    assert build_visualization_plan({})['figure_count']==16
    st=build_studio({'design_ref':'design:1','methods':['two-sample-mean-power']})['studio']; assert len(st['studio_hash'])==64
    snap=build_snapshot({'studio':st,'design_ref':'design:1'}); assert len(snap['snapshot_hash'])==64 and snap['automatic_persistence'] is False
    assert build_reproduction_plan({'snapshot_ref':'snap:1'})['automatic_execution'] is False
    assert build_export_plan({})['automatic_publication'] is False
    assert build_core_object_plan({'session_id':'sess','analysis_id':'exp1'})['automatic_core_submission'] is False
    assert build_execution_lineage_plan({'session_id':'sess'})['automatic_execution'] is False


def test_validation_errors():
    with pytest.raises(ExperimentalDesignError): two_sample_mean_power({'effect_size':0})
    with pytest.raises(ExperimentalDesignError): blocked_randomization_plan({'groups':['a','b','c'],'block_size':4})
    with pytest.raises(ExperimentalDesignError): precision_sample_size({'kind':'mean','sd':0,'half_width':1})
