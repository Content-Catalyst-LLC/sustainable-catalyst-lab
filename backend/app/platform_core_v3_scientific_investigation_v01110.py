from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_research_context_v01060 import normalize_research_context

LAB_VERSION = "0.111.0"
FEATURE_VERSION = "0.111.0"
MINIMUM_CORE_RELEASE = "3.0.0"
BRIDGE_SCHEMA = "sc-lab-platform-core-v3-scientific-investigation-runtime/0.111.0"
INVESTIGATION_SCHEMA = "sc-lab-core-v3-scientific-investigation/0.111.0"
PLAN_SCHEMA = "sc-lab-core-v3-scientific-investigation-plan/0.111.0"
CONTINUITY_SCHEMA = "sc-lab-core-v3-scientific-investigation-continuity/0.111.0"
CORE_UNIFIED_RUNTIME_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
CORE_INVESTIGATION_BINDING_ENDPOINT = "/v1/research/unified-runtime/investigation-bindings"
CORE_OBJECT_BINDING_ENDPOINT = "/v1/research/unified-runtime/object-bindings"
CORE_EXECUTION_BINDING_ENDPOINT = "/v1/research/unified-runtime/execution-bindings"
CORE_VISUAL_BINDING_ENDPOINT = "/v1/research/unified-runtime/visual-bindings"
CORE_VALIDATION_BINDING_ENDPOINT = "/v1/research/unified-runtime/validation-bindings"
CORE_PACKAGE_BINDING_ENDPOINT = "/v1/research/unified-runtime/package-bindings"

INVESTIGATION_TYPES = {
    "scientific-study", "experimental", "computational", "replication", "causal-analysis",
    "model-assessment", "evidence-synthesis", "forensic-scientific", "mixed", "other",
}
STATUSES = {"draft", "active", "paused", "review", "complete", "archived", "withdrawn"}
REF_GROUPS = (
    "object_refs", "dataset_refs", "model_refs", "experiment_refs", "analysis_refs",
    "execution_refs", "evidence_refs", "claim_refs", "hypothesis_refs", "visual_refs",
    "validation_refs", "package_refs", "protocol_refs", "method_refs", "source_refs",
)


