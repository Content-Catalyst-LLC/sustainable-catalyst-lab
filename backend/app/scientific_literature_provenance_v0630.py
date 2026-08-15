from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

from .scientific_claims_traceability_v0620 import normalize_claim, normalize_conclusion

VERSION = "0.63.0"
SOURCE_SCHEMA = "sc-lab-scientific-literature-source/0.63.0"
SOURCE_REVIEW_SCHEMA = "sc-lab-scientific-literature-review/0.63.0"
CLAIM_LINK_SCHEMA = "sc-lab-source-claim-provenance/0.63.0"
CITATION_GRAPH_SCHEMA = "sc-lab-scientific-citation-graph/0.63.0"
PACKET_SCHEMA = "sc-lab-scientific-literature-provenance-packet/0.63.0"
MAX_SOURCES = 500
MAX_CLAIM_LINKS = 1500
MAX_CITATION_EDGES = 2000
MAX_REVIEWS = 800
MAX_AUTHORS = 80

SOURCE_TYPES = {
    "journal-article", "preprint", "report", "dataset", "book", "book-chapter",
    "thesis", "conference-paper", "standard", "government-publication",
    "repository-record", "archive-record", "other",
}
SOURCE_STATUSES = {"active", "corrected", "retracted", "withdrawn", "unknown"}
PEER_REVIEW_STATUSES = {"peer-reviewed", "not-peer-reviewed", "preprint", "unknown", "not-applicable"}
SOURCE_ORIGINS = {"manual", "research-library", "doi", "crossref", "pubmed", "openalex", "repository", "archive", "other"}
SOURCE_REVIEW_DECISIONS = {"include", "include-with-caution", "exclude", "reopen"}
CLAIM_LINK_ROLES = {
    "supports", "contradicts", "contextualizes", "methodological-background",
    "uncertainty", "limitation", "replication", "non-replication",
}
CITATION_RELATIONS = {
    "cites", "supports", "contradicts", "extends", "replicates", "fails-to-replicate",
    "corrects", "retracts", "uses-data-from", "uses-method-from", "related",
}
IDENTIFIER_TYPES = {"doi", "pmid", "pmcid", "arxiv", "isbn", "issn", "handle", "uri", "library-record"}
FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64",
}


class ScientificLiteratureProvenanceError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, default: str = "") -> str:
    text = _text(value, 180)
    safe = "".join(ch for ch in text if ch.isalnum() or ch in "-_.:")
    return safe or default


def _hex_hash(value: Any) -> str:
    text = _text(value, 64).lower()
    return text if len(text) == 64 and all(ch in "0123456789abcdef" for ch in text) else ""


