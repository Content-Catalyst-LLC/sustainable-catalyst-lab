from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .integrated_research_beta_v0600 import normalize_project_summary

VERSION = "0.61.0"
STUDY_SCHEMA = "sc-lab-scientific-study/0.61.0"
LIFECYCLE_SCHEMA = "sc-lab-scientific-study-lifecycle/0.61.0"
REVIEW_SCHEMA = "sc-lab-scientific-study-stage-review/0.61.0"
PACKET_SCHEMA = "sc-lab-scientific-study-evidence-packet/0.61.0"
MAX_HYPOTHESES = 12
MAX_REVIEWS = 100
MAX_EVIDENCE_REFS = 250

STUDY_TYPES = {"observational", "experimental", "computational", "mixed"}
STUDY_STATUSES = {"draft", "active", "review", "complete", "archived"}
REVIEW_DECISIONS = {"accept", "block", "reopen"}
STAGES = (
    "question", "protocol", "data", "analysis", "validation", "uncertainty",
    "experiment", "figure", "conclusion", "reproducibility", "audit",
)

FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "dataset", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey",
    "api_key", "authorization", "cookie", "privatekey", "private_key",
}


class ScientificStudyLifecycleError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, default: str = "") -> str:
    text = _text(value, 120)
    safe = "".join(ch for ch in text if ch.isalnum() or ch in "-_.:")
    return safe or default


def _hash_refs(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:MAX_EVIDENCE_REFS]:
        text = str(item or "").strip().lower()
        if len(text) == 64 and all(ch in "0123456789abcdef" for ch in text):
            out.append(text)
    return sorted(set(out))


def _refs(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:MAX_EVIDENCE_REFS]:
        text = _text(item, 180)
        if text:
            out.append(text)
    return sorted(set(out))


def _scan_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in {k.replace("_", "") for k in FORBIDDEN_KEYS}:
                raise ScientificStudyLifecycleError(
                    f"Scientific study lifecycle accepts governed metadata/evidence references only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]")


def templates() -> dict[str, Any]:
    rows = [
        {
            "id": "observational-study",
            "label": "Observational scientific study",
            "studyType": "observational",
            "title": "Observational scientific study",
            "researchQuestion": "What association is supported by the observed evidence?",
            "hypotheses": ["State a falsifiable or testable expectation without implying causality."],
            "methodsSummary": "Describe sampling, measurement, inclusion/exclusion, transformations, and planned analysis.",
            "analysisPlan": "Specify the governed Lab analyses and validation checks to use.",
        },
        {
            "id": "experimental-study",
            "label": "Experimental scientific study",
            "studyType": "experimental",
            "title": "Experimental scientific study",
            "researchQuestion": "How does the declared intervention affect the measured outcome under the defined protocol?",
            "hypotheses": ["State the preregistered experimental expectation and direction, if justified."],
            "methodsSummary": "Describe controls, factors, response variables, replication, blocking/randomization, and safety constraints.",
            "analysisPlan": "Specify the governed analysis, validation, uncertainty, and sequential-design boundaries.",
        },
        {
            "id": "computational-study",
            "label": "Computational / modeling study",
            "studyType": "computational",
            "title": "Computational scientific study",
            "researchQuestion": "What does the governed computational model support under its stated assumptions and parameter domain?",
            "hypotheses": ["State the expected model behavior or comparative prediction."],
            "methodsSummary": "Describe model form, data provenance, calibration/validation, numerical methods, and assumptions.",
            "analysisPlan": "Specify validation, sensitivity/uncertainty, figures, and reproducibility workflow.",
        },
        {
            "id": "mixed-study",
            "label": "Mixed evidence + experiment study",
            "studyType": "mixed",
            "title": "Mixed scientific study",
            "researchQuestion": "How do observational, computational, and experimental evidence jointly inform the research question?",
            "hypotheses": ["State the study expectation and distinguish evidence classes."],
            "methodsSummary": "Describe evidence collection, transformations, modeling, experimental design, and integration strategy.",
            "analysisPlan": "Specify each governed analysis path and how results will be compared without collapsing uncertainty or provenance.",
        },
    ]
    return {"ok": True, "version": VERSION, "templates": rows, "templateHash": _hash(rows)}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "endToEndStudyLifecycle": True,
        "metadataAndEvidenceReferencesOnly": True,
        "humanStageReviewRequired": True,
        "humanConclusionReviewRequired": True,
        "automaticScientificCertificationAuthorized": False,
        "automaticCausalClaimAuthorized": False,
        "automaticPublicationAuthorized": False,
        "automaticExperimentExecutionAuthorized": False,
        "automaticHighStakesDecisionAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
        "rawScientificDataAccepted": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-study-lifecycle-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "stageCount": len(STAGES),
        "studyTypes": sorted(STUDY_TYPES),
        "humanReviewRequired": True,
        "automaticScientificCertification": False,
        "automaticPublication": False,
        "automaticExperimentExecution": False,
        "arbitraryCode": False,
    }


