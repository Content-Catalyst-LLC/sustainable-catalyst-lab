from __future__ import annotations

import shutil
import time

import pytest
from fastapi.testclient import TestClient

from app.catalog import get_method, public_catalog
from app.executor import ExecutionError, compare_languages, execute_method, language_registry
from app.expressions import ContractValidationError, evaluate_contract
from app.main import app
from app.source_generator import generate_source

client = TestClient(app)


def test_catalog_contains_nineteen_curated_methods() -> None:
    catalog = public_catalog()
    assert catalog["version"] == "0.19.0"
    assert len(catalog["methods"]) == 19
    assert get_method("kinetic")["equation"]


def test_reference_evaluator_and_validation() -> None:
    _, outputs = evaluate_contract(get_method("kinetic"), {"mass": 10, "velocity": 5})
    assert outputs["kineticEnergyJ"] == pytest.approx(125)
    assert outputs["momentumKgMs"] == pytest.approx(50)
    with pytest.raises(ContractValidationError):
        evaluate_contract(get_method("kinetic"), {"mass": 0, "velocity": 5})
    with pytest.raises(ContractValidationError):
        evaluate_contract(get_method("kinetic"), {"unknown": 1})


def test_generated_rust_is_curated_and_structured() -> None:
    method = get_method("pv")
    inputs, _ = evaluate_contract(method, {})
    filename, source = generate_source(method, "rust", inputs)
    assert filename == "method.rs"
    assert "fn main()" in source
    assert "SC_RESULT powerW=" in source
    assert "std::process::Command" not in source


@pytest.mark.parametrize(
    "language,command",
    [
        ("python", "python3"),
        ("javascript", "node"),
        ("typescript", "tsc"),
        ("c", "gcc"),
        ("cpp", "g++"),
        ("fortran", "gfortran"),
        ("go", "go"),
    ],
)
def test_available_native_languages(language: str, command: str) -> None:
    if shutil.which(command) is None:
        pytest.skip(f"{command} is unavailable")
    result = execute_method("kinetic", language, {"mass": 10, "velocity": 5}, timeout_seconds=15)
    assert result["status"] == "VALIDATED"
    assert result["outputs"]["kineticEnergyJ"] == pytest.approx(125, rel=1e-10)
    assert result["inputFingerprint"]
    assert result["outputFingerprint"]
    assert "source" not in result


def test_rust_reports_unavailable_when_worker_lacks_rustc() -> None:
    if shutil.which("rustc") is not None:
        result = execute_method("kinetic", "rust", {}, timeout_seconds=20)
        assert result["status"] == "VALIDATED"
    else:
        with pytest.raises(ExecutionError) as exc:
            execute_method("kinetic", "rust", {})
        assert exc.value.code == "runtime_unavailable"


def test_comparison_reports_native_results() -> None:
    languages = [item for item in ("python", "javascript", "c") if language_registry()[item]["available"]]
    result = compare_languages("kinetic", languages, {"mass": 10, "velocity": 5}, timeout_seconds=15)
    assert result["successfulCount"] == len(languages)
    assert result["passed"]
    assert result["comparisonFingerprint"]


def test_api_health_and_metadata() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["curatedExecutionOnly"] is True
    assert health.json()["arbitrarySourceAccepted"] is False
    assert client.get("/v1/methods").status_code == 200
    assert client.get("/v1/languages").status_code == 200


def test_api_rejects_arbitrary_source_and_unknown_method() -> None:
    response = client.post(
        "/v1/execute",
        json={"methodId": "kinetic", "language": "python", "inputs": {}, "source": "import os"},
    )
    assert response.status_code == 422
    response = client.post("/v1/execute", json={"methodId": "unknown", "language": "python", "inputs": {}})
    assert response.status_code == 404


def test_api_execute_and_compare() -> None:
    if language_registry()["python"]["available"]:
        response = client.post("/v1/execute", json={"methodId": "kinetic", "language": "python", "inputs": {"mass": 10, "velocity": 5}})
        assert response.status_code == 200
        assert response.json()["status"] == "VALIDATED"
    available = [language for language in ("python", "javascript") if language_registry()[language]["available"]]
    response = client.post("/v1/compare", json={"methodId": "kinetic", "languages": available, "inputs": {"mass": 10, "velocity": 5}})
    assert response.status_code == 200
    assert response.json()["passed"] is True


def test_in_memory_job_lifecycle() -> None:
    if not language_registry()["python"]["available"]:
        pytest.skip("python3 runtime unavailable")
    response = client.post(
        "/v1/jobs",
        json={"operation": "execute", "execute": {"methodId": "kinetic", "language": "python", "inputs": {"mass": 10, "velocity": 5}}},
    )
    assert response.status_code == 202
    job_id = response.json()["jobId"]
    record = None
    for _ in range(100):
        record = client.get(f"/v1/jobs/{job_id}").json()
        if record["status"] in {"finished", "failed"}:
            break
        time.sleep(0.02)
    assert record is not None
    assert record["status"] == "finished"
    assert record["result"]["status"] == "VALIDATED"


def test_executor_avoids_thread_unsafe_preexec_fn() -> None:
    from pathlib import Path

    executor_source = (Path(__file__).resolve().parents[1] / "app" / "executor.py").read_text()
    assert "preexec_fn=" not in executor_source
