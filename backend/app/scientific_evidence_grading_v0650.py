from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .scientific_claims_traceability_v0620 import normalize_claim
from .scientific_literature_provenance_v0630 import normalize_claim_link, normalize_source

VERSION = "0.65.0"
ASSESSMENT_SCHEMA = "sc-lab-scientific-evidence-grading-assessment/0.65.0"
GRADE_SCHEMA = "sc-lab-scientific-evidence-grade/0.65.0"
CONTRADICTION_SCHEMA = "sc-lab-scientific-contradiction-analysis/0.65.0"
CONSENSUS_SCHEMA = "sc-lab-scientific-consensus-boundary/0.65.0"
PACKET_SCHEMA = "sc-lab-scientific-evidence-consensus-packet/0.65.0"
MAX_CLAIMS = 100
MAX_SOURCES = 500
MAX_LINKS = 1000
MAX_SYNTHESES = 100
MAX_REVIEWS = 100

REVIEW_DECISIONS = {"accept-boundary", "accept-with-qualification", "block", "reopen"}
EVIDENCE_GRADES = {"insufficient", "limited", "moderate", "substantial", "contested"}
FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64", "individualdata", "participantdata",
}


class ScientificEvidenceGradingError(ValueError):
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


def _ids(value: Any, limit: int = MAX_CLAIMS) -> list[str]:
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
                raise ScientificEvidenceGradingError(
                    f"Evidence grading accepts governed metadata/evidence summaries only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "transparentRuleBasedEvidenceGrading": True,
        "contradictionAnalysis": True,
        "consensusBoundaryAssessment": True,
        "replicationDisagreementPreserved": True,
        "heterogeneityPreserved": True,
        "sourceCautionPreserved": True,
        "humanBoundaryReviewRequired": True,
        "numericTruthScoreAuthorized": False,
        "automaticConsensusCertificationAuthorized": False,
        "automaticStudyQualityScoringAuthorized": False,
        "citationCountAuthorityScoringAuthorized": False,
        "journalPrestigeScoringAuthorized": False,
        "automaticCausalCertificationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "rawScientificDataAccepted": False,
        "rawFullTextAccepted": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-evidence-grading-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "evidenceGrades": sorted(EVIDENCE_GRADES),
        "reviewDecisions": sorted(REVIEW_DECISIONS),
        "humanBoundaryReviewRequired": True,
        "numericTruthScore": False,
        "automaticConsensusCertification": False,
        "studyQualityScoring": False,
        "citationCountAuthorityScoring": False,
        "journalPrestigeScoring": False,
        "networkFetchDuringEvaluation": False,
        "rawScientificDataAccepted": False,
        "arbitraryCode": False,
    }


