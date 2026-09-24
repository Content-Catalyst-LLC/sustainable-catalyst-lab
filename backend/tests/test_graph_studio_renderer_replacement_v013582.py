import pytest
from app import graph_studio_renderer_replacement_v013582 as m

def test_health_and_catalogs():
    h=m.health(); assert h['version']=='0.135.8.2'; assert h['api_route_count']==24; assert h['primary_renderer_owner']=='graph-studio-renderer-v013582'; assert h['legacy_graph_studio_execution_allowed'] is False
    assert len(m.view_catalog()['views'])==8; assert len(m.view_catalog()['figure_modes'])==6
    assert len(m.renderer_registry()['renderers'])==5

def test_workspace_and_renderer_selection():
    assert m.normalize_workspace({'view':'analysis','mode':'distribution'})['mutates_science'] is False
    assert m.renderer_select({'requested':'auto','dimensionality':2,'point_count':20})['selected']=='svg2d'
    assert m.renderer_select({'requested':'auto','dimensionality':3,'point_count':20})['selected']=='scene3d'
    with pytest.raises(m.GraphStudioRendererReplacementError): m.normalize_workspace({'view':'bogus'})

def test_legacy_and_dom_audits():
    assert m.asset_audit({'active_graph_studio_modules':['graph-studio-renderer-replacement-v013582']})['ok'] is True
    assert m.asset_audit({'active_graph_studio_modules':['graph-studio-v0880']})['ok'] is False
    assert m.dom_audit({'primary_viewports':1,'legacy_primary_canvases_visible':0,'stacked_research_surfaces_visible':0})['ok'] is True

def test_scientific_boundaries():
    b=m.boundaries_report(); assert all(v is False for v in b.values())
    assert m.provenance_plan({'nodes':[{}],'edges':[{}]})['structural_path_is_causal_path'] is False
    assert m.review_plan({})['review_decision_certifies_validity'] is False
    assert m.handoff_plan({})['automatic_submission'] is False

def test_render_plan_preserves_values():
    r=m.render_plan({'rows':[{'x':1,'y':2},{'x':2,'y':3}]}); assert r['row_count']==2; assert r['fabricates_values'] is False