class PlatformCoreV3ScientificInvestigationError(ValueError):
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
        raise PlatformCoreV3ScientificInvestigationError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3ScientificInvestigationError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3ScientificInvestigationError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _items(value: Any, label: str, maximum: int = 5000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3ScientificInvestigationError(f"{label} must be an array.")
    if len(value) > maximum:
        raise PlatformCoreV3ScientificInvestigationError(f"{label} exceeds {maximum} entries.")
    return copy.deepcopy(value)


def _refs(value: Any, label: str, prefix: str = "lab:object") -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in _items(value, label):
        if isinstance(item, str):
            ref = _text(item, label, 1200)
        elif isinstance(item, dict):
            ref = None
            for key in (
                "object_ref", "objectRef", "dataset_ref", "datasetRef", "model_ref", "modelRef",
                "experiment_ref", "experimentRef", "analysis_ref", "analysisRef", "execution_ref", "executionRef",
                "evidence_ref", "evidenceRef", "claim_ref", "claimRef", "hypothesis_ref", "hypothesisRef",
                "visual_ref", "visualRef", "validation_ref", "validationRef", "package_ref", "packageRef",
                "protocol_ref", "protocolRef", "method_ref", "methodRef", "source_ref", "sourceRef", "ref",
            ):
                if item.get(key):
                    ref = _text(item[key], label, 1200)
                    break
            if not ref:
                ident = item.get("id") or item.get("key") or item.get("name")
                ref = f"{prefix}:{_text(ident, label, 400)}" if ident else f"{prefix}:sha256:{_hash(item)}"
        else:
            raise PlatformCoreV3ScientificInvestigationError(f"{label} entries must be references or objects.")
        if ref not in seen:
            out.append(ref)
            seen.add(ref)
    return out


def _context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ScientificInvestigationError("A scientific investigation request object is required.")
    raw = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    try:
        return normalize_research_context(raw)["context"]
    except Exception as exc:
        raise PlatformCoreV3ScientificInvestigationError(f"Invalid research context: {exc}", getattr(exc, "status_code", 400)) from exc


def _visibility(context: dict[str, Any], value: Any = None) -> str:
    v = _text(value or context.get("core_visibility") or "internal", "visibility", 20)
    if v not in {"private", "internal", "public"}:
        raise PlatformCoreV3ScientificInvestigationError("visibility must be private, internal, or public.")
    return "internal" if v == "private" else v


def _kind(raw: dict[str, Any]) -> str:
    value = _text(raw.get("investigation_type") or raw.get("investigationType") or raw.get("studyType") or "scientific-study", "investigation_type", 80)
    aliases = {
        "observational": "scientific-study", "experiment": "experimental", "experimental-study": "experimental",
        "computational-study": "computational", "modeling": "computational", "replication-study": "replication",
        "causal": "causal-analysis", "systematic-review": "evidence-synthesis", "meta-analysis": "evidence-synthesis",
        "forensic": "forensic-scientific",
    }
    value = aliases.get(value, value)
    if value not in INVESTIGATION_TYPES:
        raise PlatformCoreV3ScientificInvestigationError(f"Unsupported investigation_type: {value}")
    return value


def _collect_refs(raw: dict[str, Any]) -> dict[str, list[str]]:
    aliases = {
        "object_refs": ("object_refs", "objectRefs", "objects"),
        "dataset_refs": ("dataset_refs", "datasetRefs", "datasets"),
        "model_refs": ("model_refs", "modelRefs", "models"),
        "experiment_refs": ("experiment_refs", "experimentRefs", "experiments"),
        "analysis_refs": ("analysis_refs", "analysisRefs", "analyses", "analysis_runs", "analysisRuns"),
        "execution_refs": ("execution_refs", "executionRefs", "executions", "runs"),
        "evidence_refs": ("evidence_refs", "evidenceRefs", "evidence"),
        "claim_refs": ("claim_refs", "claimRefs", "claims"),
        "hypothesis_refs": ("hypothesis_refs", "hypothesisRefs"),
        "visual_refs": ("visual_refs", "visualRefs", "visuals", "figures"),
        "validation_refs": ("validation_refs", "validationRefs", "validations", "challenges"),
        "package_refs": ("package_refs", "packageRefs", "packages", "reproducibility_packages", "reproducibilityPackages"),
        "protocol_refs": ("protocol_refs", "protocolRefs", "protocols"),
        "method_refs": ("method_refs", "methodRefs", "methods"),
        "source_refs": ("source_refs", "sourceRefs", "sources"),
    }
    prefixes = {
        "object_refs": "lab:object", "dataset_refs": "lab:dataset", "model_refs": "lab:model",
        "experiment_refs": "lab:experiment", "analysis_refs": "lab:analysis", "execution_refs": "lab:execution",
        "evidence_refs": "lab:evidence", "claim_refs": "lab:claim", "hypothesis_refs": "lab:hypothesis",
        "visual_refs": "lab:visual", "validation_refs": "lab:validation", "package_refs": "lab:research-package",
        "protocol_refs": "lab:protocol", "method_refs": "lab:method", "source_refs": "lab:source",
    }
    out: dict[str, list[str]] = {}
    for canonical, keys in aliases.items():
        value = None
        for key in keys:
            if key in raw and raw.get(key) is not None:
                value = raw.get(key)
                break
        out[canonical] = _refs(value, canonical, prefixes[canonical]) if value is not None else []
    return out


def normalize_investigation(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("investigation") if isinstance(payload.get("investigation"), dict) else payload
    raw = _dict(raw, "investigation")
    kind = _kind(raw)
    title = _text(raw.get("title") or raw.get("name") or "Scientific investigation", "title", 1000)
    ident = _text(raw.get("id") or raw.get("investigation_key") or raw.get("investigationKey"), "investigation id", 400, required=False)
    if not ident:
        ident = f"investigation-{_hash({'project': context['project_ref'], 'title': title, 'kind': kind})[:20]}"
    investigation_ref = _text(raw.get("investigation_ref") or raw.get("investigationRef"), "investigation_ref", 1200, required=False) or f"lab:scientific-investigation:{ident}"
    status = _text(raw.get("status") or "draft", "status", 80)
    if status not in STATUSES:
        raise PlatformCoreV3ScientificInvestigationError(f"Unsupported investigation status: {status}")
    refs = _collect_refs(raw)
    metadata = _dict(raw.get("metadata"), "metadata")
    provenance = _dict(raw.get("provenance"), "provenance")
    questions = [_text(x, "research_questions", 4000) for x in _items(raw.get("research_questions") or raw.get("researchQuestions"), "research_questions")]
    declared_hypotheses = [_text(x, "declared_hypotheses", 4000) for x in _items(raw.get("declared_hypotheses") or raw.get("declaredHypotheses"), "declared_hypotheses")]
    inv = {
        "schema": INVESTIGATION_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "investigation_id": ident,
        "investigation_ref": investigation_ref,
        "investigation_type": kind,
        "title": title,
        "description": _text(raw.get("description") or raw.get("rationale"), "description", 12000, required=False) or None,
        "status": status,
        "research_questions": questions,
        "declared_hypotheses": declared_hypotheses,
        **refs,
        "visibility": _visibility(context, raw.get("visibility")),
        "lab_metadata": metadata,
        "lab_provenance": provenance,
        "underlying_investigation_remains_authoritative_in_lab": True,
        "core_runs_scientific_investigation": False,
        "core_infers_findings": False,
        "core_ranks_evidence": False,
        "core_selects_hypotheses": False,
        "core_infers_causality": False,
        "core_certifies_scientific_validity": False,
        "core_determines_truth": False,
    }
    inv["investigation_hash"] = _hash(inv)
    return {"ok": True, "context": context, "investigation": inv}


def build_core_investigation_binding(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_investigation(payload)
    context = normalized["context"]
    inv = normalized["investigation"]
    if not context.get("session_id"):
        raise PlatformCoreV3ScientificInvestigationError("session_id is required to build a Core investigation binding.")
    data = {
        "session_id": context["session_id"],
        "investigation_ref": inv["investigation_ref"],
        "investigation_type": inv["investigation_type"],
        "evidence_refs": inv["evidence_refs"],
        "claim_refs": inv["claim_refs"],
        "hypothesis_refs": inv["hypothesis_refs"],
        "visibility": inv["visibility"],
        "metadata": {
            "schema": INVESTIGATION_SCHEMA,
            "authority": PRODUCT_REF,
            "lab_release_version": LAB_VERSION,
            "context_ref": context["context_ref"],
            "project_ref": context["project_ref"],
            "workflow_ref": context.get("workflow_ref"),
            "project_state_ref": context.get("project_state_ref"),
            "title": inv["title"],
            "description": inv["description"],
            "status": inv["status"],
            "research_questions": inv["research_questions"],
            "declared_hypotheses": inv["declared_hypotheses"],
            "object_refs": inv["object_refs"],
            "dataset_refs": inv["dataset_refs"],
            "model_refs": inv["model_refs"],
            "experiment_refs": inv["experiment_refs"],
            "analysis_refs": inv["analysis_refs"],
            "execution_refs": inv["execution_refs"],
            "visual_refs": inv["visual_refs"],
            "validation_refs": inv["validation_refs"],
            "package_refs": inv["package_refs"],
            "protocol_refs": inv["protocol_refs"],
            "method_refs": inv["method_refs"],
            "source_refs": inv["source_refs"],
            "investigation_hash": inv["investigation_hash"],
            "lab_metadata": inv["lab_metadata"],
            "lab_provenance": inv["lab_provenance"],
            "underlying_investigation_remains_authoritative_in_lab": True,
            "core_records_investigation_context_only": True,
        },
    }
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "core_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "target_endpoint": CORE_INVESTIGATION_BINDING_ENDPOINT,
        "method": "POST",
        "data": data,
        "request_body": {"data": data},
        "automatic_submission": False,
        "automatic_core_mutation": False,
        "automatic_execution": False,
        "automatic_hypothesis_selection": False,
        "automatic_truth_determination": False,
    }


def bridge_evidence_context(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_investigation(payload)
    inv = normalized["investigation"]
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "investigation_ref": inv["investigation_ref"],
        "evidence_refs": inv["evidence_refs"],
        "source_refs": inv["source_refs"],
        "object_refs": inv["object_refs"],
        "evidence_count": len(inv["evidence_refs"]),
        "source_count": len(inv["source_refs"]),
        "evidence_relationships_are_declared_not_ranked": True,
        "automatic_evidence_ranking": False,
        "automatic_credibility_scoring": False,
        "automatic_truth_determination": False,
    }


def bridge_reasoning_context(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_investigation(payload)
    inv = normalized["investigation"]
    raw = payload.get("investigation") if isinstance(payload.get("investigation"), dict) else payload
    contradictions = _items(raw.get("contradictions"), "contradictions")
    competing = _items(raw.get("competing_hypotheses") or raw.get("competingHypotheses"), "competing_hypotheses")
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "investigation_ref": inv["investigation_ref"],
        "claim_refs": inv["claim_refs"],
        "hypothesis_refs": inv["hypothesis_refs"],
        "declared_hypotheses": inv["declared_hypotheses"],
        "contradictions": contradictions,
        "competing_hypotheses": competing,
        "reasoning_state_is_declared_not_core_decided": True,
        "automatic_claim_support_inference": False,
        "automatic_contradiction_resolution": False,
        "automatic_hypothesis_ranking": False,
        "automatic_causal_inference": False,
    }


def bridge_scientific_assets(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_investigation(payload)
    inv = normalized["investigation"]
    groups = {key: inv[key] for key in REF_GROUPS if key not in {"evidence_refs", "claim_refs", "hypothesis_refs"}}
    endpoint_hints = {
        "object_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "dataset_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "model_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "experiment_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "analysis_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "execution_refs": CORE_EXECUTION_BINDING_ENDPOINT,
        "visual_refs": CORE_VISUAL_BINDING_ENDPOINT,
        "validation_refs": CORE_VALIDATION_BINDING_ENDPOINT,
        "package_refs": CORE_PACKAGE_BINDING_ENDPOINT,
        "protocol_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "method_refs": CORE_OBJECT_BINDING_ENDPOINT,
        "source_refs": CORE_OBJECT_BINDING_ENDPOINT,
    }
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "investigation_ref": inv["investigation_ref"],
        "asset_groups": groups,
        "asset_counts": {k: len(v) for k, v in groups.items()},
        "core_binding_endpoint_hints": endpoint_hints,
        "references_require_existing_or_separate_specialist_bindings": True,
        "automatic_binding_submission": False,
        "automatic_artifact_transformation": False,
    }


def build_runtime_integration_plan(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_investigation(payload)
    inv = normalized["investigation"]
    binding = build_core_investigation_binding(payload)
    assets = bridge_scientific_assets(payload)
    requirements = []
    for group, refs in assets["asset_groups"].items():
        if refs:
            requirements.append({
                "group": group,
                "refs": refs,
                "count": len(refs),
                "core_endpoint": assets["core_binding_endpoint_hints"][group],
                "state": "reference-declared; ensure corresponding binding exists separately",
            })
    plan = {
        "schema": PLAN_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "investigation_ref": inv["investigation_ref"],
        "primary_operation": {
            "method": "POST",
            "endpoint": CORE_INVESTIGATION_BINDING_ENDPOINT,
            "data": binding["data"],
            "request_body": binding["request_body"],
        },
        "related_binding_requirements": requirements,
        "required_evidence_refs": inv["evidence_refs"],
        "required_claim_refs": inv["claim_refs"],
        "required_hypothesis_refs": inv["hypothesis_refs"],
        "automatic_submission": False,
        "automatic_execution": False,
        "automatic_investigation_run": False,
        "automatic_findings_inference": False,
        "automatic_hypothesis_selection": False,
        "automatic_truth_determination": False,
    }
    plan["plan_hash"] = _hash(plan)
    return {"ok": True, "context": normalized["context"], "investigation": inv, "plan": plan}


def check_investigation_continuity(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_investigation(payload)
    context = normalized["context"]
    inv = normalized["investigation"]
    expected = _dict(payload.get("expected_context"), "expected_context")
    mismatches = []
    for key in ("project_ref", "session_id", "workflow_ref", "project_state_ref", "context_ref"):
        if expected.get(key) is not None and str(expected.get(key)) != str(context.get(key)):
            mismatches.append({"field": key, "expected": expected.get(key), "actual": context.get(key)})
    duplicate_groups = {k: len(inv[k]) - len(set(inv[k])) for k in REF_GROUPS if len(inv[k]) != len(set(inv[k]))}
    return {
        "ok": not mismatches,
        "schema": CONTINUITY_SCHEMA,
        "investigation_ref": inv["investigation_ref"],
        "context_ref": context["context_ref"],
        "project_ref": context["project_ref"],
        "session_id": context.get("session_id"),
        "mismatches": mismatches,
        "duplicate_reference_groups": duplicate_groups,
        "reference_continuity_valid": not mismatches and not duplicate_groups,
        "scientific_validity_assessed": False,
        "causal_validity_assessed": False,
        "evidence_quality_ranked": False,
    }


def map_legacy_scientific_study(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    study = payload.get("study") if isinstance(payload.get("study"), dict) else payload.get("scientific_study") if isinstance(payload.get("scientific_study"), dict) else None
    if not isinstance(study, dict):
        raise PlatformCoreV3ScientificInvestigationError("study or scientific_study is required.")
    sid = _text(study.get("id") or "legacy-study", "study id", 400)
    hypotheses = _items(study.get("hypotheses"), "hypotheses")
    hypothesis_refs = []
    for index, item in enumerate(hypotheses):
        if isinstance(item, dict) and (item.get("hypothesis_ref") or item.get("hypothesisRef") or item.get("id")):
            hypothesis_refs.extend(_refs([item], "hypotheses", "lab:hypothesis"))
        elif str(item or "").strip():
            hypothesis_refs.append(f"lab:hypothesis:{sid}:{index+1}:{_hash(str(item))[:12]}")
    inv = {
        "id": sid,
        "investigation_ref": f"lab:scientific-study:{sid}",
        "investigation_type": study.get("studyType") or "scientific-study",
        "title": study.get("title") or "Scientific study",
        "description": study.get("rationale"),
        "status": "complete" if str(study.get("status")) in {"complete", "completed", "closed"} else "active" if str(study.get("status")) in {"active", "running"} else "draft",
        "research_questions": [study.get("researchQuestion")] if study.get("researchQuestion") else [],
        "declared_hypotheses": [str(x) for x in hypotheses if not isinstance(x, dict)],
        "hypothesis_refs": hypothesis_refs,
        "evidence_refs": study.get("evidenceRefs") or study.get("evidence_refs") or [],
        "protocol_refs": study.get("protocolRefs") or study.get("protocol_refs") or [],
        "execution_refs": study.get("executionRefs") or study.get("execution_refs") or [],
        "visual_refs": study.get("visualRefs") or study.get("visual_refs") or [],
        "package_refs": study.get("packageRefs") or study.get("package_refs") or [],
        "metadata": {"legacy_schema": study.get("schema"), "legacy_study_hash": study.get("studyHash"), "legacy_status": study.get("status")},
        "provenance": {"legacy_source": "scientific-study-lifecycle-v0.61.0"},
    }
    normalized = normalize_investigation({"context": context, "investigation": inv})
    binding = build_core_investigation_binding({"context": context, "investigation": inv})
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "legacy_source": "scientific-study-lifecycle-v0.61.0",
        "investigation": normalized["investigation"],
        "core_binding": binding,
        "legacy_hypothesis_text_promoted_to_truth": False,
        "automatic_submission": False,
        "automatic_execution": False,
    }


def map_legacy_argumentation_case(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    case = payload.get("case") if isinstance(payload.get("case"), dict) else payload.get("argumentation_case") if isinstance(payload.get("argumentation_case"), dict) else None
    if not isinstance(case, dict):
        raise PlatformCoreV3ScientificInvestigationError("case or argumentation_case is required.")
    cid = _text(case.get("id") or "legacy-argumentation", "case id", 400)
    hypotheses = case.get("hypotheses") if isinstance(case.get("hypotheses"), list) else []
    hypothesis_refs = _refs(hypotheses, "hypotheses", "lab:hypothesis")
    evidence = case.get("evidenceLinks") or case.get("evidence_links") or case.get("evidenceRefs") or case.get("evidence_refs") or []
    inv = {
        "id": cid,
        "investigation_ref": f"lab:scientific-argumentation:{cid}",
        "investigation_type": "scientific-study",
        "title": case.get("title") or "Scientific argumentation case",
        "description": case.get("researchQuestion") or case.get("question") or case.get("description"),
        "status": "review" if case.get("review") or case.get("reviews") else "active",
        "hypothesis_refs": hypothesis_refs,
        "evidence_refs": evidence,
        "claim_refs": case.get("claimRefs") or case.get("claim_refs") or [],
        "validation_refs": case.get("testRefs") or case.get("test_refs") or [],
        "metadata": {"legacy_schema": case.get("schema"), "legacy_case_hash": case.get("caseHash") or case.get("argumentationHash")},
        "provenance": {"legacy_source": "scientific-argumentation-v0.66.0"},
    }
    normalized = normalize_investigation({"context": context, "investigation": inv})
    binding = build_core_investigation_binding({"context": context, "investigation": inv})
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "legacy_source": "scientific-argumentation-v0.66.0",
        "investigation": normalized["investigation"],
        "core_binding": binding,
        "automatic_hypothesis_ranking": False,
        "automatic_contradiction_resolution": False,
        "automatic_submission": False,
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-investigation-runtime-integration-ready",
        "schema": BRIDGE_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "core_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "core_investigation_binding_endpoint": CORE_INVESTIGATION_BINDING_ENDPOINT,
        "investigation_types": sorted(INVESTIGATION_TYPES),
        "reference_groups": list(REF_GROUPS),
        "boundaries": {
            "lab_is_underlying_scientific_investigation_authority": True,
            "core_records_reference_first_investigation_context": True,
            "core_runs_scientific_investigation": False,
            "core_infers_findings": False,
            "core_ranks_evidence": False,
            "core_resolves_contradictions": False,
            "core_selects_hypotheses": False,
            "core_infers_causality": False,
            "core_certifies_scientific_validity": False,
            "core_determines_truth": False,
            "automatic_core_submission": False,
        },
        "integration_certification_deferred_to": "0.112.0",
    }


def health() -> dict[str, Any]:
    m = manifest()
    return {
        "ok": True,
        "status": m["status"],
        "schema": "sc-lab-platform-core-v3-scientific-investigation-runtime-health/0.111.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "core_investigation_binding_endpoint": CORE_INVESTIGATION_BINDING_ENDPOINT,
        "investigation_type_count": len(INVESTIGATION_TYPES),
        "reference_group_count": len(REF_GROUPS),
        "automatic_core_submission": False,
        "automatic_execution": False,
        "automatic_scientific_certification": False,
        "automatic_truth_determination": False,
    }