def _normalize_reviews(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(value[:MAX_REVIEWS]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        stage_id = _id(raw.get("stageId"))
        decision = _text(raw.get("decision"), 20).lower()
        if stage_id not in STAGES or decision not in REVIEW_DECISIONS:
            continue
        core = {
            "id": _id(raw.get("id"), f"review-{index+1}"),
            "stageId": stage_id,
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 1200),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
            "evidenceRefs": _refs(raw.get("evidenceRefs")),
        }
        core["reviewHash"] = _hash(core)
        out.append(core)
    return out


def normalize_study(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    _scan_forbidden(source)
    study_type = _text(source.get("studyType") or "observational", 40).lower()
    if study_type not in STUDY_TYPES:
        raise ScientificStudyLifecycleError(f"Unsupported study type: {study_type}")
    status = _text(source.get("status") or "draft", 30).lower()
    if status not in STUDY_STATUSES:
        raise ScientificStudyLifecycleError(f"Unsupported study status: {status}")
    hypotheses = []
    if isinstance(source.get("hypotheses"), list):
        hypotheses = [_text(item, 800) for item in source["hypotheses"][:MAX_HYPOTHESES] if _text(item, 800)]
    elif _text(source.get("hypothesis"), 800):
        hypotheses = [_text(source.get("hypothesis"), 800)]
    study = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), "study-active-project"),
        "title": _text(source.get("title") or "Scientific study", 220),
        "studyType": study_type,
        "status": status,
        "researchQuestion": _text(source.get("researchQuestion"), 1600),
        "rationale": _text(source.get("rationale"), 2400),
        "hypotheses": hypotheses,
        "methodsSummary": _text(source.get("methodsSummary"), 5000),
        "analysisPlan": _text(source.get("analysisPlan"), 5000),
        "uncertaintyPlan": _text(source.get("uncertaintyPlan"), 3000),
        "conclusionSummary": _text(source.get("conclusionSummary"), 5000),
        "limitations": _text(source.get("limitations"), 5000),
        "openQuestions": _text(source.get("openQuestions"), 3000),
        "evidenceRefs": _refs(source.get("evidenceRefs")),
        "evidenceHashes": _hash_refs(source.get("evidenceHashes")),
        "stageReviews": _normalize_reviews(source.get("stageReviews")),
    }
    study["studyHash"] = _hash(study)
    return study


