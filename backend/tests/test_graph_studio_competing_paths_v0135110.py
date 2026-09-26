from app import graph_studio_competing_paths_v0135110 as m

def graph():
    return {
        "nodes":[{"id":"A"},{"id":"X"},{"id":"Y"},{"id":"B"}],
        "edges":[
            {"id":"e1","from":"A","to":"X","relation":"transformed-by","metadata":{"evidenceContext":"supporting"}},
            {"id":"e2","from":"X","to":"B","relation":"renders","metadata":{"evidenceContext":"supporting"}},
            {"id":"e3","from":"A","to":"Y","relation":"binds","metadata":{"evidenceContext":"contradicting"}},
            {"id":"e4","from":"Y","to":"B","relation":"renders"},
        ],
        "object_a":"A","object_b":"B","mode":"directed","max_hops":4,"max_paths":5,
    }

def test_enumerates_multiple_paths_deterministically():
    r=m.enumerate_paths(graph())
    assert r["ok"] and r["candidate_path_count"]==2
    assert [p["edges"] for p in r["paths"]]==[["e3","e4"],["e1","e2"]] or [p["edges"] for p in r["paths"]]==[["e1","e2"],["e3","e4"]]
    assert all(p["hop_count"]==2 for p in r["paths"])

def test_declared_evidence_only():
    r=m.evidence_context(graph())
    assert r["declared_context_only"] is True and r["inferred_evidence"] is False
    totals=[x["evidence"] for x in r["paths"]]
    assert any(x["supporting"]==2 for x in totals)
    assert any(x["contradicting"]==1 and x["unclassified"]==1 for x in totals)

def test_hop_bound_and_context_packet():
    p=graph(); p["max_hops"]=1
    assert m.enumerate_paths(p)["candidate_path_count"]==0
    p=graph(); p["selected_path_index"]=1
    c=m.context_packet(p)
    assert c["ok"] and c["target"]=="project-workspace" and len(c["candidate_paths"])==2
    assert c["boundary"].startswith("Alternative declared provenance paths")

def test_contracts_are_non_adjudicative():
    a=m.acceptance_report(); e=m.evidence_contract()
    assert a["truth_ranking"] is False and a["causal_inference"] is False and a["scientific_preference"] is False
    assert e["inferred_evidence"] is False
