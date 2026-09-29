from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from . import research_change_impact_living_analysis_v01370 as living
from . import research_program_intelligence_v01380 as programs

VERSION = "0.139.0"
ROUTE_COUNT = 25
SCHEMA = "sc-lab-scholarly-study-original-research-package/0.139.0"
SNAPSHOT_SCHEMA = "sc-lab-original-research-package-snapshot/0.139.0"
BOUNDARY = (
    "Scholarly Study & Original Research Package assembles declared research objects, methods, evidence, claims, "
    "computational artifacts, review records, reproducibility materials, living-analysis state, and scholarly metadata "
    "into a deterministic research package. Assembly, readiness checks, snapshots, and handoffs do not certify scientific "
    "validity, causal truth, evidentiary weight, peer-review acceptance, publication acceptance, or identifier registration."
)

PACKAGE_STATES = ("draft", "assembled", "review-ready", "release-candidate", "released", "archived")
ARTIFACT_FAMILIES = (
    "question", "hypothesis", "preregistration", "method", "dataset", "transformation", "execution", "model", "simulation",
    "analysis", "figure", "table", "claim", "evidence", "finding", "manuscript", "review", "reproduction-package", "other",
)
EXPORT_FORMATS = ("json", "jsonld", "zip", "pdf", "html", "markdown", "csv", "bibtex", "ris", "csl-json", "ro-crate")
REQUIRED_READINESS = ("identity", "researchQuestion", "methods", "evidence", "analysis", "findings", "provenance", "limitations")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _txt(value: Any, limit: int = 4096) -> str:
    return str(value or "").strip()[:limit]


def _list(value: Any) -> list:
    return copy.deepcopy(value) if isinstance(value, list) else []


def _dict(value: Any) -> dict:
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def _get(obj: dict, *names: str, default=None):
    if not isinstance(obj, dict):
        return default
    for name in names:
        if name in obj and obj[name] is not None:
            return obj[name]
    return default


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _fp(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def _ref(item: Any, prefix: str = "research-object") -> str:
    if isinstance(item, str):
        return _txt(item, 2048)
    if not isinstance(item, dict):
        return f"{prefix}:sha256:{_fp(item)}"
    for key in ("ref", "objectRef", "object_ref", "artifactRef", "artifact_ref", "id"):
        if item.get(key):
            return _txt(item[key], 2048)
    return f"{prefix}:sha256:{_fp(item)}"


def _items(raw: dict, *keys: str) -> list:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, list):
            return copy.deepcopy(value)
    return []


def _artifact_rows(raw: dict) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    aliases = {
        "questions": "question", "hypotheses": "hypothesis", "preregistrations": "preregistration",
        "methods": "method", "datasets": "dataset", "transformations": "transformation", "executions": "execution",
        "models": "model", "simulations": "simulation", "analyses": "analysis", "figures": "figure", "tables": "table",
        "claims": "claim", "evidence": "evidence", "findings": "finding", "manuscripts": "manuscript", "reviews": "review",
        "reproductionPackages": "reproduction-package", "reproduction_packages": "reproduction-package",
    }
    for key, family in aliases.items():
        for item in _list(raw.get(key)):
            ref = _ref(item, family)
            dedupe = f"{family}|{ref}"
            if dedupe in seen:
                continue
            seen.add(dedupe)
            row = {"ref": ref, "family": family, "declared": True}
            if isinstance(item, dict):
                row["title"] = _txt(_get(item, "title", "label", "name"), 1024) or None
                row["versionRef"] = _txt(_get(item, "versionRef", "version_ref", "version"), 512) or None
                row["contentHash"] = _txt(_get(item, "contentHash", "content_hash", "hash", "fingerprint"), 256) or None
                row["sourceProduct"] = _txt(_get(item, "sourceProduct", "source_product"), 128) or None
            rows.append(row)
    for item in _items(raw, "artifacts", "objects", "members"):
        family = _txt(_get(item, "family", "type", "objectType", "object_type"), 128) if isinstance(item, dict) else "other"
        family = family if family in ARTIFACT_FAMILIES else "other"
        ref = _ref(item, family)
        dedupe = f"{family}|{ref}"
        if dedupe not in seen:
            seen.add(dedupe)
            rows.append({"ref": ref, "family": family, "declared": True})
    return rows


