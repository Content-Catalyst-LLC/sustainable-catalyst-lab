from app import graph_studio_revision_impact_v0135160 as m

GRAPH={
 "nodes":[
  {"id":"data","label":"Dataset","type":"dataset"},
  {"id":"method","label":"Method","type":"method"},
  {"id":"run","label":"Execution","type":"execution"},
  {"id":"fig","label":"Figure","type":"figure"},
  {"id":"finding","label":"Finding","type":"finding"},
  {"id":"claim","label":"Claim","type":"claim"},
 ],
 "edges":[
  {"id":"e1","from":"data","to":"method","relation":"input-to"},
  {"id":"e2","from":"method","to":"run","relation":"executed-by"},
  {"id":"e3","from":"run","to":"fig","relation":"generated"},
  {"id":"e4","from":"fig","to":"finding","relation":"supports-review-of"},
  {"id":"e5","from":"finding","to":"claim","relation":"declared-in"},
 ]
}

def p(seed="method", **kw):
 x={"graph":GRAPH,"seedId":seed,"direction":"both","maxDepth":6,"revisionAction":"revise-method","revisionRef":"method-rev-2","id":"impact-1"};x.update(kw);return x

def test_normalize_and_validate():
 n=m.normalize_graph(p()); assert n["ok"] and n["node_count"]==6 and n["edge_count"]==5 and len(n["record"]["graph_fingerprint"])==64
 v=m.validate_graph(p()); assert v["ok"] and v["cycle_count"]==0 and not v["dangling_edges"]

def test_downstream_direct_transitive():
 d=m.downstream(p()); assert d["ok"] and d["affected_node_ids"]==["run","fig","finding","claim"]
 assert d["direct_count"]==1 and d["transitive_count"]==3
 assert d["affected"][0]["impact_class"]=="direct" and d["affected"][-1]["hop_count"]==4

def test_upstream_dependencies():
 u=m.upstream(p()); assert u["ok"] and u["affected_node_ids"]==["data"] and u["direct_count"]==1

def test_both_uses_downstream_for_potential_impact():
 x=m.impact(p()); assert x["ok"] and x["direction"]=="both"
 assert x["potentially_affected_node_ids"]==["run","fig","finding","claim"]
 assert x["dependency_node_ids"]==["data"] and x["potential_impact_only"] is True

def test_depth_bound():
 d=m.downstream(p(maxDepth=2)); assert d["affected_node_ids"]==["run","fig"] and d["transitive_count"]==1

def test_cycles_are_reported_but_bounded():
 g={"nodes":[{"id":"a"},{"id":"b"},{"id":"c"}],"edges":[{"id":"1","from":"a","to":"b"},{"id":"2","from":"b","to":"c"},{"id":"3","from":"c","to":"a"}]}
 v=m.validate_graph({"graph":g}); assert v["ok"] and v["cycle_count"]==3
 d=m.downstream({"graph":g,"seedId":"a","maxDepth":12}); assert d["ok"] and set(d["affected_node_ids"])=={"b","c"}

def test_dangling_edge_detection():
 g={"nodes":[{"id":"a"}],"edges":[{"id":"e","from":"a","to":"missing"}]}
 v=m.validate_graph({"graph":g}); assert v["ok"] is False and len(v["dangling_edges"])==1

def test_snapshot_compare():
 left=m.snapshot(p(snapshotId="s1"))["snapshot"]
 g={**GRAPH,"nodes":GRAPH["nodes"]+[{"id":"ms","label":"Manuscript","type":"manuscript-section"}],"edges":GRAPH["edges"]+[{"id":"e6","from":"claim","to":"ms","relation":"reported-in"}]}
 right=m.snapshot({**p(snapshotId="s2"),"graph":g})["snapshot"]
 c=m.compare_snapshots({"left":left,"right":right}); assert c["ok"] and c["graph_changed"] and c["added_potentially_affected_node_ids"]==["ms"]

def test_revision_analysis_packet_and_contract():
 a=m.revision_analysis(p()); assert a["ok"] and a["record"]["collection"]=="graphStudioRevisionImpactAnalyses" and len(a["record"]["fingerprint"])==64
 packet=m.impact_packet(p()); assert packet["ok"] and packet["target"]=="project-workspace"
 h=m.health(); assert h["api_route_count"]==16 and h["backward_compatible_v0135150"]
 ac=m.acceptance_report(); assert ac["direct_and_transitive_impact"] and not ac["automatic_scientific_invalidation"] and not ac["truth_ranking"]
