from backend.app import graph_studio_provenance_path_analysis_v0135100 as m
G={"nodes":[{"id":"source"},{"id":"dataset"},{"id":"transform"},{"id":"method"}],"edges":[{"id":"e1","from":"source","to":"dataset","relation":"sourced-from"},{"id":"e2","from":"dataset","to":"transform","relation":"transformed-by"},{"id":"e3","from":"transform","to":"method","relation":"conditions"}]}
def test_directed_path():
    r=m.shortest_path({**G,"object_a":"source","object_b":"method","mode":"directed","max_hops":6}); assert r["found"] and r["hop_count"]==3 and r["edges"]==["e1","e2","e3"]
def test_direction_boundary():
    r=m.shortest_path({**G,"object_a":"method","object_b":"source","mode":"directed","max_hops":6}); assert r["ok"] and not r["found"]
def test_structural_reverse():
    r=m.shortest_path({**G,"object_a":"method","object_b":"source","mode":"structural","max_hops":6}); assert r["found"] and r["hop_count"]==3 and all(s["orientation"]=="reverse" for s in r["steps"])
def test_bound():
    r=m.shortest_path({**G,"object_a":"source","object_b":"method","mode":"directed","max_hops":2}); assert not r["found"]
def test_compare_and_context():
    r=m.compare_objects({**G,"object_a":"source","object_b":"method"}); assert r["ok"] and r["comparison_is_descriptive"] and not r["ranking"]
    c=m.context_packet({**G,"object_a":"source","object_b":"dataset"}); assert c["ok"] and c["target"]=="project-workspace" and not c["scientific_mutation"]
def test_contracts():
    assert m.health()["api_route_count"]==9; assert m.path_contract()["causal_inference"] is False; assert m.acceptance_report()["declared_relationships_only"] is True
