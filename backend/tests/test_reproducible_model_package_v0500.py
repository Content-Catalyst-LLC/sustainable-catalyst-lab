from __future__ import annotations
import base64, io, zipfile
import pytest
from app.reproducible_model_package import (
    ReproducibleModelPackageError, build_package, build_research_bundle, health, policies, registry_projection, verify_package,
)


def model():
    return {
        "id": "urban-heat-model", "title": "Urban heat model", "family": "declarative-expression",
        "definition": {"equation": "y = a + b*x"},
        "variables": [{"symbol": "x", "label": "Canopy", "unit": "%", "role": "input"}, {"symbol": "y", "label": "Temperature", "unit": "C", "role": "response"}],
        "parameters": [{"symbol": "a", "value": 30, "bounds": {"lower": 0, "upper": 60}}, {"symbol": "b", "value": -0.2, "bounds": {"lower": -5, "upper": 5}}],
        "datasetBindings": [{"symbol": "x", "column": "canopy", "role": "feature", "unit": "%"}, {"symbol": "y", "column": "temperature", "role": "response", "unit": "C"}],
        "assumptions": ["Illustrative linear relation"], "limitations": ["Not deployment calibrated"],
        "provenance": {"projectId": "project-1"},
    }


def figure():
    return {"id": "fig-1", "title": "Fit", "graph": {"kind": "line-scatter", "title": "Fit", "xLabel": "Canopy", "yLabel": "Temperature", "series": [{"label": "Observed", "mode": "points", "points": [{"x": 10, "y": 28}, {"x": 20, "y": 26}]}]}}


def request():
    return {
        "model": model(), "modelVersion": "1.0.0", "project": {"id": "project-1", "name": "Urban heat study"},
        "dataset": {"mode": "snapshot", "datasetId": "heat-data", "title": "Heat observations", "rows": [{"canopy": 10, "temperature": 28}, {"canopy": 20, "temperature": 26}]},
        "methods": [{"id": "method-1", "type": "cross-validation", "folds": 5}],
        "results": [{"id": "result-1", "type": "diagnostics", "rmse": 0.8}],
        "figures": [figure()],
        "provenance": {"operator": "researcher"},
    }


def test_health_and_policy():
    assert health()["ok"] and health()["portableZipBundle"]
    p = policies(); assert p["immutablePackageHash"] and p["boundaries"]["arbitraryCode"] is False


def test_build_and_verify_package():
    built = build_package(request()); package = built["package"]
    assert built["verification"]["ok"]
    assert package["schema"].endswith("/0.50.0")
    assert package["dataset"]["rowCount"] == 2
    assert package["dataset"]["snapshotHash"]
    assert package["componentHashes"]["figures"]
    assert verify_package(package)["ok"]


def test_tamper_is_detected():
    package = build_package(request())["package"]
    package["dataset"]["rows"][0]["temperature"] = 99
    checked = verify_package(package)
    assert not checked["ok"]
    assert checked["checks"]["component:dataset"] is False


def test_registry_projection_is_semantic_and_draft():
    package = build_package(request())["package"]
    projection = registry_projection(package)
    assert projection["model"]["modelVersion"] == "1.0.0"
    assert projection["model"]["type"] == "calibrated-model"
    assert projection["channel"] == "draft"
    assert projection["model"]["metadata"]["reproduciblePackageHash"] == package["packageHash"]


def test_portable_research_zip_contains_verification_files():
    result = build_research_bundle(request()); bundle = result["bundle"]
    raw = base64.b64decode(bundle["contentBase64"])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = set(z.namelist())
        assert {"manifest.json", "model.json", "dataset.json", "methods.json", "results.json", "figures.json", "environment.json", "provenance.json", "registry-projection.json", "package.json", "README.txt", "SHA256SUMS"}.issubset(names)
    assert bundle["fileCount"] == 12


def test_executable_fields_are_rejected():
    payload = request(); payload["results"] = [{"id": "bad", "python": "print('no')"}]
    with pytest.raises(ReproducibleModelPackageError, match="Executable field"):
        build_package(payload)


def test_dataset_limit_and_semver_are_governed():
    payload = request(); payload["modelVersion"] = "release-one"
    with pytest.raises(ReproducibleModelPackageError, match="semantic version"):
        build_package(payload)
