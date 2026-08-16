from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

VERSION = "0.70.0"
QUESTION_SCHEMA = "sc-lab-research-question/0.70.0"
HYPOTHESIS_SCHEMA = "sc-lab-hypothesis-registry/0.70.0"
PREREG_SCHEMA = "sc-lab-preregistration/0.70.0"
DEVIATION_SCHEMA = "sc-lab-preregistration-deviation/0.70.0"
FREEZE_SCHEMA = "sc-lab-preregistration-freeze/0.70.0"
EVALUATION_SCHEMA = "sc-lab-preregistration-evaluation/0.70.0"
PACKET_SCHEMA = "sc-lab-preregistration-packet/0.70.0"

QUESTION_TYPES = {"descriptive", "associational", "causal", "predictive", "mechanistic", "comparative", "custom"}
HYPOTHESIS_ROLES = {"primary", "secondary", "exploratory", "null", "alternative", "mechanistic", "custom"}
DIRECTION_TYPES = {"positive", "negative", "non-directional", "nonlinear", "equivalence", "non-inferiority", "custom"}
DEVIATION_TYPES = {"research-question", "hypothesis", "outcome", "analysis", "exclusion", "stopping-rule", "sample-size", "missing-data", "multiplicity", "sensitivity", "other"}
REVIEW_DECISIONS = {"accept-within-scope", "accept-with-qualification", "block", "reopen"}
RESULT_ACCESS_STATES = {"not-inspected", "unknown", "inspected"}

FORBIDDEN_KEYS = {
    "rows", "records", "rawdata", "raw_data", "dataset", "datasets", "datasetpayload", "datasetspayload",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key", "authorization",
    "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook", "python", "javascript", "shell",
    "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes", "attachmentbytes", "attachment_bytes",
    "binary", "base64", "participantdata", "participantrecords", "microdata", "outcomevector", "predictormatrix",
    "covariatematrix", "individualrecords", "subjectrecords"
}


class PreregistrationError(ValueError):
    pass


def _canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(v: Any) -> str:
    return hashlib.sha256(_canonical(v).encode("utf-8")).hexdigest()


def _text(v: Any, limit: int) -> str:
    return str(v or "").strip()[:limit]


def _id(v: Any, default: str = "") -> str:
    s = _text(v, 180)
    safe = "".join(ch for ch in s if ch.isalnum() or ch in "-_.:")
    return safe or default


def _ids(v: Any, limit: int = 120) -> list[str]:
    if not isinstance(v, list):
        return []
    out: list[str] = []
    for raw in v[:limit]:
        item = _id(raw)
        if item and item not in out:
            out.append(item)
    return out


def _texts(v: Any, limit: int = 80, item_limit: int = 1200) -> list[str]:
    if not isinstance(v, list):
        return []
    out: list[str] = []
    for raw in v[:limit]:
        item = _text(raw, item_limit)
        if item and item not in out:
            out.append(item)
    return out


def _scan_forbidden(value: Any, path: str = "$") -> None:
    forbidden = {k.replace("_", "").replace("-", "").lower() for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            norm = str(key).replace("_", "").replace("-", "").lower()
            if norm in forbidden:
                raise PreregistrationError(
                    f"Preregistration accepts governed research metadata only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{i}]")


def _timestamp(v: Any, default_now: bool = False) -> str:
    s = _text(v, 64)
    if s:
        return s
    if default_now:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return ""


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "questionTypes": sorted(QUESTION_TYPES),
        "hypothesisRoles": sorted(HYPOTHESIS_ROLES),
        "directionTypes": sorted(DIRECTION_TYPES),
        "deviationTypes": sorted(DEVIATION_TYPES),
        "preResultFreezeRequired": True,
        "frozenSnapshotImmutable": True,
        "timestampedDeviationLogRequired": True,
        "humanPreregistrationReviewRequired": True,
        "automaticHypothesisValidationAuthorized": False,
        "automaticOutcomeReclassificationAuthorized": False,
        "automaticPostHocPreregistrationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "rawScientificDataAccepted": False,
        "participantLevelDataAccepted": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "preregistration-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "preResultFreezeRequired": True,
        "frozenSnapshotImmutable": True,
        "timestampedDeviationLogRequired": True,
        "humanPreregistrationReviewRequired": True,
        "automaticPostHocPreregistration": False,
        "rawScientificDataAccepted": False,
        "arbitraryCode": False,
    }


