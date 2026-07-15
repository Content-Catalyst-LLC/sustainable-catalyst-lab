from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np
from scipy import integrate, interpolate, optimize, signal, stats

from .core import MethodInputError, _array, _number


def _coefficients(inputs: dict[str, Any], key: str = "coefficients", *, minimum: int = 1, maximum: int = 32) -> np.ndarray:
    values = _array(inputs, key, minimum=minimum, maximum=maximum)
    if np.allclose(values, 0):
        raise MethodInputError(f"{key} must include at least one non-zero coefficient.")
    return values


def _matrix(inputs: dict[str, Any], key: str, *, minimum: int = 1, maximum: int = 100, square: bool = False) -> np.ndarray:
    try:
        matrix = np.asarray(inputs.get(key), dtype=float)
    except (TypeError, ValueError) as exc:
        raise MethodInputError(f"{key} must be a finite numerical matrix.") from exc
    if matrix.ndim != 2 or matrix.shape[0] < minimum or matrix.shape[1] < minimum:
        raise MethodInputError(f"{key} must be a two-dimensional numerical matrix.")
    if matrix.shape[0] > maximum or matrix.shape[1] > maximum or not np.isfinite(matrix).all():
        raise MethodInputError(f"{key} exceeds the {maximum}x{maximum} limit or contains non-finite values.")
    if square and matrix.shape[0] != matrix.shape[1]:
        raise MethodInputError(f"{key} must be square.")
    return matrix


def _json_number(value: complex | float | np.number) -> float | dict[str, float]:
    number = complex(value)
    if abs(number.imag) <= 1e-12:
        return float(number.real)
    return {"real": float(number.real), "imaginary": float(number.imag)}


