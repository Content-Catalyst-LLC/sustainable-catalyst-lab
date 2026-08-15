from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .advanced_experimental_design import health as experimental_design_health
from .advanced_statistical_modeling import health as statistical_modeling_health
from .bayesian_inference import health as bayesian_health
from .correlated_uncertainty import health as correlated_uncertainty_health
from .data_transformations import health as data_transformations_health
from .graph_studio import health as graph_studio_health
from .probabilistic_analysis import health as probabilistic_analysis_health
from .reproducible_model_package import health as reproducible_package_health
from .scientific_audit_v0590 import health as scientific_audit_health
from .scientific_compute_hardening import policies as compute_hardening_policies
from .scientific_workflow_composer import health as workflow_composer_health
from .shared_model_handoff import health as model_handoff_health

VERSION = "0.60.0"
JOURNEY_SCHEMA = "sc-lab-integrated-research-journey/0.60.0"
READINESS_SCHEMA = "sc-lab-integrated-beta-readiness/0.60.0"
PACKET_SCHEMA = "sc-lab-integrated-research-beta-packet/0.60.0"
MAX_ANALYSIS_TYPES = 250
MAX_HASH_REFS = 250


class IntegratedResearchBetaError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _bounded_text(value: Any, limit: int = 160) -> str:
    return str(value or "").strip()[:limit]


def _count(value: Any) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(n, 10_000_000))


def _hashes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:MAX_HASH_REFS]:
        text = str(item or "").strip().lower()
        if len(text) == 64 and all(ch in "0123456789abcdef" for ch in text):
            out.append(text)
    return sorted(set(out))


