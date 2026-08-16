from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

VERSION = "0.69.0"
THEORY_SCHEMA = "sc-lab-scientific-theory/0.69.0"
CONSTRUCT_SCHEMA = "sc-lab-theory-construct/0.69.0"
RELATION_SCHEMA = "sc-lab-theory-relation/0.69.0"
PREDICTION_SCHEMA = "sc-lab-theory-prediction/0.69.0"
EVALUATION_SCHEMA = "sc-lab-theory-evaluation/0.69.0"
PACKET_SCHEMA = "sc-lab-scientific-theory-packet/0.69.0"

THEORY_TYPES = {"conceptual-model", "mechanistic-theory", "systems-theory", "causal-theory", "integrative-framework", "custom"}
CONSTRUCT_ROLES = {"exposure", "outcome", "mediator", "moderator", "confounder", "latent", "mechanism", "context", "state", "parameter", "custom"}
RELATION_TYPES = {"causes", "associates", "mediates", "moderates", "inhibits", "enables", "depends-on", "feedback", "transforms", "constrains", "custom"}
REVIEW_DECISIONS = {"accept-within-scope", "accept-with-qualification", "block", "reopen"}

FORBIDDEN_KEYS = {
    "rows", "records", "rawdata", "raw_data", "dataset", "datasets", "datasetpayload", "datasetspayload",
    "inputs", "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64", "participantdata", "participantrecords",
    "microdata", "outcomevector", "predictormatrix", "covariatematrix"
}


class ScientificTheoryError(ValueError):
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


def _ids(v: Any, limit: int = 100) -> list[str]:
    if not isinstance(v, list):
        return []
    out: list[str] = []
    for raw in v[:limit]:
        item = _id(raw)
        if item and item not in out:
            out.append(item)
    return out