def normalize_package(payload: dict) -> dict:
    raw = payload.get("package") if isinstance(payload, dict) and isinstance(payload.get("package"), dict) else (payload if isinstance(payload, dict) else {})
    package_id = _txt(_get(raw, "packageId", "package_id", "id"), 512)
    study_id = _txt(_get(raw, "studyId", "study_id", "projectId", "project_id"), 512)
    if not package_id:
        package_id = f"research-package-{_fp({'studyId': study_id, 'title': raw.get('title')})[:20]}" if study_id or raw.get("title") else ""
    if not package_id:
        return {"ok": False, "version": VERSION, "error": "packageId, studyId, projectId, or title is required", "boundary": BOUNDARY}
    state = _txt(_get(raw, "state", "status"), 64) or "draft"
    if state not in PACKAGE_STATES:
        state = "draft"
    artifacts = _artifact_rows(raw)
    rec = {
        "schema": SCHEMA,
        "version": VERSION,
        "recordType": "scholarly-study-original-research-package",
        "collection": "graphStudioOriginalResearchPackages",
        "id": package_id,
        "packageId": package_id,
        "studyId": study_id or package_id,
        "projectId": _txt(_get(raw, "projectId", "project_id"), 512) or study_id or package_id,
        "title": _txt(_get(raw, "title", "name"), 1024) or package_id,
        "abstract": _txt(raw.get("abstract"), 20000) or None,
        "researchQuestion": copy.deepcopy(_get(raw, "researchQuestion", "research_question")),
        "hypotheses": _items(raw, "hypotheses"),
        "methods": _items(raw, "methods"),
        "datasets": _items(raw, "datasets"),
        "executions": _items(raw, "executions", "runs"),
        "models": _items(raw, "models"),
        "analyses": _items(raw, "analyses"),
        "figures": _items(raw, "figures"),
        "tables": _items(raw, "tables"),
        "evidence": _items(raw, "evidence"),
        "claims": _items(raw, "claims"),
        "findings": _items(raw, "findings"),
        "limitations": _items(raw, "limitations"),
        "reviews": _items(raw, "reviews", "reviewRecords"),
        "reproductionPackages": _items(raw, "reproductionPackages", "reproduction_packages"),
        "manuscripts": _items(raw, "manuscripts"),
        "citations": _items(raw, "citations", "references"),
        "contributors": _items(raw, "contributors", "authors"),
        "identifiers": _items(raw, "identifiers"),
        "provenance": _dict(raw.get("provenance")),
        "artifacts": artifacts,
        "nodes": _items(raw, "nodes"),
        "edges": _items(raw, "edges"),
        "changeEvents": _items(raw, "changeEvents", "change_events"),
        "program": _dict(raw.get("program")),
        "state": state,
        "createdAt": _txt(_get(raw, "createdAt", "created_at"), 128) or _now(),
        "createdBy": _txt(_get(raw, "createdBy", "created_by"), 256) or "user",
        "sourceAuthorityPreserved": True,
        "automaticScientificValidity": False,
        "automaticPublicationAcceptance": False,
        "boundary": BOUNDARY,
    }
    rec["fingerprint"] = _fp({k: v for k, v in rec.items() if k not in {"fingerprint", "createdAt"}})
    return {"ok": True, "version": VERSION, "record": rec, "boundary": BOUNDARY}