def _scan_forbidden(value: Any, path: str = "$") -> None:
    normalized_forbidden = {k.replace("_", "").replace("-", "") for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in normalized_forbidden:
                raise ScientificLiteratureProvenanceError(
                    f"Literature provenance accepts bibliographic metadata and bounded notes only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]")


def _authors(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(x, 180) for x in value[:MAX_AUTHORS] if _text(x, 180)]


def _url(value: Any) -> str:
    text = _text(value, 2048)
    if not text:
        return ""
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ScientificLiteratureProvenanceError("Source URL must be an absolute http/https URL.")
    return text


def _identifiers(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, str] = {}
    for raw_key, raw_value in value.items():
        key = _text(raw_key, 40).lower()
        val = _text(raw_value, 300)
        if key in IDENTIFIER_TYPES and val:
            if key == "doi":
                val = val.lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/").removeprefix("doi:").strip()
            out[key] = val
    return dict(sorted(out.items()))


def _review_history(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(value[:MAX_REVIEWS]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 40).lower()
        if decision not in SOURCE_REVIEW_DECISIONS:
            continue
        row = {
            "id": _id(raw.get("id"), f"source-review-{index+1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 2000),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "literatureSourceRegistry": True,
        "citationGraph": True,
        "sourceToClaimProvenance": True,
        "contradictingLiteraturePreserved": True,
        "humanSourceReviewRequired": True,
        "sourceQualityNotesDeclaredNotInferred": True,
        "automaticLiteratureTruthScoringAuthorized": False,
        "automaticBibliometricAuthorityRankingAuthorized": False,
        "automaticRetractionVerificationAuthorized": False,
        "automaticClaimInferenceAuthorized": False,
        "automaticScientificCertificationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "rawFullTextAccepted": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-literature-provenance-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "sourceTypes": sorted(SOURCE_TYPES),
        "claimLinkRoles": sorted(CLAIM_LINK_ROLES),
        "citationRelations": sorted(CITATION_RELATIONS),
        "humanSourceReviewRequired": True,
        "automaticTruthScoring": False,
        "automaticAuthorityRanking": False,
        "automaticRetractionVerification": False,
        "networkFetchDuringEvaluation": False,
        "rawFullTextAccepted": False,
        "arbitraryCode": False,
    }


def normalize_source(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    _scan_forbidden(source)
    source_type = _text(source.get("sourceType") or "journal-article", 50).lower()
    if source_type not in SOURCE_TYPES:
        raise ScientificLiteratureProvenanceError(f"Unsupported literature source type: {source_type}")
    status = _text(source.get("status") or "unknown", 40).lower()
    if status not in SOURCE_STATUSES:
        raise ScientificLiteratureProvenanceError(f"Unsupported source status: {status}")
    peer_review = _text(source.get("peerReviewStatus") or "unknown", 40).lower()
    if peer_review not in PEER_REVIEW_STATUSES:
        raise ScientificLiteratureProvenanceError(f"Unsupported peer review status: {peer_review}")
    origin = _text(source.get("origin") or "manual", 40).lower()
    if origin not in SOURCE_ORIGINS:
        raise ScientificLiteratureProvenanceError(f"Unsupported literature origin: {origin}")
    year_raw = source.get("publicationYear")
    try:
        year = int(year_raw) if year_raw not in (None, "") else None
    except (TypeError, ValueError):
        raise ScientificLiteratureProvenanceError("publicationYear must be an integer year.")
    if year is not None and not (0 <= year <= 2200):
        raise ScientificLiteratureProvenanceError("publicationYear is outside the governed range.")
    record = {
        "schema": SOURCE_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), "source-1"),
        "sourceType": source_type,
        "title": _text(source.get("title"), 1200),
        "authors": _authors(source.get("authors")),
        "publicationYear": year,
        "publicationDate": _text(source.get("publicationDate"), 40),
        "containerTitle": _text(source.get("containerTitle"), 500),
        "publisher": _text(source.get("publisher"), 400),
        "volume": _text(source.get("volume"), 80),
        "issue": _text(source.get("issue"), 80),
        "pages": _text(source.get("pages"), 120),
        "identifiers": _identifiers(source.get("identifiers")),
        "sourceUrl": _url(source.get("sourceUrl")),
        "origin": origin,
        "libraryRecordRef": _id(source.get("libraryRecordRef")),
        "status": status,
        "peerReviewStatus": peer_review,
        "scopeNote": _text(source.get("scopeNote"), 2400),
        "reviewHistory": _review_history(source.get("reviewHistory")),
    }
    record["sourceHash"] = _hash(record)
    return record


def record_source_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificLiteratureProvenanceError("Source review requires a source and review record.")
    source = normalize_source(payload.get("source") if isinstance(payload.get("source"), dict) else {})
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 40).lower()
    if decision not in SOURCE_REVIEW_DECISIONS:
        raise ScientificLiteratureProvenanceError("Source review decision must be include, include-with-caution, exclude, or reopen.")
    rationale = _text(review.get("rationale"), 2000)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificLiteratureProvenanceError("Source review decisions require a rationale.")
    row = {
        "id": _id(review.get("id"), f"{source['id']}-review-{len(source['reviewHistory'])+1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
    }
    row["reviewHash"] = _hash(row)
    base = deepcopy(source)
    base.pop("sourceHash", None)
    base["reviewHistory"] = [*source["reviewHistory"], row]
    return {"ok": True, "schema": SOURCE_REVIEW_SCHEMA, "version": VERSION, "review": row, "source": normalize_source(base)}


def normalize_claim_link(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    role = _text(raw.get("role") or "contextualizes", 60).lower()
    if role not in CLAIM_LINK_ROLES:
        raise ScientificLiteratureProvenanceError(f"Unsupported source-to-claim role: {role}")
    claim_id = _id(raw.get("claimId"))
    source_id = _id(raw.get("sourceId"))
    if not claim_id or not source_id:
        raise ScientificLiteratureProvenanceError("Source-to-claim provenance requires claimId and sourceId.")
    link = {
        "schema": CLAIM_LINK_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), f"{claim_id}--{source_id}--{role}"),
        "claimId": claim_id,
        "sourceId": source_id,
        "role": role,
        "locator": _text(raw.get("locator"), 500),
        "note": _text(raw.get("note"), 1800),
        "claimHash": _hex_hash(raw.get("claimHash")),
        "sourceHash": _hex_hash(raw.get("sourceHash")),
    }
    link["linkHash"] = _hash(link)
    return link


def normalize_citation_edge(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    relation = _text(raw.get("relation") or "cites", 60).lower()
    if relation not in CITATION_RELATIONS:
        raise ScientificLiteratureProvenanceError(f"Unsupported citation relation: {relation}")
    from_id = _id(raw.get("fromSourceId"))
    to_id = _id(raw.get("toSourceId"))
    if not from_id or not to_id:
        raise ScientificLiteratureProvenanceError("Citation edges require fromSourceId and toSourceId.")
    edge = {
        "schema": CITATION_GRAPH_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), f"{from_id}--{relation}--{to_id}"),
        "fromSourceId": from_id,
        "toSourceId": to_id,
        "relation": relation,
        "locator": _text(raw.get("locator"), 500),
        "note": _text(raw.get("note"), 1600),
    }
    edge["edgeHash"] = _hash(edge)
    return edge


