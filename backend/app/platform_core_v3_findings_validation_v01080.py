from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any
from urllib.parse import quote

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_research_context_v01060 import normalize_research_context
from .scientific_claims_traceability_v0620 import normalize_claim as normalize_lab_claim
from .scientific_evidence_grading_v0650 import normalize_assessment as normalize_lab_evidence_assessment

LAB_VERSION = "0.108.0"
FEATURE_VERSION = "0.108.0"
MINIMUM_CORE_RELEASE = "3.0.0"
BRIDGE_SCHEMA = "sc-lab-platform-core-v3-findings-claims-evidence-validation/0.108.0"
FINDING_SCHEMA = "sc-lab-core-v3-finding/0.108.0"
CLAIM_SCHEMA = "sc-lab-core-v3-claim/0.108.0"
EVIDENCE_LINK_SCHEMA = "sc-lab-core-v3-evidence-link/0.108.0"
VALIDATION_SCHEMA = "sc-lab-core-v3-validation-challenge/0.108.0"
REPLICATION_SCHEMA = "sc-lab-core-v3-replication-attempt/0.108.0"
CORE_INTELLIGENCE_PREFIX = "/v1/research/intelligence"
CORE_VALIDATION_PREFIX = "/v1/research/validation-challenges"

CORE_FINDING_TYPES = {
    "observation", "result", "pattern", "anomaly", "estimate", "model_output",
    "synthesis", "negative_result", "limitation",
}
CORE_FINDING_STATUSES = {"proposed", "recorded", "revised", "superseded", "withdrawn"}
CORE_CLAIM_TYPES = {"descriptive", "interpretive", "causal", "comparative", "predictive", "normative", "methodological"}
CORE_CLAIM_STATUSES = {"proposed", "supported", "contested", "qualified", "superseded", "withdrawn", "unresolved"}
CORE_POLARITIES = {"affirmed", "denied", "uncertain", "not_applicable"}
CORE_EVIDENCE_RELATIONS = {"supports", "contradicts", "qualifies", "is_insufficient_for", "contextualizes", "derived_from"}
CORE_CHALLENGE_TYPES = {
    "alternative_hypothesis", "contradiction", "counterevidence", "sensitivity",
    "robustness", "replication", "reviewer_challenge", "methodological_challenge",
    "uncertainty_challenge", "other",
}

LAB_TO_CORE_CLAIM_TYPE = {
    "descriptive": "descriptive",
    "associational": "interpretive",
    "comparative": "comparative",
    "predictive": "predictive",
    "mechanistic": "interpretive",
    "causal": "causal",
    "methodological": "methodological",
    "null": "descriptive",
}
LAB_TO_CORE_CLAIM_STATUS = {
    "draft": "proposed",
    "active": "proposed",
    "withdrawn": "withdrawn",
    "superseded": "superseded",
}
LAB_TO_CORE_EVIDENCE_RELATION = {
    "supports": "supports",
    "contradicts": "contradicts",
    "contextualizes": "contextualizes",
    "validates": "qualifies",
    "uncertainty": "qualifies",
    "limitation": "qualifies",
}


class PlatformCoreV3FindingsValidationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 4000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise PlatformCoreV3FindingsValidationError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3FindingsValidationError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3FindingsValidationError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum_items: int = 500) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3FindingsValidationError(f"{label} must be an array.")
    if len(value) > maximum_items:
        raise PlatformCoreV3FindingsValidationError(f"{label} exceeds {maximum_items} entries.")
    return copy.deepcopy(value)


def _refs(value: Any, label: str, maximum_items: int = 500) -> list[str]:
    items = _list(value, label, maximum_items)
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, dict):
            ref = item.get("object_ref") or item.get("objectRef") or item.get("ref") or item.get("id")
        else:
            ref = item
        text = _text(ref, label, 1000)
        if text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3FindingsValidationError("A bridge request object is required.")
    raw = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    try:
        return normalize_research_context(raw)["context"]
    except Exception as exc:
        raise PlatformCoreV3FindingsValidationError(f"Invalid research context: {exc}", getattr(exc, "status_code", 400)) from exc


def _project_path(context: dict[str, Any]) -> str:
    return quote(_text(context.get("project_ref"), "project_ref", 1000), safe="")


def _visibility(context: dict[str, Any], value: Any = None) -> str:
    visibility = _text(value or context.get("core_visibility") or "internal", "visibility", 20)
    if visibility not in {"private", "internal", "public"}:
        raise PlatformCoreV3FindingsValidationError("visibility must be private, internal, or public.")
    return "internal" if visibility == "private" else visibility