def polynomial_root_scalar(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    coefficients = _coefficients(inputs, minimum=2)
    bracket = _array(inputs, "bracket", minimum=2, maximum=2)
    lower, upper = float(bracket[0]), float(bracket[1])
    if lower >= upper:
        raise MethodInputError("bracket must be ordered [lower, upper].")
    xtol = float(parameters.get("absoluteTolerance", 1e-10))
    rtol = float(parameters.get("relativeTolerance", 1e-10))
    max_iter = int(parameters.get("maxIterations", 200))
    if not (0 < xtol <= 1) or not (1e-15 <= rtol <= 1e-2) or not (1 <= max_iter <= 10000):
        raise MethodInputError("Root tolerances or maxIterations are outside the supported range.")

    def function(x: float) -> float:
        return float(np.polyval(coefficients, x))

    solver = str(parameters.get("solver", "brentq"))
    if solver not in {"brentq", "bisect", "ridder", "toms748"}: raise MethodInputError("Unsupported registered root solver.")
    f_lower, f_upper = function(lower), function(upper)
    if f_lower == 0:
        return {"root": lower, "functionValue": 0.0, "iterations": 0, "converged": True, "method": "endpoint", "solver": solver, "absoluteTolerance": xtol, "relativeTolerance": rtol}
    if f_upper == 0:
        return {"root": upper, "functionValue": 0.0, "iterations": 0, "converged": True, "method": "endpoint", "solver": solver, "absoluteTolerance": xtol, "relativeTolerance": rtol}
    if f_lower * f_upper > 0:
        raise MethodInputError("The polynomial must change sign across the bracket.")
    result = optimize.root_scalar(function, bracket=(lower, upper), method=solver, xtol=xtol, rtol=rtol, maxiter=max_iter)
    return {
        "root": float(result.root),
        "functionValue": function(float(result.root)),
        "iterations": int(result.iterations),
        "functionCalls": int(result.function_calls),
        "converged": bool(result.converged),
        "method": str(result.method),
        "solver": solver,
        "absoluteTolerance": xtol,
        "relativeTolerance": rtol,
    }


def polynomial_quadrature(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    coefficients = _coefficients(inputs)
    lower = _number(inputs, "lower")
    upper = _number(inputs, "upper")
    if lower == upper:
        return {"integral": 0.0, "absoluteErrorEstimate": 0.0, "evaluations": 0}
    epsabs = float(parameters.get("absoluteTolerance", 1e-10))
    epsrel = float(parameters.get("relativeTolerance", 1e-10))
    if not (0 < epsabs <= 1) or not (1e-15 <= epsrel <= 1e-2):
        raise MethodInputError("Quadrature tolerances are outside the supported range.")
    counter = {"count": 0}

    def function(x: float) -> float:
        counter["count"] += 1
        return float(np.polyval(coefficients, x))

    value, error = integrate.quad(function, lower, upper, epsabs=epsabs, epsrel=epsrel, limit=200)
    anti = np.polyint(coefficients)
    exact = float(np.polyval(anti, upper) - np.polyval(anti, lower))
    return {
        "integral": float(value),
        "absoluteErrorEstimate": float(error),
        "polynomialExactIntegral": exact,
        "absoluteDifference": abs(float(value) - exact),
        "evaluations": int(counter["count"]),
    }


def interpolation_query(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    x = _array(inputs, "x", minimum=2, maximum=10000)
    y = _array(inputs, "y", minimum=2, maximum=10000)
    query = _array(inputs, "query", minimum=1, maximum=10000)
    if x.size != y.size:
        raise MethodInputError("x and y must have equal length.")
    if not np.all(np.diff(x) > 0):
        raise MethodInputError("x must be strictly increasing.")
    kind = str(parameters.get("kind", "linear")).lower()
    extrapolate = bool(parameters.get("extrapolate", False))
    if not extrapolate and (np.min(query) < x[0] or np.max(query) > x[-1]):
        raise MethodInputError("query values must remain within the observed x range unless extrapolate is enabled.")
    if kind == "linear":
        function: Callable[[np.ndarray], np.ndarray] = interpolate.interp1d(
            x, y, kind="linear", bounds_error=not extrapolate, fill_value="extrapolate" if extrapolate else np.nan, assume_sorted=True
        )
    elif kind == "pchip":
        function = interpolate.PchipInterpolator(x, y, extrapolate=extrapolate)
    elif kind == "cubic":
        if x.size < 4:
            raise MethodInputError("Cubic interpolation requires at least four observed points.")
        function = interpolate.CubicSpline(x, y, extrapolate=extrapolate)
    else:
        raise MethodInputError("kind must be linear, pchip, or cubic.")
    values = np.asarray(function(query), dtype=float)
    return {"kind": kind, "query": query.tolist(), "values": values.tolist(), "extrapolated": bool(np.any((query < x[0]) | (query > x[-1])))}


def ode_first_order(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    model = str(inputs.get("model") or "exponential").lower()
    y0 = _number(inputs, "initialValue")
    start = _number(inputs, "startTime")
    end = _number(inputs, "endTime")
    points = int(_number(inputs, "points", minimum=2, maximum=2000))
    if start >= end:
        raise MethodInputError("startTime must be less than endTime.")
    rtol = float(parameters.get("relativeTolerance", 1e-7))
    atol = float(parameters.get("absoluteTolerance", 1e-9))
    if not (1e-12 <= atol <= 1e-2) or not (1e-12 <= rtol <= 1e-2):
        raise MethodInputError("ODE tolerances are outside the supported range.")

    if model == "exponential":
        rate = float(parameters.get("rate", 0.25))
        derivative = lambda t, y: [rate * y[0]]
    elif model == "decay":
        rate = float(parameters.get("rate", 0.25))
        if rate < 0:
            raise MethodInputError("decay rate must be non-negative.")
        derivative = lambda t, y: [-rate * y[0]]
    elif model == "logistic":
        rate = float(parameters.get("rate", 0.5))
        capacity = float(parameters.get("carryingCapacity", 100.0))
        if capacity <= 0:
            raise MethodInputError("carryingCapacity must be positive.")
        derivative = lambda t, y: [rate * y[0] * (1.0 - y[0] / capacity)]
    elif model == "forced_linear":
        decay = float(parameters.get("decay", 0.2))
        forcing = float(parameters.get("forcing", 1.0))
        frequency = float(parameters.get("frequency", 1.0))
        derivative = lambda t, y: [-decay * y[0] + forcing * math.sin(frequency * t)]
    else:
        raise MethodInputError("model must be exponential, decay, logistic, or forced_linear.")
    numeric_parameters = [float(v) for v in parameters.values() if isinstance(v, (int, float))]
    if not all(math.isfinite(v) for v in numeric_parameters):
        raise MethodInputError("ODE parameters must be finite.")
    times = np.linspace(start, end, points)
    solver = str(parameters.get("solver", "RK45"));
    if solver not in {"RK45", "DOP853", "Radau", "BDF", "LSODA"}: raise MethodInputError("Unsupported registered ODE solver.")
    solution = integrate.solve_ivp(derivative, (start, end), [y0], t_eval=times, rtol=rtol, atol=atol, method=solver)
    if not solution.success:
        raise MethodInputError(f"ODE solver did not converge: {solution.message}")
    values = solution.y[0]
    return {
        "model": model,
        "time": solution.t.tolist(),
        "values": values.tolist(),
        "finalValue": float(values[-1]),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "functionEvaluations": int(solution.nfev),
        "success": True,
        "message": str(solution.message),
        "solver": solver,
        "absoluteTolerance": atol,
        "relativeTolerance": rtol,
    }


def eigen_analysis(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    matrix = _matrix(inputs, "matrix", maximum=50, square=True)
    symmetric_tolerance = float(parameters.get("symmetricTolerance", 1e-10))
    symmetric = bool(np.allclose(matrix, matrix.T, atol=symmetric_tolerance, rtol=symmetric_tolerance))
    solver = str(parameters.get("solver", "automatic"));
    if solver == "automatic": solver = "eigh" if symmetric else "eig"
    if solver == "eigh" and not symmetric: raise MethodInputError("eigh requires a symmetric matrix within symmetricTolerance.")
    if solver == "eigh": values, vectors = np.linalg.eigh(matrix)
    elif solver == "eig": values, vectors = np.linalg.eig(matrix)
    else: raise MethodInputError("solver must be automatic, eigh, or eig.")
    residuals = []
    for index in range(values.size):
        vector = vectors[:, index]
        residuals.append(float(np.linalg.norm(matrix @ vector - values[index] * vector)))
    return {
        "symmetric": symmetric,
        "eigenvalues": [_json_number(value) for value in values],
        "eigenvectors": [[_json_number(value) for value in vectors[:, index]] for index in range(values.size)],
        "residualNorms": residuals,
        "spectralRadius": float(np.max(np.abs(values))),
        "trace": float(np.trace(matrix)),
        "determinant": float(np.linalg.det(matrix)),
        "conditionNumber": float(np.linalg.cond(matrix)),
        "solver": solver,
    }


def bounded_minimize(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    objective = str(inputs.get("objective") or "quadratic").lower()
    lower = _number(inputs, "lower")
    upper = _number(inputs, "upper")
    if lower >= upper:
        raise MethodInputError("lower must be less than upper.")
    coefficients = inputs.get("coefficients") or []
    if objective == "quadratic":
        if not isinstance(coefficients, list) or len(coefficients) != 3:
            coefficients = [1.0, -4.0, 7.0]
        a, b, c = [float(v) for v in coefficients]
        function = lambda x: a * x * x + b * x + c
    elif objective == "quartic":
        if not isinstance(coefficients, list) or len(coefficients) != 5:
            coefficients = [1.0, 0.0, -3.0, 0.0, 2.0]
        coeff = np.asarray(coefficients, dtype=float)
        function = lambda x: float(np.polyval(coeff, x))
    elif objective == "oscillatory":
        amplitude = float(parameters.get("amplitude", 1.0))
        frequency = float(parameters.get("frequency", 3.0))
        offset = float(parameters.get("offset", 0.05))
        function = lambda x: amplitude * math.sin(frequency * x) + offset * x * x
    else:
        raise MethodInputError("objective must be quadratic, quartic, or oscillatory.")
    result = optimize.minimize_scalar(function, bounds=(lower, upper), method="bounded", options={"xatol": float(parameters.get("absoluteTolerance", 1e-8)), "maxiter": int(parameters.get("maxIterations", 1000))})
    return {
        "objective": objective,
        "x": float(result.x),
        "minimum": float(result.fun),
        "iterations": int(result.nit),
        "functionEvaluations": int(result.nfev),
        "success": bool(result.success),
        "message": str(result.message),
    }


def linear_program(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    c = _array(inputs, "objective", minimum=1, maximum=100)
    a_ub_raw = inputs.get("inequalityMatrix") or []
    b_ub_raw = inputs.get("inequalityVector") or []
    a_eq_raw = inputs.get("equalityMatrix") or []
    b_eq_raw = inputs.get("equalityVector") or []
    a_ub = None if not a_ub_raw else _matrix({"matrix": a_ub_raw}, "matrix", maximum=200)
    b_ub = None if not b_ub_raw else _array({"vector": b_ub_raw}, "vector", minimum=1, maximum=200)
    a_eq = None if not a_eq_raw else _matrix({"matrix": a_eq_raw}, "matrix", maximum=200)
    b_eq = None if not b_eq_raw else _array({"vector": b_eq_raw}, "vector", minimum=1, maximum=200)
    if a_ub is not None and (a_ub.shape[1] != c.size or b_ub is None or b_ub.size != a_ub.shape[0]):
        raise MethodInputError("inequalityMatrix and inequalityVector dimensions must match the objective.")
    if a_eq is not None and (a_eq.shape[1] != c.size or b_eq is None or b_eq.size != a_eq.shape[0]):
        raise MethodInputError("equalityMatrix and equalityVector dimensions must match the objective.")
    raw_bounds = inputs.get("bounds")
    bounds: list[tuple[float | None, float | None]] | None = None
    if raw_bounds is not None:
        if not isinstance(raw_bounds, list) or len(raw_bounds) != c.size:
            raise MethodInputError("bounds must contain one [lower, upper] pair per decision variable.")
        bounds = []
        for pair in raw_bounds:
            if not isinstance(pair, list) or len(pair) != 2:
                raise MethodInputError("Each bounds entry must be [lower, upper].")
            lower = None if pair[0] is None else float(pair[0])
            upper = None if pair[1] is None else float(pair[1])
            if lower is not None and upper is not None and lower > upper:
                raise MethodInputError("A lower bound cannot exceed its upper bound.")
            bounds.append((lower, upper))
    solver = str(parameters.get("solver", "highs"))
    if solver not in {"highs", "highs-ds", "highs-ipm"}: raise MethodInputError("Unsupported registered linear-program solver.")
    result = optimize.linprog(c, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=bounds, method=solver)
    return {
        "success": bool(result.success),
        "status": int(result.status),
        "message": str(result.message),
        "objectiveMinimum": float(result.fun) if result.fun is not None else None,
        "solution": result.x.tolist() if result.x is not None else [],
        "iterations": int(getattr(result, "nit", 0) or 0),
        "slack": result.slack.tolist() if getattr(result, "slack", None) is not None else [],
        "equalityResiduals": result.con.tolist() if getattr(result, "con", None) is not None else [],
        "solver": solver,
    }


def fft_spectrum(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    values = _array(inputs, "values", minimum=4, maximum=262144)
    sample_rate = _number(inputs, "sampleRate", minimum=0, exclusive_minimum=True)
    window_name = str(parameters.get("window", "hann")).lower()
    detrend = str(parameters.get("detrend", "constant")).lower()
    windows = {"hann": signal.windows.hann, "hamming": signal.windows.hamming, "blackman": signal.windows.blackman, "rectangular": lambda n: np.ones(n)}
    if window_name not in windows:
        raise MethodInputError("window must be hann, hamming, blackman, or rectangular.")
    if detrend not in {"constant", "linear", "none"}:
        raise MethodInputError("detrend must be constant, linear, or none.")
    adjusted = values if detrend == "none" else signal.detrend(values, type=detrend)
    window = windows[window_name](values.size)
    coherent_gain = float(np.sum(window) / values.size)
    transformed = np.fft.rfft(adjusted * window)
    frequency = np.fft.rfftfreq(values.size, d=1.0 / sample_rate)
    amplitude = np.abs(transformed) * 2.0 / max(values.size * coherent_gain, np.finfo(float).eps)
    if amplitude.size:
        amplitude[0] /= 2.0
        if values.size % 2 == 0 and amplitude.size > 1:
            amplitude[-1] /= 2.0
    power = amplitude**2
    peak_index = int(np.argmax(amplitude[1:]) + 1) if amplitude.size > 1 else 0
    return {
        "frequencyHz": frequency.tolist(),
        "amplitude": amplitude.tolist(),
        "power": power.tolist(),
        "peakFrequencyHz": float(frequency[peak_index]),
        "peakAmplitude": float(amplitude[peak_index]),
        "sampleCount": int(values.size),
        "sampleRateHz": sample_rate,
        "window": window_name,
        "detrend": detrend,
    }


def _model_value(model: str, variables: dict[str, np.ndarray | float], parameters: dict[str, Any]) -> np.ndarray:
    keys = list(variables.keys())
    if model == "linear":
        coefficients = parameters.get("coefficients") or [1.0] * len(keys)
        if not isinstance(coefficients, list) or len(coefficients) != len(keys):
            raise MethodInputError("linear model coefficients must match the variable count.")
        intercept = float(parameters.get("intercept", 0.0))
        result: np.ndarray | float = intercept
        for coefficient, key in zip(coefficients, keys):
            result = result + float(coefficient) * variables[key]
        return np.asarray(result, dtype=float)
    if model == "product":
        result = np.asarray(1.0)
        for key in keys:
            result = result * variables[key]
        return np.asarray(result, dtype=float)
    if model == "ratio":
        if len(keys) != 2:
            raise MethodInputError("ratio model requires exactly two variables.")
        denominator = np.asarray(variables[keys[1]], dtype=float)
        if np.any(np.isclose(denominator, 0)):
            raise MethodInputError("ratio model denominator approaches zero.")
        return np.asarray(variables[keys[0]], dtype=float) / denominator
    if model == "power":
        if len(keys) != 1:
            raise MethodInputError("power model requires exactly one variable.")
        exponent = float(parameters.get("exponent", 2.0))
        return np.asarray(variables[keys[0]], dtype=float) ** exponent
    raise MethodInputError("model must be linear, product, ratio, or power.")


def monte_carlo_propagation(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    model = str(inputs.get("model") or "linear").lower()
    distributions = inputs.get("distributions")
    samples = int(_number(inputs, "samples", minimum=100, maximum=500000))
    if not isinstance(distributions, list) or not 1 <= len(distributions) <= 20:
        raise MethodInputError("distributions must contain between 1 and 20 variable definitions.")
    rng = np.random.default_rng(0 if seed is None else seed)
    variables: dict[str, np.ndarray] = {}
    for definition in distributions:
        if not isinstance(definition, dict):
            raise MethodInputError("Each distribution must be an object.")
        name = str(definition.get("name") or "")[:64]
        if not name or name in variables:
            raise MethodInputError("Distribution names must be non-empty and unique.")
        family = str(definition.get("distribution") or "normal").lower()
        if family == "normal":
            mean, std = float(definition.get("mean", 0)), float(definition.get("stdDev", 1))
            if std < 0:
                raise MethodInputError("Normal standard deviations must be non-negative.")
            variables[name] = rng.normal(mean, std, samples)
        elif family == "uniform":
            lower, upper = float(definition.get("lower", 0)), float(definition.get("upper", 1))
            if lower >= upper:
                raise MethodInputError("Uniform lower must be less than upper.")
            variables[name] = rng.uniform(lower, upper, samples)
        elif family == "triangular":
            lower, mode, upper = float(definition.get("lower", 0)), float(definition.get("mode", 0.5)), float(definition.get("upper", 1))
            if not lower <= mode <= upper or lower == upper:
                raise MethodInputError("Triangular parameters must satisfy lower <= mode <= upper.")
            variables[name] = rng.triangular(lower, mode, upper, samples)
        else:
            raise MethodInputError("distribution must be normal, uniform, or triangular.")
    outputs = _model_value(model, variables, parameters)
    outputs = np.asarray(outputs, dtype=float)
    if outputs.shape != (samples,) or not np.isfinite(outputs).all():
        raise MethodInputError("The selected uncertainty model produced invalid values.")
    confidence = float(parameters.get("confidence", 0.95))
    if not 0.5 < confidence < 1:
        raise MethodInputError("confidence must be between 0.5 and 1.")
    tail = (1 - confidence) / 2
    quantiles = np.quantile(outputs, [tail, 0.5, 1 - tail])
    correlations = {}
    if np.std(outputs) > 0:
        for name, values in variables.items():
            correlations[name] = float(np.corrcoef(values, outputs)[0, 1]) if np.std(values) > 0 else 0.0
    histogram_counts, histogram_edges = np.histogram(outputs, bins=max(8, min(40, int(round(math.sqrt(samples))))))
    return {
        "model": model,
        "samples": samples,
        "histogram": {"counts": histogram_counts.astype(int).tolist(), "edges": histogram_edges.astype(float).tolist()},
        "mean": float(np.mean(outputs)),
        "standardDeviation": float(np.std(outputs, ddof=1)),
        "minimum": float(np.min(outputs)),
        "maximum": float(np.max(outputs)),
        "median": float(quantiles[1]),
        "confidence": confidence,
        "confidenceInterval": [float(quantiles[0]), float(quantiles[2])],
        "inputOutputCorrelations": correlations,
    }


def bootstrap_mean_interval(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    values = _array(inputs, "values", minimum=2, maximum=100000)
    resamples = int(_number(inputs, "resamples", minimum=100, maximum=50000))
    confidence = float(parameters.get("confidence", 0.95))
    if not 0.5 < confidence < 1:
        raise MethodInputError("confidence must be between 0.5 and 1.")
    rng = np.random.default_rng(0 if seed is None else seed)
    max_cells = 5_000_000
    batch = max(1, min(resamples, max_cells // values.size))
    means: list[np.ndarray] = []
    remaining = resamples
    while remaining:
        count = min(batch, remaining)
        indexes = rng.integers(0, values.size, size=(count, values.size))
        means.append(np.mean(values[indexes], axis=1))
        remaining -= count
    bootstrap = np.concatenate(means)
    tail = (1 - confidence) / 2
    lower, upper = np.quantile(bootstrap, [tail, 1 - tail])
    histogram_counts, histogram_edges = np.histogram(bootstrap, bins=max(8, min(40, int(round(math.sqrt(resamples))))))
    return {
        "histogram": {"counts": histogram_counts.astype(int).tolist(), "edges": histogram_edges.astype(float).tolist()},
        "sampleMean": float(np.mean(values)),
        "sampleStandardDeviation": float(np.std(values, ddof=1)),
        "bootstrapMean": float(np.mean(bootstrap)),
        "bootstrapStandardError": float(np.std(bootstrap, ddof=1)),
        "confidence": confidence,
        "confidenceInterval": [float(lower), float(upper)],
        "resamples": resamples,
        "seed": 0 if seed is None else int(seed),
    }


def local_sensitivity(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    model = str(inputs.get("model") or "linear").lower()
    baseline_raw = inputs.get("baseline")
    if not isinstance(baseline_raw, dict) or not 1 <= len(baseline_raw) <= 20:
        raise MethodInputError("baseline must be an object containing between 1 and 20 variables.")
    baseline: dict[str, float] = {}
    for key, value in baseline_raw.items():
        number = float(value)
        if not math.isfinite(number):
            raise MethodInputError("baseline values must be finite.")
        baseline[str(key)[:64]] = number
    relative_step = float(parameters.get("relativeStep", 1e-4))
    absolute_step = float(parameters.get("absoluteStep", 1e-8))
    if not (1e-8 <= relative_step <= 0.1) or not (1e-12 <= absolute_step <= 1):
        raise MethodInputError("Sensitivity step sizes are outside the supported range.")
    base_output = float(_model_value(model, baseline, parameters))
    rows = []
    for key, value in baseline.items():
        step = max(abs(value) * relative_step, absolute_step)
        plus = dict(baseline); minus = dict(baseline)
        plus[key] = value + step; minus[key] = value - step
        plus_output = float(_model_value(model, plus, parameters))
        minus_output = float(_model_value(model, minus, parameters))
        derivative = (plus_output - minus_output) / (2 * step)
        elasticity = None if base_output == 0 else derivative * value / base_output
        rows.append({"variable": key, "baseline": value, "step": step, "derivative": derivative, "elasticity": elasticity})
    rows.sort(key=lambda row: abs(row["derivative"]), reverse=True)
    return {"model": model, "baselineOutput": base_output, "sensitivities": rows}


def parameter_sweep(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    del seed
    model = str(inputs.get("model") or "logistic_growth").lower()
    parameter_name = str(inputs.get("parameter") or "rate")
    values = _array(inputs, "values", minimum=1, maximum=10000)
    fixed = inputs.get("fixed") or {}
    if not isinstance(fixed, dict):
        raise MethodInputError("fixed must be an object.")
    rows = []
    for value in values:
        local = {str(k): float(v) for k, v in fixed.items() if isinstance(v, (int, float))}
        local[parameter_name] = float(value)
        if model == "logistic_growth":
            initial = float(local.get("initial", 10.0)); rate = float(local.get("rate", 0.5)); capacity = float(local.get("carryingCapacity", 100.0)); time = float(local.get("time", 10.0))
            if initial <= 0 or capacity <= 0:
                raise MethodInputError("logistic_growth requires positive initial and carryingCapacity.")
            result = capacity / (1 + ((capacity - initial) / initial) * math.exp(-rate * time))
        elif model == "projectile_range":
            speed = float(local.get("speed", 20.0)); angle = math.radians(float(local.get("angleDeg", 45.0))); gravity = float(local.get("gravity", 9.80665))
            if speed < 0 or gravity <= 0:
                raise MethodInputError("projectile_range requires non-negative speed and positive gravity.")
            result = speed * speed * math.sin(2 * angle) / gravity
        elif model == "photovoltaic_output":
            result = float(local.get("irradiance", 1000)) * float(local.get("area", 10)) * float(local.get("efficiency", 0.2)) * float(local.get("systemFactor", 0.85))
        elif model == "michaelis_menten":
            vmax = float(local.get("vmax", 10)); substrate = float(local.get("substrate", 5)); km = float(local.get("km", 2))
            if substrate < 0 or vmax < 0 or km <= 0:
                raise MethodInputError("michaelis_menten requires non-negative vmax/substrate and positive km.")
            result = vmax * substrate / (km + substrate)
        else:
            raise MethodInputError("model must be logistic_growth, projectile_range, photovoltaic_output, or michaelis_menten.")
        if not math.isfinite(result):
            raise MethodInputError("The parameter sweep produced a non-finite result.")
        rows.append({"parameterValue": float(value), "output": float(result)})
    outputs = np.asarray([row["output"] for row in rows], dtype=float)
    return {
        "model": model,
        "parameter": parameter_name,
        "rows": rows,
        "minimumOutput": float(outputs.min()),
        "maximumOutput": float(outputs.max()),
        "monotonicIncreasing": bool(np.all(np.diff(outputs) >= 0)),
        "monotonicDecreasing": bool(np.all(np.diff(outputs) <= 0)),
    }
