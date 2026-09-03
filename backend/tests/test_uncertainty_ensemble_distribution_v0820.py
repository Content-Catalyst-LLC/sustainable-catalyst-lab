import pytest
from app.uncertainty_ensemble_distribution_v0820 import *

def test_health_and_boundaries():
    h=health(); assert h['status']=='uncertainty-ensemble-distribution-ready'; assert h['version']=='0.82.0'; assert h['engineVersion']=='2.9.0'; assert h['automaticUncertaintyInference'] is False; assert h['automaticKDE'] is False

def test_interval_requires_explicit_level_for_named_semantics():
    with pytest.raises(UncertaintyVisualizationError): normalize_uncertainty({'semantics':'confidence','records':[{'x':0,'lower':1,'upper':2}]})

def test_interval_validation():
    u=normalize_uncertainty({'semantics':'credible','level':.95,'records':[{'x':1,'lower':2,'center':3,'upper':4}]}); assert u['records'][0]['center']==3; assert u['isObservation'] is False
    with pytest.raises(UncertaintyVisualizationError): normalize_uncertainty({'records':[{'lower':2,'upper':1}]})

def test_quantile_ribbon_validation():
    u=normalize_uncertainty({'type':'quantile-ribbon','quantileLevels':[.1,.5,.9],'records':[{'x':0,'values':[1,2,3]}]}); assert u['quantileLevels']==[.1,.5,.9]
    with pytest.raises(UncertaintyVisualizationError): normalize_uncertainty({'type':'quantile-ribbon','quantileLevels':[.9,.1],'records':[{'values':[1,2]}]})

def test_empirical_distribution_is_nonparametric():
    d=normalize_distribution({'samples':[1,2,3,4,5],'semantics':'posterior','bins':2,'units':'kg'}); assert d['sampleCount']==5; assert sum(x['count'] for x in d['histogram']['cells'])==5; assert d['boxSummary']['median']==3; assert d['boundaries']['automaticParametricFit'] is False

def test_distribution_rejects_nonfinite():
    with pytest.raises(UncertaintyVisualizationError): normalize_distribution({'samples':[1,float('nan')]})

def test_ensemble_exact_alignment_envelope():
    e=normalize_ensemble({'members':[{'id':'a','states':[{'x':0,'y':1},{'x':1,'y':2}]},{'id':'b','states':[{'x':0,'y':3},{'x':1,'y':4}]}],'deriveEnvelope':True,'quantiles':[.25,.5,.75]}); assert e['envelope']; assert len(e['envelope']['records'])==2

def test_ensemble_refuses_implicit_alignment():
    with pytest.raises(UncertaintyVisualizationError): normalize_ensemble({'members':[{'states':[{'x':0,'y':1}]},{'states':[{'x':1,'y':2}]}],'deriveEnvelope':True,'quantiles':[.25,.75]})

def test_layer_and_figure_preserve_base():
    f=attach_uncertainty({'baseFigure':{'renderer':'svg2d','fingerprint':'base-1','title':'F'},'uncertaintyLayers':[{'uncertaintySeries':[{'records':[{'x':0,'lower':1,'upper':2}]}]}]}); assert f['baseFigureFingerprint']=='base-1'; assert f['boundaries']['baseFigureMutation'] is False

def test_workspace_compatibility():
    w=build_workspace({'figures':[]})['workspace']; assert w['compatibility']['v0810Markup'] is True; assert w['engineVersion']=='2.9.0'
