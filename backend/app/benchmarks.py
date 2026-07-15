from __future__ import annotations

import copy
import math
import time
from dataclasses import dataclass
from typing import Any, Callable

from .schemas import ComputeRequest, ComputeResponse

Executor = Callable[[ComputeRequest], ComputeResponse]


@dataclass(frozen=True)
class BenchmarkDefinition:
    id: str
    title: str
    method: str
    domain: str
    description: str
    inputs: dict[str, Any]
    parameters: dict[str, Any]
    assertions: list[dict[str, Any]]
    random_seed: int | None = None
    tags: tuple[str, ...] = ()
    units: dict[str, str] | None = None
    browser_reference: bool = False
    convergence: dict[str, Any] | None = None

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "method": self.method,
            "domain": self.domain,
            "description": self.description,
            "inputs": copy.deepcopy(self.inputs),
            "parameters": copy.deepcopy(self.parameters),
            "assertions": copy.deepcopy(self.assertions),
            "randomSeed": self.random_seed,
            "tags": list(self.tags),
            "units": copy.deepcopy(self.units or {}),
            "browserReference": self.browser_reference,
            "convergence": copy.deepcopy(self.convergence),
        }


def _assert(path: str, operation: str, expected: Any = None, **options: Any) -> dict[str, Any]:
    row = {"path": path, "operation": operation}
    if expected is not None:
        row["expected"] = expected
    row.update(options)
    return row


