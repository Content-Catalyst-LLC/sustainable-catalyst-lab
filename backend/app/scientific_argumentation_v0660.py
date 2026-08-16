from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .scientific_claims_traceability_v0620 import normalize_claim

VERSION = "0.66.0"
CASE_SCHEMA = "sc-lab-scientific-argumentation-case/0.66.0"
HYPOTHESIS_SCHEMA = "sc-lab-scientific-hypothesis/0.66.0"
EVIDENCE_LINK_SCHEMA = "sc-lab-hypothesis-evidence-link/0.66.0"
TEST_SCHEMA = "sc-lab-discriminating-test/0.66.0"
PACKET_SCHEMA = "sc-lab-scientific-argumentation-packet/0.66.0"
MAX_HYPOTHESES = 24
MAX_PREDICTIONS = 100
MAX_LINKS = 600
MAX_TESTS = 100
MAX_REVIEWS = 100
MAX_EVIDENCE = 1000

HYPOTHESIS_DECISIONS = {"retain", "provisionally-prefer", "reject", "block", "reopen"}
CASE_DECISIONS = {"accept-argument-map", "accept-with-unresolved-alternatives", "block", "reopen"}
EVIDENCE_RELATIONS = {
    "supports", "contradicts", "neutral", "contextualizes", "uncertainty",
    "falsifying-candidate", "discriminates-for", "discriminates-against",
}
PREDICTION_OUTCOMES = {"present", "absent", "increase", "decrease", "association", "no-effect", "custom"}
FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64", "individualdata", "participantdata",
}


class ScientificArgumentationError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, default: str = "") -> str:
    text = _text(value, 180)
    safe = "".join(ch for ch in text if ch.isalnum() or ch in "-_.:")
    return safe or default


def _ids(value: Any, limit: int = 100) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for raw in value[:limit]:
        item = _id(raw)
        if item and item not in out:
            out.append(item)
    return out