def _record_types(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out = []
    for item in value[:MAX_ANALYSIS_TYPES]:
        text = _bounded_text(item, 100)
        if text:
            out.append(text)
    return sorted(set(out))


def normalize_project_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    forbidden = {"rows", "records", "rawData", "dataset", "datasetsPayload", "inputs", "secrets", "credentials"}
    if any(key in source for key in forbidden):
        raise IntegratedResearchBetaError("Integrated beta readiness accepts metadata summaries only; raw datasets, inputs, secrets, and credentials are not accepted.")
    counts_source = source.get("counts") if isinstance(source.get("counts"), dict) else {}
    count_keys = (
        "datasets", "models", "analysisPackets", "visualizations", "experiments", "reports",
        "scientificWorkflowsV0570", "scientificWorkflowRunsV0570", "reproduciblePackages",
    )
    counts = {key: _count(counts_source.get(key)) for key in count_keys}
    audit_source = source.get("audit") if isinstance(source.get("audit"), dict) else {}
    audit = {
        "gate": _bounded_text(audit_source.get("gate"), 48),
        "auditHash": (_hashes([audit_source.get("auditHash")]) or [None])[0],
        "humanReviewRequired": bool(audit_source.get("humanReviewRequired", True)),
    }
    return {
        "id": _bounded_text(source.get("id") or "active-project", 120),
        "title": _bounded_text(source.get("title") or source.get("name") or "Active Lab project", 180),
        "schemaVersion": _bounded_text(source.get("schemaVersion"), 40),
        "counts": counts,
        "analysisRecordTypes": _record_types(source.get("analysisRecordTypes")),
        "workflowRunHashes": _hashes(source.get("workflowRunHashes")),
        "packageHashes": _hashes(source.get("packageHashes")),
        "figureHashes": _hashes(source.get("figureHashes")),
        "audit": audit,
    }


def capability_matrix() -> dict[str, Any]:
    checks = [
        ("model-handoff", "Lab ↔ Workbench model contract", "0.49.0", model_handoff_health()),
        ("reproducibility", "Reproducible model packages", "0.50.0", reproducible_package_health()),
        ("statistics", "Advanced statistical modeling", "0.51.0", statistical_modeling_health()),
        ("bayesian", "Bayesian inference", "0.52.0", bayesian_health()),
        ("dependency", "Correlated uncertainty", "0.53.0", correlated_uncertainty_health()),
        ("transformations", "Scientific data transformations", "0.55.0", data_transformations_health()),
        ("experiments", "Advanced experimental design", "0.56.0", experimental_design_health()),
        ("figures", "Graph Studio", "0.47.0", graph_studio_health()),
        ("workflow", "Scientific Workflow Composer", "0.57.0", workflow_composer_health()),
        ("probabilistic", "Probabilistic analysis", "0.48.0", probabilistic_analysis_health()),
        ("audit", "Scientific audit", "0.59.0", scientific_audit_health()),
    ]
    capabilities = []
    for key, label, version, result in checks:
        capabilities.append({"id": key, "label": label, "version": version, "available": bool(result.get("ok", True))})
    compute = compute_hardening_policies()
    capabilities.append({"id": "compute", "label": "Large-model / large-dataset compute hardening", "version": "0.58.0", "available": bool(compute.get("ok", True))})
    return {
        "ok": all(row["available"] for row in capabilities),
        "version": VERSION,
        "capabilities": capabilities,
        "capabilityHash": _hash(capabilities),
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "betaMilestone": True,
        "metadataOnlyReadinessInput": True,
        "tamperEvidentBetaPacket": True,
        "deterministicReadinessEvidence": True,
        "humanReviewRequired": True,
        "automaticScientificCertificationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "automaticRegistryPromotionAuthorized": False,
        "automaticHighStakesDecisionAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
        "rawSensitiveDataInBetaPacket": False,
    }


def health() -> dict[str, Any]:
    matrix = capability_matrix()
    return {
        "ok": bool(matrix["ok"]),
        "status": "integrated-scientific-research-beta-ready" if matrix["ok"] else "integration-incomplete",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "capabilityCount": len(matrix["capabilities"]),
        "capabilityHash": matrix["capabilityHash"],
        "humanReviewRequired": True,
        "automaticCertification": False,
        "automaticPublication": False,
        "arbitraryCode": False,
    }


def _has_type(types: set[str], *needles: str) -> bool:
    lowered = {value.lower() for value in types}
    return any(any(needle in value for needle in needles) for value in lowered)


def research_journey(payload: dict[str, Any]) -> dict[str, Any]:
    project = normalize_project_summary(payload.get("project") if isinstance(payload, dict) else None)
    counts = project["counts"]
    types = set(project["analysisRecordTypes"])
    audit_gate = project["audit"]["gate"]

    steps = [
        {"id": "data", "label": "Data foundation", "required": True, "complete": counts["datasets"] > 0},
        {"id": "transformation", "label": "Transformation lineage", "required": False, "complete": _has_type(types, "data-transformation-v0550")},
        {"id": "model", "label": "Model / scientific analysis", "required": True, "complete": counts["models"] > 0 or _has_type(types, "advanced-statistical-model", "bayesian", "dynamic-systems", "probabilistic", "uncertainty")},
        {"id": "validation", "label": "Validation / diagnostics", "required": True, "complete": _has_type(types, "validation", "diagnostic", "cross-validation", "workflow-run-v0570") or counts["scientificWorkflowRunsV0570"] > 0},
        {"id": "uncertainty", "label": "Uncertainty evidence", "required": False, "complete": _has_type(types, "uncertainty", "probabilistic", "bayesian")},
        {"id": "experiment", "label": "Experimental design", "required": False, "complete": counts["experiments"] > 0 or _has_type(types, "experimental-design", "sequential-experiment")},
        {"id": "figure", "label": "Scientific figure", "required": False, "complete": counts["visualizations"] > 0 or bool(project["figureHashes"])},
        {"id": "workflow", "label": "Reproducible workflow", "required": True, "complete": counts["scientificWorkflowsV0570"] > 0 and (counts["scientificWorkflowRunsV0570"] > 0 or bool(project["workflowRunHashes"]))},
        {"id": "reproducibility", "label": "Reproducibility package", "required": True, "complete": counts["reproduciblePackages"] > 0 or bool(project["packageHashes"]) or _has_type(types, "reproducible-model-package", "model-package")},
        {"id": "audit", "label": "Scientific audit", "required": True, "complete": audit_gate in {"audit-ready", "human-review-required"}, "blocked": audit_gate == "blocked"},
    ]
    for step in steps:
        step["status"] = "blocked" if step.get("blocked") else ("complete" if step["complete"] else ("required" if step["required"] else "optional"))
    required = [step for step in steps if step["required"]]
    missing = [step["id"] for step in required if not step["complete"]]
    blocked = [step["id"] for step in steps if step.get("blocked")]
    return {
        "ok": not blocked,
        "schema": JOURNEY_SCHEMA,
        "version": VERSION,
        "projectId": project["id"],
        "projectHash": _hash(project),
        "steps": steps,
        "requiredComplete": len(required) - len(missing),
        "requiredTotal": len(required),
        "missingRequired": missing,
        "blockedSteps": blocked,
        "humanReviewRequired": True,
    }


def beta_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    journey = research_journey(payload)
    matrix = capability_matrix()
    blockers: list[str] = []
    warnings: list[str] = []
    if not matrix["ok"]:
        blockers.append("One or more required Lab capability contracts are unavailable.")
    if journey["blockedSteps"]:
        blockers.append("The current scientific audit is blocked.")
    if journey["missingRequired"]:
        warnings.append("Complete required research-journey evidence: " + ", ".join(journey["missingRequired"]) + ".")
    gate = "blocked" if blockers else ("needs-evidence" if journey["missingRequired"] else "beta-review-ready")
    readiness = {
        "ok": gate != "blocked",
        "schema": READINESS_SCHEMA,
        "version": VERSION,
        "gate": gate,
        "projectId": journey["projectId"],
        "projectHash": journey["projectHash"],
        "capabilityHash": matrix["capabilityHash"],
        "requiredComplete": journey["requiredComplete"],
        "requiredTotal": journey["requiredTotal"],
        "blockers": blockers,
        "warnings": warnings,
        "humanReviewRequired": True,
        "automaticScientificCertificationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "readyForBetaUse": gate == "beta-review-ready",
    }
    readiness["readinessHash"] = _hash(readiness)
    return readiness


def build_beta_packet(payload: dict[str, Any]) -> dict[str, Any]:
    project = normalize_project_summary(payload.get("project") if isinstance(payload, dict) else None)
    readiness = beta_readiness({"project": project})
    journey = research_journey({"project": project})
    packet = {
        "schema": PACKET_SCHEMA,
        "version": VERSION,
        "projectId": project["id"],
        "projectTitle": project["title"],
        "projectHash": readiness["projectHash"],
        "capabilityHash": readiness["capabilityHash"],
        "gate": readiness["gate"],
        "readyForBetaUse": readiness["readyForBetaUse"],
        "humanReviewRequired": True,
        "requiredJourney": {"complete": journey["requiredComplete"], "total": journey["requiredTotal"], "missing": journey["missingRequired"]},
        "evidenceRefs": {
            "workflowRunHashes": project["workflowRunHashes"],
            "packageHashes": project["packageHashes"],
            "figureHashes": project["figureHashes"],
            "auditHash": project["audit"]["auditHash"],
        },
        "boundaries": {
            "rawSensitiveDataIncluded": False,
            "automaticScientificCertificationAuthorized": False,
            "automaticPublicationAuthorized": False,
            "automaticHighStakesDecisionAuthorized": False,
        },
    }
    packet["packetHash"] = _hash(packet)
    return {"ok": True, "version": VERSION, "packet": packet}


def verify_beta_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) and isinstance(payload.get("packet"), dict) else payload
    if not isinstance(packet, dict):
        raise IntegratedResearchBetaError("A beta packet is required.")
    expected = str(packet.get("packetHash") or "")
    body = deepcopy(packet)
    body.pop("packetHash", None)
    actual = _hash(body)
    return {"ok": bool(expected) and expected == actual, "version": VERSION, "expectedHash": expected, "actualHash": actual}