def record_stage_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificStudyLifecycleError("A study and stage review are required.")
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else {})
    review_raw = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review_raw)
    stage_id = _id(review_raw.get("stageId"))
    decision = _text(review_raw.get("decision"), 20).lower()
    if stage_id not in STAGES:
        raise ScientificStudyLifecycleError("A governed lifecycle stage is required for review.")
    if decision not in REVIEW_DECISIONS:
        raise ScientificStudyLifecycleError("Stage review decision must be accept, block, or reopen.")
    rationale = _text(review_raw.get("rationale"), 1200)
    if decision in {"accept", "block"} and len(rationale) < 4:
        raise ScientificStudyLifecycleError("Accepted or blocked stages require a review rationale.")
    raw = {
        "id": _id(review_raw.get("id"), f"{study['id']}-{stage_id}-review-{len(study['stageReviews'])+1}"),
        "stageId": stage_id,
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review_raw.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review_raw.get("reviewedAt"), 64),
        "evidenceRefs": _refs(review_raw.get("evidenceRefs")),
    }
    raw["reviewHash"] = _hash(raw)
    source = deepcopy(study)
    source.pop("studyHash", None)
    source["stageReviews"] = [*study["stageReviews"], raw]
    updated = normalize_study(source)
    return {"ok": True, "schema": REVIEW_SCHEMA, "version": VERSION, "review": raw, "study": updated}


def _analysis_types(project: dict[str, Any]) -> set[str]:
    return {str(x).lower() for x in project.get("analysisRecordTypes", [])}


def _contains(types: set[str], *needles: str) -> bool:
    return any(any(needle in value for needle in needles) for value in types)


def _latest_review(study: dict[str, Any], stage_id: str) -> dict[str, Any] | None:
    matches = [row for row in study.get("stageReviews", []) if row.get("stageId") == stage_id]
    return matches[-1] if matches else None


def evaluate_lifecycle(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificStudyLifecycleError("Study lifecycle evaluation requires a study and project metadata summary.")
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else {})
    project = normalize_project_summary(payload.get("project") if isinstance(payload.get("project"), dict) else {})
    counts = project["counts"]
    types = _analysis_types(project)
    audit_gate = project.get("audit", {}).get("gate", "")
    experiment_required = study["studyType"] in {"experimental", "mixed"}

    evidence_complete = {
        "question": bool(study["researchQuestion"]),
        "protocol": bool(study["methodsSummary"] and study["analysisPlan"]),
        "data": counts.get("datasets", 0) > 0,
        "analysis": counts.get("models", 0) > 0 or _contains(types, "statistical", "bayesian", "dynamic-systems", "probabilistic", "model", "analysis"),
        "validation": counts.get("scientificWorkflowRunsV0570", 0) > 0 or _contains(types, "validation", "diagnostic", "cross-validation", "workflow-run"),
        "uncertainty": bool(study["uncertaintyPlan"] or study["limitations"]) and (_contains(types, "uncertainty", "probabilistic", "bayesian") or bool(study["limitations"])),
        "experiment": (not experiment_required) or counts.get("experiments", 0) > 0 or _contains(types, "experimental-design", "sequential-experiment"),
        "figure": counts.get("visualizations", 0) > 0 or bool(project.get("figureHashes")),
        "conclusion": bool(study["conclusionSummary"] and study["limitations"]),
        "reproducibility": counts.get("reproduciblePackages", 0) > 0 or bool(project.get("packageHashes")) or (counts.get("scientificWorkflowsV0570", 0) > 0 and counts.get("scientificWorkflowRunsV0570", 0) > 0),
        "audit": audit_gate in {"audit-ready", "human-review-required"},
    }
    required_map = {
        "question": True, "protocol": True, "data": True, "analysis": True, "validation": True,
        "uncertainty": True, "experiment": experiment_required, "figure": False,
        "conclusion": True, "reproducibility": True, "audit": True,
    }
    stages = []
    blocked = []
    missing = []
    pending_review = []
    for stage_id in STAGES:
        required = required_map[stage_id]
        complete = bool(evidence_complete[stage_id])
        review = _latest_review(study, stage_id)
        decision = review.get("decision") if review else ""
        if audit_gate == "blocked" and stage_id == "audit":
            decision = "block"
        is_blocked = decision == "block"
        accepted = decision == "accept" and complete
        not_applicable = stage_id == "experiment" and not experiment_required
        if is_blocked:
            status = "blocked"
            blocked.append(stage_id)
        elif not_applicable:
            status = "not-applicable"
        elif not complete:
            status = "needs-evidence" if required else "optional"
            if required:
                missing.append(stage_id)
        elif required and not accepted:
            status = "needs-review"
            pending_review.append(stage_id)
        elif accepted:
            status = "accepted"
        else:
            status = "evidence-ready"
        stages.append({
            "id": stage_id,
            "label": {
                "question":"Research question & hypotheses", "protocol":"Protocol & analysis plan", "data":"Data & provenance",
                "analysis":"Analysis / modeling", "validation":"Validation & diagnostics", "uncertainty":"Uncertainty & limitations",
                "experiment":"Experimental evidence", "figure":"Scientific figures", "conclusion":"Conclusions & limitations",
                "reproducibility":"Reproducibility package", "audit":"Scientific audit",
            }[stage_id],
            "required": required,
            "evidenceComplete": complete,
            "reviewDecision": decision or None,
            "reviewHash": review.get("reviewHash") if review else None,
            "status": status,
        })
    required_ids = [row["id"] for row in stages if row["required"]]
    if blocked:
        gate = "blocked"
    elif missing:
        gate = "needs-evidence"
    elif pending_review:
        gate = "needs-review"
    else:
        gate = "study-complete"
    core = {
        "schema": LIFECYCLE_SCHEMA,
        "version": VERSION,
        "studyId": study["id"],
        "studyHash": study["studyHash"],
        "projectId": project["id"],
        "projectHash": _hash(project),
        "studyType": study["studyType"],
        "gate": gate,
        "stages": stages,
        "requiredStageIds": required_ids,
        "missingEvidence": missing,
        "pendingHumanReview": pending_review,
        "blockedStages": blocked,
        "humanReviewRequired": True,
        "scientificCertificationClaim": False,
    }
    core["lifecycleHash"] = _hash(core)
    return {"ok": not blocked, **core}


