from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .scientific_study_lifecycle_v0610 import normalize_study

VERSION = "0.62.0"
CLAIM_SCHEMA = "sc-lab-scientific-claim/0.62.0"
CONCLUSION_SCHEMA = "sc-lab-scientific-conclusion/0.62.0"
MATRIX_SCHEMA = "sc-lab-scientific-evidence-matrix/0.62.0"
REVIEW_SCHEMA = "sc-lab-scientific-claim-review/0.62.0"
PACKET_SCHEMA = "sc-lab-conclusion-traceability-packet/0.62.0"
MAX_CLAIMS = 100
MAX_CONCLUSIONS = 40
MAX_EVIDENCE_LINKS = 400
MAX_REVIEW_ROWS = 250
MAX_PROJECT_EVIDENCE = 600

CLAIM_TYPES = {
    "descriptive", "associational", "comparative", "predictive",
    "mechanistic", "causal", "methodological", "null",
}
CLAIM_STATUSES = {"draft", "active", "withdrawn", "superseded"}
EVIDENCE_ROLES = {"supports", "contradicts", "contextualizes", "validates", "uncertainty", "limitation"}
SOURCE_TYPES = {
    "dataset", "analysis", "model", "experiment", "figure", "workflow",
    "reproducibility", "audit", "study", "external-reference",
}
CLAIM_REVIEW_DECISIONS = {"accept", "accept-with-qualification", "block", "reject", "reopen"}
CONCLUSION_REVIEW_DECISIONS = {"accept", "block", "reopen"}
FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code",
}


class ScientificClaimsTraceabilityError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, default: str = "") -> str:
    text = _text(value, 160)
    safe = "".join(ch for ch in text if ch.isalnum() or ch in "-_.:")
    return safe or default


def _hex_hash(value: Any) -> str:
    text = _text(value, 64).lower()
    return text if len(text) == 64 and all(ch in "0123456789abcdef" for ch in text) else ""


def _refs(value: Any, limit: int = MAX_EVIDENCE_LINKS) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:limit]:
        text = _text(item, 180)
        if text:
            out.append(text)
    return sorted(set(out))


