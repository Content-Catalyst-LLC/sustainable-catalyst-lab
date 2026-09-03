import hashlib, json, pytest
from app.provenance_aware_figures_v0830 import *

def fp(v): return hashlib.sha256(v.encode()).hexdigest()

def provenance():
    return {'datasets':[{'id':'data','fingerprint':fp('data'),'uri':'dataset://observed'}], 'transformations':[{'id':'log','fingerprint':fp('transform'),'method':'declared-log'}], 'models':[{'id':'m1','fingerprint':fp('model'),'version':'1'}], 'renderer':{'id':'svg2d','version':'2.10.0'}, 'state':{'filter':'all'}, 'uncertainty':[{'id':'u1','fingerprint':fp('uncertainty')}]}

def test_health_and_boundaries():
    h=health(); assert h['status']=='provenance-aware-scientific-figures-ready'; assert h['version']=='0.83.0'; assert h['engineVersion']=='2.10.0'; assert h['automaticProvenanceRepair'] is False

def test_normalize_requires_renderer_and_sha256():
    with pytest.raises(FigureProvenanceError): normalize_provenance({'datasets':[{'id':'x','fingerprint':'bad'}],'renderer':{'id':'svg2d'}})
    with pytest.raises(FigureProvenanceError): normalize_provenance({'datasets':[]})

def test_normalize_fingerprints_state_and_parameters():
    p=provenance(); p['transformations'][0]['parameters']={'base':10}; n=normalize_provenance(p); assert len(n['stateFingerprint'])==64; assert len(n['transformations'][0]['parametersFingerprint'])==64

def test_attach_preserves_base_and_builds_lineage():
    base={'renderer':'svg2d','title':'Observed data','values':[1,2,3]}; f=attach_provenance({'baseFigure':base,'provenance':provenance()}); assert f['baseFigure']==base; assert len(f['baseFigureFingerprint'])==64; assert len(f['lineageFingerprint'])==64; assert f['boundaries']['baseFigureMutation'] is False

def test_declared_base_mismatch_refused():
    with pytest.raises(FigureProvenanceError): attach_provenance({'baseFigure':{'renderer':'svg2d'},'baseFigureFingerprint':fp('wrong'),'provenance':provenance()})

def test_verification_detects_tampering_without_repair():
    f=attach_provenance({'baseFigure':{'renderer':'svg2d','values':[1,2]},'provenance':provenance()}); assert verify_provenance(f)['verified'] is True
    f['baseFigure']['values'][0]=99; v=verify_provenance(f); assert v['verified'] is False; assert v['status']=='lineage-mismatch'; assert v['boundaries']['automaticProvenanceRepair'] is False

def test_export_manifest_carries_verification():
    f=attach_provenance({'baseFigure':{'renderer':'canvas-spatial','fingerprint':fp('base')},'provenance':provenance()}); e=build_export_manifest({'figure':f,'format':'pdf','dimensions':{'width':8,'height':6}})['exportManifest']; assert e['format']=='pdf'; assert e['provenanceVerified'] is True; assert e['lineageFingerprint']==f['lineageFingerprint']

def test_workspace_compatibility():
    w=build_workspace({'figures':[]})['workspace']; assert w['compatibility']['v0820Uncertainty'] is True; assert w['engineVersion']=='2.10.0'
