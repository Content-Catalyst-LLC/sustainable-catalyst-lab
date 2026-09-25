from app import graph_studio_incremental_interaction_v0135852 as m

def test_health():
    h=m.health(); assert h['ok']; assert h['version']=='0.135.8.5.2'; assert h['api_route_count']==7
    assert h['incremental_rendering'] is True
    assert h['full_redraw_for_ordinary_interaction'] is False

def test_relationship_filter_contract():
    r=m.relationship_filter_contract(); assert r['selector_replaced_during_filter'] is False
    assert r['filter_uses_edge_relation_metadata'] is True
    assert set(r['event_sources'])=={'input','change'}

def test_persistence_contract():
    p=m.persistence_contract(); assert p['local_cache_immediate'] is True
    assert p['project_store_debounced'] is True and p['project_store_debounce_ms']==220

def test_acceptance():
    a=m.acceptance_report(); assert a['incremental_interaction'] is True
    assert a['relationship_filter_works'] is True
    assert a['ordinary_interaction_full_redraw'] is False