def normalize_finding(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    source = payload.get("finding") if isinstance(payload.get("finding"), dict) else payload
    finding_id = _text(source.get("id") or source.get("finding_key") or source.get("findingKey"), "finding id", 240, required=False)
    finding_type = _text(source.get("finding_type") or source.get("findingType") or "result", "finding_type", 80)
    if finding_type not in CORE_FINDING_TYPES:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported Core finding_type: {finding_type}")
    status = _text(source.get("status") or "proposed", "finding status", 80)
    if status not in CORE_FINDING_STATUSES:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported Core finding status: {status}")
    statement = _text(source.get("statement") or source.get("finding") or source.get("result"), "finding statement", 8000)
    title = _text(source.get("title") or statement[:120], "finding title", 600)
    method_ref = _text(source.get("method_ref") or source.get("methodRef"), "method_ref", 1000, required=False) or None
    execution_ref = _text(source.get("analysis_run_ref") or source.get("analysisRunRef") or source.get("execution_ref") or source.get("executionRef"), "execution_ref", 1000, required=False) or None
    source_refs = _refs(source.get("source_refs") or source.get("sourceRefs") or source.get("evidence_refs") or source.get("evidenceRefs"), "source_refs")
    uncertainty = _dict(source.get("uncertainty"), "uncertainty")
    limitations = _list(source.get("limitations"), "limitations", 200)
    metadata = _dict(source.get("metadata"), "metadata")
    provenance = _dict(source.get("provenance"), "provenance")
    key = finding_id or f"lab-finding-{_hash({'project': context['project_ref'], 'statement': statement, 'type': finding_type})[:20]}"
    normalized = {
        "schema": FINDING_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "finding_key": key,
        "title": title,
        "statement": statement,
        "finding_type": finding_type,
        "status": status,
        "method_ref": method_ref,
        "analysis_run_ref": execution_ref,
        "source_refs": source_refs,
        "uncertainty": uncertainty,
        "limitations": limitations,
        "metadata": metadata,
        "provenance": provenance,
        "declared_by_lab": True,
        "generated_by_core": False,
        "scientific_validity_certified": False,
    }
    normalized["finding_hash"] = _hash(normalized)
    return {"ok": True, "context": context, "finding": normalized}


def normalize_claim(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("claim") if isinstance(payload.get("claim"), dict) else payload
    is_lab_v062 = any(k in raw for k in ("claimType", "studyId", "evidenceLinks", "scopeNote", "reviewHistory"))
    if is_lab_v062:
        try:
            lab = normalize_lab_claim(raw)
        except Exception as exc:
            raise PlatformCoreV3FindingsValidationError(f"Invalid Lab scientific claim: {exc}", 422) from exc
        claim_type = LAB_TO_CORE_CLAIM_TYPE.get(lab["claimType"], "interpretive")
        status = LAB_TO_CORE_CLAIM_STATUS.get(lab["status"], "proposed")
        claim_key = lab["id"]
        claim_text = lab["statement"]
        scope = {"note": lab.get("scopeNote") or "", "study_id": lab.get("studyId")}
        qualifications = []
        metadata = {
            "lab_claim_schema": lab.get("schema"),
            "lab_claim_type": lab.get("claimType"),
            "lab_claim_status": lab.get("status"),
            "lab_claim_hash": lab.get("claimHash"),
            "lab_review_history": lab.get("reviewHistory", []),
            "lab_evidence_links": lab.get("evidenceLinks", []),
            "lab_conclusion_ids": lab.get("conclusionIds", []),
        }
        provenance = _dict(raw.get("provenance"), "provenance")
    else:
        claim_key = _text(raw.get("id") or raw.get("claim_key") or raw.get("claimKey"), "claim id", 240, required=False)
        claim_text = _text(raw.get("claim_text") or raw.get("claimText") or raw.get("statement"), "claim_text", 8000)
        claim_type = _text(raw.get("claim_type") or raw.get("claimType") or "interpretive", "claim_type", 80)
        status = _text(raw.get("status") or "proposed", "claim status", 80)
        scope = _dict(raw.get("scope"), "scope")
        qualifications = _list(raw.get("qualifications"), "qualifications", 200)
        metadata = _dict(raw.get("metadata"), "metadata")
        provenance = _dict(raw.get("provenance"), "provenance")
    if claim_type not in CORE_CLAIM_TYPES:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported Core claim_type: {claim_type}")
    if status not in CORE_CLAIM_STATUSES:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported Core claim status: {status}")
    polarity = _text(raw.get("polarity") or "not_applicable", "polarity", 40)
    if polarity not in CORE_POLARITIES:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported polarity: {polarity}")
    subject_ref = _text(raw.get("subject_ref") or raw.get("subjectRef"), "subject_ref", 1000, required=False) or None
    predicate = _text(raw.get("predicate"), "predicate", 500, required=False) or None
    object_ref = _text(raw.get("object_ref") or raw.get("objectRef"), "object_ref", 1000, required=False) or None
    if any(x for x in (subject_ref, predicate, object_ref)) and not all(x for x in (subject_ref, predicate, object_ref)):
        raise PlatformCoreV3FindingsValidationError("subject_ref, predicate, and object_ref must be supplied together.")
    if polarity in {"affirmed", "denied"} and not all(x for x in (subject_ref, predicate, object_ref)):
        raise PlatformCoreV3FindingsValidationError("affirmed/denied polarity requires a complete structured claim.")
    key = claim_key or f"lab-claim-{_hash({'project': context['project_ref'], 'claim': claim_text, 'type': claim_type})[:20]}"
    normalized = {
        "schema": CLAIM_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "claim_key": key,
        "claim_text": claim_text,
        "claim_type": claim_type,
        "status": status,
        "subject_ref": subject_ref,
        "predicate": predicate,
        "object_ref": object_ref,
        "polarity": polarity,
        "scope": scope,
        "uncertainty": _dict(raw.get("uncertainty"), "uncertainty"),
        "qualifications": qualifications,
        "metadata": metadata,
        "provenance": provenance,
        "declared_by_lab": True,
        "generated_by_core": False,
        "truth_determined_by_bridge": False,
    }
    normalized["claim_hash"] = _hash(normalized)
    return {"ok": True, "context": context, "claim": normalized}


def _wrap(target_path: str, data: dict[str, Any], context: dict[str, Any], schema: str) -> dict[str, Any]:
    return {
        "ok": True,
        "schema": schema,
        "target_path": target_path,
        "automatic_submission": False,
        "automatic_core_mutation": False,
        "automatic_scientific_execution": False,
        "scientific_validity_certified": False,
        "data": data,
        "request_body": {"data": data},
        "context": context,
        "payload_hash": _hash(data),
    }


def build_core_finding_binding(payload: dict[str, Any]) -> dict[str, Any]:
    out = normalize_finding(payload); context = out["context"]; finding = out["finding"]
    data = {
        k: finding[k] for k in (
            "finding_key", "title", "statement", "finding_type", "status", "method_ref",
            "analysis_run_ref", "source_refs", "uncertainty", "limitations"
        )
    }
    data["metadata"] = {
        "authority": PRODUCT_REF,
        "context_ref": context["context_ref"],
        "session_id": context.get("session_id"),
        "lab_release_version": LAB_VERSION,
        "lab_finding_hash": finding["finding_hash"],
        "underlying_finding_remains_authoritative_in_lab": True,
        "lab_metadata": finding["metadata"],
    }
    data["provenance"] = {
        "source": "sustainable-catalyst-lab",
        "researcher_ref": context.get("researcher_ref"),
        "agent_ref": context.get("agent_ref"),
        "lab_provenance": finding["provenance"],
    }
    data["created_by"] = context.get("researcher_ref") or context.get("agent_ref") or "sustainable-catalyst-lab"
    path = f"{CORE_INTELLIGENCE_PREFIX}/projects/{_project_path(context)}/findings"
    return _wrap(path, data, context, BRIDGE_SCHEMA)


def build_core_claim_binding(payload: dict[str, Any]) -> dict[str, Any]:
    out = normalize_claim(payload); context = out["context"]; claim = out["claim"]
    data = {
        k: claim[k] for k in (
            "claim_key", "claim_text", "claim_type", "status", "subject_ref", "predicate",
            "object_ref", "polarity", "scope", "uncertainty", "qualifications"
        )
    }
    data["metadata"] = {
        "authority": PRODUCT_REF,
        "context_ref": context["context_ref"],
        "session_id": context.get("session_id"),
        "lab_release_version": LAB_VERSION,
        "lab_claim_hash": claim["claim_hash"],
        "underlying_claim_remains_authoritative_in_lab": True,
        "lab_metadata": claim["metadata"],
    }
    data["provenance"] = {
        "source": "sustainable-catalyst-lab",
        "researcher_ref": context.get("researcher_ref"),
        "agent_ref": context.get("agent_ref"),
        "lab_provenance": claim["provenance"],
    }
    data["created_by"] = context.get("researcher_ref") or context.get("agent_ref") or "sustainable-catalyst-lab"
    path = f"{CORE_INTELLIGENCE_PREFIX}/projects/{_project_path(context)}/claims"
    return _wrap(path, data, context, BRIDGE_SCHEMA)


def build_core_evidence_link_binding(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    e = payload.get("evidence_link") if isinstance(payload.get("evidence_link"), dict) else payload
    target_type = _text(e.get("target_type") or e.get("targetType") or "claim", "target_type", 40)
    if target_type not in {"finding", "interpretation", "claim"}:
        raise PlatformCoreV3FindingsValidationError("target_type must be finding, interpretation, or claim.")
    relation = _text(e.get("relation") or e.get("role") or "supports", "relation", 80)
    relation = LAB_TO_CORE_EVIDENCE_RELATION.get(relation, relation)
    if relation not in CORE_EVIDENCE_RELATIONS:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported Core evidence relation: {relation}")
    evidence_ref = _text(e.get("evidence_ref") or e.get("evidenceRef") or e.get("ref"), "evidence_ref", 1000)
    target_id = _text(e.get("target_id") or e.get("targetId"), "target_id", 1000)
    key = _text(e.get("id") or e.get("evidence_link_key") or e.get("evidenceLinkKey"), "evidence link id", 240, required=False)
    if not key:
        key = f"lab-evidence-link-{_hash({'e': evidence_ref, 't': target_type, 'id': target_id, 'r': relation})[:20]}"
    assessment = _dict(e.get("assessment"), "assessment")
    if isinstance(e.get("lab_evidence_assessment"), dict):
        try:
            assessment["lab_evidence_boundary"] = normalize_lab_evidence_assessment(e["lab_evidence_assessment"])
        except Exception as exc:
            raise PlatformCoreV3FindingsValidationError(f"Invalid Lab evidence assessment: {exc}", 422) from exc
    data = {
        "evidence_link_key": key,
        "evidence_ref": evidence_ref,
        "evidence_kind": _text(e.get("evidence_kind") or e.get("evidenceKind") or "scientific", "evidence_kind", 120),
        "target_type": target_type,
        "target_id": target_id,
        "relation": relation,
        "locator": _text(e.get("locator"), "locator", 2000, required=False) or None,
        "declared_strength": _text(e.get("declared_strength") or e.get("declaredStrength"), "declared_strength", 120, required=False) or None,
        "assessment_basis": _text(e.get("assessment_basis") or e.get("assessmentBasis"), "assessment_basis", 4000, required=False) or None,
        "assessment": assessment,
        "uncertainty": _dict(e.get("uncertainty"), "uncertainty"),
        "metadata": {
            "authority": PRODUCT_REF,
            "context_ref": context["context_ref"],
            "session_id": context.get("session_id"),
            "lab_release_version": LAB_VERSION,
            "lab_relation": e.get("relation") or e.get("role"),
            "evidence_strength_is_declared_not_core_judged": True,
            "lab_metadata": _dict(e.get("metadata"), "metadata"),
        },
        "provenance": {"source": "sustainable-catalyst-lab", "lab_provenance": _dict(e.get("provenance"), "provenance")},
        "created_by": context.get("researcher_ref") or context.get("agent_ref") or "sustainable-catalyst-lab",
    }
    path = f"{CORE_INTELLIGENCE_PREFIX}/projects/{_project_path(context)}/evidence-links"
    return _wrap(path, data, context, EVIDENCE_LINK_SCHEMA)


def build_core_contradiction_binding(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    c = payload.get("contradiction") if isinstance(payload.get("contradiction"), dict) else payload
    claim_a = _text(c.get("claim_a_id") or c.get("claimAId"), "claim_a_id", 1000)
    claim_b = _text(c.get("claim_b_id") or c.get("claimBId"), "claim_b_id", 1000)
    if claim_a == claim_b:
        raise PlatformCoreV3FindingsValidationError("claim_a_id and claim_b_id must differ.")
    key = _text(c.get("id") or c.get("contradiction_key") or c.get("contradictionKey"), "contradiction id", 240, required=False)
    if not key:
        key = f"lab-contradiction-{_hash({'a': claim_a, 'b': claim_b})[:20]}"
    status = _text(c.get("status") or "unresolved", "status", 80)
    if status not in {"candidate", "recorded", "unresolved", "qualified", "resolved_externally", "superseded", "withdrawn"}:
        raise PlatformCoreV3FindingsValidationError("Unsupported contradiction status.")
    data = {
        "contradiction_key": key,
        "claim_a_id": claim_a,
        "claim_b_id": claim_b,
        "contradiction_type": _text(c.get("contradiction_type") or c.get("contradictionType") or "declared", "contradiction_type", 120),
        "status": status,
        "basis_refs": _refs(c.get("basis_refs") or c.get("basisRefs"), "basis_refs"),
        "rationale": _text(c.get("rationale"), "rationale", 6000, required=False) or None,
        "provenance": {"source": "sustainable-catalyst-lab", "context_ref": context["context_ref"], "lab_provenance": _dict(c.get("provenance"), "provenance")},
        "created_by": context.get("researcher_ref") or context.get("agent_ref") or "sustainable-catalyst-lab",
    }
    path = f"{CORE_INTELLIGENCE_PREFIX}/projects/{_project_path(context)}/contradictions"
    return _wrap(path, data, context, BRIDGE_SCHEMA)


def build_core_validation_challenge_binding(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    v = payload.get("validation") if isinstance(payload.get("validation"), dict) else payload.get("challenge") if isinstance(payload.get("challenge"), dict) else payload
    challenge_type = _text(v.get("challenge_type") or v.get("challengeType") or "other", "challenge_type", 80)
    if challenge_type not in CORE_CHALLENGE_TYPES:
        raise PlatformCoreV3FindingsValidationError(f"Unsupported Core challenge_type: {challenge_type}")
    title = _text(v.get("title"), "title", 600)
    key = _text(v.get("id") or v.get("challenge_key") or v.get("challengeKey"), "challenge id", 240, required=False)
    if not key:
        key = f"lab-challenge-{_hash({'project': context['project_ref'], 'type': challenge_type, 'title': title})[:20]}"
    status = _text(v.get("status") or "open", "status", 80)
    if status not in {"open", "recorded", "responded", "revised", "closed", "withdrawn"}:
        raise PlatformCoreV3FindingsValidationError("Unsupported challenge status.")
    metadata = _dict(v.get("metadata"), "metadata")
    if isinstance(v.get("lab_evidence_assessment"), dict):
        try:
            metadata["lab_evidence_boundary"] = normalize_lab_evidence_assessment(v["lab_evidence_assessment"])
        except Exception as exc:
            raise PlatformCoreV3FindingsValidationError(f"Invalid Lab evidence assessment: {exc}", 422) from exc
    data = {
        "challenge_key": key,
        "project_ref": context["project_ref"],
        "challenge_type": challenge_type,
        "title": title,
        "description": _text(v.get("description") or v.get("statement"), "description", 8000, required=False) or None,
        "status": status,
        "source_ref": _text(v.get("source_ref") or v.get("sourceRef"), "source_ref", 1000, required=False) or None,
        "raised_by_ref": _text(v.get("raised_by_ref") or v.get("raisedByRef") or context.get("researcher_ref") or context.get("agent_ref"), "raised_by_ref", 1000, required=False) or None,
        "visibility": _visibility(context, v.get("visibility")),
        "metadata": {
            "authority": PRODUCT_REF,
            "context_ref": context["context_ref"],
            "session_id": context.get("session_id"),
            "lab_release_version": LAB_VERSION,
            "challenge_state_is_declared_not_core_decided": True,
            "lab_metadata": metadata,
        },
        "provenance": {"source": "sustainable-catalyst-lab", "lab_provenance": _dict(v.get("provenance"), "provenance")},
        "created_by": context.get("researcher_ref") or context.get("agent_ref") or "sustainable-catalyst-lab",
    }
    return _wrap(f"{CORE_VALIDATION_PREFIX}/challenges", data, context, VALIDATION_SCHEMA)


def build_core_replication_binding(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    r = payload.get("replication") if isinstance(payload.get("replication"), dict) else payload
    challenge_id = _text(r.get("challenge_id") or r.get("challengeId"), "challenge_id", 1000)
    target_ref = _text(r.get("target_ref") or r.get("targetRef"), "target_ref", 1000)
    key = _text(r.get("id") or r.get("attempt_key") or r.get("attemptKey"), "replication id", 240, required=False)
    if not key:
        key = f"lab-replication-{_hash({'challenge': challenge_id, 'target': target_ref, 'execution': r.get('execution_ref') or r.get('executionRef')})[:20]}"
    data = {
        "attempt_key": key,
        "challenge_id": challenge_id,
        "project_ref": context["project_ref"],
        "target_ref": target_ref,
        "protocol_ref": _text(r.get("protocol_ref") or r.get("protocolRef"), "protocol_ref", 1000, required=False) or None,
        "execution_ref": _text(r.get("execution_ref") or r.get("executionRef"), "execution_ref", 1000, required=False) or None,
        "package_ref": _text(r.get("package_ref") or r.get("packageRef"), "package_ref", 1000, required=False) or None,
        "result_status": _text(r.get("result_status") or r.get("resultStatus") or "recorded", "result_status", 120),
        "evidence": _refs(r.get("evidence") or r.get("evidence_refs") or r.get("evidenceRefs"), "evidence"),
        "visibility": _visibility(context, r.get("visibility")),
        "provenance": {
            "source": "sustainable-catalyst-lab",
            "context_ref": context["context_ref"],
            "replication_result_is_declared_not_core_certified": True,
            "lab_provenance": _dict(r.get("provenance"), "provenance"),
        },
        "created_by": context.get("researcher_ref") or context.get("agent_ref") or "sustainable-catalyst-lab",
    }
    return _wrap(f"{CORE_VALIDATION_PREFIX}/replications", data, context, REPLICATION_SCHEMA)


def map_legacy_scientific_claim(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("claim") if isinstance(payload.get("claim"), dict) else payload.get("scientific_claim") if isinstance(payload.get("scientific_claim"), dict) else None
    if not isinstance(raw, dict):
        raise PlatformCoreV3FindingsValidationError("claim or scientific_claim is required.")
    normalized = normalize_claim({"context": context, "claim": raw})
    binding = build_core_claim_binding({"context": context, "claim": raw})
    evidence_bindings = []
    try:
        lab = normalize_lab_claim(raw)
    except Exception:
        lab = None
    if lab:
        for link in lab.get("evidenceLinks", []):
            evidence_bindings.append(build_core_evidence_link_binding({
                "context": context,
                "evidence_link": {
                    "id": link.get("id"),
                    "evidence_ref": link.get("ref"),
                    "target_type": "claim",
                    "target_id": normalized["claim"]["claim_key"],
                    "relation": link.get("role"),
                    "assessment": {"lab_source_type": link.get("sourceType"), "lab_link_hash": link.get("linkHash"), "note": link.get("note")},
                },
            }))
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "normalized_claim": normalized["claim"],
        "core_claim_binding": binding,
        "core_evidence_bindings": evidence_bindings,
        "automatic_submission": False,
        "automatic_claim_inference": False,
        "automatic_scientific_certification": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "platform-core-v3-findings-claims-evidence-validation-ready",
        "schema": BRIDGE_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "finding_contract": "sc.research.finding-claim-evidence.v1",
        "validation_contract": "sc.research.validation-challenge.v1",
        "automatic_core_submission": False,
        "automatic_claim_inference": False,
        "automatic_finding_generation": False,
        "automatic_evidence_judgment": False,
        "automatic_contradiction_resolution": False,
        "automatic_replication_certification": False,
        "scientific_validity_certified": False,
        "truth_determined": False,
    }


def manifest() -> dict[str, Any]:
    return {
        **health(),
        "bridge_version": FEATURE_VERSION,
        "core_paths": {
            "findings": f"{CORE_INTELLIGENCE_PREFIX}/projects/{{project_id}}/findings",
            "claims": f"{CORE_INTELLIGENCE_PREFIX}/projects/{{project_id}}/claims",
            "evidence_links": f"{CORE_INTELLIGENCE_PREFIX}/projects/{{project_id}}/evidence-links",
            "contradictions": f"{CORE_INTELLIGENCE_PREFIX}/projects/{{project_id}}/contradictions",
            "validation_challenges": f"{CORE_VALIDATION_PREFIX}/challenges",
            "replications": f"{CORE_VALIDATION_PREFIX}/replications",
        },
        "boundaries": {
            "lab_declares_findings_claims_evidence_assessments": True,
            "core_records_reference_first_research_intelligence": True,
            "lab_remains_authoritative_for_underlying_science": True,
            "human_review_boundaries_preserved": True,
            "core_generates_findings_or_claims": False,
            "bridge_ranks_evidence": False,
            "bridge_resolves_contradictions": False,
            "bridge_certifies_replication": False,
            "bridge_certifies_scientific_validity": False,
            "bridge_determines_truth": False,
        },
        "next_release": "0.109.0 Visual Reasoning & Scientific Scene Bridge",
    }
