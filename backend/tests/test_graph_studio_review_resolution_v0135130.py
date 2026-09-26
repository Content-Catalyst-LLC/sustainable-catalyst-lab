from app import graph_studio_review_resolution_v0135130 as m


def payload():
    return {
      "thread":{"annotations":[{"id":"a1"},{"id":"a2"},{"id":"a3"}]},
      "resolutionRecord":{"id":"r1","threadId":"t1","resolutions":[
        {"id":"r-a1","annotationId":"a1","disposition":"addressed","action":"revise-method","revisionRef":"method-v2","response":"Method was revised.","createdAt":"2026-09-26T01:00:00Z"},
        {"id":"r-a2","annotationId":"a2","disposition":"deferred","action":"follow-up","response":"Requires another dataset.","createdAt":"2026-09-26T01:05:00Z"},
      ]}
    }


def test_normalize_and_summary():
    p=payload(); n=m.normalize_record(p); assert n["ok"] and n["record"]["thread_id"]=="t1" and len(n["record"]["resolutions"])==2
    s=m.summarize(p); assert s["latest_disposition_count"]==2 and s["pending_count"]==1 and s["by_disposition"]["addressed"]==1


def test_revision_ref_required():
    p=payload(); p["resolutionRecord"]["resolutions"][0].pop("revisionRef")
    n=m.normalize_record(p); assert not n["ok"] and "revisionRef" in n["error"]


def test_pending_actions_lineage_packet():
    p=payload(); assert m.pending(p)["pending_annotation_ids"]==["a3"]
    assert len(m.revision_actions(p)["actions"])==2
    line=m.decision_lineage(p); assert line["append_only"] and set(line["by_annotation"])=={"a1","a2"}
    packet=m.resolution_packet(p); assert packet["ok"] and packet["target"]=="project-workspace" and packet["summary"]["pending_count"]==1


def test_contracts():
    h=m.health(); assert h["api_route_count"]==11 and h["append_only_decision_lineage"]
    a=m.acceptance_report(); assert not a["annotation_mutation"] and not a["full_graph_redraw_for_resolution"] and not a["truth_ranking"]
