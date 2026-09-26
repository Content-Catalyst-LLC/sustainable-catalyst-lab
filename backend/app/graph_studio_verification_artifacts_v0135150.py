from __future__ import annotations
import hashlib, json, re

VERSION = "0.135.15.0"
ROUTE_COUNT = 13
ARTIFACT_TYPES = (
    "dataset", "method", "execution", "figure", "model", "notebook",
    "document", "evidence-source", "reproduction-result", "code",
    "environment", "other",
)
OUTCOMES = ("passed", "failed", "inconclusive")
VERIFY_METHODS = (
    "artifact-inspection", "rerun", "source-check", "figure-check",
    "method-check", "manual-review",
)
MAX_ARTIFACTS = 100
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _text(value, limit=12000):
    return str(value or "").strip()[:limit]


def _bundle(payload):
    if not isinstance(payload, dict):
        return {}
    for key in ("bundle", "verificationBundle", "verification_bundle", "record"):
        if isinstance(payload.get(key), dict):
            return payload[key]
    return payload


def _audit_record(payload):
    if not isinstance(payload, dict):
        return {}
    for key in ("auditRecord", "audit_record"):
        if isinstance(payload.get(key), dict):
            return payload[key]
    return {}


def _artifact_fingerprint(artifact):
    raw = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def normalize_artifact(raw, index=0):
    if not isinstance(raw, dict):
        raise ValueError("verification artifact must be an object")
    artifact_type = _text(raw.get("artifactType", raw.get("artifact_type")), 64)
    artifact_ref = _text(raw.get("artifactRef", raw.get("artifact_ref")), 2048)
    sha256 = _text(raw.get("sha256"), 128).lower() or None
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(f"unsupported artifactType: {artifact_type}")
    if not artifact_ref:
        raise ValueError("artifactRef is required")
    if sha256 and not SHA256_RE.match(sha256):
        raise ValueError("sha256 must be a 64-character hexadecimal digest")
    artifact = {
        "id": _text(raw.get("id"), 256) or f"verification-artifact-{index+1}",
        "artifact_type": artifact_type,
        "artifact_ref": artifact_ref,
        "title": _text(raw.get("title"), 1024) or None,
        "version_ref": _text(raw.get("versionRef", raw.get("version_ref")), 1024) or None,
        "sha256": sha256,
        "source_object_ref": _text(raw.get("sourceObjectRef", raw.get("source_object_ref")), 2048) or None,
        "execution_ref": _text(raw.get("executionRef", raw.get("execution_ref")), 2048) or None,
        "uri": _text(raw.get("uri"), 4096) or None,
        "media_type": _text(raw.get("mediaType", raw.get("media_type")), 256) or None,
        "captured_at": _text(raw.get("capturedAt", raw.get("captured_at")), 128) or None,
        "note": _text(raw.get("note"), 12000) or None,
    }
    artifact["manifest_fingerprint"] = _artifact_fingerprint(artifact)
    return artifact


def normalize_bundle(payload):
    raw = _bundle(payload)
    if not isinstance(raw, dict):
        return {"ok": False, "version": VERSION, "error": "verification bundle must be an object"}
    artifacts = []
    try:
        for i, item in enumerate((raw.get("artifacts") or [])[:MAX_ARTIFACTS]):
            artifacts.append(normalize_artifact(item, i))
    except ValueError as exc:
        return {"ok": False, "version": VERSION, "error": str(exc)}

    required = {
        "thread_id": _text(raw.get("threadId", raw.get("thread_id")), 512),
        "resolution_record_id": _text(raw.get("resolutionRecordId", raw.get("resolution_record_id")), 512),
        "audit_record_id": _text(raw.get("auditRecordId", raw.get("audit_record_id")), 512),
        "annotation_id": _text(raw.get("annotationId", raw.get("annotation_id")), 512),
        "verification_event_id": _text(raw.get("verificationEventId", raw.get("verification_event_id")), 512),
    }
    for key, value in required.items():
        if not value:
            return {"ok": False, "version": VERSION, "error": f"{key} is required"}

    outcome = _text(raw.get("verificationOutcome", raw.get("verification_outcome")), 64)
    method = _text(raw.get("verificationMethod", raw.get("verification_method")), 128)
    scope = _text(raw.get("verificationScope", raw.get("verification_scope")), 2048)
    if outcome not in OUTCOMES:
        return {"ok": False, "version": VERSION, "error": "verificationOutcome is required and must be supported"}
    if method not in VERIFY_METHODS:
        return {"ok": False, "version": VERSION, "error": "verificationMethod is required and must be supported"}
    if not scope:
        return {"ok": False, "version": VERSION, "error": "verificationScope is required"}
    if not artifacts:
        return {"ok": False, "version": VERSION, "error": "at least one verification artifact is required"}

    record = {
        "schema": "sc-lab-graph-studio-verification-artifact-bundle/0.135.15.0",
        "version": VERSION,
        "record_type": "graph-studio-verification-artifact-bundle",
        "collection": "graphStudioVerificationArtifactBundles",
        "id": _text(raw.get("id"), 256) or "verification-artifact-bundle",
        "thread_id": required["thread_id"],
        "resolution_record_id": required["resolution_record_id"],
        "audit_record_id": required["audit_record_id"],
        "annotation_id": required["annotation_id"],
        "verification_event_id": required["verification_event_id"],
        "verification_outcome": outcome,
        "verification_method": method,
        "verification_scope": scope,
        "artifacts": artifacts,
        "created_at": _text(raw.get("createdAt", raw.get("created_at")), 128) or None,
        "updated_at": _text(raw.get("updatedAt", raw.get("updated_at")), 128) or None,
        "author": _text(raw.get("author"), 256) or "user",
        "boundary": "Verification artifact manifests document exactly what was inspected for a review action. Artifact presence, hashing, or a passing workflow outcome does not establish scientific truth, causal validity, evidence weight, or preferred interpretation.",
    }
    return {"ok": True, "version": VERSION, "record": record, "artifact_count": len(artifacts)}


