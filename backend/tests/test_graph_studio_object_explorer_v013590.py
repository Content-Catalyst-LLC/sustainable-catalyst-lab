from app import graph_studio_object_explorer_v013590 as m
GRAPH={"nodes":[{"id":"source","label":"Source"},{"id":"dataset","label":"Dataset"},{"id":"transform","label":"Transform"},{"id":"method","label":"Method"},{"id":"figure","label":"Figure"}],"edges":[{"id":"e1","from":"source","to":"dataset","relation":"sourced-from"},{"id":"e2","from":"dataset","to":"transform","relation":"transformed-by"},{"id":"e3","from":"transform","to":"method","relation":"conditions"},{"id":"e4","from":"method","to":"figure","relation":"renders"}]}
def test_health():
    h=m.health(); assert h['ok'] and h['version']=='0.135.9.0' and h['api_route_count']==10
def test_one_hop_neighborhood():
    r=m.neighborhood({**GRAPH,'selected_node':'dataset','depth':1}); assert set(r['nodes'])=={'source','dataset','transform'} and set(r['edges'])=={'e1','e2'}
def test_two_hop_neighborhood():
    r=m.neighborhood({**GRAPH,'selected_node':'dataset','depth':2}); assert set(r['nodes'])=={'source','dataset','transform','method'} and set(r['edges'])=={'e1','e2','e3'}
def test_object_summary():
    r=m.object_summary({**GRAPH,'selected_node':'dataset'}); assert r['ok'] and r['incoming_count']==1 and r['outgoing_count']==1
def test_relation_summary():
    r=m.relation_summary({**GRAPH,'selected_node':'dataset'}); assert {x['relation'] for x in r['relationships']}=={'sourced-from','transformed-by'}
def test_acceptance():
    a=m.acceptance_report(); assert a['declared_relationships_only'] and a['cross_workspace_navigation'] and not a['full_graph_redraw_for_scope']
