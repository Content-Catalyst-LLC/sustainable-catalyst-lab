from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
import math
import re
from typing import Any
import zipfile

from .graph_studio import GraphStudioError, normalize_figure
from .model_registry import capture_environment
from .shared_model_handoff import ModelHandoffError, normalize_shared_model

VERSION = "0.50.0"
PACKAGE_SCHEMA = "sc-lab-reproducible-model-package/0.50.0"
RESEARCH_BUNDLE_SCHEMA = "sc-lab-model-research-bundle/0.50.0"
REGISTRY_PROJECTION_SCHEMA = "sc-lab-model-package-registry-projection/0.50.0"
MAX_PACKAGE_BYTES = 8 * 1024 * 1024
MAX_DATASET_ROWS = 5000
MAX_RESULTS = 100
MAX_METHODS = 100
MAX_FIGURES = 50
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
FORBIDDEN_KEYS = {
    "code", "script", "command", "shell", "python", "javascript", "callback", "callbackurl",
    "callback_url", "webhook", "webhookurl", "webhook_url", "subprocess", "eval", "exec", "import",
    "binary", "executable",
}


class ReproducibleModelPackageError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ReproducibleModelPackageError("Research package content must be finite JSON data.") from exc


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, max_len: int = 500, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ReproducibleModelPackageError(f"{label} is required.")
    if len(text) > max_len:
        raise ReproducibleModelPackageError(f"{label} exceeds {max_len} characters.")
    return text


