from app import graph_studio_review_closure_v0135200 as m


def synthesis(open_state=False, dissent=True, failed_ver=False):
    thread_state="open" if open_state else "resolved"
    return {
      "projectId":"p1",
      "reviewThreads":[{"id":"t1","title":"Method review","status":thread_state,"subjectRefs":["claim:1"]}],
      "resolutionRecords":[{"id":"r1","threadId":"t1","resolutions":[{"id":"a1","status":thread_state}]}],
      "reviewerPanels":[{"id":"panel1","threadId":"t1","reviewers":[{"id":"u1"},{"id":"u2"}],"assessments":[{"reviewerId":"u1"},{"reviewerId":"u2"}],"signoffs":[{"reviewerId":"u1"},{"reviewerId":"u2"}],"dissents":[{"id":"d1","reviewerId":"u2","statement":"Alternative interpretation"}] if dissent else []}],
      "verificationBundles":[{"id":"v1","threadId":"t1","status":"failed" if failed_ver else "verified"}],
      "reproductionBridges":[{"id":"rep1","threadId":"t1","status":"completed"}],
      "impactAnalyses":[{"id":"i1","threadId":"t1"}],
      "auditRecords":[{"id":"audit1","threadId":"t1"}],
    }


def test_health_and_acceptance_boundaries():
    h=m.health(); assert h["ok"] and h["version"]=="0.135.20.0" and h["api_route_count"]==21
    a=m.acceptance_report(); assert a["review_closure_packages"] and a["publication_readiness"] and a["fingerprinted_freeze"]
    assert a["automatic_scientific_validity"] is False and a["automatic_publication_acceptance"] is False and a["majority_voting"] is False


def test_ready_with_dissent_is_disclosure_not_consensus():
    r=m.readiness_report({"projectId":"p1", **synthesis()})
    assert r["ok"] and r["administratively_ready"] is True and r["state"]=="ready-with-disclosures"
    assert not r["blockers"] and any(x["code"]=="reviewer-dissent" for x in r["disclosures"])
    assert r["scientific_validity"] is None and r["consensus_required"] is False


def test_open_review_blocks_readiness():
    r=m.readiness_report({"projectId":"p1", **synthesis(open_state=True)})
    assert r["state"]=="not-ready" and any(x["code"]=="administrative-closure" for x in r["blockers"])


def test_failed_verification_blocks_readiness():
    r=m.readiness_report({"projectId":"p1", **synthesis(failed_ver=True)})
    assert r["state"]=="not-ready" and any(x["code"]=="verification-integrity" for x in r["blockers"])


def test_build_manifest_and_freeze_roundtrip():
    p={"projectId":"p1", **synthesis(), "closureNotes":"ready for handoff"}
    b=m.build_closure(p); assert b["ok"] and b["package"]["manifest"]["components"]["reviewThreads"]==1
    f=m.freeze_package(p); assert f["ok"] and f["package"]["frozen"] is True
    v=m.verify_freeze({"package":f["package"]}); assert v["verified"] is True


def test_not_ready_requires_explicit_archival_freeze():
    p={"projectId":"p1", **synthesis(open_state=True)}
    f=m.freeze_package(p); assert f["ok"] is False
    f=m.freeze_package({**p,"allowNotReadyFreeze":True}); assert f["ok"] and f["freeze"]["archivalOnly"] is True


def test_handoffs_and_reopen_are_human_governed():
    p={"projectId":"p1", **synthesis()}
    h=m.publication_handoff(p); assert h["ok"] and h["packet"]["target"]=="publication-studio" and h["packet"]["publicationAcceptance"] is None
    a=m.audit_event_draft(p); assert a["event"]["appendOnly"] is True
    rp=m.reopen_plan({"package":m.build_closure(p)["package"],"reason":"new evidence"}); assert rp["plan"]["requiresHumanConfirmation"] is True and rp["plan"]["automaticReopen"] is False


def test_compare_detects_package_change():
    a=m.build_closure({"projectId":"p1", **synthesis(dissent=False)})["package"]
    b=m.build_closure({"projectId":"p1", **synthesis(dissent=True)})["package"]
    c=m.compare_packages({"before":a,"after":b}); assert c["changed"] and c["fingerprintChanged"]