def _scan_forbidden(value: Any, path: str = "$") -> None:
    normalized_forbidden = {k.replace("_", "").replace("-", "") for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in normalized_forbidden:
                raise ScientificClaimsTraceabilityError(
                    f"Claims traceability accepts governed metadata/evidence references only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "scientificClaimsEvidenceMatrix": True,
        "conclusionTraceability": True,
        "explicitEvidenceLinkingRequired": True,
        "contradictingEvidencePreserved": True,
        "uncertaintyAndLimitationsPreserved": True,
        "humanClaimReviewRequired": True,
        "humanConclusionReviewRequired": True,
        "automaticClaimInferenceAuthorized": False,
        "automaticScientificCertificationAuthorized": False,
        "automaticCausalClaimAuthorized": False,
        "automaticConclusionGenerationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "rawScientificDataAccepted": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-claims-traceability-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "claimTypes": sorted(CLAIM_TYPES),
        "evidenceRoles": sorted(EVIDENCE_ROLES),
        "sourceTypes": sorted(SOURCE_TYPES),
        "humanClaimReviewRequired": True,
        "humanConclusionReviewRequired": True,
        "automaticClaimInference": False,
        "automaticCausalClaim": False,
        "automaticConclusionGeneration": False,
        "automaticPublication": False,
        "arbitraryCode": False,
    }


def _normalize_review_rows(value: Any, allowed: set[str], prefix: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(value[:MAX_REVIEW_ROWS]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 40).lower()
        if decision not in allowed:
            continue
        row = {
            "id": _id(raw.get("id"), f"{prefix}-review-{index+1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 1800),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
            "evidenceRefs": _refs(raw.get("evidenceRefs"), 80),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def _normalize_evidence_links(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(value[:MAX_EVIDENCE_LINKS]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        role = _text(raw.get("role"), 40).lower()
        source_type = _text(raw.get("sourceType"), 40).lower()
        ref = _id(raw.get("ref"))
        if role not in EVIDENCE_ROLES or source_type not in SOURCE_TYPES or not ref:
            continue
        row = {
            "id": _id(raw.get("id"), f"evidence-link-{index+1}"),
            "role": role,
            "sourceType": source_type,
            "ref": ref,
            "hash": _hex_hash(raw.get("hash")),
            "note": _text(raw.get("note"), 1000),
        }
        row["linkHash"] = _hash(row)
        out.append(row)
    return out


def normalize_claim(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    _scan_forbidden(source)
    claim_type = _text(source.get("claimType") or "descriptive", 40).lower()
    if claim_type not in CLAIM_TYPES:
        raise ScientificClaimsTraceabilityError(f"Unsupported scientific claim type: {claim_type}")
    status = _text(source.get("status") or "draft", 40).lower()
    if status not in CLAIM_STATUSES:
        raise ScientificClaimsTraceabilityError(f"Unsupported scientific claim status: {status}")
    claim = {
        "schema": CLAIM_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), "claim-1"),
        "studyId": _id(source.get("studyId"), "study-active-project"),
        "statement": _text(source.get("statement"), 4000),
        "claimType": claim_type,
        "status": status,
        "scopeNote": _text(source.get("scopeNote"), 2400),
        "evidenceLinks": _normalize_evidence_links(source.get("evidenceLinks")),
        "conclusionIds": _refs(source.get("conclusionIds"), 80),
        "reviewHistory": _normalize_review_rows(source.get("reviewHistory"), CLAIM_REVIEW_DECISIONS, _id(source.get("id"), "claim")),
    }
    claim["claimHash"] = _hash(claim)
    return claim


def normalize_conclusion(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    _scan_forbidden(source)
    conclusion = {
        "schema": CONCLUSION_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), "conclusion-1"),
        "studyId": _id(source.get("studyId"), "study-active-project"),
        "statement": _text(source.get("statement"), 5000),
        "claimIds": _refs(source.get("claimIds"), 100),
        "limitationRefs": _refs(source.get("limitationRefs"), 100),
        "caveats": _text(source.get("caveats"), 3000),
        "reviewHistory": _normalize_review_rows(source.get("reviewHistory"), CONCLUSION_REVIEW_DECISIONS, _id(source.get("id"), "conclusion")),
    }
    conclusion["conclusionHash"] = _hash(conclusion)
    return conclusion


def record_claim_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificClaimsTraceabilityError("Claim review requires a claim and review record.")
    claim = normalize_claim(payload.get("claim") if isinstance(payload.get("claim"), dict) else {})
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 40).lower()
    if decision not in CLAIM_REVIEW_DECISIONS:
        raise ScientificClaimsTraceabilityError("Claim review decision must be accept, accept-with-qualification, block, reject, or reopen.")
    rationale = _text(review.get("rationale"), 1800)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificClaimsTraceabilityError("Claim review decisions require a review rationale.")
    row = {
        "id": _id(review.get("id"), f"{claim['id']}-review-{len(claim['reviewHistory'])+1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
        "evidenceRefs": _refs(review.get("evidenceRefs"), 80),
    }
    row["reviewHash"] = _hash(row)
    source = deepcopy(claim); source.pop("claimHash", None); source["reviewHistory"] = [*claim["reviewHistory"], row]
    return {"ok": True, "schema": REVIEW_SCHEMA, "version": VERSION, "review": row, "claim": normalize_claim(source)}


def record_conclusion_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificClaimsTraceabilityError("Conclusion review requires a conclusion and review record.")
    conclusion = normalize_conclusion(payload.get("conclusion") if isinstance(payload.get("conclusion"), dict) else {})
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 40).lower()
    if decision not in CONCLUSION_REVIEW_DECISIONS:
        raise ScientificClaimsTraceabilityError("Conclusion review decision must be accept, block, or reopen.")
    rationale = _text(review.get("rationale"), 1800)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificClaimsTraceabilityError("Conclusion review decisions require a review rationale.")
    row = {
        "id": _id(review.get("id"), f"{conclusion['id']}-review-{len(conclusion['reviewHistory'])+1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
        "evidenceRefs": _refs(review.get("evidenceRefs"), 80),
    }
    row["reviewHash"] = _hash(row)
    source = deepcopy(conclusion); source.pop("conclusionHash", None); source["reviewHistory"] = [*conclusion["reviewHistory"], row]
    return {"ok": True, "version": VERSION, "review": row, "conclusion": normalize_conclusion(source)}


def _normalize_project_evidence(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    _scan_forbidden(source)
    catalog = []
    for index, raw in enumerate(source.get("evidenceCatalog", [])[:MAX_PROJECT_EVIDENCE] if isinstance(source.get("evidenceCatalog"), list) else []):
        if not isinstance(raw, dict):
            continue
        source_type = _text(raw.get("sourceType"), 40).lower()
        ref = _id(raw.get("ref"))
        if source_type not in SOURCE_TYPES or not ref:
            continue
        catalog.append({
            "ref": ref,
            "sourceType": source_type,
            "hash": _hex_hash(raw.get("hash")),
            "title": _text(raw.get("title"), 220),
        })
    project = {
        "id": _id(source.get("id"), "active-project"),
        "studyId": _id(source.get("studyId"), "study-active-project"),
        "evidenceCatalog": catalog,
    }
    project["projectEvidenceHash"] = _hash(project)
    return project


def _latest_review(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[-1] if rows else None


def evaluate_matrix(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificClaimsTraceabilityError("Evidence matrix evaluation requires study, claims, conclusions, and project evidence metadata.")
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else {})
    project = _normalize_project_evidence(payload.get("project") if isinstance(payload.get("project"), dict) else {})
    claims = [normalize_claim(row) for row in (payload.get("claims") or [])[:MAX_CLAIMS] if isinstance(row, dict)] if isinstance(payload.get("claims"), list) else []
    conclusions = [normalize_conclusion(row) for row in (payload.get("conclusions") or [])[:MAX_CONCLUSIONS] if isinstance(row, dict)] if isinstance(payload.get("conclusions"), list) else []
    catalog_refs = {row["ref"]: row for row in project["evidenceCatalog"]}
    claim_ids = {row["id"] for row in claims}
    conclusion_ids = {row["id"] for row in conclusions}

    claim_rows = []
    blocked_claims: list[str] = []
    contested_claims: list[str] = []
    missing_evidence_claims: list[str] = []
    pending_claim_review: list[str] = []
    traceable_claims: list[str] = []
    for claim in claims:
        active_links = claim["evidenceLinks"]
        supports = [x for x in active_links if x["role"] == "supports"]
        primary_support = [x for x in supports if x["sourceType"] != "figure"]
        contradictions = [x for x in active_links if x["role"] == "contradicts"]
        uncertainty = [x for x in active_links if x["role"] in {"uncertainty", "limitation"}]
        unresolved = [x["ref"] for x in active_links if x["sourceType"] != "external-reference" and x["ref"] not in catalog_refs]
        review = _latest_review(claim["reviewHistory"])
        decision = review.get("decision") if review else ""
        causal_design_block = claim["claimType"] == "causal" and study["studyType"] not in {"experimental", "mixed"}
        rejected = decision == "reject"
        blocked = decision == "block" or causal_design_block
        evidence_ok = bool(primary_support) and not unresolved
        context_required = claim["claimType"] != "methodological"
        context_ok = bool(uncertainty) or not context_required
        qualified = decision == "accept-with-qualification"
        accepted = decision in {"accept", "accept-with-qualification"}

        if rejected:
            gate = "rejected"
            blocked_claims.append(claim["id"])
        elif blocked:
            gate = "blocked"
            blocked_claims.append(claim["id"])
        elif not evidence_ok:
            gate = "needs-evidence"
            missing_evidence_claims.append(claim["id"])
        elif not context_ok:
            gate = "needs-context"
            missing_evidence_claims.append(claim["id"])
        elif contradictions and not qualified:
            gate = "contested"
            contested_claims.append(claim["id"])
            pending_claim_review.append(claim["id"])
        elif not accepted:
            gate = "needs-review"
            pending_claim_review.append(claim["id"])
        else:
            gate = "traceable"
            traceable_claims.append(claim["id"])

        used_by = sorted({c["id"] for c in conclusions if claim["id"] in c["claimIds"]})
        claim_rows.append({
            "claimId": claim["id"], "claimHash": claim["claimHash"], "claimType": claim["claimType"],
            "statement": claim["statement"], "gate": gate, "supportCount": len(supports),
            "primarySupportCount": len(primary_support), "contradictionCount": len(contradictions),
            "uncertaintyLimitationCount": len(uncertainty), "unresolvedEvidenceRefs": sorted(set(unresolved)),
            "reviewDecision": decision or None, "reviewHash": review.get("reviewHash") if review else None,
            "conclusionIds": used_by, "causalDesignCompatible": not causal_design_block,
            "automaticScientificValidityClaim": False,
        })

    claim_gate = {row["claimId"]: row["gate"] for row in claim_rows}
    conclusion_rows = []
    blocked_conclusions: list[str] = []
    missing_trace_conclusions: list[str] = []
    pending_conclusion_review: list[str] = []
    traceable_conclusions: list[str] = []
    for conclusion in conclusions:
        unknown_claims = [cid for cid in conclusion["claimIds"] if cid not in claim_ids]
        linked_gates = [claim_gate.get(cid, "missing") for cid in conclusion["claimIds"]]
        review = _latest_review(conclusion["reviewHistory"])
        decision = review.get("decision") if review else ""
        blocked = decision == "block" or any(g in {"blocked", "rejected"} for g in linked_gates)
        trace_missing = not conclusion["claimIds"] or bool(unknown_claims) or any(g in {"needs-evidence", "needs-context"} for g in linked_gates)
        claim_review_pending = any(g in {"needs-review", "contested"} for g in linked_gates)
        context_missing = not (conclusion["caveats"] or conclusion["limitationRefs"])
        accepted = decision == "accept"
        if blocked:
            gate = "blocked"; blocked_conclusions.append(conclusion["id"])
        elif trace_missing or context_missing:
            gate = "needs-trace"; missing_trace_conclusions.append(conclusion["id"])
        elif claim_review_pending or not accepted:
            gate = "needs-review"; pending_conclusion_review.append(conclusion["id"])
        else:
            gate = "traceable"; traceable_conclusions.append(conclusion["id"])
        conclusion_rows.append({
            "conclusionId": conclusion["id"], "conclusionHash": conclusion["conclusionHash"],
            "statement": conclusion["statement"], "claimIds": conclusion["claimIds"],
            "unknownClaimIds": unknown_claims, "linkedClaimGates": linked_gates,
            "limitationRefs": conclusion["limitationRefs"], "hasCaveats": bool(conclusion["caveats"]),
            "reviewDecision": decision or None, "reviewHash": review.get("reviewHash") if review else None,
            "gate": gate, "automaticConclusionClaim": False,
        })

    orphan_claims = sorted(claim_ids - {cid for c in conclusions for cid in c["claimIds"]})
    unknown_conclusion_ids = sorted({cid for claim in claims for cid in claim["conclusionIds"] if cid not in conclusion_ids})
    if blocked_claims or blocked_conclusions:
        gate = "blocked"
    elif missing_evidence_claims or missing_trace_conclusions:
        gate = "needs-evidence"
    elif contested_claims:
        gate = "contested"
    elif pending_claim_review or pending_conclusion_review:
        gate = "needs-review"
    elif not claims or not conclusions:
        gate = "needs-evidence"
    else:
        gate = "traceable"

    core = {
        "schema": MATRIX_SCHEMA, "version": VERSION, "studyId": study["id"], "studyHash": study["studyHash"],
        "projectEvidenceHash": project["projectEvidenceHash"], "gate": gate, "claimRows": claim_rows,
        "conclusionRows": conclusion_rows, "orphanClaimIds": orphan_claims,
        "unknownConclusionIds": unknown_conclusion_ids, "blockedClaimIds": sorted(set(blocked_claims)),
        "contestedClaimIds": sorted(set(contested_claims)), "missingEvidenceClaimIds": sorted(set(missing_evidence_claims)),
        "pendingClaimReviewIds": sorted(set(pending_claim_review)), "blockedConclusionIds": sorted(set(blocked_conclusions)),
        "missingTraceConclusionIds": sorted(set(missing_trace_conclusions)),
        "pendingConclusionReviewIds": sorted(set(pending_conclusion_review)),
        "traceableClaimIds": sorted(set(traceable_claims)), "traceableConclusionIds": sorted(set(traceable_conclusions)),
        "humanReviewRequired": True, "scientificCertificationClaim": False, "causalValidityClaim": False,
    }
    core["matrixHash"] = _hash(core)
    return {"ok": gate != "blocked", **core}


def build_traceability_packet(payload: dict[str, Any]) -> dict[str, Any]:
    matrix = evaluate_matrix(payload)
    claims = [normalize_claim(row) for row in (payload.get("claims") or [])[:MAX_CLAIMS] if isinstance(row, dict)] if isinstance(payload.get("claims"), list) else []
    conclusions = [normalize_conclusion(row) for row in (payload.get("conclusions") or [])[:MAX_CONCLUSIONS] if isinstance(row, dict)] if isinstance(payload.get("conclusions"), list) else []
    packet = {
        "schema": PACKET_SCHEMA, "version": VERSION, "studyId": matrix["studyId"], "studyHash": matrix["studyHash"],
        "projectEvidenceHash": matrix["projectEvidenceHash"], "matrixHash": matrix["matrixHash"], "gate": matrix["gate"],
        "claimHashes": {row["id"]: row["claimHash"] for row in claims},
        "conclusionHashes": {row["id"]: row["conclusionHash"] for row in conclusions},
        "claimGates": {row["claimId"]: row["gate"] for row in matrix["claimRows"]},
        "conclusionGates": {row["conclusionId"]: row["gate"] for row in matrix["conclusionRows"]},
        "traceableClaimIds": matrix["traceableClaimIds"], "traceableConclusionIds": matrix["traceableConclusionIds"],
        "contestedClaimIds": matrix["contestedClaimIds"], "orphanClaimIds": matrix["orphanClaimIds"],
        "boundaries": {
            "rawScientificDataIncluded": False, "credentialsIncluded": False,
            "automaticClaimInference": False, "automaticScientificCertification": False,
            "automaticCausalClaim": False, "automaticConclusionGeneration": False,
            "automaticPublication": False, "humanClaimReviewRequired": True,
            "humanConclusionReviewRequired": True, "contradictingEvidencePreserved": True,
        },
    }
    packet["packetHash"] = _hash(packet)
    return {"ok": True, "packet": packet, "matrix": matrix}


def verify_traceability_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) and isinstance(payload.get("packet"), dict) else {}
    expected = _text(packet.get("packetHash"), 64).lower()
    core = deepcopy(packet); core.pop("packetHash", None)
    actual = _hash(core)
    valid = len(expected) == 64 and expected == actual and packet.get("schema") == PACKET_SCHEMA and packet.get("version") == VERSION
    return {"ok": valid, "version": VERSION, "expectedHash": expected, "actualHash": actual, "tampered": not valid}