def build_study_packet(payload: dict[str, Any]) -> dict[str, Any]:
    lifecycle = evaluate_lifecycle(payload)
    study = normalize_study(payload.get("study") if isinstance(payload, dict) and isinstance(payload.get("study"), dict) else {})
    review_hashes = [row["reviewHash"] for row in study["stageReviews"]]
    packet = {
        "schema": PACKET_SCHEMA,
        "version": VERSION,
        "studyId": study["id"],
        "studyType": study["studyType"],
        "studyHash": study["studyHash"],
        "projectHash": lifecycle["projectHash"],
        "lifecycleHash": lifecycle["lifecycleHash"],
        "gate": lifecycle["gate"],
        "requiredStageIds": lifecycle["requiredStageIds"],
        "missingEvidence": lifecycle["missingEvidence"],
        "pendingHumanReview": lifecycle["pendingHumanReview"],
        "blockedStages": lifecycle["blockedStages"],
        "stageStatuses": {row["id"]: row["status"] for row in lifecycle["stages"]},
        "reviewHashes": review_hashes,
        "evidenceRefs": study["evidenceRefs"],
        "evidenceHashes": study["evidenceHashes"],
        "boundaries": {
            "rawScientificDataIncluded": False,
            "credentialsIncluded": False,
            "automaticScientificCertification": False,
            "automaticCausalClaim": False,
            "automaticPublication": False,
            "automaticExperimentExecution": False,
            "humanReviewRequired": True,
        },
    }
    packet["packetHash"] = _hash(packet)
    return {"ok": True, "packet": packet, "lifecycle": lifecycle}


def verify_study_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) and isinstance(payload.get("packet"), dict) else {}
    expected = _text(packet.get("packetHash"), 64).lower()
    core = deepcopy(packet)
    core.pop("packetHash", None)
    actual = _hash(core)
    valid = len(expected) == 64 and expected == actual and packet.get("schema") == PACKET_SCHEMA and packet.get("version") == VERSION
    return {"ok": valid, "version": VERSION, "expectedHash": expected, "actualHash": actual, "tampered": not valid}