def _review_history(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(value[:MAX_REVIEWS]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 60).lower()
        if decision not in REVIEW_DECISIONS:
            continue
        row = {
            "id": _id(raw.get("id"), f"boundary-review-{index + 1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 3000),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def normalize_assessment(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    assessment = {
        "schema": ASSESSMENT_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "evidence-boundary-1"),
        "title": _text(raw.get("title") or "Scientific evidence and consensus boundary", 600),
        "claimIds": _ids(raw.get("claimIds")),
        "synthesisProtocolIds": _ids(raw.get("synthesisProtocolIds"), MAX_SYNTHESES),
        "scopePopulation": _text(raw.get("scopePopulation"), 1200),
        "scopeContext": _text(raw.get("scopeContext"), 1200),
        "scopeOutcome": _text(raw.get("scopeOutcome"), 1200),
        "boundaryStatement": _text(raw.get("boundaryStatement"), 5000),
        "qualificationNote": _text(raw.get("qualificationNote"), 4000),
        "reviewHistory": _review_history(raw.get("reviewHistory")),
    }
    assessment["assessmentHash"] = _hash(assessment)
    return assessment


def record_boundary_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificEvidenceGradingError("Boundary review requires an assessment and review metadata.")
    assessment = normalize_assessment(payload.get("assessment") if isinstance(payload.get("assessment"), dict) else {})
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 60).lower()
    if decision not in REVIEW_DECISIONS:
        raise ScientificEvidenceGradingError(
            "Boundary review decision must be accept-boundary, accept-with-qualification, block, or reopen."
        )
    rationale = _text(review.get("rationale"), 3000)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificEvidenceGradingError("Boundary review decisions require a rationale.")
    if decision == "accept-boundary" and len(assessment.get("boundaryStatement") or "") < 10:
        raise ScientificEvidenceGradingError("Accepting a consensus boundary requires an explicit boundary statement.")
    if decision == "accept-with-qualification" and len(assessment.get("qualificationNote") or "") < 10:
        raise ScientificEvidenceGradingError("Qualified boundary acceptance requires an explicit qualification note.")
    row = {
        "id": _id(review.get("id"), f"{assessment['id']}-review-{len(assessment['reviewHistory']) + 1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
    }
    row["reviewHash"] = _hash(row)
    base = deepcopy(assessment)
    base.pop("assessmentHash", None)
    base["reviewHistory"] = [*assessment["reviewHistory"], row]
    return {"ok": True, "version": VERSION, "review": row, "assessment": normalize_assessment(base)}


def _latest_decision(record: dict[str, Any]) -> str | None:
    rows = record.get("reviewHistory") if isinstance(record.get("reviewHistory"), list) else []
    return _text(rows[-1].get("decision"), 80).lower() if rows else None


def _source_gate(source: dict[str, Any]) -> str:
    if source.get("status") in {"retracted", "withdrawn"}:
        return "excluded"
    decision = _latest_decision(source)
    if decision == "exclude":
        return "excluded"
    if decision == "include-with-caution":
        return "reviewed-with-caution"
    if decision == "include":
        return "reviewed"
    return "needs-review"


def _synthesis_packet(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    packet = raw.get("packet") if isinstance(raw.get("packet"), dict) else raw
    if not isinstance(packet, dict):
        return None
    protocol_id = _id(packet.get("protocolId"))
    if not protocol_id:
        return None
    meta = packet.get("metaAnalysis") if isinstance(packet.get("metaAnalysis"), dict) else None
    replication_rows = packet.get("replicationRows") if isinstance(packet.get("replicationRows"), list) else []
    claim_coverage = packet.get("claimCoverage") if isinstance(packet.get("claimCoverage"), dict) else {}
    return {
        "protocolId": protocol_id,
        "protocolHash": _text(packet.get("protocolHash"), 64).lower(),
        "packetHash": _text(packet.get("packetHash"), 64).lower(),
        "gate": _text(packet.get("gate"), 80).lower(),
        "metaAnalysis": {
            "k": int(meta.get("k") or 0),
            "model": _text(meta.get("model"), 40),
            "pooledEffect": meta.get("pooledEffect"),
            "ciLow": meta.get("ciLow"),
            "ciHigh": meta.get("ciHigh"),
            "iSquaredPercent": float(meta.get("iSquaredPercent") or 0.0),
            "tauSquared": float(meta.get("tauSquared") or 0.0),
        } if meta else None,
        "replicationRows": [
            {
                "replicationSourceId": _id(row.get("replicationSourceId")),
                "originalSourceId": _id(row.get("originalSourceId")),
                "gate": _text(row.get("gate"), 80).lower(),
            }
            for row in replication_rows[:MAX_SOURCES] if isinstance(row, dict)
        ],
        "claimCoverage": {str(k): int(v or 0) for k, v in list(claim_coverage.items())[:MAX_CLAIMS]},
    }


def _claim_grade(
    claim: dict[str, Any],
    sources_by_id: dict[str, dict[str, Any]],
    links: list[dict[str, Any]],
    syntheses: list[dict[str, Any]],
) -> dict[str, Any]:
    claim_id = claim["id"]
    literature_links = [link for link in links if link.get("claimId") == claim_id]
    role_sources: dict[str, set[str]] = {}
    unreviewed: set[str] = set()
    caution: set[str] = set()
    excluded: set[str] = set()
    unresolved: set[str] = set()
    for link in literature_links:
        source_id = link.get("sourceId") or ""
        source = sources_by_id.get(source_id)
        if not source:
            unresolved.add(source_id)
            continue
        gate = _source_gate(source)
        if gate == "needs-review":
            unreviewed.add(source_id)
            continue
        if gate == "excluded":
            excluded.add(source_id)
            continue
        if gate == "reviewed-with-caution":
            caution.add(source_id)
        role_sources.setdefault(link.get("role") or "contextualizes", set()).add(source_id)

    internal_support = sum(1 for link in claim.get("evidenceLinks", []) if isinstance(link, dict) and link.get("role") in {"supports", "validates"})
    internal_contradictions = sum(1 for link in claim.get("evidenceLinks", []) if isinstance(link, dict) and link.get("role") == "contradicts")
    support_sources = role_sources.get("supports", set()) | role_sources.get("replication", set())
    contradiction_sources = role_sources.get("contradicts", set()) | role_sources.get("non-replication", set())
    uncertainty_sources = role_sources.get("uncertainty", set()) | role_sources.get("limitation", set())
    replication_sources = role_sources.get("replication", set())
    nonreplication_sources = role_sources.get("non-replication", set())

    relevant_syntheses = [s for s in syntheses if int(s.get("claimCoverage", {}).get(claim_id, 0) or 0) > 0]
    synthesis_reviewed = [s for s in relevant_syntheses if s.get("gate") == "synthesis-reviewed"]
    synthesis_blocked = [s for s in relevant_syntheses if s.get("gate") == "blocked"]
    high_heterogeneity = any((s.get("metaAnalysis") or {}).get("iSquaredPercent", 0.0) >= 75.0 for s in relevant_syntheses)
    moderate_heterogeneity = any(50.0 <= (s.get("metaAnalysis") or {}).get("iSquaredPercent", 0.0) < 75.0 for s in relevant_syntheses)
    replication_disagreement = sum(
        1 for synthesis in relevant_syntheses for row in synthesis.get("replicationRows", [])
        if row.get("gate") in {"discordant-direction", "direction-consistent-different-magnitude"}
    )
    replication_consistency = sum(
        1 for synthesis in relevant_syntheses for row in synthesis.get("replicationRows", [])
        if row.get("gate") == "directionally-consistent"
    )
    support_count = len(support_sources) + internal_support
    contradiction_count = len(contradiction_sources) + internal_contradictions + replication_disagreement
    contested = contradiction_count > 0 or high_heterogeneity

    if contested:
        grade = "contested"
    elif synthesis_reviewed and support_count >= 2 and replication_consistency >= 1:
        grade = "substantial"
    elif synthesis_reviewed or support_count >= 2:
        grade = "moderate"
    elif support_count >= 1:
        grade = "limited"
    else:
        grade = "insufficient"

    claim_decision = _latest_decision(claim)
    claim_blocked = claim_decision in {"block", "reject"} or bool(synthesis_blocked)
    if claim_blocked:
        candidate = "blocked"
    elif grade == "insufficient":
        candidate = "not-assessable"
    elif grade == "contested":
        candidate = "qualified-agreement-candidate" if claim_decision == "accept-with-qualification" else "contested"
    elif claim_decision not in {"accept", "accept-with-qualification"}:
        candidate = "needs-claim-review"
    elif grade == "substantial" and not caution and not moderate_heterogeneity and claim_decision == "accept":
        candidate = "bounded-consensus-candidate"
    elif grade in {"moderate", "substantial"}:
        candidate = "qualified-agreement-candidate"
    else:
        candidate = "emerging-agreement"

    row = {
        "schema": GRADE_SCHEMA,
        "claimId": claim_id,
        "claimHash": claim.get("claimHash"),
        "claimType": claim.get("claimType"),
        "claimDecision": claim_decision,
        "evidenceGrade": grade,
        "consensusCandidate": candidate,
        "reviewedSupportCount": support_count,
        "reviewedContradictionCount": contradiction_count,
        "literatureSupportSourceIds": sorted(support_sources),
        "literatureContradictionSourceIds": sorted(contradiction_sources),
        "replicationSourceIds": sorted(replication_sources),
        "nonReplicationSourceIds": sorted(nonreplication_sources),
        "uncertaintyLimitationSourceIds": sorted(uncertainty_sources),
        "unreviewedSourceIds": sorted(unreviewed),
        "cautionSourceIds": sorted(caution),
        "excludedSourceIds": sorted(excluded),
        "unresolvedSourceIds": sorted(x for x in unresolved if x),
        "reviewedSynthesisProtocolIds": sorted(s["protocolId"] for s in synthesis_reviewed),
        "synthesisProtocolIds": sorted(s["protocolId"] for s in relevant_syntheses),
        "replicationConsistencyCount": replication_consistency,
        "replicationDisagreementCount": replication_disagreement,
        "highHeterogeneity": high_heterogeneity,
        "moderateHeterogeneity": moderate_heterogeneity,
        "sourceCautionPresent": bool(caution),
        "humanClaimReviewRequired": True,
    }
    row["gradeHash"] = _hash(row)
    return row


def evaluate_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificEvidenceGradingError("Evidence grading requires assessment, claims, literature provenance, and synthesis metadata.")
    _scan_forbidden({k: v for k, v in payload.items() if k not in {"assessment", "claims", "sources", "claimLinks", "syntheses"}})
    assessment = normalize_assessment(payload.get("assessment") if isinstance(payload.get("assessment"), dict) else {})
    claims = [normalize_claim(x) for x in (payload.get("claims") or [])[:MAX_CLAIMS] if isinstance(x, dict)] if isinstance(payload.get("claims"), list) else []
    sources = [normalize_source(x) for x in (payload.get("sources") or [])[:MAX_SOURCES] if isinstance(x, dict)] if isinstance(payload.get("sources"), list) else []
    links = [normalize_claim_link(x) for x in (payload.get("claimLinks") or [])[:MAX_LINKS] if isinstance(x, dict)] if isinstance(payload.get("claimLinks"), list) else []
    syntheses = [x for x in (_synthesis_packet(raw) for raw in (payload.get("syntheses") or [])[:MAX_SYNTHESES]) if x] if isinstance(payload.get("syntheses"), list) else []

    claim_ids = assessment["claimIds"] or [c["id"] for c in claims]
    claim_by_id = {c["id"]: c for c in claims}
    unresolved_claim_ids = [cid for cid in claim_ids if cid not in claim_by_id]
    rows = [_claim_grade(claim_by_id[cid], {s["id"]: s for s in sources}, links, syntheses) for cid in claim_ids if cid in claim_by_id]

    contradictions = []
    for row in rows:
        factors = []
        if row["reviewedContradictionCount"]:
            factors.append("direct-contradiction")
        if row["replicationDisagreementCount"]:
            factors.append("replication-disagreement")
        if row["highHeterogeneity"]:
            factors.append("high-heterogeneity")
        elif row["moderateHeterogeneity"]:
            factors.append("moderate-heterogeneity")
        if row["sourceCautionPresent"]:
            factors.append("source-caution")
        contradiction = {
            "schema": CONTRADICTION_SCHEMA,
            "claimId": row["claimId"],
            "state": "multi-factor" if len(factors) > 1 else (factors[0] if factors else "none-observed"),
            "factors": factors,
            "contradictionSourceIds": row["literatureContradictionSourceIds"],
            "nonReplicationSourceIds": row["nonReplicationSourceIds"],
            "replicationDisagreementCount": row["replicationDisagreementCount"],
            "highHeterogeneity": row["highHeterogeneity"],
            "requiresQualifiedInterpretation": bool(row["reviewedContradictionCount"] or row["replicationDisagreementCount"] or row["highHeterogeneity"]),
        }
        contradiction["contradictionHash"] = _hash(contradiction)
        contradictions.append(contradiction)

    latest = assessment["reviewHistory"][-1] if assessment["reviewHistory"] else None
    decision = latest.get("decision") if latest else None
    has_blocked = any(row["consensusCandidate"] == "blocked" for row in rows)
    has_insufficient = bool(unresolved_claim_ids) or not rows or any(row["evidenceGrade"] in {"insufficient", "limited"} for row in rows)
    has_contested = any(row["evidenceGrade"] == "contested" for row in rows)
    has_moderate = any(row["evidenceGrade"] == "moderate" for row in rows)
    all_substantial = bool(rows) and all(row["evidenceGrade"] == "substantial" for row in rows)
    claim_reviews_ready = all(row["claimDecision"] in {"accept", "accept-with-qualification"} for row in rows)
    contested_claims_qualified = all(
        row["evidenceGrade"] != "contested" or row["claimDecision"] == "accept-with-qualification" for row in rows
    )

    if decision == "block" or has_blocked:
        gate = "blocked"
    elif has_insufficient:
        gate = "needs-evidence"
    elif has_contested and not (decision == "accept-with-qualification" and contested_claims_qualified and len(assessment["qualificationNote"]) >= 10):
        gate = "contested"
    elif not claim_reviews_ready:
        gate = "needs-review"
    elif all_substantial and decision == "accept-boundary" and len(assessment["boundaryStatement"]) >= 10:
        gate = "consensus-bounded"
    elif decision == "accept-with-qualification" and len(assessment["qualificationNote"]) >= 10:
        gate = "consensus-bounded-with-qualification"
    elif has_moderate and decision == "accept-boundary":
        gate = "needs-review"
    else:
        gate = "needs-review"

    grade_counts = {grade: sum(row["evidenceGrade"] == grade for row in rows) for grade in sorted(EVIDENCE_GRADES)}
    boundary = {
        "schema": CONSENSUS_SCHEMA,
        "assessmentId": assessment["id"],
        "gate": gate,
        "boundaryStatement": assessment["boundaryStatement"],
        "qualificationNote": assessment["qualificationNote"],
        "scope": {
            "population": assessment["scopePopulation"],
            "context": assessment["scopeContext"],
            "outcome": assessment["scopeOutcome"],
        },
        "claimIds": [row["claimId"] for row in rows],
        "unresolvedClaimIds": unresolved_claim_ids,
        "gradeCounts": grade_counts,
        "humanBoundaryReviewDecision": decision,
        "humanBoundaryReviewRequired": True,
        "automaticConsensusCertification": False,
        "numericTruthScore": None,
    }
    boundary["boundaryHash"] = _hash(boundary)
    response = {
        "ok": True,
        "version": VERSION,
        "assessment": assessment,
        "gate": gate,
        "claimGrades": rows,
        "contradictions": contradictions,
        "consensusBoundary": boundary,
        "unresolvedClaimIds": unresolved_claim_ids,
        "sourceCount": len(sources),
        "claimLinkCount": len(links),
        "synthesisCount": len(syntheses),
        "gradeCounts": grade_counts,
        "boundaries": {
            "evidenceGradeIsTransparentRuleStateNotTruthScore": True,
            "contradictionsPreserved": True,
            "replicationDisagreementPreserved": True,
            "heterogeneityPreserved": True,
            "humanBoundaryReviewRequired": True,
            "automaticConsensusCertification": False,
            "automaticCausalCertification": False,
            "automaticPublication": False,
        },
    }
    response["evaluationHash"] = _hash(response)
    return response


def build_consensus_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_evidence(payload)
    assessment = result["assessment"]
    packet = {
        "ok": True,
        "version": VERSION,
        "schema": PACKET_SCHEMA,
        "assessmentId": assessment["id"],
        "assessmentHash": assessment["assessmentHash"],
        "gate": result["gate"],
        "evaluationHash": result["evaluationHash"],
        "claimGrades": [
            {
                "claimId": row["claimId"],
                "claimHash": row["claimHash"],
                "evidenceGrade": row["evidenceGrade"],
                "consensusCandidate": row["consensusCandidate"],
                "reviewedSupportCount": row["reviewedSupportCount"],
                "reviewedContradictionCount": row["reviewedContradictionCount"],
                "replicationConsistencyCount": row["replicationConsistencyCount"],
                "replicationDisagreementCount": row["replicationDisagreementCount"],
                "highHeterogeneity": row["highHeterogeneity"],
                "sourceCautionPresent": row["sourceCautionPresent"],
                "gradeHash": row["gradeHash"],
            }
            for row in result["claimGrades"]
        ],
        "contradictions": result["contradictions"],
        "consensusBoundary": result["consensusBoundary"],
        "boundaries": result["boundaries"],
    }
    packet["packetHash"] = _hash(packet)
    return packet


def verify_consensus_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) and isinstance(payload.get("packet"), dict) else payload
    if not isinstance(packet, dict):
        raise ScientificEvidenceGradingError("Packet verification requires a scientific evidence/consensus packet.")
    supplied = _text(packet.get("packetHash"), 64).lower()
    base = deepcopy(packet)
    base.pop("packetHash", None)
    expected = _hash(base)
    return {
        "ok": supplied == expected,
        "version": VERSION,
        "schema": packet.get("schema"),
        "suppliedHash": supplied,
        "expectedHash": expected,
    }
