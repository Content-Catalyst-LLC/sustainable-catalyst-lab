from __future__ import annotations

import math
import time
from typing import Any

import numpy as np
import pandas as pd
from scipy import integrate, optimize, stats


class MethodInputError(ValueError):
    pass


def _number(inputs: dict[str, Any], key: str, *, minimum: float | None = None, maximum: float | None = None, exclusive_minimum: bool = False) -> float:
    try:
        value = float(inputs[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise MethodInputError(f"{key} must be a finite number.") from exc
    if not math.isfinite(value):
        raise MethodInputError(f"{key} must be finite.")
    if minimum is not None and (value <= minimum if exclusive_minimum else value < minimum):
        op = "greater than" if exclusive_minimum else "at least"
        raise MethodInputError(f"{key} must be {op} {minimum}.")
    if maximum is not None and value > maximum:
        raise MethodInputError(f"{key} must be no greater than {maximum}.")
    return value


def _array(inputs: dict[str, Any], key: str, *, minimum: int = 1, maximum: int = 100000) -> np.ndarray:
    raw = inputs.get(key)
    if not isinstance(raw, list) or not minimum <= len(raw) <= maximum:
        raise MethodInputError(f"{key} must contain between {minimum} and {maximum} numerical values.")
    try:
        values = np.asarray(raw, dtype=float)
    except (TypeError, ValueError) as exc:
        raise MethodInputError(f"{key} must contain only numerical values.") from exc
    if values.ndim != 1 or not np.isfinite(values).all():
        raise MethodInputError(f"{key} must be a finite one-dimensional array.")
    return values


def kinetic_energy(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    mass = _number(inputs, "mass", minimum=0, exclusive_minimum=True)
    velocity = _number(inputs, "velocity")
    return {"kineticEnergyJ": 0.5 * mass * velocity**2, "momentumKgMs": mass * velocity}


def projectile_motion(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    speed = _number(inputs, "speed", minimum=0, exclusive_minimum=True)
    angle = math.radians(_number(inputs, "angleDeg", minimum=-89.999, maximum=89.999))
    height = _number(inputs, "height", minimum=0)
    g = float(parameters.get("gravity", 9.80665))
    if not math.isfinite(g) or g <= 0:
        raise MethodInputError("gravity must be positive and finite.")
    vy = speed * math.sin(angle)
    flight = (vy + math.sqrt(vy**2 + 2 * g * height)) / g
    return {"rangeM": speed * math.cos(angle) * flight, "maxHeightM": height + vy**2/(2*g), "flightTimeS": flight}


def photovoltaic_output(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    irradiance = _number(inputs, "irradiance", minimum=0)
    area = _number(inputs, "area", minimum=0)
    efficiency = _number(inputs, "efficiency", minimum=0, maximum=1)
    system_factor = _number(inputs, "systemFactor", minimum=0, maximum=1)
    return {"powerW": irradiance * area * efficiency * system_factor}


def michaelis_menten(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    vmax = _number(inputs, "vmax", minimum=0)
    substrate = _number(inputs, "substrate", minimum=0)
    km = _number(inputs, "km", minimum=0, exclusive_minimum=True)
    return {"rate": vmax * substrate / (km + substrate)}


def descriptive_statistics(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    values = _array(inputs, "values", minimum=1)
    series = pd.Series(values)
    return {
        "count": int(values.size), "mean": float(values.mean()), "median": float(np.median(values)),
        "sampleStdDev": float(values.std(ddof=1)) if values.size > 1 else 0.0,
        "minimum": float(values.min()), "maximum": float(values.max()),
        "q1": float(series.quantile(0.25)), "q3": float(series.quantile(0.75)),
        "skewness": float(stats.skew(values, bias=False)) if values.size > 2 else None,
    }


def linear_regression(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    x = _array(inputs, "x", minimum=2)
    y = _array(inputs, "y", minimum=2)
    if x.size != y.size:
        raise MethodInputError("x and y must have equal length.")
    if np.allclose(x, x[0]):
        raise MethodInputError("x must not be constant.")
    result = stats.linregress(x, y)
    predictions = result.intercept + result.slope * x
    residuals = y - predictions
    return {
        "slope": float(result.slope), "intercept": float(result.intercept), "rValue": float(result.rvalue),
        "rSquared": float(result.rvalue**2), "pValue": float(result.pvalue), "standardError": float(result.stderr),
        "rmse": float(np.sqrt(np.mean(residuals**2))), "predictions": predictions.tolist(), "residuals": residuals.tolist(),
    }


def solve_linear_system(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    try:
        matrix = np.asarray(inputs.get("matrix"), dtype=float)
        vector = np.asarray(inputs.get("vector"), dtype=float)
    except (TypeError, ValueError) as exc:
        raise MethodInputError("matrix and vector must be numerical arrays.") from exc
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not 1 <= matrix.shape[0] <= 100:
        raise MethodInputError("matrix must be a square matrix between 1x1 and 100x100.")
    if vector.shape != (matrix.shape[0],) or not np.isfinite(matrix).all() or not np.isfinite(vector).all():
        raise MethodInputError("vector length must equal the matrix dimension and all values must be finite.")
    condition = float(np.linalg.cond(matrix))
    threshold = float(parameters.get("conditionThreshold", 1e14))
    policy = str(parameters.get("illConditionedPolicy", "reject"))
    requested_solver = str(parameters.get("solver", "automatic")).lower()
    ill_conditioned = (not math.isfinite(condition)) or condition > threshold
    if ill_conditioned and policy == "reject":
        raise MethodInputError("matrix is singular or exceeds the governed condition-number threshold.")
    use_lstsq = requested_solver == "least-squares" or (requested_solver == "automatic" and ill_conditioned) or (ill_conditioned and policy == "least-squares")
    if use_lstsq:
        solution, residual_values, rank, singular_values = np.linalg.lstsq(matrix, vector, rcond=None)
        solver = "least-squares"
    else:
        solution = np.linalg.solve(matrix, vector)
        residual_values = np.asarray([], dtype=float)
        rank = int(np.linalg.matrix_rank(matrix))
        singular_values = np.linalg.svd(matrix, compute_uv=False)
        solver = "solve"
    residual = matrix @ solution - vector
    return {"solution": solution.tolist(), "conditionNumber": condition, "conditionThreshold": threshold, "illConditioned": ill_conditioned, "solver": solver, "rank": int(rank), "singularValues": singular_values.tolist(), "leastSquaresResiduals": residual_values.tolist(), "residualNorm": float(np.linalg.norm(residual))}


def polynomial_roots(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    coefficients = _array(inputs, "coefficients", minimum=2, maximum=101)
    if np.isclose(coefficients[0], 0):
        raise MethodInputError("The leading polynomial coefficient must be non-zero.")
    roots = np.roots(coefficients)
    serial = [{"real": float(v.real), "imaginary": float(v.imag)} for v in roots]
    return {"degree": int(coefficients.size - 1), "roots": serial}


def sampled_integration(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    x = _array(inputs, "x", minimum=2)
    y = _array(inputs, "y", minimum=2)
    if x.size != y.size:
        raise MethodInputError("x and y must have equal length.")
    if not np.all(np.diff(x) > 0):
        raise MethodInputError("x must be strictly increasing.")
    trapezoid = float(np.trapezoid(y, x))
    simpson = float(integrate.simpson(y, x=x)) if x.size >= 3 else trapezoid
    return {"trapezoid": trapezoid, "simpson": simpson, "sampleCount": int(x.size)}


def monte_carlo_pi(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    samples = int(_number(inputs, "samples", minimum=100, maximum=1_000_000))
    actual_seed = 0 if seed is None else seed
    rng = np.random.default_rng(actual_seed)
    points = rng.random((samples, 2))
    inside = int(np.count_nonzero(np.sum(points**2, axis=1) <= 1.0))
    estimate = 4.0 * inside / samples
    standard_error = math.sqrt(max(estimate * (4 - estimate), 0.0) / samples)
    return {"estimate": estimate, "absoluteError": abs(math.pi-estimate), "standardError": standard_error, "samples": samples, "insideCircle": inside}


def controlled_delay(inputs: dict[str, Any], parameters: dict[str, Any], seed: int | None) -> dict[str, Any]:
    seconds = _number(inputs, "seconds", minimum=0, maximum=10)
    started = time.perf_counter()
    time.sleep(seconds)
    return {"requestedSeconds": seconds, "elapsedSeconds": time.perf_counter() - started}
