import pytest
from app.visual_research_narrative_figure_composer_v01180 import *


def figure(ref='lab:figure:f1', kind='statistical-figure'):
    return {'id':'fig1','figure_ref':ref,'figure_kind':kind,'title':'Observed response','caption':'Observed response with declared uncertainty.','alt_text':'A response curve with uncertainty band.','source_refs':['lab:dataset:d1'],'method_refs':['lab:method:m1'],'finding_refs':['lab:finding:f1']}


def narrative():
    return {
        'id':'nar1','title':'Research narrative','format':'research-report','publication_profile':'journal',
        'figures':[figure()],
        'sections':[{'id':'results','type':'results','title':'Results','blocks':[{'type':'paragraph','text':'The declared result is shown in Figure 1.'},{'type':'figure','figure_refs':['lab:figure:f1']}]}],
        'source_refs':['lab:dataset:d1'],'method_refs':['lab:method:m1'],'finding_refs':['lab:finding:f1']
    }


def test_catalog_manifest_health():
    assert schema_info()['api_route_count']==19
    assert len(catalog()['figure_kinds'])==12
    assert manifest()['features']['reference_first_figure_registry'] is True
    assert manifest()['boundaries']['automatic_caption_inference'] is False
    assert health()['version']=='0.118.0'


def test_normalize_narrative_reference_first():
    n=normalize_narrative(narrative())
    assert n['narrative']['figures'][0]['immutable_underlying_figure'] is True
    assert n['automatic_figure_mutation'] is False
    assert len(n['narrative']['narrative_hash'])==64


def test_unknown_figure_reference_rejected():
    p=narrative(); p['sections'][0]['blocks'][1]['figure_refs']=['lab:figure:missing']
    with pytest.raises(VisualResearchNarrativeError): normalize_narrative(p)


def test_figure_plate_preserves_order():
    f2=figure('lab:scene:s1','scientific-3d-4d-scene'); f2['id']='fig2'; f2['title']='Scene'
    x=build_figure_plate({'figures':[figure(),f2],'columns':2,'caption':'Two declared views.'})
    assert [p['panel_label'] for p in x['plate']['panel_labels']]==['A','B']
    assert x['automatic_figure_reordering'] is False


def test_caption_is_declared_not_inferred():
    with pytest.raises(VisualResearchNarrativeError): build_caption_package({'figure':{**figure(),'caption':None}})
    x=build_caption_package({'figure':figure()})
    assert x['automatic_caption_inference'] is False and x['automatic_result_interpretation'] is False


def test_annotation_and_links_no_weighting():
    a=build_annotation_layer({'figure_ref':'lab:figure:f1','annotations':[{'text':'Threshold declared by analyst.','type':'threshold','evidence_refs':['lab:evidence:e1']}]})
    assert a['automatic_annotation_generation'] is False and a['automatic_evidence_weighting'] is False
    l=build_research_links({'target_ref':'lab:figure:f1','method_refs':['lab:method:m1'],'finding_refs':['lab:finding:f1']})
    assert l['automatic_relationship_inference'] is False


def test_provenance_trace():
    t=trace_provenance({'narrative':narrative()})['provenance_trace']
    assert t['source_refs']==['lab:dataset:d1'] and t['method_refs']==['lab:method:m1']
    assert len(t['trace_hash'])==64


def test_layout_export_publication_package():
    l=build_layout_plan({'narrative':narrative(),'layout_mode':'journal'})
    assert l['automatic_scientific_reordering'] is False
    e=build_export_plan({'narrative':narrative(),'formats':['pdf','html','json']})
    assert e['automatic_file_write'] is False and e['export_plan']['vector_first'] is True
    p=build_publication_package({'narrative':narrative()})
    assert p['automatic_publication'] is False and p['publication_package']['scientific_validity_certified'] is False


def test_revision_snapshot_deterministic():
    a=build_revision_snapshot({'narrative':narrative()})['snapshot']
    b=build_revision_snapshot({'narrative':narrative()})['snapshot']
    assert a['snapshot_hash']==b['snapshot_hash'] and a['snapshot_ref']==b['snapshot_ref']


def test_core_visual_plan_and_accessibility():
    c=build_core_visual_plan({'narrative':narrative(),'session_id':'s1'})
    assert c['automatic_core_submission'] is False and c['core_renders_narrative'] is False
    good=accessibility_audit({'narrative':narrative()}); assert good['accessible'] is True
    p=narrative(); p['figures'][0]['alt_text']=''; bad=accessibility_audit({'narrative':p}); assert bad['accessible'] is False
