from __future__ import annotations
import copy, hashlib, json, re
from datetime import datetime, timezone

VERSION = "0.135.18.0"
ROUTE_COUNT = 18
MAX_REVIEWERS = 64
MAX_ASSESSMENTS = 500
MAX_DISSENTS = 250
ROLES = ("primary-reviewer", "independent-reviewer", "method-reviewer", "data-reviewer", "reproduction-reviewer", "editor", "observer")
ASSESSMENT_STATES = ("addressed", "further-revision", "accept-with-reservation", "unable-to-assess", "abstain")
SIGNOFF_STATES = ("signed", "withheld", "abstained")
DISSENT_KINDS = ("methodological", "evidentiary", "interpretive", "reproducibility", "scope", "other")
BOUNDARY = (
    "Multi-reviewer panel records preserve independent review judgments and disagreement. "
    "Counts, sign-offs, or repeated assessments do not establish scientific truth, evidentiary weight, "
    "causal validity, consensus, or an automatic review resolution."
)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _text(value, limit=4096):
    if value is None:
        return ""
    return str(value).strip()[:limit]


def _slug(value, fallback="record"):
    s = re.sub(r"[^a-zA-Z0-9._:-]+", "-", _text(value, 256)).strip("-")
    return s or fallback


def _fp(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def normalize_reviewer(payload):
    if not isinstance(payload, dict):
        return {"ok": False, "version": VERSION, "error": "reviewer must be an object"}
    raw = payload.get("reviewer") if isinstance(payload.get("reviewer"), dict) else payload
    rid = _text(raw.get("reviewerId", raw.get("reviewer_id", raw.get("id"))), 256)
    if not rid:
        return {"ok": False, "version": VERSION, "error": "reviewerId is required"}
    role = _text(raw.get("role"), 64) or "independent-reviewer"
    if role not in ROLES:
        return {"ok": False, "version": VERSION, "error": "unsupported reviewer role"}
    rec = {
        "schema": "sc-lab-reviewer/0.135.18.0",
        "version": VERSION,
        "record_type": "reviewer",
        "reviewer_id": rid,
        "display_name": _text(raw.get("displayName", raw.get("display_name")), 512) or rid,
        "role": role,
        "affiliation": _text(raw.get("affiliation"), 1024) or None,
        "expertise_tags": [_text(x, 128) for x in (raw.get("expertiseTags", raw.get("expertise_tags")) or [])[:50] if _text(x, 128)],
        "conflict_disclosure": _text(raw.get("conflictDisclosure", raw.get("conflict_disclosure")), 5000) or None,
        "independence_attested": bool(raw.get("independenceAttested", raw.get("independence_attested", False))),
        "created_at": _text(raw.get("createdAt", raw.get("created_at")), 128) or _now(),
    }
    rec["fingerprint"] = _fp(rec)
    return {"ok": True, "version": VERSION, "record": rec}


def normalize_panel(payload):
    if not isinstance(payload, dict):
        return {"ok": False, "version": VERSION, "error": "payload must be an object"}
    raw = payload.get("panel") if isinstance(payload.get("panel"), dict) else payload
    pid = _text(raw.get("id", raw.get("panelId", raw.get("panel_id"))), 256)
    if not pid:
        pid = f"review-panel-{_slug(raw.get('threadId', raw.get('thread_id')), 'unbound')}"
    reviewers_raw = raw.get("reviewers") or []
    reviewers, errors, seen = [], [], set()
    if len(reviewers_raw) > MAX_REVIEWERS:
        errors.append(f"reviewers exceeds maximum {MAX_REVIEWERS}")
    for item in reviewers_raw[:MAX_REVIEWERS]:
        n = normalize_reviewer(item if isinstance(item, dict) else {"reviewerId": item})
        if not n.get("ok"):
            errors.append(n.get("error", "invalid reviewer")); continue
        r = n["record"]
        if r["reviewer_id"] in seen:
            errors.append(f"duplicate reviewerId: {r['reviewer_id']}"); continue
        seen.add(r["reviewer_id"]); reviewers.append(r)
    rec = {
        "schema": "sc-lab-multi-reviewer-panel/0.135.18.0",
        "version": VERSION,
        "record_type": "multi-reviewer-panel",
        "collection": "graphStudioMultiReviewerPanels",
        "id": pid,
        "thread_id": _text(raw.get("threadId", raw.get("thread_id")), 2048) or None,
        "resolution_record_id": _text(raw.get("resolutionRecordId", raw.get("resolution_record_id")), 2048) or None,
        "audit_record_id": _text(raw.get("auditRecordId", raw.get("audit_record_id")), 2048) or None,
        "verification_bundle_refs": [_text(x, 2048) for x in (raw.get("verificationBundleRefs", raw.get("verification_bundle_refs")) or [])[:200] if _text(x, 2048)],
        "reproduction_bridge_refs": [_text(x, 2048) for x in (raw.get("reproductionBridgeRefs", raw.get("reproduction_bridge_refs")) or [])[:200] if _text(x, 2048)],
        "subject_refs": [_text(x, 2048) for x in (raw.get("subjectRefs", raw.get("subject_refs")) or [])[:500] if _text(x, 2048)],
        "review_version_ref": _text(raw.get("reviewVersionRef", raw.get("review_version_ref")), 2048) or None,
        "reviewers": reviewers,
        "assessments": copy.deepcopy((raw.get("assessments") or [])[:MAX_ASSESSMENTS]),
        "signoffs": copy.deepcopy((raw.get("signoffs") or [])[:MAX_ASSESSMENTS]),
        "dissents": copy.deepcopy((raw.get("dissents") or [])[:MAX_DISSENTS]),
        "created_at": _text(raw.get("createdAt", raw.get("created_at")), 128) or _now(),
        "author": _text(raw.get("author"), 256) or "user",
        "boundary": BOUNDARY,
    }
    rec["fingerprint"] = _fp(rec)
    return {"ok": not errors, "version": VERSION, "record": rec, "errors": errors}


def validate_panel(payload):
    n = normalize_panel(payload)
    if not n.get("record"):
        return n
    rec, errors = n["record"], list(n.get("errors") or [])
    if not rec["thread_id"]:
        errors.append("threadId is required")
    if len(rec["reviewers"]) < 2:
        errors.append("at least two distinct reviewers are required for a multi-reviewer panel")
    return {"ok": not errors, "version": VERSION, "record": rec, "errors": errors, "boundary": BOUNDARY}


def assign_reviewer(payload):
    p = normalize_panel(payload)
    if not p.get("record"):
        return p
    panel = p["record"]
    rn = normalize_reviewer(payload.get("reviewer") or {})
    if not rn.get("ok"):
        return rn
    r = rn["record"]
    if any(x["reviewer_id"] == r["reviewer_id"] for x in panel["reviewers"]):
        return {"ok": False, "version": VERSION, "error": "reviewer already assigned", "panel": panel}
    if len(panel["reviewers"]) >= MAX_REVIEWERS:
        return {"ok": False, "version": VERSION, "error": f"reviewer limit {MAX_REVIEWERS} reached"}
    panel["reviewers"].append(r); panel["fingerprint"] = _fp(panel)
    return {"ok": True, "version": VERSION, "panel": panel, "reviewer": r, "automatic_assessment": False}


def _panel_and_reviewer(payload):
    p = validate_panel(payload)
    if not p.get("record"):
        return None, None, p
    panel = p["record"]
    rid = _text(payload.get("reviewerId", payload.get("reviewer_id")), 256)
    reviewer = next((r for r in panel["reviewers"] if r["reviewer_id"] == rid), None)
    if not reviewer:
        return panel, None, {"ok": False, "version": VERSION, "error": "reviewerId must refer to an assigned reviewer"}
    return panel, reviewer, None


def record_assessment(payload):
    panel, reviewer, err = _panel_and_reviewer(payload)
    if err: return err
    state = _text(payload.get("assessmentState", payload.get("assessment_state")), 64)
    if state not in ASSESSMENT_STATES:
        return {"ok": False, "version": VERSION, "error": "unsupported assessmentState"}
    aid = _text(payload.get("assessmentId", payload.get("assessment_id")), 256) or f"assessment-{_slug(panel['id'])}-{_slug(reviewer['reviewer_id'])}-{len(panel['assessments'])+1}"
    rec = {
        "schema": "sc-lab-independent-review-assessment/0.135.18.0", "version": VERSION, "record_type": "independent-review-assessment",
        "id": aid, "panel_id": panel["id"], "reviewer_id": reviewer["reviewer_id"], "assessment_state": state,
        "review_version_ref": _text(payload.get("reviewVersionRef", payload.get("review_version_ref")), 2048) or panel["review_version_ref"],
        "subject_refs": [_text(x,2048) for x in (payload.get("subjectRefs", payload.get("subject_refs")) or panel["subject_refs"])[:500] if _text(x,2048)],
        "rationale": _text(payload.get("rationale"), 12000) or None,
        "limitations": _text(payload.get("limitations"), 12000) or None,
        "supersedes_assessment_id": _text(payload.get("supersedesAssessmentId", payload.get("supersedes_assessment_id")), 256) or None,
        "created_at": _text(payload.get("createdAt", payload.get("created_at")), 128) or _now(),
        "independent_record": True, "automatic_panel_outcome": False, "boundary": BOUNDARY,
    }
    rec["fingerprint"] = _fp(rec); panel["assessments"].append(rec); panel["fingerprint"] = _fp(panel)
    return {"ok": True, "version": VERSION, "panel": panel, "record": rec, "majority_calculated": False, "consensus_inferred": False}


def record_signoff(payload):
    panel, reviewer, err = _panel_and_reviewer(payload)
    if err: return err
    state = _text(payload.get("signoffState", payload.get("signoff_state")), 64)
    if state not in SIGNOFF_STATES:
        return {"ok": False, "version": VERSION, "error": "unsupported signoffState"}
    sid = _text(payload.get("signoffId", payload.get("signoff_id")), 256) or f"signoff-{_slug(panel['id'])}-{_slug(reviewer['reviewer_id'])}-{len(panel['signoffs'])+1}"
    rec = {
        "schema": "sc-lab-independent-review-signoff/0.135.18.0", "version": VERSION, "record_type": "independent-review-signoff",
        "id": sid, "panel_id": panel["id"], "reviewer_id": reviewer["reviewer_id"], "signoff_state": state,
        "review_version_ref": _text(payload.get("reviewVersionRef", payload.get("review_version_ref")), 2048) or panel["review_version_ref"],
        "assessment_ref": _text(payload.get("assessmentRef", payload.get("assessment_ref")), 256) or None,
        "note": _text(payload.get("note"), 12000) or None,
        "created_at": _text(payload.get("createdAt", payload.get("created_at")), 128) or _now(),
        "signs_for_self_only": True, "automatic_resolution": False, "scientific_truth_attested": False, "boundary": BOUNDARY,
    }
    rec["fingerprint"] = _fp(rec); panel["signoffs"].append(rec); panel["fingerprint"] = _fp(panel)
    return {"ok": True, "version": VERSION, "panel": panel, "record": rec, "automatic_resolution": False}


def record_dissent(payload):
    panel, reviewer, err = _panel_and_reviewer(payload)
    if err: return err
    kind = _text(payload.get("dissentKind", payload.get("dissent_kind")), 64) or "other"
    if kind not in DISSENT_KINDS:
        return {"ok": False, "version": VERSION, "error": "unsupported dissentKind"}
    statement = _text(payload.get("statement"), 16000)
    if not statement:
        return {"ok": False, "version": VERSION, "error": "dissent statement is required"}
    did = _text(payload.get("dissentId", payload.get("dissent_id")), 256) or f"dissent-{_slug(panel['id'])}-{_slug(reviewer['reviewer_id'])}-{len(panel['dissents'])+1}"
    rec = {
        "schema": "sc-lab-review-dissent/0.135.18.0", "version": VERSION, "record_type": "review-dissent",
        "id": did, "panel_id": panel["id"], "reviewer_id": reviewer["reviewer_id"], "dissent_kind": kind,
        "statement": statement, "alternative_interpretation": _text(payload.get("alternativeInterpretation", payload.get("alternative_interpretation")), 16000) or None,
        "evidence_refs": [_text(x,2048) for x in (payload.get("evidenceRefs", payload.get("evidence_refs")) or [])[:500] if _text(x,2048)],
        "assessment_ref": _text(payload.get("assessmentRef", payload.get("assessment_ref")), 256) or None,
        "created_at": _text(payload.get("createdAt", payload.get("created_at")), 128) or _now(),
        "preserved_even_if_minority": True, "automatic_override": False, "boundary": BOUNDARY,
    }
    rec["fingerprint"] = _fp(rec); panel["dissents"].append(rec); panel["fingerprint"] = _fp(panel)
    return {"ok": True, "version": VERSION, "panel": panel, "record": rec, "dissent_preserved": True}


def independence_check(payload):
    p = normalize_panel(payload)
    if not p.get("record"): return p
    panel = p["record"]; ids = [r["reviewer_id"] for r in panel["reviewers"]]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    unattested = [r["reviewer_id"] for r in panel["reviewers"] if not r.get("independence_attested")]
    disclosed = [r["reviewer_id"] for r in panel["reviewers"] if r.get("conflict_disclosure")]
    return {"ok": not duplicate_ids, "version": VERSION, "duplicate_reviewer_ids": duplicate_ids, "independence_not_attested": unattested,
            "conflict_disclosures_present": disclosed, "independence_is_user_attested_not_system_inferred": True, "automatic_disqualification": False, "boundary": BOUNDARY}


def panel_matrix(payload):
    p = normalize_panel(payload)
    if not p.get("record"): return p
    panel = p["record"]
    rows = []
    for r in panel["reviewers"]:
        rid = r["reviewer_id"]
        ass = [x for x in panel["assessments"] if isinstance(x, dict) and _text(x.get("reviewer_id", x.get("reviewerId")),256)==rid]
        sig = [x for x in panel["signoffs"] if isinstance(x, dict) and _text(x.get("reviewer_id", x.get("reviewerId")),256)==rid]
        dis = [x for x in panel["dissents"] if isinstance(x, dict) and _text(x.get("reviewer_id", x.get("reviewerId")),256)==rid]
        rows.append({"reviewer_id":rid,"display_name":r["display_name"],"role":r["role"],"latest_assessment_state":_text(ass[-1].get("assessment_state", ass[-1].get("assessmentState")),64) if ass else None,
                     "latest_signoff_state":_text(sig[-1].get("signoff_state", sig[-1].get("signoffState")),64) if sig else None,"assessment_count":len(ass),"signoff_count":len(sig),"dissent_count":len(dis)})
    return {"ok": True, "version": VERSION, "panel_id": panel["id"], "rows": rows, "majority_calculated": False, "consensus_score": None, "winner": None, "boundary": BOUNDARY}


def completion_status(payload):
    m = panel_matrix(payload)
    if not m.get("ok"): return m
    total=len(m["rows"]); with_assessment=sum(1 for r in m["rows"] if r["latest_assessment_state"]); with_signoff=sum(1 for r in m["rows"] if r["latest_signoff_state"])
    administratively_complete = total >= 2 and with_assessment == total and with_signoff == total
    unresolved_reviewers=[r["reviewer_id"] for r in m["rows"] if not r["latest_assessment_state"] or not r["latest_signoff_state"]]
    return {"ok": True, "version": VERSION, "panel_id": m["panel_id"], "reviewer_count":total,"reviewers_with_assessment":with_assessment,"reviewers_with_signoff":with_signoff,
            "administratively_complete":administratively_complete,"unresolved_reviewer_ids":unresolved_reviewers,"scientifically_resolved":None,"automatic_resolution":False,"boundary":BOUNDARY}


def audit_event_draft(payload):
    p = normalize_panel(payload)
    if not p.get("record"): return p
    panel=p["record"]; kind=_text(payload.get("eventType", payload.get("event_type")),64) or "review-panel-updated"
    allowed=("review-panel-created","reviewer-assigned","independent-assessment-recorded","independent-signoff-recorded","dissent-recorded","review-panel-updated")
    if kind not in allowed: return {"ok":False,"version":VERSION,"error":"unsupported panel audit event type"}
    return {"ok":True,"version":VERSION,"event":{"eventType":kind,"panelId":panel["id"],"reviewerId":_text(payload.get("reviewerId", payload.get("reviewer_id")),256) or None,
            "recordRef":_text(payload.get("recordRef", payload.get("record_ref")),512) or None,"note":_text(payload.get("note"),8000) or None},
            "append_only_target":"graphStudioReviewAudits","automatic_append":False,"automatic_resolution":False,"boundary":BOUNDARY}


def panel_packet(payload):
    v=validate_panel(payload)
    if not v.get("ok"): return v
    panel=v["record"]; matrix=panel_matrix({"panel":panel}); completion=completion_status({"panel":panel}); independence=independence_check({"panel":panel})
    packet={"schema":"sc-lab-multi-reviewer-panel-packet/0.135.18.0","version":VERSION,"panel":panel,"matrix":matrix,"completion":completion,"independence":independence,
            "automatic_consensus":False,"automatic_resolution":False,"truth_ranking":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"packet":packet}


def fingerprint(payload):
    p=normalize_panel(payload)
    if not p.get("record"): return p
    return {"ok":True,"version":VERSION,"algorithm":"sha256","fingerprint":_fp(p["record"])}


def status(payload):
    p=normalize_panel(payload)
    if not p.get("record"): return p
    panel=p["record"]; c=completion_status({"panel":panel})
    return {"ok":True,"version":VERSION,"panel_ready":len(panel["reviewers"])>=2,"reviewer_count":len(panel["reviewers"]),"assessment_count":len(panel["assessments"]),
            "signoff_count":len(panel["signoffs"]),"dissent_count":len(panel["dissents"]),"administratively_complete":c.get("administratively_complete",False),
            "scientific_consensus_inferred":False,"automatic_resolution":False,"boundary":BOUNDARY}


def health():
    return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"multi_reviewer_panels":True,"independent_assessments":True,"independent_signoff":True,"dissent_preservation":True,
            "append_oriented_records":True,"review_audit_handoff":True,"backward_compatible_v0135170":True}


