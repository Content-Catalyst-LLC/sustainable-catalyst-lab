from app import graph_studio_review_workspace_consolidation_v0135210 as m


def sample(order=False):
    threads=[{"id":"t2","status":"resolved"},{"id":"t1","status":"resolved"}]
    if order: threads=list(reversed(threads))
    return {
        "projectId":"p1",
        "reviewThreads":threads,
        "resolutionRecords":[{"id":"r1","threadId":"t1"}],
        "auditRecords":[{"id":"a1","threadId":"t1"}],
        "verificationBundles":[{"id":"v1","threadId":"t1"}],
        "impactAnalyses":[{"id":"i1","threadId":"t1"}],
        "reproductionBridges":[{"id":"rep1","threadId":"t1"}],
        "reviewerPanels":[{"id":"panel1","threadId":"t1"}],
        "crossReviewSyntheses":[{"id":"syn1","projectId":"p1"}],
        "reviewClosurePackages":[{"id":"c1","projectId":"p1"}],
    }


def test_health_acceptance_and_contract():
    h=m.health(); assert h["ok"] and h["version"]=="0.135.21.0" and h["api_route_count"]==18
    a=m.acceptance_report(); assert a["single_review_workspace_controller"] and a["deterministic_hydration"] and a["runtime_certification"]
    assert a["automatic_scientific_validity"] is False and a["automatic_publication_acceptance"] is False and a["full_graph_redraw"] is False
    c=m.contract(); assert c["collection"]=="graphStudioReviewWorkspaceCertifications" and len(c["restoreOrder"])==9


def test_deterministic_state_digest_is_order_independent():
    a=m.normalize_workspace(sample(False))["state"]
    b=m.normalize_workspace(sample(True))["state"]
    assert a["stateDigest"]==b["stateDigest"]
    assert a["counts"]["reviewThreads"]==2 and a["rendererMode"]=="incremental"


def test_duplicate_ids_fail_validation_without_deleting_history():
    p=sample(); p["reviewThreads"].append({"id":"t1","status":"open"})
    v=m.validate_workspace(p)
    assert v["ok"] is False and "reviewThreads" in v["state"]["duplicateIds"]
    assert len(v["state"]["collections"]["reviewThreads"])==3


def test_restore_plan_is_ordered_and_no_redraw():
    r=m.restore_plan(sample())
    assert r["ok"] and [x["collection"] for x in r["plan"]["steps"]]==m.RESTORE_ORDER
    assert r["plan"]["fullGraphRedraw"] is False and r["plan"]["rendererAction"]=="preserve-scene-graph"


def test_ownership_audit_rejects_legacy_executor_and_duplicate_owner():
    inv=[
      {"domain":"renderer","module":"graph-studio-renderer-replacement-v013582","version":"0.135.8.2"},
      {"domain":"renderer","module":"other-renderer","version":"0.135.8.2"},
      {"module":"graph-studio-v0840"},
    ]
    a=m.ownership_audit({"runtimeInventory":inv})
    assert a["ok"] is False and "renderer" in a["duplicateOwnerDomains"] and "graph-studio-v0840" in a["disallowedActiveModules"]


def test_listener_audit_rejects_duplicate_consolidation_listener():
    p={"listeners":[
      {"event":"sc-lab:project:changed","owner":"graph-studio-review-workspace-consolidation-v0135210"},
      {"event":"sc-lab:project:changed","owner":"graph-studio-review-workspace-consolidation-v0135210"},
    ]}
    a=m.listener_audit(p); assert a["ok"] is False and "sc-lab:project:changed" in a["duplicateConsolidationListeners"]


def test_certification_and_project_packet_preserve_scientific_boundaries():
    c=m.certify(sample())
    assert c["ok"] and c["certification"]["certified"] is True
    assert c["certification"]["scientificValidity"] is None and c["certification"]["publicationAcceptance"] is None
    assert c["certification"]["fullGraphRedraw"] is False
    p=m.project_workspace_packet(sample()); assert p["ok"] and p["packet"]["target"]=="project-workspace" and p["packet"]["readOnly"] is True


def test_performance_profile_reports_large_collection_without_renderer_work():
    p={"projectId":"large","reviewThreads":[{"id":f"t{i}"} for i in range(2500)],"auditRecords":[{"id":f"a{i}"} for i in range(2500)]}
    r=m.performance_profile(p)
    assert r["ok"] and r["records"]==5000 and r["rendererWork"]=="none" and r["fullGraphRedraw"] is False