def _latest_review(source: dict[str, Any]) -> dict[str, Any] | None:
    rows = source.get("reviewHistory") if isinstance(source.get("reviewHistory"), list) else []
    return rows[-1] if rows else None


def _source_gate(source: dict[str, Any]) -> tuple[str, str | None]:
    review = _latest_review(source)
    decision = review.get("decision") if review else None
    if source.get("status") in {"retracted", "withdrawn"}:
        return "unusable-status", decision
    if decision == "exclude":
        return "excluded", decision
    if decision == "include-with-caution":
        return "reviewed-with-caution", decision
    if decision == "include":
        return "reviewed", decision
    return "needs-review", decision


def _duplicates(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = {}
    for source in sources:
        for kind, value in source.get("identifiers", {}).items():
            key = f"{kind}:{value.lower()}"
            buckets.setdefault(key, []).append(source["id"])
    return [
        {"identifier": key, "sourceIds": sorted(ids)}
        for key, ids in sorted(buckets.items()) if len(set(ids)) > 1
    ]


def evaluate_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificLiteratureProvenanceError("Literature provenance evaluation requires sources, claims, claim links, and citation edges.")
    _scan_forbidden({k: v for k, v in payload.items() if k not in {"sources", "claims", "conclusions", "claimLinks", "citationEdges"}})
    sources = [normalize_source(x) for x in (payload.get("sources") or [])[:MAX_SOURCES] if isinstance(x, dict)] if isinstance(payload.get("sources"), list) else []
    claims = [normalize_claim(x) for x in (payload.get("claims") or [])[:100] if isinstance(x, dict)] if isinstance(payload.get("claims"), list) else []
    conclusions = [normalize_conclusion(x) for x in (payload.get("conclusions") or [])[:40] if isinstance(x, dict)] if isinstance(payload.get("conclusions"), list) else []
    links = [normalize_claim_link(x) for x in (payload.get("claimLinks") or [])[:MAX_CLAIM_LINKS] if isinstance(x, dict)] if isinstance(payload.get("claimLinks"), list) else []
    edges = [normalize_citation_edge(x) for x in (payload.get("citationEdges") or [])[:MAX_CITATION_EDGES] if isinstance(x, dict)] if isinstance(payload.get("citationEdges"), list) else []

    source_by_id = {s["id"]: s for s in sources}
    claim_by_id = {c["id"]: c for c in claims}
    source_rows = []
    for source in sources:
        gate, decision = _source_gate(source)
        source_rows.append({
            "sourceId": source["id"], "title": source["title"], "sourceType": source["sourceType"],
            "status": source["status"], "peerReviewStatus": source["peerReviewStatus"], "gate": gate,
            "reviewDecision": decision, "sourceHash": source["sourceHash"],
        })

    unresolved_links = []
    claim_rows = []
    for claim in claims:
        claim_links = [link for link in links if link["claimId"] == claim["id"]]
        unresolved_sources = sorted({link["sourceId"] for link in claim_links if link["sourceId"] not in source_by_id})
        unresolved_links.extend([link["id"] for link in claim_links if link["sourceId"] not in source_by_id])
        reviewed_links = []
        cautious_links = []
        contradiction_links = []
        for link in claim_links:
            source = source_by_id.get(link["sourceId"])
            if not source:
                continue
            gate, _ = _source_gate(source)
            if gate == "reviewed":
                reviewed_links.append(link)
            elif gate == "reviewed-with-caution":
                cautious_links.append(link)
            if link["role"] in {"contradicts", "non-replication"} and gate in {"reviewed", "reviewed-with-caution"}:
                contradiction_links.append(link)
        review_rows = claim.get("reviewHistory", [])
        claim_decision = review_rows[-1].get("decision") if review_rows else ""
        if not claim_links:
            gate = "literature-unlinked"
        elif unresolved_sources:
            gate = "needs-source"
        elif not (reviewed_links or cautious_links):
            gate = "needs-source-review"
        elif contradiction_links and claim_decision != "accept-with-qualification":
            gate = "contested"
        else:
            gate = "traceable"
        claim_rows.append({
            "claimId": claim["id"], "claimHash": claim["claimHash"], "statement": claim["statement"],
            "gate": gate, "sourceLinkCount": len(claim_links), "reviewedSourceLinkCount": len(reviewed_links),
            "cautiousSourceLinkCount": len(cautious_links), "contradictingSourceCount": len(contradiction_links),
            "unresolvedSourceIds": unresolved_sources, "claimReviewDecision": claim_decision or None,
            "automaticTruthClaim": False,
        })

    unresolved_edges = []
    self_edges = []
    for edge in edges:
        missing = [sid for sid in (edge["fromSourceId"], edge["toSourceId"]) if sid not in source_by_id]
        if missing:
            unresolved_edges.append({"edgeId": edge["id"], "missingSourceIds": sorted(set(missing))})
        if edge["fromSourceId"] == edge["toSourceId"]:
            self_edges.append(edge["id"])

    linked_source_ids = {link["sourceId"] for link in links if link["sourceId"] in source_by_id}
    graph_source_ids = {sid for edge in edges for sid in (edge["fromSourceId"], edge["toSourceId"]) if sid in source_by_id}
    orphan_source_ids = sorted(set(source_by_id) - linked_source_ids - graph_source_ids)
    duplicate_groups = _duplicates(sources)

    claim_gates = [row["gate"] for row in claim_rows]
    if unresolved_edges or any(g == "needs-source" for g in claim_gates):
        gate = "needs-source"
    elif any(g == "needs-source-review" for g in claim_gates):
        gate = "needs-source-review"
    elif any(g == "contested" for g in claim_gates):
        gate = "contested"
    elif claims and all(g == "traceable" for g in claim_gates):
        gate = "traceable"
    else:
        gate = "literature-unlinked"

    result = {
        "ok": True,
        "version": VERSION,
        "schema": CITATION_GRAPH_SCHEMA,
        "gate": gate,
        "sourceCount": len(sources),
        "claimCount": len(claims),
        "conclusionCount": len(conclusions),
        "claimLinkCount": len(links),
        "citationEdgeCount": len(edges),
        "sourceRows": source_rows,
        "claimRows": claim_rows,
        "unresolvedClaimLinkIds": sorted(set(unresolved_links)),
        "unresolvedCitationEdges": unresolved_edges,
        "selfCitationEdgeIds": sorted(set(self_edges)),
        "orphanSourceIds": orphan_source_ids,
        "duplicateIdentifierGroups": duplicate_groups,
        "boundaries": {
            "automaticTruthScoring": False,
            "automaticAuthorityRanking": False,
            "automaticRetractionVerification": False,
            "automaticClaimInference": False,
            "networkFetchDuringEvaluation": False,
            "rawFullTextIncluded": False,
        },
    }
    result["citationGraphHash"] = _hash({"sources": [s["sourceHash"] for s in sources], "claimLinks": [x["linkHash"] for x in links], "citationEdges": [x["edgeHash"] for x in edges]})
    result["evaluationHash"] = _hash({k: v for k, v in result.items() if k != "evaluationHash"})
    return result


def build_provenance_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_provenance(payload)
    sources = [normalize_source(x) for x in (payload.get("sources") or [])[:MAX_SOURCES] if isinstance(x, dict)] if isinstance(payload.get("sources"), list) else []
    links = [normalize_claim_link(x) for x in (payload.get("claimLinks") or [])[:MAX_CLAIM_LINKS] if isinstance(x, dict)] if isinstance(payload.get("claimLinks"), list) else []
    edges = [normalize_citation_edge(x) for x in (payload.get("citationEdges") or [])[:MAX_CITATION_EDGES] if isinstance(x, dict)] if isinstance(payload.get("citationEdges"), list) else []
    packet = {
        "schema": PACKET_SCHEMA,
        "version": VERSION,
        "gate": result["gate"],
        "sourceRecords": [{
            "id": s["id"], "sourceType": s["sourceType"], "title": s["title"], "publicationYear": s["publicationYear"],
            "identifiers": s["identifiers"], "origin": s["origin"], "status": s["status"],
            "peerReviewStatus": s["peerReviewStatus"], "sourceHash": s["sourceHash"],
            "reviewHash": (_latest_review(s) or {}).get("reviewHash"),
        } for s in sources],
        "claimLinks": [{"id": x["id"], "claimId": x["claimId"], "sourceId": x["sourceId"], "role": x["role"], "locator": x["locator"], "linkHash": x["linkHash"]} for x in links],
        "citationEdges": [{"id": x["id"], "fromSourceId": x["fromSourceId"], "toSourceId": x["toSourceId"], "relation": x["relation"], "edgeHash": x["edgeHash"]} for x in edges],
        "claimRows": result["claimRows"],
        "duplicateIdentifierGroups": result["duplicateIdentifierGroups"],
        "unresolvedCitationEdges": result["unresolvedCitationEdges"],
        "citationGraphHash": result["citationGraphHash"],
        "evaluationHash": result["evaluationHash"],
        "boundaries": result["boundaries"],
    }
    packet["packetHash"] = _hash(packet)
    return {"ok": True, "version": VERSION, "packet": packet}


def verify_provenance_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) and isinstance(payload.get("packet"), dict) else payload
    if not isinstance(packet, dict):
        return {"ok": False, "version": VERSION, "reason": "packet-required"}
    expected = _text(packet.get("packetHash"), 64).lower()
    body = deepcopy(packet)
    body.pop("packetHash", None)
    actual = _hash(body)
    return {"ok": bool(expected and expected == actual), "version": VERSION, "expected": expected, "actual": actual}