def normalize_question(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    qtype = _text(raw.get("questionType"), 80).lower() or "custom"
    if qtype not in QUESTION_TYPES:
        qtype = "custom"
    row = {
        "schema": QUESTION_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "research-question-1"),
        "studyId": _id(raw.get("studyId")),
        "question": _text(raw.get("question"), 5000),
        "questionType": qtype,
        "rationale": _text(raw.get("rationale"), 5000),
        "populationBoundary": _text(raw.get("populationBoundary"), 4000),
        "exposureOrIntervention": _text(raw.get("exposureOrIntervention"), 3000),
        "comparator": _text(raw.get("comparator"), 3000),
        "outcomeBoundary": _text(raw.get("outcomeBoundary"), 3000),
        "timeHorizon": _text(raw.get("timeHorizon"), 1200),
        "linkedTheoryIds": _ids(raw.get("linkedTheoryIds"), 80),
        "linkedClaimIds": _ids(raw.get("linkedClaimIds"), 120),
        "note": _text(raw.get("note"), 3000),
    }
    row["questionHash"] = _hash(row)
    return row


def normalize_hypothesis(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    role = _text(raw.get("role"), 80).lower() or "primary"
    if role not in HYPOTHESIS_ROLES:
        role = "custom"
    direction = _text(raw.get("direction"), 80).lower() or "non-directional"
    if direction not in DIRECTION_TYPES:
        direction = "custom"
    row = {
        "schema": HYPOTHESIS_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "registered-hypothesis-1"),
        "studyId": _id(raw.get("studyId")),
        "researchQuestionId": _id(raw.get("researchQuestionId")),
        "linkedArgumentHypothesisId": _id(raw.get("linkedArgumentHypothesisId")),
        "linkedTheoryPredictionId": _id(raw.get("linkedTheoryPredictionId")),
        "role": role,
        "statement": _text(raw.get("statement"), 5000),
        "direction": direction,
        "outcomeRef": _id(raw.get("outcomeRef")),
        "exposureRef": _id(raw.get("exposureRef")),
        "effectOrContrast": _text(raw.get("effectOrContrast"), 3000),
        "falsificationBoundary": _text(raw.get("falsificationBoundary"), 5000),
        "note": _text(raw.get("note"), 3000),
    }
    row["hypothesisHash"] = _hash(row)
    return row


