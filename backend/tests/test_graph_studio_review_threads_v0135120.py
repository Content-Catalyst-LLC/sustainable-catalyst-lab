from app import graph_studio_review_threads_v0135120 as m


def thread():
    return {
        "id":"review-1","title":"Dataset to figure review","status":"in-review",
        "objectA":{"id":"A","label":"Dataset A"},"objectB":{"id":"B","label":"Figure B"},
        "selectedPathIndex":1,"candidatePathCount":2,
        "selectedPath":{"nodes":["A","X","B"],"edges":["e1","e2"]},
        "annotations":[
            {"id":"a1","kind":"observation","scope":"path","targetId":"path:1","note":"This path uses the transform branch.","pathIndex":1},
            {"id":"a2","kind":"limitation","scope":"edge","targetId":"e2","note":"Renderer parameters are not represented here.","pathIndex":1},
            {"id":"a3","kind":"claim-link","scope":"object-b","targetId":"B","claimRef":"claim-17","note":"Explicitly link this figure to claim-17.","pathIndex":1},
        ]
    }


def test_normalizes_thread_and_annotations():
    r=m.normalize_thread(thread())
    assert r["ok"] and r["annotation_count"]==3
    assert r["thread"]["status"]=="in-review"
    assert r["thread"]["annotations"][2]["claim_ref"]=="claim-17"


def test_summary_and_claim_links_are_explicit():
    s=m.summarize_thread(thread()); c=m.claim_links(thread())
    assert s["by_kind"]["observation"]==1 and s["by_kind"]["limitation"]==1 and s["by_kind"]["claim-link"]==1
    assert c["explicit_only"] is True and c["inferred_claim_links"] is False
    assert c["links"]==[{"annotation_id":"a3","claim_ref":"claim-17","scope":"object-b","target_id":"B","note":"Explicitly link this figure to claim-17."}]


def test_claim_link_requires_reference():
    p=thread(); p["annotations"][2].pop("claimRef")
    r=m.normalize_thread(p)
    assert r["ok"] is False and "claimRef" in r["error"]


def test_review_packet_and_fingerprint_are_deterministic():
    p=m.review_packet(thread()); f1=m.fingerprint(thread()); f2=m.fingerprint(thread())
    assert p["ok"] and p["target"]=="project-workspace" and len(p["claim_links"])==1
    assert f1["fingerprint"]==f2["fingerprint"] and len(f1["fingerprint"])==64


def test_contracts_are_non_adjudicative():
    a=m.acceptance_report(); c=m.annotation_contract()
    assert a["full_graph_redraw_for_annotation"] is False
    assert a["truth_ranking"] is False and a["causal_inference"] is False and a["evidence_weight_inference"] is False
    assert c["inferred_claim_links"] is False