def validate_bundle(payload):
    normalized = normalize_bundle(payload)
    if not normalized.get("ok"):
        return normalized
    record = normalized["record"]
    audit = _audit_record(payload)
    errors = []
    warnings = []
    binding_valid = None

    if audit:
        events = [e for e in (audit.get("events") or [])[:500] if isinstance(e, dict)]
        event = next((e for e in events if _text(e.get("id"), 512) == record["verification_event_id"]), None)
        if not event:
            errors.append("verificationEventId was not found in auditRecord")
            binding_valid = False
        else:
            event_type = _text(event.get("eventType", event.get("event_type")), 64)
            annotation_id = _text(event.get("annotationId", event.get("annotation_id")), 512)
            outcome = _text(event.get("outcome"), 64)
            method = _text(event.get("verificationMethod", event.get("verification_method")), 128)
            ref = _text(event.get("verificationRef", event.get("verification_ref")), 2048)
            checks = [
                (event_type == "verification-recorded", "bound audit event is not verification-recorded"),
                (annotation_id == record["annotation_id"], "annotationId does not match bound audit event"),
                (outcome == record["verification_outcome"], "verificationOutcome does not match bound audit event"),
                (method == record["verification_method"], "verificationMethod does not match bound audit event"),
                (ref == record["id"], "audit verificationRef does not point to this artifact bundle"),
            ]
            for ok, msg in checks:
                if not ok:
                    errors.append(msg)
            binding_valid = not errors
    else:
        warnings.append("auditRecord was not supplied; event binding was not independently checked")

    no_hash = [a["id"] for a in record["artifacts"] if not a.get("sha256")]
    if no_hash:
        warnings.append(f"{len(no_hash)} artifact(s) do not include sha256")
    return {
        "ok": not errors,
        "version": VERSION,
        "binding_valid": binding_valid,
        "artifact_count": len(record["artifacts"]),
        "sha256_coverage": len(record["artifacts"]) - len(no_hash),
        "errors": errors,
        "warnings": warnings,
        "record": record,
    }


def summarize(payload):
    normalized = normalize_bundle(payload)
    if not normalized.get("ok"):
        return normalized
    record = normalized["record"]
    by_type = {t: 0 for t in ARTIFACT_TYPES}
    sha_count = source_count = execution_count = version_count = 0
    for artifact in record["artifacts"]:
        by_type[artifact["artifact_type"]] += 1
        sha_count += bool(artifact.get("sha256"))
        source_count += bool(artifact.get("source_object_ref"))
        execution_count += bool(artifact.get("execution_ref"))
        version_count += bool(artifact.get("version_ref"))
    return {
        "ok": True,
        "version": VERSION,
        "bundle_id": record["id"],
        "artifact_count": len(record["artifacts"]),
        "by_type": {k: v for k, v in by_type.items() if v},
        "sha256_count": sha_count,
        "version_ref_count": version_count,
        "source_object_ref_count": source_count,
        "execution_ref_count": execution_count,
    }