def contract():
    return {"ok":True,"version":VERSION,"roles":list(ROLES),"assessment_states":list(ASSESSMENT_STATES),"signoff_states":list(SIGNOFF_STATES),"dissent_kinds":list(DISSENT_KINDS),
            "project_collection":"graphStudioMultiReviewerPanels","max_reviewers":MAX_REVIEWERS,"max_assessments":MAX_ASSESSMENTS,"max_dissents":MAX_DISSENTS,
            "majority_voting":False,"consensus_scoring":False,"automatic_resolution":False,"truth_ranking":False}


def browser_contract():
    return {"ok":True,"version":VERSION,"required_actions":["create-panel","assign-reviewer","record-independent-assessment","record-independent-signoff","record-dissent","open-panel-context"],
            "full_render_count_must_not_increase":True,"panel_summary_must_not_rank_reviewers":True}


def acceptance_report():
    return {"ok":True,"version":VERSION,"multi_reviewer_panels":True,"independent_assessment_lineage":True,"independent_signoff":True,"dissent_preserved":True,
            "abstention_preserved":True,"conflict_disclosure_supported":True,"independence_user_attested":True,"project_persistence_explicit":True,"cross_workspace_panel_handoff":True,
            "full_graph_redraw_for_panel":False,"majority_voting":False,"consensus_scoring":False,"reviewer_ranking":False,"automatic_resolution":False,"automatic_scientific_validity":False,
            "automatic_claim_confirmation":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"scientific_preference":False}