def _scan_forbidden(value: Any, path: str = "$") -> None:
    forbidden = {k.replace("_", "").replace("-", "").lower() for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            norm = str(key).replace("_", "").replace("-", "").lower()
            if norm in forbidden:
                raise ScientificTheoryError(
                    f"Scientific theory modeling accepts governed conceptual metadata only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{i}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "theoryTypes": sorted(THEORY_TYPES),
        "constructRoles": sorted(CONSTRUCT_ROLES),
        "relationTypes": sorted(RELATION_TYPES),
        "explicitConstructDefinitionsRequired": True,
        "explicitMechanismsForCausalRelationsRequired": True,
        "testablePredictionsRequired": True,
        "falsificationBoundariesRequired": True,
        "humanTheoryReviewRequired": True,
        "automaticTheoryProofAuthorized": False,
        "automaticCausalCertificationAuthorized": False,
        "automaticUniversalGeneralizationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "rawScientificDataAccepted": False,
        "participantLevelDataAccepted": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-theory-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "theoryTypes": sorted(THEORY_TYPES),
        "humanTheoryReviewRequired": True,
        "automaticTheoryProof": False,
        "automaticCausalCertification": False,
        "rawScientificDataAccepted": False,
        "arbitraryCode": False,
    }


def _reviews(v: Any) -> list[dict[str, Any]]:
    if not isinstance(v, list):
        return []
    out = []
    for i, raw in enumerate(v[:100]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 80).lower()
        if decision not in REVIEW_DECISIONS:
            continue
        row = {
            "id": _id(raw.get("id"), f"theory-review-{i+1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 4000),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def normalize_theory(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    theory_type = _text(raw.get("theoryType"), 80).lower() or "conceptual-model"
    if theory_type not in THEORY_TYPES:
        theory_type = "custom"
    theory = {
        "schema": THEORY_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "scientific-theory-1"),
        "title": _text(raw.get("title") or "Scientific theory", 600),
        "theoryType": theory_type,
        "studyId": _id(raw.get("studyId")),
        "linkedClaimIds": _ids(raw.get("linkedClaimIds"), 120),
        "linkedHypothesisIds": _ids(raw.get("linkedHypothesisIds"), 120),
        "linkedModelIds": _ids(raw.get("linkedModelIds"), 120),
        "purpose": _text(raw.get("purpose"), 5000),
        "scopeBoundary": _text(raw.get("scopeBoundary"), 5000),
        "coreMechanism": _text(raw.get("coreMechanism"), 5000),
        "assumptions": _text(raw.get("assumptions"), 6000),
        "limitations": _text(raw.get("limitations"), 6000),
        "reviewHistory": _reviews(raw.get("reviewHistory")),
    }
    theory["theoryHash"] = _hash(theory)
    return theory


def normalize_construct(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    role = _text(raw.get("role"), 80).lower() or "custom"
    if role not in CONSTRUCT_ROLES:
        role = "custom"
    row = {
        "schema": CONSTRUCT_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "construct-1"),
        "theoryId": _id(raw.get("theoryId")),
        "name": _text(raw.get("name") or "Construct", 500),
        "role": role,
        "definition": _text(raw.get("definition"), 5000),
        "operationalization": _text(raw.get("operationalization"), 5000),
        "unitOrScale": _text(raw.get("unitOrScale"), 500),
        "linkedEvidenceRefs": _ids(raw.get("linkedEvidenceRefs"), 120),
        "note": _text(raw.get("note"), 3000),
    }
    if not row["theoryId"]:
        raise ScientificTheoryError("Theory constructs require theoryId.")
    row["constructHash"] = _hash(row)
    return row


def normalize_relation(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    relation_type = _text(raw.get("relationType"), 80).lower() or "associates"
    if relation_type not in RELATION_TYPES:
        relation_type = "custom"
    row = {
        "schema": RELATION_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "relation-1"),
        "theoryId": _id(raw.get("theoryId")),
        "sourceConstructId": _id(raw.get("sourceConstructId")),
        "targetConstructId": _id(raw.get("targetConstructId")),
        "relationType": relation_type,
        "mechanism": _text(raw.get("mechanism"), 5000),
        "equationRef": _id(raw.get("equationRef")),
        "causalAssumptionRef": _id(raw.get("causalAssumptionRef")),
        "uncertaintyNote": _text(raw.get("uncertaintyNote"), 3000),
        "linkedEvidenceRefs": _ids(raw.get("linkedEvidenceRefs"), 120),
    }
    if not row["theoryId"] or not row["sourceConstructId"] or not row["targetConstructId"]:
        raise ScientificTheoryError("Theory relations require theoryId, sourceConstructId, and targetConstructId.")
    if row["sourceConstructId"] == row["targetConstructId"] and relation_type != "feedback":
        raise ScientificTheoryError("A non-feedback relation cannot connect a construct to itself.")
    row["relationHash"] = _hash(row)
    return row


def normalize_prediction(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    row = {
        "schema": PREDICTION_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "prediction-1"),
        "theoryId": _id(raw.get("theoryId")),
        "hypothesisId": _id(raw.get("hypothesisId")),
        "statement": _text(raw.get("statement"), 5000),
        "expectedDirection": _text(raw.get("expectedDirection"), 500),
        "discriminatingAgainstIds": _ids(raw.get("discriminatingAgainstIds"), 100),
        "falsificationCondition": _text(raw.get("falsificationCondition"), 5000),
        "linkedEvidenceRefs": _ids(raw.get("linkedEvidenceRefs"), 120),
        "note": _text(raw.get("note"), 3000),
    }
    if not row["theoryId"]:
        raise ScientificTheoryError("Theory predictions require theoryId.")
    row["predictionHash"] = _hash(row)
    return row


def _select(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("theory"), dict):
        raise ScientificTheoryError("Scientific theory evaluation requires a theory object.")
    theory = normalize_theory(payload["theory"])
    constructs = [normalize_construct(x) for x in (payload.get("constructs") or []) if isinstance(x, dict)]
    relations = [normalize_relation(x) for x in (payload.get("relations") or []) if isinstance(x, dict)]
    predictions = [normalize_prediction(x) for x in (payload.get("predictions") or []) if isinstance(x, dict)]
    constructs = [x for x in constructs if x["theoryId"] == theory["id"]]
    relations = [x for x in relations if x["theoryId"] == theory["id"]]
    predictions = [x for x in predictions if x["theoryId"] == theory["id"]]
    return theory, constructs, relations, predictions


def build_graph(payload: dict[str, Any]) -> dict[str, Any]:
    theory, constructs, relations, predictions = _select(payload)
    graph = {
        "theoryId": theory["id"],
        "nodes": [
            {"id": x["id"], "label": x["name"], "role": x["role"], "definitionHash": _hash(x["definition"])}
            for x in constructs
        ],
        "edges": [
            {
                "id": x["id"], "source": x["sourceConstructId"], "target": x["targetConstructId"],
                "relationType": x["relationType"], "mechanismHash": _hash(x["mechanism"]),
            }
            for x in relations
        ],
        "predictions": [
            {"id": x["id"], "hypothesisId": x["hypothesisId"], "statementHash": _hash(x["statement"]),
             "falsificationHash": _hash(x["falsificationCondition"])}
            for x in predictions
        ],
    }
    graph["graphHash"] = _hash(graph)
    return {"ok": True, "version": VERSION, "graph": graph}


def record_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("theory"), dict) or not isinstance(payload.get("review"), dict):
        raise ScientificTheoryError("Theory review requires theory and review objects.")
    theory = normalize_theory(payload["theory"])
    raw = payload["review"]
    _scan_forbidden(raw)
    decision = _text(raw.get("decision"), 80).lower()
    if decision not in REVIEW_DECISIONS:
        raise ScientificTheoryError("Theory review decision is not recognized.")
    rationale = _text(raw.get("rationale"), 4000)
    if decision != "reopen" and len(rationale) < 4:
        raise ScientificTheoryError("Theory review decisions require a rationale.")
    if decision == "accept-with-qualification" and len(theory.get("limitations") or "") < 8:
        raise ScientificTheoryError("Qualified theory review requires explicit limitations.")
    row = {
        "id": _id(raw.get("id"), f"{theory['id']}-review-{len(theory['reviewHistory'])+1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(raw.get("reviewedAt"), 64),
    }
    row["reviewHash"] = _hash(row)
    theory["reviewHistory"] = [*theory["reviewHistory"], row]
    theory["theoryHash"] = _hash({k: v for k, v in theory.items() if k != "theoryHash"})
    return {"ok": True, "version": VERSION, "theory": theory, "review": row}


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    theory, constructs, relations, predictions = _select(payload)
    construct_ids = {x["id"] for x in constructs}
    unresolved = sorted({
        ref for r in relations for ref in (r["sourceConstructId"], r["targetConstructId"]) if ref not in construct_ids
    })
    undefined = [x["id"] for x in constructs if len(x["definition"]) < 8]
    unoperationalized = [x["id"] for x in constructs if x["role"] not in {"latent", "mechanism", "context"} and len(x["operationalization"]) < 4]
    causal_without_mechanism = [x["id"] for x in relations if x["relationType"] == "causes" and len(x["mechanism"]) < 8]
    predictions_without_falsification = [x["id"] for x in predictions if len(x["falsificationCondition"]) < 8]
    predictions_without_statement = [x["id"] for x in predictions if len(x["statement"]) < 8]
    evidence_refs = sorted({ref for x in constructs for ref in x["linkedEvidenceRefs"]} |
                           {ref for x in relations for ref in x["linkedEvidenceRefs"]} |
                           {ref for x in predictions for ref in x["linkedEvidenceRefs"]})
    latest_review = theory["reviewHistory"][-1]["decision"] if theory["reviewHistory"] else ""

    reasons: list[str] = []
    if latest_review == "block":
        gate = "blocked"; reasons.append("Human theory review blocks interpretation.")
    elif len(constructs) < 2:
        gate = "needs-constructs"; reasons.append("At least two explicitly defined constructs are required.")
    elif undefined:
        gate = "needs-construct-definitions"; reasons.append("Every construct requires an explicit definition.")
    elif unoperationalized:
        gate = "needs-operationalization"; reasons.append("Empirical constructs require an operationalization boundary.")
    elif not relations:
        gate = "needs-relations"; reasons.append("At least one explicit relation is required.")
    elif unresolved:
        gate = "unresolved-construct-reference"; reasons.append("Every relation endpoint must resolve to a theory construct.")
    elif causal_without_mechanism:
        gate = "needs-mechanism"; reasons.append("Causal relations require an explicit mechanism statement.")
    elif not predictions or predictions_without_statement:
        gate = "needs-predictions"; reasons.append("The theory requires at least one testable prediction.")
    elif predictions_without_falsification:
        gate = "needs-falsification-boundary"; reasons.append("Every prediction requires a falsification condition.")
    elif not evidence_refs:
        gate = "needs-evidence-linkage"; reasons.append("At least one construct, relation, or prediction must link to governed project evidence.")
    elif len(theory["scopeBoundary"]) < 8:
        gate = "needs-scope-boundary"; reasons.append("The theory requires an explicit scope boundary.")
    elif latest_review not in {"accept-within-scope", "accept-with-qualification"}:
        gate = "needs-review"; reasons.append("Human theory review is required after structure and predictions are explicit.")
    elif latest_review == "accept-with-qualification":
        gate = "theory-bounded-with-qualification"; reasons.append("Human review accepted the theory within stated qualifications.")
    else:
        gate = "theory-bounded"; reasons.append("Human review accepted the theory within its stated scope.")

    graph = build_graph({"theory": theory, "constructs": constructs, "relations": relations, "predictions": predictions})["graph"]
    result = {
        "ok": True,
        "schema": EVALUATION_SCHEMA,
        "version": VERSION,
        "theory": theory,
        "gate": gate,
        "reasons": reasons,
        "constructCount": len(constructs),
        "relationCount": len(relations),
        "predictionCount": len(predictions),
        "evidenceRefCount": len(evidence_refs),
        "unresolvedConstructRefs": unresolved,
        "undefinedConstructIds": undefined,
        "unoperationalizedConstructIds": unoperationalized,
        "causalRelationsMissingMechanism": causal_without_mechanism,
        "predictionsMissingFalsification": predictions_without_falsification,
        "latestHumanReview": latest_review or None,
        "graphHash": graph["graphHash"],
        "humanReviewRequired": True,
        "automaticTheoryProof": False,
        "automaticCausalCertification": False,
        "automaticUniversalGeneralization": False,
    }
    result["evaluationHash"] = _hash(result)
    return result


def build_packet(payload: dict[str, Any]) -> dict[str, Any]:
    result = evaluate(payload)
    theory, constructs, relations, predictions = _select(payload)
    packet = {
        "ok": True,
        "schema": PACKET_SCHEMA,
        "version": VERSION,
        "theoryId": theory["id"],
        "theoryHash": theory["theoryHash"],
        "gate": result["gate"],
        "graphHash": result["graphHash"],
        "evaluationHash": result["evaluationHash"],
        "constructHashes": [x["constructHash"] for x in constructs],
        "relationHashes": [x["relationHash"] for x in relations],
        "predictionHashes": [x["predictionHash"] for x in predictions],
        "reviewHashes": [x["reviewHash"] for x in theory["reviewHistory"]],
        "linkedClaimIds": theory["linkedClaimIds"],
        "linkedHypothesisIds": theory["linkedHypothesisIds"],
        "linkedModelIds": theory["linkedModelIds"],
        "scopeBoundaryHash": _hash(theory["scopeBoundary"]),
        "limitationsHash": _hash(theory["limitations"]),
        "humanReviewRequired": True,
        "automaticTheoryProof": False,
        "automaticCausalCertification": False,
        "rawScientificDataIncluded": False,
    }
    packet["packetHash"] = _hash(packet)
    return packet


def verify_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) else None
    if not isinstance(packet, dict):
        raise ScientificTheoryError("Packet verification requires packet.")
    supplied = _text(packet.get("packetHash"), 64)
    body = deepcopy(packet)
    body.pop("packetHash", None)
    expected = _hash(body)
    return {"ok": supplied == expected, "version": VERSION, "packetHash": supplied, "expectedPacketHash": expected}
