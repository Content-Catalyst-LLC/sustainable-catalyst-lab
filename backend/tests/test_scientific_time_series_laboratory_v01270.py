import math
import numpy as np
import pytest
from app.scientific_time_series_laboratory_v01270 import *


def series(n=96, period=12):
    t=list(range(n)); y=[10+0.05*i+2*math.sin(2*math.pi*i/period)+0.2*math.sin(2*math.pi*i/5) for i in t]
    return {"times":t,"values":y,"units":"index"}


def test_health_catalog_schema():
    h=health(); c=catalog(); s=schema_info()
    assert h['version']=='0.127.0' and h['method_family_count']==15 and h['figure_family_count']==18
    assert c['automatic_model_selection'] is False and s['limits']['rows']==100000


def test_normalize_and_frequency_audit():
    n=normalize_series(series())['series']; assert n['row_count']==96 and len(n['series_hash'])==64
    a=frequency_audit(series()); assert a['regular'] is True and a['frequency_certified'] is False
    with pytest.raises(TimeSeriesLaboratoryError): normalize_series({'times':[0,2,1],'values':[1,2,3]})


def test_decomposition_acf_pacf():
    d=decompose_series({**series(),'period':12}); assert len(d['seasonal_pattern'])==12 and d['automatic_period_selection'] is False
    a=autocorrelation({**series(),'max_lag':12}); p=partial_autocorrelation({**series(),'max_lag':8})
    assert len(a['acf'])==13 and len(p['pacf'])==9 and p['significance_labels_assigned'] is False


def test_stationarity_and_differencing_are_diagnostic():
    s=stationarity_diagnostics(series()); assert s['automatic_stationarity_decision'] is False and 't_statistic' in s['adf_regression']
    d=difference_series({**series(),'order':1}); assert d['result_length']==95 and d['automatic_order_selection'] is False


def test_ar_arima_ets_state_space():
    ar=fit_autoregression({**series(),'order':3}); assert ar['model']=='AR' and len(ar['coefficients'])==4
    ai=fit_arima({**series(),'p':2,'d':1,'q':1}); assert ai['order']=={'p':2,'d':1,'q':1} and ai['model_selected'] is False
    ets=exponential_smoothing({**series(),'period':12,'alpha':.3,'beta':.1,'gamma':.2}); assert ets['period']==12 and ets['automatic_parameter_optimization'] is False
    ss=state_space_local_linear_trend({**series(),'level_variance':.01,'trend_variance':.001,'observation_variance':.2}); assert len(ss['level'])==96 and ss['automatic_variance_estimation'] is False


def test_forecasts_and_rolling_evaluation():
    for model,spec in [('ar',{'order':3}),('arima',{'p':2,'d':1,'q':1}),('ets',{'period':12}),('state-space',{'observation_variance':.5})]:
        f=forecast({**series(),'model':model,'model_spec':spec,'horizon':6}); assert len(f['point_forecast'])==6 and f['forecast_is_observed_evidence'] is False
    r=rolling_origin_evaluation({**series(60),'model':'ar','model_spec':{'order':2},'min_train':40,'step':4}); assert r['metrics']['rmse']>=0 and r['automatic_model_selection'] is False


def test_residual_diagnostics():
    ar=fit_autoregression({**series(),'order':3}); r=residual_diagnostics({'residuals':ar['residuals'],'max_lag':8})
    assert r['ljung_box']['df']==8 and r['model_validity_certified'] is False


def test_change_points_regimes_anomalies():
    y=[0.0]*30+[5.0]*30+[2.0]*30
    cp=change_point_analysis({'values':y,'max_breaks':4,'min_size':10,'penalty':1}); assert len(cp['changepoints'])>=2 and cp['structural_break_certified'] is False
    rg=regime_analysis({'values':y,'max_breaks':4,'min_size':10,'penalty':1}); assert len(rg['regimes'])>=3 and rg['causal_regime_interpretation'] is False
    aa=y.copy(); aa[10]=20; an=anomaly_screen({'values':aa,'threshold':3}); assert any(x['index']==10 for x in an['flags']) and an['automatic_exclusion'] is False


def test_cross_correlation_and_spectral():
    x=[math.sin(i/4) for i in range(80)]; y=[0,0]+x[:-2]
    c=cross_correlation({'x_values':x,'y_values':y,'max_lag':5}); assert len(c['cross_correlation'])==11 and c['automatic_lead_lag_causality'] is False
    s=spectral_analysis(series(120,12)); assert len(s['spectrum'])>10 and s['automatic_cycle_certification'] is False


def test_irregular_spectral_requires_declared_interval():
    p={'times':[0,1,2,4,5,6],'values':[1,2,1,2,1,2]}
    with pytest.raises(TimeSeriesLaboratoryError): spectral_analysis(p)
    assert spectral_analysis({**p,'sampling_interval':1.0})['sampling_interval']==1.0


def test_visual_studio_snapshot_core_boundaries():
    v=build_visualization_plan({}); assert v['figure_count']==18 and v['automatic_claim_generation'] is False
    st=build_studio({'series_ref':'series:1','methods':['acf-pacf']})['studio']; assert len(st['studio_hash'])==64
    snap=build_snapshot({'studio':st,'series_ref':'series:1'}); assert len(snap['snapshot_hash'])==64 and snap['automatic_persistence'] is False
    assert build_reproduction_plan({'snapshot_ref':'snap:1'})['automatic_execution'] is False
    assert build_export_plan({})['automatic_publication'] is False
    assert build_core_object_plan({'session_id':'sess','analysis_id':'ts1'})['automatic_core_submission'] is False
    assert build_execution_lineage_plan({'session_id':'sess'})['automatic_execution'] is False
    b=interpretation_boundaries_report(); assert b['causal_validity_certified'] is False and len(b['boundaries'])>=10
