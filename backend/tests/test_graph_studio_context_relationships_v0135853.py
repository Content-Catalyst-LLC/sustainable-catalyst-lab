from app import graph_studio_context_relationships_v0135853 as m

GRAPH={
 "nodes":[{"id":"source"},{"id":"dataset"},{"id":"transform"},{"id":"binding"}],
 "edges":[
   {"id":"e1","from":"source","to":"dataset","relation":"sourced-from"},
   {"id":"e2","from":"dataset","to":"transform","relation":"transformed-by"},
   {"id":"e3","from":"dataset","to":"binding","relation":"binds"},
 ]
}
def test_health():
    h=m.health(); assert h["ok"] and h["version"]=="0.135.8.5.3" and h["api_route_count"]==8
def test_upstream_sourced_from_is_compatible():
    r=m.relationship_options({**GRAPH,"selected_node":"dataset","traversal":"upstream","relation":"sourced-from"}); assert r["current_match_count"]==1 and r["current_compatible"] and not r["zero_match"]
def test_downstream_sourced_from_sticks_as_zero_match():
    r=m.relationship_options({**GRAPH,"selected_node":"dataset","traversal":"downstream","relation":"sourced-from"}); assert r["relation"]=="sourced-from" and r["current_match_count"]==0 and r["zero_match"]
    opt=next(x for x in r["options"] if x["relation"]=="sourced-from"); assert opt["disabled"] is False
def test_downstream_transformed_by_is_available_and_other_impossible_relation_disabled():
    r=m.relationship_options({**GRAPH,"selected_node":"dataset","traversal":"downstream","relation":"all"});
    by={x["relation"]:x for x in r["options"]}; assert by["transformed-by"]["count"]==1 and not by["transformed-by"]["disabled"]; assert by["sourced-from"]["count"]==0 and by["sourced-from"]["disabled"]
def test_all_mode_relation_counts_global_edges():
    r=m.relationship_options({**GRAPH,"selected_node":"dataset","traversal":"all","relation":"sourced-from"}); assert r["current_match_count"]==1