BENCHMARKS: tuple[BenchmarkDefinition, ...] = (
    BenchmarkDefinition(
        id="root.sqrt2.brentq",
        title="Brent root of x² − 2",
        method="numerics.root_scalar_polynomial",
        domain="root-finding",
        description="Known-answer root benchmark for a sign-changing polynomial bracket.",
        inputs={"coefficients": [1, 0, -2], "bracket": [0, 2]},
        parameters={"absoluteTolerance": 1e-12, "relativeTolerance": 1e-12, "maxIterations": 200},
        assertions=[
            _assert("root", "close", math.sqrt(2), absoluteTolerance=1e-10, relativeTolerance=1e-10, unit="dimensionless"),
            _assert("functionValue", "absolute_below", 1e-10),
            _assert("converged", "equal", True),
        ],
        tags=("known-answer", "convergence", "browser-reference"),
        browser_reference=True,
        convergence={
            "parameterSets": [
                {"absoluteTolerance": 1e-4, "relativeTolerance": 1e-4},
                {"absoluteTolerance": 1e-8, "relativeTolerance": 1e-8},
                {"absoluteTolerance": 1e-12, "relativeTolerance": 1e-12},
            ],
            "metricPath": "root",
            "reference": math.sqrt(2),
            "expectedTrend": "non-increasing-error",
        },
    ),
    BenchmarkDefinition(
        id="quadrature.polynomial.exact",
        title="Exact polynomial quadrature",
        method="numerics.adaptive_quadrature_polynomial",
        domain="integration",
        description="Adaptive integration is checked against the analytic antiderivative.",
        inputs={"coefficients": [3, 0, 2], "lower": 0, "upper": 2},
        parameters={"absoluteTolerance": 1e-12, "relativeTolerance": 1e-12},
        assertions=[
            _assert("integral", "close", 12.0, absoluteTolerance=1e-10, relativeTolerance=1e-10, unit="integral units"),
            _assert("polynomialExactIntegral", "close", 12.0, absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("absoluteDifference", "less_equal", 1e-10),
        ],
        tags=("known-answer", "analytic", "browser-reference"),
        browser_reference=True,
    ),
    BenchmarkDefinition(
        id="interpolation.linear.reference",
        title="Linear interpolation reference points",
        method="numerics.interpolation",
        domain="interpolation",
        description="A straight-line dataset must interpolate to exact midpoint values.",
        inputs={"x": [0, 1, 2], "y": [0, 2, 4], "query": [0.5, 1.5]},
        parameters={"kind": "linear", "extrapolate": False},
        assertions=[
            _assert("values", "sequence_close", [1.0, 3.0], absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("extrapolated", "equal", False),
        ],
        tags=("known-answer", "browser-reference"),
        browser_reference=True,
    ),
    BenchmarkDefinition(
        id="ode.exponential.analytic",
        title="Exponential ODE analytic solution",
        method="numerics.ode_first_order",
        domain="differential-equations",
        description="RK45 output is checked against y(t)=2e^(0.25t) at t=4.",
        inputs={"model": "exponential", "initialValue": 2, "startTime": 0, "endTime": 4, "points": 81},
        parameters={"rate": 0.25, "relativeTolerance": 1e-9, "absoluteTolerance": 1e-11},
        assertions=[
            _assert("finalValue", "close", 2 * math.e, absoluteTolerance=2e-7, relativeTolerance=2e-7, unit="state units"),
            _assert("success", "equal", True),
        ],
        tags=("known-answer", "convergence", "browser-reference"),
        browser_reference=True,
        convergence={
            "parameterSets": [
                {"rate": 0.25, "relativeTolerance": 1e-3, "absoluteTolerance": 1e-6},
                {"rate": 0.25, "relativeTolerance": 1e-6, "absoluteTolerance": 1e-9},
                {"rate": 0.25, "relativeTolerance": 1e-9, "absoluteTolerance": 1e-12},
            ],
            "metricPath": "finalValue",
            "reference": 2 * math.e,
            "expectedTrend": "non-increasing-error",
        },
    ),
    BenchmarkDefinition(
        id="eigen.symmetric.2x2",
        title="Symmetric 2×2 eigen benchmark",
        method="numerics.eigen_analysis",
        domain="linear-algebra",
        description="A symmetric matrix with analytic eigenvalues 1 and 3 validates eigenpairs and residuals.",
        inputs={"matrix": [[2, 1], [1, 2]]},
        parameters={"symmetricTolerance": 1e-12},
        assertions=[
            _assert("eigenvalues", "sorted_sequence_close", [1.0, 3.0], absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("residualNorms", "max_below", 1e-10),
            _assert("trace", "close", 4.0, absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("determinant", "close", 3.0, absoluteTolerance=1e-12, relativeTolerance=1e-12),
        ],
        tags=("known-answer", "residual", "browser-reference"),
        browser_reference=True,
    ),
    BenchmarkDefinition(
        id="optimization.quadratic.minimum",
        title="Quadratic bounded minimum",
        method="optimization.scalar_bounded",
        domain="optimization",
        description="The registered quadratic x²−4x+7 has an exact minimum of 3 at x=2.",
        inputs={"objective": "quadratic", "lower": -10, "upper": 10, "coefficients": [1, -4, 7]},
        parameters={"absoluteTolerance": 1e-10, "maxIterations": 1000},
        assertions=[
            _assert("x", "close", 2.0, absoluteTolerance=1e-6, relativeTolerance=1e-8),
            _assert("minimum", "close", 3.0, absoluteTolerance=1e-8, relativeTolerance=1e-8),
            _assert("success", "equal", True),
        ],
        tags=("known-answer", "browser-reference"),
        browser_reference=True,
    ),
    BenchmarkDefinition(
        id="optimization.linear.reference",
        title="Two-variable linear program",
        method="optimization.linear_program",
        domain="optimization",
        description="A bounded two-variable model validates HiGHS objective and decision values.",
        inputs={
            "objective": [-3, -2],
            "inequalityMatrix": [[2, 1], [1, 2]],
            "inequalityVector": [18, 16],
            "bounds": [[0, None], [0, None]],
        },
        parameters={},
        assertions=[
            _assert("objectiveMinimum", "close", -88.0 / 3.0, absoluteTolerance=1e-8, relativeTolerance=1e-8),
            _assert("solution", "sequence_close", [20.0 / 3.0, 14.0 / 3.0], absoluteTolerance=1e-8, relativeTolerance=1e-8),
            _assert("success", "equal", True),
        ],
        tags=("known-answer", "constraint-residual"),
    ),
    BenchmarkDefinition(
        id="fft.single-tone.4hz",
        title="Single-tone FFT at 4 Hz",
        method="signal.fft_spectrum",
        domain="signal-processing",
        description="A periodic unit-amplitude signal validates frequency-bin and amplitude recovery.",
        inputs={"values": [0, 1, 0, -1] * 8, "sampleRate": 16},
        parameters={"window": "rectangular", "detrend": "none"},
        assertions=[
            _assert("peakFrequencyHz", "close", 4.0, absoluteTolerance=1e-12, relativeTolerance=1e-12, unit="Hz"),
            _assert("peakAmplitude", "close", 1.0, absoluteTolerance=1e-12, relativeTolerance=1e-12),
        ],
        tags=("known-answer", "spectral"),
        units={"sampleRate": "Hz"},
    ),
    BenchmarkDefinition(
        id="monte-carlo.linear.seeded",
        title="Seeded linear uncertainty propagation",
        method="uncertainty.monte_carlo_propagation",
        domain="uncertainty-analysis",
        description="A fixed-seed normal input validates reproducibility and statistical agreement.",
        inputs={
            "model": "linear",
            "samples": 50000,
            "distributions": [
                {"name": "x", "distribution": "normal", "mean": 10, "stdDev": 2},
                {"name": "y", "distribution": "normal", "mean": 5, "stdDev": 1},
            ],
        },
        parameters={"coefficients": [2, -1], "intercept": 3, "confidence": 0.95},
        random_seed=27101,
        assertions=[
            _assert("mean", "close", 18.0, absoluteTolerance=0.05, relativeTolerance=0.005),
            _assert("standardDeviation", "close", math.sqrt(17), absoluteTolerance=0.05, relativeTolerance=0.02),
            _assert("samples", "equal", 50000),
        ],
        tags=("seeded", "statistical", "reproducibility"),
    ),
    BenchmarkDefinition(
        id="bootstrap.constant.zero-variance",
        title="Bootstrap constant-sample interval",
        method="uncertainty.bootstrap_mean_interval",
        domain="uncertainty-analysis",
        description="A constant sample must produce a zero-width confidence interval and zero standard error.",
        inputs={"values": [7, 7, 7, 7, 7, 7], "resamples": 1000},
        parameters={"confidence": 0.95},
        random_seed=27102,
        assertions=[
            _assert("sampleMean", "close", 7.0, absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("bootstrapStandardError", "absolute_below", 1e-12),
            _assert("confidenceInterval", "sequence_close", [7.0, 7.0], absoluteTolerance=1e-12, relativeTolerance=1e-12),
        ],
        tags=("seeded", "known-answer", "stability"),
    ),
    BenchmarkDefinition(
        id="sensitivity.product.analytic",
        title="Product-model analytic sensitivities",
        method="sensitivity.local_finite_difference",
        domain="sensitivity-analysis",
        description="Finite differences are checked against analytic product derivatives.",
        inputs={"model": "product", "baseline": {"efficiency": 0.2, "area": 10, "irradiance": 1000}},
        parameters={"relativeStep": 1e-5, "absoluteStep": 1e-9},
        assertions=[
            _assert("baselineOutput", "close", 2000.0, absoluteTolerance=1e-8, relativeTolerance=1e-8),
            _assert("sensitivities", "named_derivatives_close", {"efficiency": 10000.0, "area": 200.0, "irradiance": 2.0}, absoluteTolerance=2e-4, relativeTolerance=2e-5),
        ],
        tags=("known-answer", "derivative"),
    ),
    BenchmarkDefinition(
        id="sweep.photovoltaic.monotonic",
        title="Photovoltaic efficiency sweep",
        method="simulation.parameter_sweep",
        domain="parameter-sweeps",
        description="A deterministic efficiency sweep validates exact endpoints and monotonic response.",
        inputs={
            "model": "photovoltaic_output",
            "parameter": "efficiency",
            "values": [0.1, 0.15, 0.2, 0.25],
            "fixed": {"irradiance": 1000, "area": 10, "systemFactor": 0.8},
        },
        parameters={},
        assertions=[
            _assert("minimumOutput", "close", 800.0, absoluteTolerance=1e-10, relativeTolerance=1e-10, unit="W"),
            _assert("maximumOutput", "close", 2000.0, absoluteTolerance=1e-10, relativeTolerance=1e-10, unit="W"),
            _assert("monotonicIncreasing", "equal", True),
        ],
        tags=("known-answer", "monotonic", "browser-reference"),
        units={"minimumOutput": "W", "maximumOutput": "W"},
        browser_reference=True,
    ),
    BenchmarkDefinition(
        id="linear-system.reference.2x2",
        title="Two-equation linear system",
        method="numerics.linear_system",
        domain="linear-algebra",
        description="A known 2×2 system validates solution and residual diagnostics.",
        inputs={"matrix": [[3, 2], [1, 2]], "vector": [5, 5]},
        parameters={},
        assertions=[
            _assert("solution", "sequence_close", [0.0, 2.5], absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("residualNorm", "less_equal", 1e-12),
        ],
        tags=("known-answer", "residual", "browser-reference"),
        browser_reference=True,
    ),
    BenchmarkDefinition(
        id="sampled-integration.parabola",
        title="Sampled parabola integration",
        method="numerics.sampled_integration",
        domain="integration",
        description="Simpson integration of a quadratic on uniform points must reproduce 1/3.",
        inputs={"x": [0, 0.25, 0.5, 0.75, 1.0], "y": [0, 0.0625, 0.25, 0.5625, 1.0]},
        parameters={},
        assertions=[
            _assert("simpson", "close", 1.0 / 3.0, absoluteTolerance=1e-12, relativeTolerance=1e-12),
            _assert("trapezoid", "close", 0.34375, absoluteTolerance=1e-12, relativeTolerance=1e-12),
        ],
        tags=("known-answer", "browser-reference"),
        browser_reference=True,
    ),
)

REGISTRY = {benchmark.id: benchmark for benchmark in BENCHMARKS}


def catalog() -> list[dict[str, Any]]:
    return [benchmark.public() for benchmark in BENCHMARKS]


def resolve(benchmark_id: str) -> BenchmarkDefinition:
    try:
        return REGISTRY[benchmark_id]
    except KeyError as exc:
        raise KeyError(f"Unknown numerical benchmark: {benchmark_id}") from exc


def _extract(source: Any, path: str) -> Any:
    current = source
    if not path:
        return current
    for segment in path.split("."):
        if isinstance(current, dict):
            if segment not in current:
                raise KeyError(f"Output path not found: {path}")
            current = current[segment]
        elif isinstance(current, list) and segment.isdigit():
            current = current[int(segment)]
        else:
            raise KeyError(f"Output path not found: {path}")
    return current


def _numbers(value: Any) -> list[float]:
    if not isinstance(value, list):
        raise TypeError("Expected a numerical list.")
    result = []
    for item in value:
        if isinstance(item, dict) and "real" in item and abs(float(item.get("imaginary", 0))) <= 1e-12:
            result.append(float(item["real"]))
        else:
            result.append(float(item))
    return result


def _close(actual: float, expected: float, assertion: dict[str, Any]) -> tuple[bool, dict[str, float]]:
    absolute = float(assertion.get("absoluteTolerance", 1e-9))
    relative = float(assertion.get("relativeTolerance", 1e-9))
    error = abs(float(actual) - float(expected))
    allowed = absolute + relative * abs(float(expected))
    return error <= allowed, {"absoluteError": error, "allowedError": allowed}


def evaluate_assertion(outputs: dict[str, Any], assertion: dict[str, Any]) -> dict[str, Any]:
    path = str(assertion.get("path") or "")
    operation = str(assertion.get("operation") or "equal")
    expected = assertion.get("expected")
    result: dict[str, Any] = {"path": path, "operation": operation, "expected": expected, "unit": assertion.get("unit")}
    try:
        actual = _extract(outputs, path)
        result["actual"] = actual
        detail: dict[str, Any] = {}
        if operation == "equal":
            passed = actual == expected
        elif operation == "close":
            passed, detail = _close(float(actual), float(expected), assertion)
        elif operation == "sequence_close":
            actual_numbers = _numbers(actual)
            expected_numbers = _numbers(expected)
            if len(actual_numbers) != len(expected_numbers):
                passed = False
                detail = {"reason": "length_mismatch", "actualLength": len(actual_numbers), "expectedLength": len(expected_numbers)}
            else:
                checks = [_close(a, e, assertion) for a, e in zip(actual_numbers, expected_numbers)]
                passed = all(row[0] for row in checks)
                detail = {"maximumAbsoluteError": max((row[1]["absoluteError"] for row in checks), default=0.0)}
        elif operation == "sorted_sequence_close":
            actual_numbers = sorted(_numbers(actual))
            expected_numbers = sorted(_numbers(expected))
            checks = [_close(a, e, assertion) for a, e in zip(actual_numbers, expected_numbers)] if len(actual_numbers) == len(expected_numbers) else []
            passed = len(actual_numbers) == len(expected_numbers) and all(row[0] for row in checks)
            detail = {"maximumAbsoluteError": max((row[1]["absoluteError"] for row in checks), default=None)}
        elif operation == "absolute_below":
            threshold = float(expected)
            passed = abs(float(actual)) < threshold
            detail = {"absoluteValue": abs(float(actual)), "threshold": threshold}
        elif operation == "less_equal":
            passed = float(actual) <= float(expected)
        elif operation == "max_below":
            values = _numbers(actual)
            passed = max(values, default=0.0) < float(expected)
            detail = {"maximum": max(values, default=0.0)}
        elif operation == "named_derivatives_close":
            if not isinstance(actual, list) or not isinstance(expected, dict):
                passed = False
                detail = {"reason": "invalid_derivative_shape"}
            else:
                actual_map = {str(row.get("variable")): float(row.get("derivative")) for row in actual if isinstance(row, dict)}
                checks = []
                for key, expected_value in expected.items():
                    if key not in actual_map:
                        checks.append((False, {"variable": key, "reason": "missing"}))
                    else:
                        ok, row_detail = _close(actual_map[key], float(expected_value), assertion)
                        row_detail["variable"] = key
                        checks.append((ok, row_detail))
                passed = all(row[0] for row in checks)
                detail = {"variables": [row[1] for row in checks]}
        else:
            passed = False
            detail = {"reason": f"unsupported_operation:{operation}"}
        result.update(detail)
        result["passed"] = bool(passed)
    except Exception as exc:
        result["passed"] = False
        result["error"] = str(exc)
    return result


def run_benchmark(benchmark_id: str, executor: Executor) -> dict[str, Any]:
    benchmark = resolve(benchmark_id)
    request = ComputeRequest(
        method=benchmark.method,
        inputs=copy.deepcopy(benchmark.inputs),
        parameters=copy.deepcopy(benchmark.parameters),
        units=copy.deepcopy(benchmark.units or {}),
        requested_outputs=["summary", "values", "validation", "provenance"],
        random_seed=benchmark.random_seed,
    )
    started = time.perf_counter()
    response = executor(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    outputs = response.outputs
    assertions = [evaluate_assertion(outputs, row) for row in benchmark.assertions]
    return {
        "schema": "sc-lab-numerical-benchmark-result/1.0",
        "benchmark": benchmark.public(),
        "methodVersion": response.method_version,
        "passed": all(row.get("passed") for row in assertions),
        "assertions": assertions,
        "outputs": outputs,
        "computeValidation": response.validation,
        "provenance": response.provenance.model_dump(mode="json", by_alias=True),
        "benchmarkRuntimeMs": elapsed_ms,
    }


def run_suite(executor: Executor, benchmark_ids: list[str] | None = None) -> dict[str, Any]:
    selected = [resolve(value) for value in benchmark_ids] if benchmark_ids else list(BENCHMARKS)
    results = []
    started = time.perf_counter()
    for benchmark in selected:
        try:
            results.append(run_benchmark(benchmark.id, executor))
        except Exception as exc:
            results.append({
                "schema": "sc-lab-numerical-benchmark-result/1.0",
                "benchmark": benchmark.public(),
                "passed": False,
                "assertions": [],
                "error": str(exc),
            })
    passed = sum(1 for row in results if row.get("passed"))
    return {
        "schema": "sc-lab-numerical-benchmark-suite-result/1.0",
        "benchmarkCount": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "success": passed == len(results),
        "runtimeMs": (time.perf_counter() - started) * 1000,
        "results": results,
    }


def run_convergence(benchmark_id: str, executor: Executor) -> dict[str, Any]:
    benchmark = resolve(benchmark_id)
    definition = benchmark.convergence
    if not definition:
        raise ValueError(f"Benchmark {benchmark_id} does not define a convergence series.")
    reference = float(definition["reference"])
    metric_path = str(definition["metricPath"])
    rows = []
    for index, overrides in enumerate(definition.get("parameterSets") or []):
        request = ComputeRequest(
            method=benchmark.method,
            inputs=copy.deepcopy(benchmark.inputs),
            parameters={**copy.deepcopy(benchmark.parameters), **copy.deepcopy(overrides)},
            units=copy.deepcopy(benchmark.units or {}),
            requested_outputs=["summary", "values"],
            random_seed=benchmark.random_seed,
        )
        response = executor(request)
        actual = float(_extract(response.outputs, metric_path))
        rows.append({
            "level": index + 1,
            "parameters": overrides,
            "actual": actual,
            "reference": reference,
            "absoluteError": abs(actual - reference),
            "runtimeMs": response.provenance.duration_ms,
        })
    errors = [row["absoluteError"] for row in rows]
    non_increasing = all(errors[index + 1] <= errors[index] * 1.05 + 1e-15 for index in range(len(errors) - 1))
    ratios = [None if errors[index + 1] == 0 else errors[index] / errors[index + 1] for index in range(len(errors) - 1)]
    return {
        "schema": "sc-lab-numerical-convergence-result/1.0",
        "benchmark": benchmark.public(),
        "metricPath": metric_path,
        "reference": reference,
        "rows": rows,
        "errorRatios": ratios,
        "nonIncreasingError": non_increasing,
        "passed": non_increasing and errors[-1] <= errors[0],
    }
