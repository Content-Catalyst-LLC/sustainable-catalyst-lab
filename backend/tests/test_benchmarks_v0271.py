from fastapi.testclient import TestClient

from app.benchmarks import catalog, run_convergence, run_suite
from app.compute import run_compute
from app.main import app


def execute(request):
    return run_compute(request, {"client": "pytest", "authMode": "test"})


def test_catalog_contains_fourteen_benchmarks():
    rows = catalog()
    assert len(rows) == 14
    assert all(row["method"] for row in rows)
    assert sum(1 for row in rows if row["browserReference"]) >= 8


def test_all_benchmarks_pass_known_answers():
    report = run_suite(execute)
    assert report["success"] is True
    assert report["passed"] == 14
    assert report["failed"] == 0


def test_root_and_ode_convergence_improve():
    for benchmark_id in ("root.sqrt2.brentq", "ode.exponential.analytic"):
        report = run_convergence(benchmark_id, execute)
        assert report["passed"] is True
        assert report["nonIncreasingError"] is True
        assert report["rows"][-1]["absoluteError"] <= report["rows"][0]["absoluteError"]


def test_benchmark_endpoints_with_open_development_auth():
    with TestClient(app) as client:
        listing = client.get("/v1/benchmarks")
        assert listing.status_code == 200
        assert listing.json()["benchmarkCount"] == 14

        single = client.post("/v1/benchmarks/run", json={"benchmarkId": "root.sqrt2.brentq"})
        assert single.status_code == 200
        assert single.json()["passed"] is True

        convergence = client.post("/v1/benchmarks/convergence", json={"benchmarkId": "ode.exponential.analytic"})
        assert convergence.status_code == 200
        assert convergence.json()["passed"] is True


def test_health_exposes_benchmark_count():
    with TestClient(app) as client:
        body = client.get("/health").json()
        assert body["version"] == "0.36.1"
        assert body["benchmarkCount"] == 14