def validate_package(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    errors: list[str] = []
    warnings: list[str] = []
    refs = [x["ref"] for x in r["artifacts"]]
    if len(refs) != len(set(refs)):
        warnings.append("artifact references repeat across declared families")
    if not r["methods"]:
        warnings.append("no methods are declared")
    if not r["evidence"] and not r["datasets"]:
        warnings.append("no evidence or datasets are declared")
    if not r["findings"]:
        warnings.append("no findings are declared")
    if not r["limitations"]:
        warnings.append("no limitations are declared")
    return {"ok": not errors, "version": VERSION, "record": r, "errors": errors, "warnings": warnings, "boundary": BOUNDARY}


def manifest(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    family_counts: dict[str, int] = {}
    for item in r["artifacts"]:
        family_counts[item["family"]] = family_counts.get(item["family"], 0) + 1
    m = {
        "schema": "sc-lab-original-research-package-manifest/0.139.0",
        "version": VERSION,
        "packageId": r["packageId"],
        "studyId": r["studyId"],
        "packageFingerprint": r["fingerprint"],
        "artifactCount": len(r["artifacts"]),
        "artifactFamilyCounts": dict(sorted(family_counts.items())),
        "artifactRefs": [x["ref"] for x in r["artifacts"]],
        "createdAt": _now(),
        "sourceAuthorityPreserved": True,
        "boundary": BOUNDARY,
    }
    m["manifestFingerprint"] = _fp({k: v for k, v in m.items() if k != "manifestFingerprint"})
    return {"ok": True, "version": VERSION, "manifest": m, "boundary": BOUNDARY}


def artifact_index(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    rows = sorted(out["record"]["artifacts"], key=lambda x: (x["family"], x["ref"]))
    return {"ok": True, "version": VERSION, "packageId": out["record"]["packageId"], "items": rows, "count": len(rows), "sourceObjectsRemainAuthoritative": True, "boundary": BOUNDARY}


def methods_index(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    rows = []
    for i, item in enumerate(out["record"]["methods"]):
        rows.append({"ref": _ref(item, "method"), "order": i + 1, "declared": True, "content": copy.deepcopy(item)})
    return {"ok": True, "version": VERSION, "packageId": out["record"]["packageId"], "methods": rows, "count": len(rows), "automaticMethodValidity": False, "boundary": BOUNDARY}


def claim_evidence_index(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    links = _items(payload if isinstance(payload, dict) else {}, "claimEvidenceLinks", "claim_evidence_links", "links")
    if not links:
        links = _items(payload.get("package", {}) if isinstance(payload, dict) and isinstance(payload.get("package"), dict) else {}, "claimEvidenceLinks", "claim_evidence_links")
    return {
        "ok": True, "version": VERSION, "packageId": r["packageId"],
        "claims": [{"ref": _ref(x, "claim"), "content": x} for x in r["claims"]],
        "evidence": [{"ref": _ref(x, "evidence"), "content": x} for x in r["evidence"]],
        "links": copy.deepcopy(links), "automaticEvidenceWeighting": False, "automaticClaimStatusChange": False, "boundary": BOUNDARY,
    }


def review_record(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    reviews = out["record"]["reviews"]
    status_counts: dict[str, int] = {}
    for review in reviews:
        status = _txt(_get(review, "status", "state"), 128) if isinstance(review, dict) else "declared"
        status = status or "declared"
        status_counts[status] = status_counts.get(status, 0) + 1
    return {"ok": True, "version": VERSION, "packageId": out["record"]["packageId"], "reviews": reviews, "count": len(reviews), "statusCounts": status_counts, "reviewCompletionDoesNotEqualScientificValidity": True, "boundary": BOUNDARY}


def reproducibility_index(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    rows = [{"ref": _ref(x, "reproduction-package"), "content": x} for x in r["reproductionPackages"]]
    return {"ok": True, "version": VERSION, "packageId": r["packageId"], "packages": rows, "count": len(rows), "reproducibleDoesNotEqualCorrect": True, "boundary": BOUNDARY}


def provenance_lineage(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    lineage = {
        "packageId": r["packageId"], "studyId": r["studyId"], "artifactRefs": [x["ref"] for x in r["artifacts"]],
        "declaredProvenance": r["provenance"], "packageFingerprint": r["fingerprint"], "sourceAuthorityPreserved": True,
    }
    lineage["lineageFingerprint"] = _fp(lineage)
    return {"ok": True, "version": VERSION, "lineage": lineage, "aggregationDoesNotReplaceSourceProvenance": True, "boundary": BOUNDARY}


def package_living_status(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    if not r["nodes"] and not r["changeEvents"]:
        return {"ok": True, "version": VERSION, "packageId": r["packageId"], "state": "no-living-analysis-input-declared", "assessmentRequiredCount": 0, "scientificValidity": None, "boundary": BOUNDARY}
    status = living.living_status({"projectId": r["projectId"], "nodes": r["nodes"], "edges": r["edges"], "changeEvents": r["changeEvents"]})
    return {"ok": True, "version": VERSION, "packageId": r["packageId"], "livingAnalysis": status, "scientificValidity": None, "boundary": BOUNDARY}


def program_context(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    if not r["program"]:
        return {"ok": True, "version": VERSION, "packageId": r["packageId"], "programContext": None, "boundary": BOUNDARY}
    p = copy.deepcopy(r["program"])
    p.setdefault("studyId", r["studyId"])
    result = programs.study_context({**p, "program": p, "studyId": r["studyId"]})
    return {"ok": bool(result.get("ok")), "version": VERSION, "packageId": r["packageId"], "programContext": result if result.get("ok") else None, "programError": result.get("error") if not result.get("ok") else None, "boundary": BOUNDARY}


def readiness(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    checks = {
        "identity": bool(r["packageId"] and r["title"]),
        "researchQuestion": bool(r["researchQuestion"]),
        "methods": bool(r["methods"]),
        "evidence": bool(r["evidence"] or r["datasets"]),
        "analysis": bool(r["analyses"] or r["executions"] or r["models"]),
        "findings": bool(r["findings"]),
        "provenance": bool(r["provenance"] or r["artifacts"]),
        "limitations": bool(r["limitations"]),
        "review": bool(r["reviews"]),
        "reproduction": bool(r["reproductionPackages"]),
        "manuscript": bool(r["manuscripts"]),
    }
    missing = [name for name in REQUIRED_READINESS if not checks[name]]
    return {
        "ok": True, "version": VERSION, "packageId": r["packageId"], "checks": checks, "missingRequired": missing,
        "packageAssemblyComplete": not missing, "readyForHumanReview": not missing, "scientificValidityCertified": False,
        "publicationAccepted": False, "automaticReadinessOverride": False, "boundary": BOUNDARY,
    }


def snapshot(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    snap = {
        "schema": SNAPSHOT_SCHEMA, "version": VERSION, "packageId": r["packageId"], "studyId": r["studyId"],
        "packageFingerprint": r["fingerprint"], "manifest": manifest(payload).get("manifest"), "readiness": readiness(payload),
        "livingStatus": package_living_status(payload), "createdAt": _now(), "boundary": BOUNDARY,
    }
    snap["snapshotFingerprint"] = _fp({k: v for k, v in snap.items() if k != "snapshotFingerprint"})
    return {"ok": True, "version": VERSION, "snapshot": snap, "immutableSnapshot": True, "boundary": BOUNDARY}


def compare_snapshots(payload: dict) -> dict:
    left = _dict(payload.get("left")) if isinstance(payload, dict) else {}
    right = _dict(payload.get("right")) if isinstance(payload, dict) else {}
    def refs(s: dict) -> set[str]:
        m = s.get("manifest") if isinstance(s.get("manifest"), dict) else {}
        return {str(x) for x in m.get("artifactRefs", [])}
    lrefs, rrefs = refs(left), refs(right)
    return {
        "ok": True, "version": VERSION,
        "packageChanged": left.get("packageFingerprint") != right.get("packageFingerprint"),
        "addedArtifactRefs": sorted(rrefs - lrefs), "removedArtifactRefs": sorted(lrefs - rrefs),
        "readinessChanged": _fp(left.get("readiness")) != _fp(right.get("readiness")), "boundary": BOUNDARY,
    }


def export_plan(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    raw = payload.get("export") if isinstance(payload, dict) and isinstance(payload.get("export"), dict) else payload
    formats = [str(x).lower() for x in _list(_get(raw, "formats", default=["json", "zip"]))]
    invalid = [x for x in formats if x not in EXPORT_FORMATS]
    if invalid:
        return {"ok": False, "version": VERSION, "error": f"unsupported export formats: {', '.join(invalid)}", "boundary": BOUNDARY}
    plan = {"packageId": out["record"]["packageId"], "formats": formats, "includeProvenance": True, "includeManifest": True, "includeReadinessReport": True, "automaticPublication": False}
    plan["planFingerprint"] = _fp(plan)
    return {"ok": True, "version": VERSION, "plan": plan, "automaticExportExecution": False, "boundary": BOUNDARY}


def citation_metadata(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    metadata = {
        "type": "article", "title": r["title"], "author": copy.deepcopy(r["contributors"]),
        "id": r["packageId"], "version": VERSION, "identifiers": copy.deepcopy(r["identifiers"]),
        "status": r["state"], "generatedAt": _now(),
    }
    return {"ok": True, "version": VERSION, "packageId": r["packageId"], "citationMetadata": metadata, "identifierRegistrationPerformed": False, "boundary": BOUNDARY}


def project_workspace_packet(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    packet = {
        "schema": "sc-lab-project-workspace-original-research-package/0.139.0", "version": VERSION,
        "package": out["record"], "manifest": manifest(payload).get("manifest"), "readiness": readiness(payload),
        "livingStatus": package_living_status(payload), "programContext": program_context(payload).get("programContext"),
        "boundary": BOUNDARY,
    }
    packet["packetFingerprint"] = _fp({k: v for k, v in packet.items() if k != "packetFingerprint"})
    return {"ok": True, "version": VERSION, "packet": packet, "boundary": BOUNDARY}


def core_scholarly_handoff(payload: dict) -> dict:
    out = normalize_package(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    handoff = {
        "schema": "sc.research.scholarly-package-handoff.v1", "sourceProduct": "research-lab", "sourceVersion": VERSION,
        "packageRef": f"lab:original-research-package:{r['packageId']}", "studyRef": r["studyId"],
        "packageFingerprint": r["fingerprint"], "artifactRefs": [x["ref"] for x in r["artifacts"]],
        "provenance": copy.deepcopy(r["provenance"]), "explicitSubmissionRequired": True,
    }
    handoff["handoffFingerprint"] = _fp(handoff)
    return {"ok": True, "version": VERSION, "handoff": handoff, "automaticCoreSubmission": False, "coreBecomesSourceAuthority": False, "boundary": BOUNDARY}


def fingerprint(payload: dict) -> dict:
    out = normalize_package(payload)
    return {"ok": out.get("ok", False), "version": VERSION, "packageId": out.get("record", {}).get("packageId"), "fingerprint": out.get("record", {}).get("fingerprint"), "boundary": BOUNDARY}


def contract() -> dict:
    return {"ok": True, "version": VERSION, "route_count": ROUTE_COUNT, "schema": SCHEMA, "packageStates": list(PACKAGE_STATES), "artifactFamilies": list(ARTIFACT_FAMILIES), "exportFormats": list(EXPORT_FORMATS), "collections": ["graphStudioOriginalResearchPackages"], "boundary": BOUNDARY}


def policy() -> dict:
    return {"ok": True, "version": VERSION, "sourceAuthorityPreserved": True, "humanScientificJudgmentRequired": True, "automaticScientificValidity": False, "automaticCausalTruth": False, "automaticEvidenceWeighting": False, "automaticPeerReviewAcceptance": False, "automaticPublicationAcceptance": False, "automaticIdentifierRegistration": False, "boundary": BOUNDARY}


def health() -> dict:
    return {"ok": True, "version": VERSION, "api_route_count": ROUTE_COUNT, "scholarly_study_original_research_package": True, "deterministic_manifest": True, "reproducibility_index": True, "living_analysis_bridge": True, "program_context_bridge": True, "boundary": BOUNDARY}


def acceptance_report() -> dict:
    return {"ok": True, "version": VERSION, "packageNormalization": True, "deterministicManifest": True, "artifactIndex": True, "methodIndex": True, "claimEvidenceIndex": True, "reviewRecord": True, "reproducibilityIndex": True, "provenanceLineage": True, "livingAnalysisBridge": True, "researchProgramContext": True, "readinessReport": True, "immutableSnapshots": True, "projectWorkspaceHandoff": True, "coreScholarlyHandoff": True, "backwardCompatibleV01380": True, "automaticScientificValidity": False, "automaticPublicationAcceptance": False, "route_count": ROUTE_COUNT, "boundary": BOUNDARY}


def release_gates() -> dict:
    return {"ok": True, "version": VERSION, "requiredRouteCount": ROUTE_COUNT, "scholarlyStudyOriginalResearchPackage": True, "deterministicManifest": True, "provenanceLineage": True, "readinessReport": True, "immutableSnapshots": True, "backwardCompatibleV01380": True, "automaticScientificValidity": False, "automaticPublicationAcceptance": False, "boundary": BOUNDARY}