def _reviews(v: Any) -> list[dict[str, Any]]:
    if not isinstance(v, list):
        return []
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(v[:100]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 80).lower()
        if decision not in REVIEW_DECISIONS:
            continue
        row = {
            "id": _id(raw.get("id"), f"preregistration-review-{i+1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 4000),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _timestamp(raw.get("reviewedAt")),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def normalize_preregistration(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    result_state = _text(raw.get("resultsAccessState"), 80).lower() or "unknown"
    if result_state not in RESULT_ACCESS_STATES:
        result_state = "unknown"
    row = {
        "schema": PREREG_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "preregistration-1"),
        "studyId": _id(raw.get("studyId")),
        "title": _text(raw.get("title") or "Scientific preregistration", 600),
        "researchQuestionIds": _ids(raw.get("researchQuestionIds"), 100),
        "hypothesisIds": _ids(raw.get("hypothesisIds"), 160),
        "primaryOutcome": _text(raw.get("primaryOutcome"), 4000),
        "secondaryOutcomes": _texts(raw.get("secondaryOutcomes"), 80, 1800),
        "analysisPlan": _text(raw.get("analysisPlan"), 8000),
        "inclusionCriteria": _text(raw.get("inclusionCriteria"), 5000),
        "exclusionCriteria": _text(raw.get("exclusionCriteria"), 5000),
        "stoppingRule": _text(raw.get("stoppingRule"), 5000),
        "sampleSizeRationale": _text(raw.get("sampleSizeRationale"), 5000),
        "missingDataPlan": _text(raw.get("missingDataPlan"), 5000),
        "multiplicityPlan": _text(raw.get("multiplicityPlan"), 5000),
        "sensitivityPlan": _text(raw.get("sensitivityPlan"), 5000),
        "resultsAccessState": result_state,
        "preResultAttestation": _text(raw.get("preResultAttestation"), 3000),
        "scopeBoundary": _text(raw.get("scopeBoundary"), 5000),
        "limitations": _text(raw.get("limitations"), 5000),
        "reviewHistory": _reviews(raw.get("reviewHistory")),
    }
    plan_body = {k: v for k, v in row.items() if k != "reviewHistory"}
    row["planHash"] = _hash(plan_body)
    row["preregistrationHash"] = _hash(row)
    return row


def normalize_deviation(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    dtype = _text(raw.get("deviationType"), 80).lower() or "other"
    if dtype not in DEVIATION_TYPES:
        dtype = "other"
    row = {
        "schema": DEVIATION_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "preregistration-deviation-1"),
        "preregistrationId": _id(raw.get("preregistrationId")),
        "freezeHash": _text(raw.get("freezeHash"), 64),
        "deviationType": dtype,
        "sectionRef": _text(raw.get("sectionRef"), 500),
        "description": _text(raw.get("description"), 5000),
        "rationale": _text(raw.get("rationale"), 5000),
        "impactOnInterpretation": _text(raw.get("impactOnInterpretation"), 5000),
        "discoveredAt": _timestamp(raw.get("discoveredAt")),
        "declaredAt": _timestamp(raw.get("declaredAt")),
        "linkedEvidenceRefs": _ids(raw.get("linkedEvidenceRefs"), 120),
    }
    if not row["preregistrationId"]:
        raise PreregistrationError("Preregistration deviations require preregistrationId.")
    row["deviationHash"] = _hash(row)
    return row


def _select(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None, list[dict[str, Any]]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("preregistration"), dict):
        raise PreregistrationError("Preregistration evaluation requires a preregistration object.")
    prereg = normalize_preregistration(payload["preregistration"])
    questions = [normalize_question(x) for x in (payload.get("questions") or []) if isinstance(x, dict)]
    hypotheses = [normalize_hypothesis(x) for x in (payload.get("hypotheses") or []) if isinstance(x, dict)]
    questions = [x for x in questions if not x["studyId"] or not prereg["studyId"] or x["studyId"] == prereg["studyId"]]
    hypotheses = [x for x in hypotheses if not x["studyId"] or not prereg["studyId"] or x["studyId"] == prereg["studyId"]]
    freeze = payload.get("freeze") if isinstance(payload.get("freeze"), dict) else None
    deviations = [normalize_deviation(x) for x in (payload.get("deviations") or []) if isinstance(x, dict)]
    deviations = [x for x in deviations if x["preregistrationId"] == prereg["id"]]
    return prereg, questions, hypotheses, deepcopy(freeze) if freeze else None, deviations


def _snapshot(prereg: dict[str, Any], questions: list[dict[str, Any]], hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    q_by_id = {x["id"]: x for x in questions}
    h_by_id = {x["id"]: x for x in hypotheses}
    selected_q = [q_by_id[x] for x in prereg["researchQuestionIds"] if x in q_by_id]
    selected_h = [h_by_id[x] for x in prereg["hypothesisIds"] if x in h_by_id]
    return {
        "preregistrationId": prereg["id"],
        "studyId": prereg["studyId"],
        "preregistrationPlanHash": prereg["planHash"],
        "researchQuestionHashes": [x["questionHash"] for x in selected_q],
        "hypothesisHashes": [x["hypothesisHash"] for x in selected_h],
        "primaryOutcomeHash": _hash(prereg["primaryOutcome"]),
        "secondaryOutcomesHash": _hash(prereg["secondaryOutcomes"]),
        "analysisPlanHash": _hash(prereg["analysisPlan"]),
        "inclusionCriteriaHash": _hash(prereg["inclusionCriteria"]),
        "exclusionCriteriaHash": _hash(prereg["exclusionCriteria"]),
        "stoppingRuleHash": _hash(prereg["stoppingRule"]),
        "sampleSizeRationaleHash": _hash(prereg["sampleSizeRationale"]),
        "missingDataPlanHash": _hash(prereg["missingDataPlan"]),
        "multiplicityPlanHash": _hash(prereg["multiplicityPlan"]),
        "sensitivityPlanHash": _hash(prereg["sensitivityPlan"]),
        "scopeBoundaryHash": _hash(prereg["scopeBoundary"]),
    }


def freeze_preregistration(payload: dict[str, Any]) -> dict[str, Any]:
    prereg, questions, hypotheses, _freeze, _deviations = _select(payload)
    if prereg["resultsAccessState"] != "not-inspected":
        raise PreregistrationError("Preregistration can be frozen only when resultsAccessState is explicitly not-inspected.")
    if len(prereg["preResultAttestation"]) < 12:
        raise PreregistrationError("Pre-result freeze requires an explicit attestation.")
    snapshot = _snapshot(prereg, questions, hypotheses)
    row = {
        "ok": True,
        "schema": FREEZE_SCHEMA,
        "version": VERSION,
        "preregistrationId": prereg["id"],
        "frozenAt": _timestamp(payload.get("frozenAt"), default_now=True),
        "resultsAccessState": prereg["resultsAccessState"],
        "preResultAttestationHash": _hash(prereg["preResultAttestation"]),
        "snapshot": snapshot,
        "snapshotHash": _hash(snapshot),
        "immutable": True,
        "automaticPostHocPreregistration": False,
    }
    row["freezeHash"] = _hash(row)
    return row


def verify_freeze(payload: dict[str, Any]) -> dict[str, Any]:
    prereg, questions, hypotheses, freeze, _deviations = _select(payload)
    if not freeze:
        return {"ok": False, "version": VERSION, "reason": "missing-freeze"}
    expected_snapshot = _snapshot(prereg, questions, hypotheses)
    supplied_snapshot = freeze.get("snapshot") if isinstance(freeze.get("snapshot"), dict) else {}
    supplied_snapshot_hash = _text(freeze.get("snapshotHash"), 64)
    expected_snapshot_hash = _hash(expected_snapshot)
    supplied_freeze_hash = _text(freeze.get("freezeHash"), 64)
    body = {
        "ok": bool(freeze.get("ok")),
        "schema": _text(freeze.get("schema"), 120),
        "version": _text(freeze.get("version"), 40),
        "preregistrationId": _id(freeze.get("preregistrationId")),
        "frozenAt": _timestamp(freeze.get("frozenAt")),
        "resultsAccessState": _text(freeze.get("resultsAccessState"), 80),
        "preResultAttestationHash": _text(freeze.get("preResultAttestationHash"), 64),
        "snapshot": supplied_snapshot,
        "snapshotHash": supplied_snapshot_hash,
        "immutable": bool(freeze.get("immutable")),
        "automaticPostHocPreregistration": bool(freeze.get("automaticPostHocPreregistration")),
    }
    expected_freeze_hash = _hash(body)
    return {
        "ok": supplied_snapshot == expected_snapshot and supplied_snapshot_hash == expected_snapshot_hash and supplied_freeze_hash == expected_freeze_hash,
        "version": VERSION,
        "snapshotMatchesCurrentRegisteredPlan": supplied_snapshot == expected_snapshot,
        "snapshotHashMatches": supplied_snapshot_hash == expected_snapshot_hash,
        "freezeHashMatches": supplied_freeze_hash == expected_freeze_hash,
        "expectedSnapshotHash": expected_snapshot_hash,
        "expectedFreezeHash": expected_freeze_hash,
    }


def record_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("preregistration"), dict) or not isinstance(payload.get("review"), dict):
        raise PreregistrationError("Preregistration review requires preregistration and review objects.")
    prereg = normalize_preregistration(payload["preregistration"])
    raw = payload["review"]
    _scan_forbidden(raw)
    decision = _text(raw.get("decision"), 80).lower()
    if decision not in REVIEW_DECISIONS:
        raise PreregistrationError("Preregistration review decision is not recognized.")
    rationale = _text(raw.get("rationale"), 4000)
    if decision != "reopen" and len(rationale) < 4:
        raise PreregistrationError("Preregistration review decisions require a rationale.")
    if decision == "accept-with-qualification" and len(prereg["limitations"]) < 8:
        raise PreregistrationError("Qualified preregistration review requires explicit limitations.")
    row = {
        "id": _id(raw.get("id"), f"{prereg['id']}-review-{len(prereg['reviewHistory'])+1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _timestamp(raw.get("reviewedAt"), default_now=True),
    }
    row["reviewHash"] = _hash(row)
    prereg["reviewHistory"] = [*prereg["reviewHistory"], row]
    prereg["preregistrationHash"] = _hash({k: v for k, v in prereg.items() if k != "preregistrationHash"})
    return {"ok": True, "version": VERSION, "preregistration": prereg, "review": row}


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    prereg, questions, hypotheses, freeze, deviations = _select(payload)
    q_ids = {x["id"] for x in questions}
    h_ids = {x["id"] for x in hypotheses}
    missing_q = [x for x in prereg["researchQuestionIds"] if x not in q_ids]
    missing_h = [x for x in prereg["hypothesisIds"] if x not in h_ids]
    selected_q = [x for x in questions if x["id"] in prereg["researchQuestionIds"]]
    selected_h = [x for x in hypotheses if x["id"] in prereg["hypothesisIds"]]
    incomplete_q = [x["id"] for x in selected_q if len(x["question"]) < 8 or len(x["populationBoundary"]) < 8 or len(x["outcomeBoundary"]) < 4]
    incomplete_h = [x["id"] for x in selected_h if len(x["statement"]) < 8 or len(x["falsificationBoundary"]) < 8]
    deviation_missing_rationale = [x["id"] for x in deviations if len(x["description"]) < 8 or len(x["rationale"]) < 8 or not x["declaredAt"]]
    latest_review = prereg["reviewHistory"][-1]["decision"] if prereg["reviewHistory"] else ""
    freeze_check = verify_freeze(payload) if freeze else {"ok": False, "reason": "missing-freeze"}

    reasons: list[str] = []
    if latest_review == "block":
        gate = "blocked"; reasons.append("Human preregistration review blocks interpretation.")
    elif not prereg["researchQuestionIds"] or not selected_q:
        gate = "needs-research-question"; reasons.append("At least one explicit research question must be registered.")
    elif missing_q or incomplete_q:
        gate = "research-question-incomplete"; reasons.append("Registered research questions must resolve and define population and outcome boundaries.")
    elif not prereg["hypothesisIds"] or not selected_h:
        gate = "needs-hypotheses"; reasons.append("At least one explicit hypothesis must be registered.")
    elif missing_h or incomplete_h:
        gate = "hypothesis-registry-incomplete"; reasons.append("Registered hypotheses must resolve and state a falsification boundary.")
    elif len(prereg["primaryOutcome"]) < 4:
        gate = "needs-primary-outcome"; reasons.append("A primary outcome must be declared before freeze.")
    elif len(prereg["analysisPlan"]) < 12:
        gate = "needs-analysis-plan"; reasons.append("A substantive analysis plan is required before freeze.")
    elif len(prereg["exclusionCriteria"]) < 4:
        gate = "needs-exclusion-rules"; reasons.append("Exclusion criteria, including an explicit none statement when appropriate, are required.")
    elif len(prereg["stoppingRule"]) < 4:
        gate = "needs-stopping-rule"; reasons.append("A stopping rule must be declared before freeze.")
    elif len(prereg["sampleSizeRationale"]) < 8:
        gate = "needs-sample-size-rationale"; reasons.append("A sample-size or information-size rationale is required.")
    elif prereg["resultsAccessState"] != "not-inspected" or len(prereg["preResultAttestation"]) < 12:
        gate = "pre-result-attestation-required"; reasons.append("The researcher must explicitly attest that results have not been inspected before freeze.")
    elif not freeze:
        gate = "needs-freeze"; reasons.append("The registered plan must be frozen before result interpretation.")
    elif not freeze_check.get("ok"):
        gate = "freeze-integrity-failure"; reasons.append("The frozen snapshot does not match the current registered plan or its hashes.")
    elif deviation_missing_rationale:
        gate = "needs-deviation-rationale"; reasons.append("Every post-freeze deviation requires a description, rationale, and declaration timestamp.")
    elif latest_review not in {"accept-within-scope", "accept-with-qualification"}:
        gate = "needs-review"; reasons.append("Human preregistration review is required after freeze and deviation logging.")
    elif latest_review == "accept-with-qualification":
        gate = "preregistration-bounded-with-qualification"; reasons.append("Human review accepted the frozen registration with stated qualifications.")
    elif deviations:
        gate = "preregistration-bounded-with-deviations"; reasons.append("The registration remains interpretable with explicit timestamped post-freeze deviations.")
    else:
        gate = "preregistration-bounded"; reasons.append("Human review accepted the frozen registration within its stated scope.")

    result = {
        "ok": True,
        "schema": EVALUATION_SCHEMA,
        "version": VERSION,
        "preregistration": prereg,
        "gate": gate,
        "reasons": reasons,
        "researchQuestionCount": len(selected_q),
        "hypothesisCount": len(selected_h),
        "deviationCount": len(deviations),
        "missingResearchQuestionIds": missing_q,
        "missingHypothesisIds": missing_h,
        "incompleteResearchQuestionIds": incomplete_q,
        "incompleteHypothesisIds": incomplete_h,
        "deviationsMissingRationale": deviation_missing_rationale,
        "freezeVerified": bool(freeze_check.get("ok")),
        "freezeHash": _text(freeze.get("freezeHash"), 64) if freeze else None,
        "latestHumanReview": latest_review or None,
        "humanReviewRequired": True,
        "preResultFreezeRequired": True,
        "automaticHypothesisValidation": False,
        "automaticPostHocPreregistration": False,
        "automaticOutcomeReclassification": False,
    }
    result["evaluationHash"] = _hash(result)
    return result


def build_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = evaluate(payload)
    prereg, questions, hypotheses, freeze, deviations = _select(payload)
    q_by_id = {x["id"]: x for x in questions}
    h_by_id = {x["id"]: x for x in hypotheses}
    packet = {
        "ok": True,
        "schema": PACKET_SCHEMA,
        "version": VERSION,
        "preregistrationId": prereg["id"],
        "preregistrationHash": prereg["preregistrationHash"],
        "gate": result["gate"],
        "evaluationHash": result["evaluationHash"],
        "freezeHash": _text(freeze.get("freezeHash"), 64) if freeze else "",
        "snapshotHash": _text(freeze.get("snapshotHash"), 64) if freeze else "",
        "researchQuestionHashes": [q_by_id[x]["questionHash"] for x in prereg["researchQuestionIds"] if x in q_by_id],
        "hypothesisHashes": [h_by_id[x]["hypothesisHash"] for x in prereg["hypothesisIds"] if x in h_by_id],
        "deviationHashes": [x["deviationHash"] for x in deviations],
        "reviewHashes": [x["reviewHash"] for x in prereg["reviewHistory"]],
        "primaryOutcomeHash": _hash(prereg["primaryOutcome"]),
        "analysisPlanHash": _hash(prereg["analysisPlan"]),
        "exclusionCriteriaHash": _hash(prereg["exclusionCriteria"]),
        "stoppingRuleHash": _hash(prereg["stoppingRule"]),
        "scopeBoundaryHash": _hash(prereg["scopeBoundary"]),
        "humanReviewRequired": True,
        "preResultFreezeRequired": True,
        "automaticPostHocPreregistration": False,
        "rawScientificDataIncluded": False,
    }
    packet["packetHash"] = _hash(packet)
    return packet


def verify_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) else None
    if not isinstance(packet, dict):
        raise PreregistrationError("Packet verification requires packet.")
    supplied = _text(packet.get("packetHash"), 64)
    body = deepcopy(packet)
    body.pop("packetHash", None)
    expected = _hash(body)
    return {"ok": supplied == expected, "version": VERSION, "packetHash": supplied, "expectedPacketHash": expected}