def _scan_forbidden(value: Any, path: str = "$") -> None:
    normalized_forbidden = {k.replace("_", "").replace("-", "") for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in normalized_forbidden:
                raise ScientificArgumentationError(
                    f"Scientific argumentation accepts governed metadata/evidence references only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "competingHypothesesSupported": True,
        "predictionsExplicit": True,
        "falsifyingEvidencePreserved": True,
        "discriminatingTestsExplicit": True,
        "unresolvedAlternativesPreserved": True,
        "humanHypothesisReviewRequired": True,
        "humanArgumentReviewRequired": True,
        "automaticHypothesisProofAuthorized": False,
        "automaticWinnerSelectionAuthorized": False,
        "automaticFalsificationAuthorized": False,
        "automaticCausalCertificationAuthorized": False,
        "numericTruthScoreAuthorized": False,
        "automaticPublicationAuthorized": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "rawScientificDataAccepted": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-argumentation-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "hypothesisReviewDecisions": sorted(HYPOTHESIS_DECISIONS),
        "caseReviewDecisions": sorted(CASE_DECISIONS),
        "evidenceRelations": sorted(EVIDENCE_RELATIONS),
        "humanHypothesisReviewRequired": True,
        "humanArgumentReviewRequired": True,
        "automaticHypothesisProof": False,
        "automaticWinnerSelection": False,
        "automaticFalsification": False,
        "numericTruthScore": False,
        "rawScientificDataAccepted": False,
        "arbitraryCode": False,
    }


def _review_history(value: Any, allowed: set[str], prefix: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(value[:MAX_REVIEWS]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 80).lower()
        if decision not in allowed:
            continue
        row = {
            "id": _id(raw.get("id"), f"{prefix}-review-{index + 1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 3000),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def _latest_decision(record: dict[str, Any]) -> str | None:
    rows = record.get("reviewHistory") if isinstance(record.get("reviewHistory"), list) else []
    return _text(rows[-1].get("decision"), 80).lower() if rows else None


def normalize_case(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    case = {
        "schema": CASE_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "argument-case-1"),
        "title": _text(raw.get("title") or "Competing hypotheses", 600),
        "researchQuestion": _text(raw.get("researchQuestion"), 5000),
        "claimIds": _ids(raw.get("claimIds"), 100),
        "evidenceBoundaryAssessmentIds": _ids(raw.get("evidenceBoundaryAssessmentIds"), 100),
        "scopeNote": _text(raw.get("scopeNote"), 4000),
        "decisionBoundary": _text(raw.get("decisionBoundary"), 4000),
        "reviewHistory": _review_history(raw.get("reviewHistory"), CASE_DECISIONS, _id(raw.get("id"), "argument-case-1")),
    }
    case["caseHash"] = _hash(case)
    return case


def _prediction(raw: dict[str, Any], index: int) -> dict[str, Any]:
    _scan_forbidden(raw)
    expected = _text(raw.get("expectedOutcome"), 80).lower() or "custom"
    if expected not in PREDICTION_OUTCOMES:
        expected = "custom"
    row = {
        "id": _id(raw.get("id"), f"prediction-{index + 1}"),
        "statement": _text(raw.get("statement"), 3000),
        "expectedOutcome": expected,
        "testId": _id(raw.get("testId")),
        "boundaryNote": _text(raw.get("boundaryNote"), 2000),
    }
    row["predictionHash"] = _hash(row)
    return row


def normalize_hypothesis(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    hypothesis_id = _id(raw.get("id"), "hypothesis-1")
    predictions = []
    if isinstance(raw.get("predictions"), list):
        predictions = [_prediction(x, i) for i, x in enumerate(raw["predictions"][:MAX_PREDICTIONS]) if isinstance(x, dict)]
    hypothesis = {
        "schema": HYPOTHESIS_SCHEMA,
        "version": VERSION,
        "id": hypothesis_id,
        "title": _text(raw.get("title") or hypothesis_id, 600),
        "statement": _text(raw.get("statement"), 5000),
        "mechanism": _text(raw.get("mechanism"), 5000),
        "linkedClaimIds": _ids(raw.get("linkedClaimIds"), 100),
        "scopeNote": _text(raw.get("scopeNote"), 3000),
        "predictions": predictions,
        "reviewHistory": _review_history(raw.get("reviewHistory"), HYPOTHESIS_DECISIONS, hypothesis_id),
    }
    hypothesis["hypothesisHash"] = _hash(hypothesis)
    return hypothesis


def normalize_evidence_link(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    relation = _text(raw.get("relation"), 80).lower()
    if relation not in EVIDENCE_RELATIONS:
        raise ScientificArgumentationError("Evidence relation must be a registered v0.66 argumentation relation.")
    link = {
        "schema": EVIDENCE_LINK_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "argument-evidence-1"),
        "hypothesisId": _id(raw.get("hypothesisId")),
        "evidenceRef": _id(raw.get("evidenceRef")),
        "relation": relation,
        "predictionId": _id(raw.get("predictionId")),
        "testId": _id(raw.get("testId")),
        "note": _text(raw.get("note"), 3000),
    }
    if not link["hypothesisId"] or not link["evidenceRef"]:
        raise ScientificArgumentationError("Hypothesis evidence links require hypothesisId and evidenceRef.")
    link["linkHash"] = _hash(link)
    return link


def normalize_discriminating_test(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    expectations = []
    for index, item in enumerate((raw.get("expectations") or [])[:MAX_HYPOTHESES] if isinstance(raw.get("expectations"), list) else []):
        if not isinstance(item, dict):
            continue
        expected = _text(item.get("expectedOutcome"), 80).lower() or "custom"
        if expected not in PREDICTION_OUTCOMES:
            expected = "custom"
        expectations.append({
            "hypothesisId": _id(item.get("hypothesisId")),
            "expectedOutcome": expected,
            "predictionId": _id(item.get("predictionId")),
            "note": _text(item.get("note"), 1600),
        })
    test = {
        "schema": TEST_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "discriminating-test-1"),
        "title": _text(raw.get("title") or "Discriminating test", 600),
        "methodRef": _id(raw.get("methodRef")),
        "evidenceRef": _id(raw.get("evidenceRef")),
        "expectations": expectations,
        "status": _text(raw.get("status") or "planned", 80).lower(),
        "limitations": _text(raw.get("limitations"), 3000),
    }
    test["testHash"] = _hash(test)
    return test


def record_hypothesis_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificArgumentationError("Hypothesis review requires hypothesis and review metadata.")
    hypothesis = normalize_hypothesis(payload.get("hypothesis") if isinstance(payload.get("hypothesis"), dict) else {})
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 80).lower()
    if decision not in HYPOTHESIS_DECISIONS:
        raise ScientificArgumentationError("Hypothesis review decision is not recognized.")
    rationale = _text(review.get("rationale"), 3000)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificArgumentationError("Hypothesis review decisions require a rationale.")
    row = {
        "id": _id(review.get("id"), f"{hypothesis['id']}-review-{len(hypothesis['reviewHistory']) + 1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
    }
    row["reviewHash"] = _hash(row)
    base = deepcopy(hypothesis); base.pop("hypothesisHash", None); base["reviewHistory"] = [*hypothesis["reviewHistory"], row]
    return {"ok": True, "version": VERSION, "review": row, "hypothesis": normalize_hypothesis(base)}


def record_case_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificArgumentationError("Argument review requires case and review metadata.")
    case = normalize_case(payload.get("case") if isinstance(payload.get("case"), dict) else {})
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 80).lower()
    if decision not in CASE_DECISIONS:
        raise ScientificArgumentationError("Argument review decision is not recognized.")
    rationale = _text(review.get("rationale"), 3000)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificArgumentationError("Argument review decisions require a rationale.")
    if decision == "accept-with-unresolved-alternatives" and len(case.get("decisionBoundary") or "") < 10:
        raise ScientificArgumentationError("Unresolved-alternative acceptance requires an explicit decision boundary.")
    row = {
        "id": _id(review.get("id"), f"{case['id']}-review-{len(case['reviewHistory']) + 1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
    }
    row["reviewHash"] = _hash(row)
    base = deepcopy(case); base.pop("caseHash", None); base["reviewHistory"] = [*case["reviewHistory"], row]
    return {"ok": True, "version": VERSION, "review": row, "case": normalize_case(base)}


def _catalog(raw: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for item in raw[:MAX_EVIDENCE]:
        if not isinstance(item, dict):
            continue
        _scan_forbidden(item)
        evidence_id = _id(item.get("id"))
        if not evidence_id:
            continue
        out[evidence_id] = {
            "id": evidence_id,
            "type": _text(item.get("type"), 100),
            "hash": _text(item.get("hash"), 64).lower(),
            "gate": _text(item.get("gate"), 80).lower(),
            "claimIds": _ids(item.get("claimIds"), 100),
        }
    return out


def evaluate_argumentation(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificArgumentationError("Scientific argumentation requires a case, hypotheses, evidence links, and discriminating tests.")
    _scan_forbidden({k: v for k, v in payload.items() if k not in {"case", "hypotheses", "evidenceLinks", "tests", "evidenceCatalog", "claims"}})
    case = normalize_case(payload.get("case") if isinstance(payload.get("case"), dict) else {})
    hypotheses = [normalize_hypothesis(x) for x in (payload.get("hypotheses") or [])[:MAX_HYPOTHESES] if isinstance(x, dict)] if isinstance(payload.get("hypotheses"), list) else []
    links = [normalize_evidence_link(x) for x in (payload.get("evidenceLinks") or [])[:MAX_LINKS] if isinstance(x, dict)] if isinstance(payload.get("evidenceLinks"), list) else []
    tests = [normalize_discriminating_test(x) for x in (payload.get("tests") or [])[:MAX_TESTS] if isinstance(x, dict)] if isinstance(payload.get("tests"), list) else []
    claims = [normalize_claim(x) for x in (payload.get("claims") or [])[:100] if isinstance(x, dict)] if isinstance(payload.get("claims"), list) else []
    evidence = _catalog(payload.get("evidenceCatalog"))

    h_by_id = {h["id"]: h for h in hypotheses}
    claim_ids = {c["id"] for c in claims}
    unresolved_case_claims = sorted(cid for cid in case["claimIds"] if cid not in claim_ids)
    unresolved_links = sorted({link["evidenceRef"] for link in links if link["evidenceRef"] not in evidence})
    unresolved_hypothesis_links = sorted({link["hypothesisId"] for link in links if link["hypothesisId"] not in h_by_id})

    test_rows = []
    discriminating_test_count = 0
    for test in tests:
        hids = [x.get("hypothesisId") for x in test["expectations"] if x.get("hypothesisId") in h_by_id]
        unique_hids = sorted(set(hids))
        distinct_outcomes = {x.get("expectedOutcome") for x in test["expectations"] if x.get("hypothesisId") in h_by_id}
        discriminates = len(unique_hids) >= 2 and len(distinct_outcomes) >= 2
        if discriminates:
            discriminating_test_count += 1
        row = {
            "testId": test["id"],
            "hypothesisIds": unique_hids,
            "distinctExpectedOutcomes": sorted(distinct_outcomes),
            "discriminates": discriminates,
            "status": test["status"],
            "evidenceRef": test["evidenceRef"],
            "testHash": test["testHash"],
        }
        row["assessmentHash"] = _hash(row)
        test_rows.append(row)

    hypothesis_rows = []
    for h in hypotheses:
        hlinks = [x for x in links if x["hypothesisId"] == h["id"]]
        resolved = [x for x in hlinks if x["evidenceRef"] in evidence]
        counts = {relation: sum(1 for x in resolved if x["relation"] == relation) for relation in sorted(EVIDENCE_RELATIONS)}
        falsification_challenge = counts["falsifying-candidate"] + counts["discriminates-against"] > 0
        decision = _latest_decision(h)
        if decision in {"block", "reject"}:
            state = "human-rejected"
        elif falsification_challenge and decision not in {"retain", "provisionally-prefer"}:
            state = "falsification-challenge"
        elif not h["predictions"]:
            state = "needs-predictions"
        elif not resolved:
            state = "needs-evidence"
        elif decision is None or decision == "reopen":
            state = "needs-review"
        elif decision == "provisionally-prefer":
            state = "provisionally-preferred"
        else:
            state = "retained"
        row = {
            "hypothesisId": h["id"],
            "hypothesisHash": h["hypothesisHash"],
            "decision": decision,
            "state": state,
            "predictionCount": len(h["predictions"]),
            "linkedClaimIds": h["linkedClaimIds"],
            "unresolvedClaimIds": sorted(cid for cid in h["linkedClaimIds"] if cid not in claim_ids),
            "resolvedEvidenceCount": len(resolved),
            "unresolvedEvidenceRefs": sorted({x["evidenceRef"] for x in hlinks if x["evidenceRef"] not in evidence}),
            "supportCount": counts["supports"] + counts["discriminates-for"],
            "contradictionCount": counts["contradicts"] + counts["discriminates-against"],
            "falsifyingChallengeCount": counts["falsifying-candidate"] + counts["discriminates-against"],
            "uncertaintyCount": counts["uncertainty"],
            "neutralContextCount": counts["neutral"] + counts["contextualizes"],
            "falsificationChallenge": falsification_challenge,
            "humanReviewRequired": True,
            "automaticProof": False,
            "automaticFalsification": False,
        }
        row["argumentHash"] = _hash(row)
        hypothesis_rows.append(row)

    active_rows = [r for r in hypothesis_rows if r["state"] != "human-rejected"]
    provisionally_preferred = [r for r in hypothesis_rows if r["decision"] == "provisionally-prefer" and r["state"] != "human-rejected"]
    unresolved_alternatives = len(active_rows) > 1
    latest_case_decision = _latest_decision(case)
    any_missing_predictions = any(r["predictionCount"] == 0 for r in active_rows)
    any_unresolved = bool(unresolved_links or unresolved_hypothesis_links or unresolved_case_claims or any(r["unresolvedClaimIds"] for r in hypothesis_rows))
    any_falsification_challenge = any(r["falsificationChallenge"] and r["decision"] not in {"retain", "provisionally-prefer", "reject", "block"} for r in hypothesis_rows)
    all_active_reviewed = bool(active_rows) and all(r["decision"] in {"retain", "provisionally-prefer"} for r in active_rows)

    if latest_case_decision == "block":
        gate = "blocked"
    elif len(hypotheses) < 2:
        gate = "needs-alternatives"
    elif any_missing_predictions:
        gate = "needs-predictions"
    elif discriminating_test_count == 0:
        gate = "needs-discriminating-test"
    elif any_unresolved or not links:
        gate = "needs-evidence"
    elif any_falsification_challenge:
        gate = "falsification-challenge"
    elif not all_active_reviewed:
        gate = "needs-review"
    elif unresolved_alternatives:
        if latest_case_decision == "accept-with-unresolved-alternatives" and len(case["decisionBoundary"]) >= 10:
            gate = "argument-bounded-with-unresolved-alternatives"
        elif len(provisionally_preferred) == 1 and latest_case_decision == "accept-argument-map":
            gate = "provisional-preference-reviewed"
        else:
            gate = "alternatives-unresolved"
    elif latest_case_decision == "accept-argument-map":
        gate = "argument-bounded"
    else:
        gate = "needs-review"

    result = {
        "ok": True,
        "version": VERSION,
        "case": case,
        "gate": gate,
        "hypothesisRows": hypothesis_rows,
        "discriminatingTests": test_rows,
        "unresolvedEvidenceRefs": unresolved_links,
        "unresolvedHypothesisIds": unresolved_hypothesis_links,
        "unresolvedCaseClaimIds": unresolved_case_claims,
        "activeHypothesisIds": [r["hypothesisId"] for r in active_rows],
        "provisionallyPreferredHypothesisIds": [r["hypothesisId"] for r in provisionally_preferred],
        "unresolvedAlternatives": unresolved_alternatives,
        "discriminatingTestCount": discriminating_test_count,
        "humanHypothesisReviewRequired": True,
        "humanArgumentReviewDecision": latest_case_decision,
        "automaticHypothesisProof": False,
        "automaticWinnerSelection": False,
        "automaticFalsification": False,
        "numericTruthScore": None,
        "boundaries": policies(),
    }
    result["evaluationHash"] = _hash(result)
    return result


def build_argumentation_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_argumentation(payload)
    packet = {
        "ok": True,
        "version": VERSION,
        "schema": PACKET_SCHEMA,
        "caseId": result["case"]["id"],
        "caseHash": result["case"]["caseHash"],
        "gate": result["gate"],
        "evaluationHash": result["evaluationHash"],
        "hypotheses": [
            {
                "hypothesisId": r["hypothesisId"],
                "hypothesisHash": r["hypothesisHash"],
                "decision": r["decision"],
                "state": r["state"],
                "predictionCount": r["predictionCount"],
                "resolvedEvidenceCount": r["resolvedEvidenceCount"],
                "supportCount": r["supportCount"],
                "contradictionCount": r["contradictionCount"],
                "falsifyingChallengeCount": r["falsifyingChallengeCount"],
                "argumentHash": r["argumentHash"],
            }
            for r in result["hypothesisRows"]
        ],
        "discriminatingTests": result["discriminatingTests"],
        "activeHypothesisIds": result["activeHypothesisIds"],
        "provisionallyPreferredHypothesisIds": result["provisionallyPreferredHypothesisIds"],
        "unresolvedAlternatives": result["unresolvedAlternatives"],
        "unresolvedEvidenceRefs": result["unresolvedEvidenceRefs"],
        "humanArgumentReviewDecision": result["humanArgumentReviewDecision"],
        "boundaries": result["boundaries"],
    }
    packet["packetHash"] = _hash(packet)
    return packet


def verify_argumentation_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) and isinstance(payload.get("packet"), dict) else payload
    if not isinstance(packet, dict):
        raise ScientificArgumentationError("Packet verification requires a scientific argumentation packet.")
    supplied = _text(packet.get("packetHash"), 64).lower()
    base = deepcopy(packet); base.pop("packetHash", None)
    expected = _hash(base)
    return {"ok": supplied == expected, "version": VERSION, "schema": packet.get("schema"), "suppliedHash": supplied, "expectedHash": expected}