def fingerprint(payload):
    normalized = normalize_bundle(payload)
    if not normalized.get("ok"):
        return normalized
    canonical = json.dumps(normalized["record"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {
        "ok": True,
        "version": VERSION,
        "algorithm": "sha256",
        "fingerprint": hashlib.sha256(canonical).hexdigest(),
        "canonical_bytes": len(canonical),
    }


def integrity(payload):
    normalized = normalize_bundle(payload)
    if not normalized.get("ok"):
        return normalized
    record = normalized["record"]
    ids = [a["id"] for a in record["artifacts"]]
    refs = [a["artifact_ref"] for a in record["artifacts"]]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    duplicate_refs = sorted({x for x in refs if refs.count(x) > 1})
    invalid_hashes = [a["id"] for a in record["artifacts"] if a.get("sha256") and not SHA256_RE.match(a["sha256"])]
    return {
        "ok": not duplicate_ids and not invalid_hashes,
        "version": VERSION,
        "duplicate_artifact_ids": duplicate_ids,
        "duplicate_artifact_refs": duplicate_refs,
        "invalid_sha256_artifact_ids": invalid_hashes,
        "artifact_count": len(record["artifacts"]),
        "bundle_fingerprint": fingerprint(payload).get("fingerprint"),
    }


def event_bindings(payload):
    bundles = payload.get("bundles") if isinstance(payload, dict) else None
    if bundles is None:
        bundles = [_bundle(payload)] if isinstance(payload, dict) else []
    items = []
    for raw in (bundles or [])[:500]:
        n = normalize_bundle({"bundle": raw})
        if not n.get("ok"):
            continue
        r = n["record"]
        items.append({
            "bundle_id": r["id"],
            "verification_event_id": r["verification_event_id"],
            "annotation_id": r["annotation_id"],
            "artifact_count": len(r["artifacts"]),
            "verification_outcome": r["verification_outcome"],
        })
    return {"ok": True, "version": VERSION, "binding_count": len(items), "items": items}


def compare(payload):
    if not isinstance(payload, dict):
        return {"ok": False, "version": VERSION, "error": "payload must be an object"}
    left = normalize_bundle({"bundle": payload.get("left") or {}})
    right = normalize_bundle({"bundle": payload.get("right") or {}})
    if not left.get("ok"):
        return {"ok": False, "version": VERSION, "side": "left", "error": left.get("error")}
    if not right.get("ok"):
        return {"ok": False, "version": VERSION, "side": "right", "error": right.get("error")}
    la = {a["artifact_ref"]: a for a in left["record"]["artifacts"]}
    ra = {a["artifact_ref"]: a for a in right["record"]["artifacts"]}
    added = sorted(set(ra) - set(la))
    removed = sorted(set(la) - set(ra))
    changed = sorted(k for k in set(la) & set(ra) if la[k]["manifest_fingerprint"] != ra[k]["manifest_fingerprint"])
    unchanged = sorted(k for k in set(la) & set(ra) if la[k]["manifest_fingerprint"] == ra[k]["manifest_fingerprint"])
    return {
        "ok": True,
        "version": VERSION,
        "left_bundle_id": left["record"]["id"],
        "right_bundle_id": right["record"]["id"],
        "added_artifact_refs": added,
        "removed_artifact_refs": removed,
        "changed_artifact_refs": changed,
        "unchanged_artifact_refs": unchanged,
    }


def verification_packet(payload):
    normalized = normalize_bundle(payload)
    if not normalized.get("ok"):
        return normalized
    return {
        "ok": True,
        "version": VERSION,
        "target": "project-workspace",
        "bundle": normalized["record"],
        "validation": validate_bundle(payload),
        "summary": summarize(payload),
        "integrity": integrity(payload),
        "fingerprint": fingerprint(payload),
        "boundary": normalized["record"]["boundary"],
    }


def health():
    return {
        "ok": True,
        "version": VERSION,
        "api_route_count": ROUTE_COUNT,
        "typed_verification_artifacts": True,
        "multi_artifact_evidence_bundles": True,
        "audit_event_binding": True,
        "sha256_artifact_fingerprints": True,
        "project_workspace_handoff": True,
        "backward_compatible_v0135140": True,
    }


def contract():
    return {
        "ok": True,
        "version": VERSION,
        "artifact_types": list(ARTIFACT_TYPES),
        "verification_outcomes": list(OUTCOMES),
        "verification_methods": list(VERIFY_METHODS),
        "project_collection": "graphStudioVerificationArtifactBundles",
        "max_artifacts_per_bundle": MAX_ARTIFACTS,
        "verification_event_ref_must_equal_bundle_id": True,
        "truth_ranking": False,
        "causal_inference": False,
        "evidence_weight_inference": False,
    }


def browser_contract():
    return {
        "ok": True,
        "version": VERSION,
        "required_actions": [
            "add-artifact-to-draft", "record-verification-bundle", "save-bundles",
            "open-verification-context",
        ],
        "full_render_count_must_not_increase": True,
    }


def acceptance_report():
    return {
        "ok": True,
        "version": VERSION,
        "typed_verification_artifacts": True,
        "multi_artifact_evidence_bundles": True,
        "audit_event_binding": True,
        "sha256_artifact_fingerprints": True,
        "project_persistence_explicit": True,
        "cross_workspace_verification_handoff": True,
        "full_graph_redraw_for_verification_artifacts": False,
        "audit_history_mutation": False,
        "resolution_mutation": False,
        "annotation_mutation": False,
        "truth_ranking": False,
        "causal_inference": False,
        "evidence_weight_inference": False,
        "scientific_preference": False,
    }