def _scan(value: Any, path: str = "package") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ReproducibleModelPackageError(f"Non-finite numeric value is not permitted at {path}.")
    if isinstance(value, dict):
        forbidden = {k.replace("-", "").replace("_", "").lower() for k in FORBIDDEN_KEYS}
        for key, child in value.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in forbidden:
                raise ReproducibleModelPackageError(f"Executable field is not permitted in a research package: {path}.{key}.")
            _scan(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan(child, f"{path}[{index}]")


def _normalize_generic_records(values: Any, label: str, limit: int) -> list[dict[str, Any]]:
    if values in (None, ""):
        return []
    if not isinstance(values, list):
        raise ReproducibleModelPackageError(f"{label} must be an array.")
    if len(values) > limit:
        raise ReproducibleModelPackageError(f"{label} exceeds the {limit}-record package limit.")
    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(values):
        if not isinstance(raw, dict):
            raise ReproducibleModelPackageError(f"{label}[{index}] must be an object.")
        row = deepcopy(raw)
        _scan(row, f"{label}[{index}]")
        row_id = _text(row.get("id") or row.get("recordId") or f"{label}-{index + 1}", f"{label}[{index}].id", 180, True)
        row["id"] = row_id
        row["recordHash"] = _digest({k: v for k, v in row.items() if k != "recordHash"})
        rows.append(row)
    return rows


def _normalize_dataset(value: Any) -> dict[str, Any]:
    if value in (None, ""):
        return {"mode": "none", "datasetId": "", "title": "", "rows": [], "rowCount": 0, "snapshotHash": None}
    if not isinstance(value, dict):
        raise ReproducibleModelPackageError("dataset must be an object.")
    src = deepcopy(value)
    _scan(src, "dataset")
    rows = src.get("rows") or src.get("data") or []
    if not isinstance(rows, list):
        raise ReproducibleModelPackageError("dataset rows must be an array.")
    if len(rows) > MAX_DATASET_ROWS:
        raise ReproducibleModelPackageError(f"Dataset snapshot exceeds {MAX_DATASET_ROWS} rows.")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ReproducibleModelPackageError(f"dataset.rows[{index}] must be an object.")
        _scan(row, f"dataset.rows[{index}]")
    dataset_id = _text(src.get("datasetId") or src.get("id"), "datasetId", 180)
    mode = _text(src.get("mode") or ("snapshot" if rows else ("reference" if dataset_id else "none")), "dataset mode", 20, True)
    if mode not in {"none", "reference", "snapshot"}:
        raise ReproducibleModelPackageError("dataset mode must be none, reference, or snapshot.")
    if mode == "snapshot" and not rows:
        raise ReproducibleModelPackageError("Snapshot dataset mode requires rows.")
    snapshot_basis = deepcopy(rows) if rows else None
    return {
        "mode": mode,
        "datasetId": dataset_id,
        "title": _text(src.get("title") or src.get("name"), "dataset title", 240),
        "source": _text(src.get("source") or src.get("url"), "dataset source", 1000),
        "bindings": deepcopy(src.get("bindings") or []),
        "rows": deepcopy(rows),
        "rowCount": len(rows),
        "snapshotHash": _digest(snapshot_basis) if snapshot_basis is not None else None,
        "metadata": deepcopy(src.get("metadata") or {}),
    }


def _normalize_figures(values: Any) -> list[dict[str, Any]]:
    if values in (None, ""):
        return []
    if not isinstance(values, list):
        raise ReproducibleModelPackageError("figures must be an array.")
    if len(values) > MAX_FIGURES:
        raise ReproducibleModelPackageError(f"figures exceeds the {MAX_FIGURES}-figure package limit.")
    figures: list[dict[str, Any]] = []
    for index, row in enumerate(values):
        try:
            figures.append(normalize_figure(row))
        except GraphStudioError as exc:
            raise ReproducibleModelPackageError(f"figures[{index}]: {exc}") from exc
    return figures


def _component_hashes(model: dict[str, Any], dataset: dict[str, Any], methods: list[dict[str, Any]], results: list[dict[str, Any]], figures: list[dict[str, Any]], environment: dict[str, Any], provenance: dict[str, Any]) -> dict[str, str]:
    return {
        "model": _digest(model),
        "dataset": _digest(dataset),
        "methods": _digest(methods),
        "results": _digest(results),
        "figures": _digest(figures),
        "environment": _digest(environment),
        "provenance": _digest(provenance),
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "packageSchema": PACKAGE_SCHEMA,
        "researchBundleSchema": RESEARCH_BUNDLE_SCHEMA,
        "registryProjectionSchema": REGISTRY_PROJECTION_SCHEMA,
        "preserves": [
            "shared-computational-model", "dataset-reference-or-snapshot", "methods", "results", "figures",
            "environment-lock", "assumptions", "limitations", "provenance", "component-hashes", "package-hash",
        ],
        "exports": ["json", "zip"],
        "registryIntegration": True,
        "immutablePackageHash": True,
        "verification": ["package-hash", "component-hashes", "shared-model-hash", "dataset-snapshot-hash"],
        "limits": {"maximumPackageBytes": MAX_PACKAGE_BYTES, "maximumDatasetRows": MAX_DATASET_ROWS, "maximumResults": MAX_RESULTS, "maximumMethods": MAX_METHODS, "maximumFigures": MAX_FIGURES},
        "boundaries": {"arbitraryCode": False, "embeddedExecutables": False, "automaticPublication": False, "automaticPromotion": False, "automaticRemoteDelivery": False},
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "reproducible-model-packages-ready",
        "version": VERSION,
        "packageSchema": PACKAGE_SCHEMA,
        "researchBundleSchema": RESEARCH_BUNDLE_SCHEMA,
        "registryProjection": True,
        "portableZipBundle": True,
        "componentHashVerification": True,
        "arbitraryCode": False,
    }


def build_package(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ReproducibleModelPackageError("Model package request must be an object.")
    try:
        model = normalize_shared_model(payload.get("model") or payload.get("sharedModel") or {})
    except ModelHandoffError as exc:
        raise ReproducibleModelPackageError(str(exc)) from exc
    project = payload.get("project") if isinstance(payload.get("project"), dict) else {}
    project_id = _text(project.get("id") or payload.get("projectId") or model.get("provenance", {}).get("projectId") or "default", "projectId", 180, True)
    project_title = _text(project.get("title") or project.get("name") or payload.get("projectTitle") or "Lab Project", "project title", 300, True)
    model_version = _text(payload.get("modelVersion") or "1.0.0", "modelVersion", 120, True)
    if not SEMVER_RE.fullmatch(model_version):
        raise ReproducibleModelPackageError("modelVersion must use semantic version syntax such as 1.0.0.")
    dataset = _normalize_dataset(payload.get("dataset") or {"datasetId": (model.get("dataset") or {}).get("datasetId"), "bindings": (model.get("dataset") or {}).get("bindings") or []})
    methods = _normalize_generic_records(payload.get("methods") or [], "methods", MAX_METHODS)
    results = _normalize_generic_records(payload.get("results") or [], "results", MAX_RESULTS)
    figures = _normalize_figures(payload.get("figures") or [])
    environment = capture_environment(payload.get("environment") if isinstance(payload.get("environment"), dict) else {})
    provenance = deepcopy(payload.get("provenance") or {}) if isinstance(payload.get("provenance"), dict) else {}
    provenance.update({
        "projectId": project_id,
        "projectTitle": project_title,
        "createdByProduct": "sustainable-catalyst-lab",
        "createdByRelease": VERSION,
        "sourceModelHash": model.get("sharedModelHash"),
    })
    _scan(provenance, "provenance")
    package_id = _text(payload.get("packageId") or f"pkg-{model['id']}-{model_version.replace('.', '-')}-{_digest({'m': model.get('sharedModelHash'), 'p': project_id})[:12]}", "packageId", 180, True)
    if not ID_RE.fullmatch(package_id):
        raise ReproducibleModelPackageError("packageId contains unsupported characters.")
    component_hashes = _component_hashes(model, dataset, methods, results, figures, environment, provenance)
    package = {
        "schema": PACKAGE_SCHEMA,
        "version": VERSION,
        "recordType": "reproducible-model-package",
        "id": package_id,
        "title": _text(payload.get("title") or f"{model['title']} — reproducible package", "package title", 300, True),
        "modelVersion": model_version,
        "project": {"id": project_id, "title": project_title},
        "model": model,
        "dataset": dataset,
        "methods": methods,
        "results": results,
        "figures": figures,
        "environment": environment,
        "assumptions": deepcopy(model.get("assumptions") or []),
        "limitations": deepcopy(model.get("limitations") or []),
        "provenance": provenance,
        "componentHashes": component_hashes,
        "createdAt": _now(),
        "boundaries": {"arbitraryCode": False, "embeddedExecutables": False, "automaticPublication": False, "automaticPromotion": False},
    }
    package["packageHash"] = _digest({k: v for k, v in package.items() if k not in {"createdAt", "packageHash"}})
    size = len(_canonical(package).encode("utf-8"))
    if size > MAX_PACKAGE_BYTES:
        raise ReproducibleModelPackageError(f"Reproducible package exceeds the {MAX_PACKAGE_BYTES}-byte limit.")
    package["sizeBytes"] = size
    package["registryProjection"] = registry_projection(package)
    return {"ok": True, "package": package, "verification": verify_package(package)}


def verify_package(payload: dict[str, Any]) -> dict[str, Any]:
    package = payload.get("package") if isinstance(payload, dict) and isinstance(payload.get("package"), dict) else payload
    if not isinstance(package, dict):
        raise ReproducibleModelPackageError("A reproducible model package is required.")
    if package.get("schema") != PACKAGE_SCHEMA or package.get("version") != VERSION:
        raise ReproducibleModelPackageError("Unsupported reproducible model package contract.")
    expected_components = package.get("componentHashes") if isinstance(package.get("componentHashes"), dict) else {}
    actual_components = _component_hashes(
        package.get("model") or {}, package.get("dataset") or {}, package.get("methods") or [], package.get("results") or [],
        package.get("figures") or [], package.get("environment") or {}, package.get("provenance") or {},
    )
    checks = {f"component:{key}": expected_components.get(key) == value for key, value in actual_components.items()}
    expected_package_hash = package.get("packageHash")
    basis = {k: deepcopy(v) for k, v in package.items() if k not in {"createdAt", "packageHash", "sizeBytes", "registryProjection"}}
    checks["packageHash"] = bool(expected_package_hash) and expected_package_hash == _digest(basis)
    model = package.get("model") or {}
    shared_hash = model.get("sharedModelHash")
    if shared_hash:
        model_basis = deepcopy(model); model_basis.pop("sharedModelHash", None)
        checks["sharedModelHash"] = shared_hash == _digest(model_basis)
    dataset = package.get("dataset") or {}
    if dataset.get("snapshotHash"):
        checks["datasetSnapshotHash"] = dataset.get("snapshotHash") == _digest(dataset.get("rows") or [])
    return {"ok": all(checks.values()), "checks": checks, "packageId": package.get("id"), "packageHash": expected_package_hash}


def registry_projection(package: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(package, dict) or package.get("schema") != PACKAGE_SCHEMA:
        raise ReproducibleModelPackageError("A normalized v0.50.0 package is required for registry projection.")
    model = package.get("model") or {}
    definition = model.get("scientificDefinition") or {}
    variables = model.get("variables") or []
    parameters = model.get("parameters") or []
    output_symbol = definition.get("outputSymbol") or "output"
    input_props = {str(row.get("symbol")): {"type": "number", "unit": row.get("unit") or ""} for row in variables if str(row.get("symbol") or "") != output_symbol}
    parameter_map = {
        str(row.get("symbol")): {"value": row.get("value"), "unit": row.get("unit") or "", "bounds": deepcopy(row.get("bounds") or {})}
        for row in parameters if row.get("symbol")
    }
    artifact_ids = [package["id"]] + [str(row.get("id")) for row in package.get("figures") or [] if row.get("id")] + [str(row.get("id")) for row in package.get("results") or [] if row.get("id")]
    return {
        "schema": REGISTRY_PROJECTION_SCHEMA,
        "version": VERSION,
        "model": {
            "id": model.get("id"),
            "modelVersion": package.get("modelVersion"),
            "title": model.get("title"),
            "description": f"Reproducible Lab model package {package.get('id')}",
            "projectId": (package.get("project") or {}).get("id") or "default",
            "type": "calibrated-model",
            "sourceRevision": (package.get("environment") or {}).get("sourceRevision"),
            "artifactIds": sorted(set(artifact_ids)),
            "inputSchema": {"type": "object", "properties": input_props},
            "outputSchema": {"type": "object", "properties": {str(output_symbol): {"type": "number"}}},
            "defaultInputs": {},
            "parameters": parameter_map,
            "environment": deepcopy(package.get("environment") or {}),
            "provenance": deepcopy(package.get("provenance") or {}),
            "metadata": {
                "reproduciblePackageId": package.get("id"),
                "reproduciblePackageHash": package.get("packageHash"),
                "sharedModelHash": model.get("sharedModelHash"),
                "datasetSnapshotHash": (package.get("dataset") or {}).get("snapshotHash"),
                "figureCount": len(package.get("figures") or []),
                "resultCount": len(package.get("results") or []),
                "methodCount": len(package.get("methods") or []),
            },
        },
        "channel": "draft",
    }


def build_research_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    built = build_package(payload)
    package = built["package"]
    files: dict[str, bytes] = {}
    def add_json(name: str, value: Any) -> None:
        files[name] = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    add_json("manifest.json", {"schema": RESEARCH_BUNDLE_SCHEMA, "version": VERSION, "packageId": package["id"], "packageHash": package["packageHash"], "createdAt": package["createdAt"]})
    add_json("model.json", package["model"])
    add_json("dataset.json", package["dataset"])
    add_json("methods.json", package["methods"])
    add_json("results.json", package["results"])
    add_json("figures.json", package["figures"])
    add_json("environment.json", package["environment"])
    add_json("provenance.json", package["provenance"])
    add_json("registry-projection.json", package["registryProjection"])
    add_json("package.json", package)
    readme = (
        f"Sustainable Catalyst Lab reproducible model research bundle v{VERSION}\n"
        f"Package: {package['id']}\nModel: {package['model']['title']}\nModel version: {package['modelVersion']}\n"
        f"Package SHA-256: {package['packageHash']}\n\n"
        "This bundle contains declarative scientific records and provenance only. It does not authorize arbitrary code execution, automatic publication, or automatic registry promotion.\n"
    ).encode("utf-8")
    files["README.txt"] = readme
    sums = "".join(f"{sha256(content).hexdigest()}  {name}\n" for name, content in sorted(files.items())).encode("utf-8")
    files["SHA256SUMS"] = sums
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            archive.writestr(name, content)
    raw = out.getvalue()
    if len(raw) > MAX_PACKAGE_BYTES:
        raise ReproducibleModelPackageError(f"Research bundle exceeds the {MAX_PACKAGE_BYTES}-byte limit.")
    filename = re.sub(r"[^A-Za-z0-9._-]+", "-", package["id"]).strip("-") + "-research-bundle-v0500.zip"
    return {
        "ok": True,
        "bundle": {
            "schema": RESEARCH_BUNDLE_SCHEMA,
            "version": VERSION,
            "filename": filename,
            "mimeType": "application/zip",
            "sizeBytes": len(raw),
            "sha256": sha256(raw).hexdigest(),
            "contentBase64": base64.b64encode(raw).decode("ascii"),
            "packageId": package["id"],
            "packageHash": package["packageHash"],
            "fileCount": len(files),
        },
        "package": package,
        "verification": built["verification"],
    }
