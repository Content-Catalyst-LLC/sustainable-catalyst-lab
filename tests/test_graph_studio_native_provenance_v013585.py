from backend.app import graph_studio_native_provenance_v013585 as m

def sample():
    return {"nodes":[{"id":"a"},{"id":"b"},{"id":"c"}],"edges":[{"id":"e1","from":"a","to":"b","relation":"binds"},{"id":"e2","from":"b","to":"c","relation":"renders"}]}

def test_health_and_boundaries():
    h=m.health(); assert h["ok"] and h["native_graph_state_engine"] and not h["mutation_observer_owns_interaction"] and not h["presentation_state_mutates_science"]

def test_native_runtime_contract():
    c=m.runtime_contract(); assert c["single_graph_controller"] and c["stable_object_ids"] and c["observer_driven_renders"]==0

def test_graph_normalization_drops_unknown_endpoints():
    p=sample(); p["edges"].append({"from":"c","to":"missing","relation":"bad"}); g=m.normalize_graph(p); assert g["node_count"]==3 and g["edge_count"]==2 and not g["missing_edges_inferred"]

def test_downstream_subgraph():
    p=sample()|{"mode":"downstream","selected_node":"a"}; r=m.traverse(p); assert set(r["visible_nodes"])=={"a","b","c"} and set(r["visible_edges"])=={"e1","e2"}

def test_upstream_subgraph():
    p=sample()|{"mode":"upstream","selected_node":"c"}; r=m.traverse(p); assert set(r["visible_nodes"])=={"a","b","c"}

def test_focus_subgraph():
    p=sample()|{"mode":"focus","selected_node":"b"}; r=m.traverse(p); assert r["visible_nodes"]==["b"] and r["visible_edges"]==[]

def test_relation_filter():
    p=sample()|{"mode":"downstream","selected_node":"a","relation":"binds"}; r=m.traverse(p); assert set(r["visible_nodes"])=={"a","b"} and set(r["visible_edges"])=={"e1"}

def test_browser_hardening():
    b=m.browser_hardening_contract(); assert not b["mutation_observer_interaction_owner"] and b["interaction_loop_count_expected"]==0 and b["observer_driven_renders_expected"]==0

def test_acceptance():
    a=m.acceptance_report(); assert a["graph_controller_count"]==1 and a["observer_driven_renders"]==0 and not a["hard_coded_dom_edge_order_semantics"]
