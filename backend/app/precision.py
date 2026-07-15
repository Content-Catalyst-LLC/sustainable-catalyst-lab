from __future__ import annotations

import math
from copy import deepcopy
from typing import Any

import numpy as np
from scipy import integrate, optimize

from .methods.core import MethodInputError

PROFILES: dict[str, dict[str, Any]] = {
    "fast": {
        "title": "Fast exploratory",
        "absoluteTolerance": 1e-6,
        "relativeTolerance": 1e-5,
        "conditionThreshold": 1e10,
        "description": "Favors lower runtime for exploratory analysis while retaining bounded solver checks.",
    },
    "balanced": {
        "title": "Balanced scientific",
        "absoluteTolerance": 1e-9,
        "relativeTolerance": 1e-8,
        "conditionThreshold": 1e12,
        "description": "Default scientific profile balancing runtime, residual quality, and reproducibility.",
    },
    "strict": {
        "title": "Strict validation",
        "absoluteTolerance": 1e-12,
        "relativeTolerance": 1e-11,
        "conditionThreshold": 1e10,
        "description": "Tight tolerances, strict unit validation, and stronger convergence warnings.",
    },
    "diagnostic": {
        "title": "Diagnostic comparison",
        "absoluteTolerance": 1e-11,
        "relativeTolerance": 1e-10,
        "conditionThreshold": 1e12,
        "description": "Runs reference comparisons and exposes detailed floating-point and solver diagnostics.",
    },
}

SOLVERS: dict[str, dict[str, Any]] = {
    "numerics.root_scalar_polynomial": {
        "default": "brentq",
        "allowed": ["brentq", "bisect", "ridder", "toms748"],
        "rationale": "Brent's method combines bracket safety with superlinear convergence.",
    },
    "numerics.adaptive_quadrature_polynomial": {
        "default": "gauss-kronrod",
        "allowed": ["gauss-kronrod"],
        "rationale": "Adaptive Gauss-Kronrod provides an error estimate and exact polynomial cross-check.",
    },
    "numerics.ode_first_order": {
        "default": "RK45",
        "allowed": ["RK45", "DOP853", "Radau", "BDF", "LSODA"],
        "rationale": "Automatic selection chooses explicit or implicit integration from profile and stiffness hints.",
    },
    "numerics.linear_system": {
        "default": "solve",
        "allowed": ["solve", "least-squares", "automatic"],
        "rationale": "Direct solve is preferred for well-conditioned square systems; least-squares is safer near rank deficiency.",
    },
    "numerics.eigen_analysis": {
        "default": "automatic",
        "allowed": ["automatic", "eigh", "eig"],
        "rationale": "Symmetric matrices use the Hermitian solver for stability and real eigenpairs.",
    },
    "optimization.scalar_bounded": {
        "default": "bounded",
        "allowed": ["bounded"],
        "rationale": "The bounded scalar optimizer respects the governed finite interval.",
    },
    "optimization.linear_program": {
        "default": "highs",
        "allowed": ["highs", "highs-ds", "highs-ipm"],
        "rationale": "HiGHS provides modern dual-simplex and interior-point implementations with feasibility diagnostics.",
    },
}

EXPECTED_UNITS: dict[str, dict[str, str]] = {
    "mechanics.kinetic_energy": {"mass": "kg", "velocity": "m/s"},
    "mechanics.projectile_motion": {"speed": "m/s", "angleDeg": "deg", "height": "m"},
    "energy.photovoltaic_output": {"irradiance": "W/m2", "area": "m2", "efficiency": "1", "systemFactor": "1"},
    "numerics.ode_first_order": {"startTime": "s", "endTime": "s"},
    "signal.fft_spectrum": {"sampleRate": "Hz"},
}

UNIT_ALIASES = {
    "dimensionless": "1", "unitless": "1", "none": "1", "": "1",
    "degrees": "deg", "degree": "deg", "°": "deg",
    "m s-1": "m/s", "m/s": "m/s", "ms-1": "m/s",
    "w/m²": "W/m2", "w/m2": "W/m2", "W/m^2": "W/m2",
    "m²": "m2", "m^2": "m2",
    "seconds": "s", "second": "s", "sec": "s",
    "hz": "Hz", "kilograms": "kg", "kilogram": "kg",
}


def _dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True, exclude_none=True)
    return dict(value) if isinstance(value, dict) else {}


def _finite(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def normalize_unit(value: Any) -> str:
    text = str(value or "").strip()
    return UNIT_ALIASES.get(text, UNIT_ALIASES.get(text.lower(), text))


def policy_catalog() -> dict[str, Any]:
    return {
        "schema": "sc-lab-solver-governance-catalog/1.0",
        "version": "0.27.3",
        "precision": {
            "numericType": "IEEE-754 binary64",
            "numpyDtype": "float64",
            "machineEpsilon": float(np.finfo(np.float64).eps),
            "smallestNormal": float(np.finfo(np.float64).tiny),
            "largestFinite": float(np.finfo(np.float64).max),
        },
        "profiles": [{"id": key, **value} for key, value in PROFILES.items()],
        "solvers": [{"method": key, **value} for key, value in SOLVERS.items()],
        "unitPolicies": ["off", "warn", "strict"],
        "uncertaintyStandards": ["method-default", "GUM-inspired", "Monte-Carlo", "bootstrap"],
        "referenceComparison": True,
    }


def recommend(payload: Any, method: Any) -> dict[str, Any]:
    governance = _dict(getattr(payload, "governance", None))
    profile_id = str(governance.get("precisionProfile") or "balanced")
    profile = deepcopy(PROFILES.get(profile_id, PROFILES["balanced"]))
    solver_info = deepcopy(SOLVERS.get(method.id, {"default": "registered-default", "allowed": ["registered-default"], "rationale": "The registered implementation is the governed solver."}))
    requested = str(governance.get("requestedSolver") or "").strip()
    solver_policy = str(governance.get("solverPolicy") or "automatic")
    inputs = getattr(payload, "inputs", {}) or {}
    parameters = getattr(payload, "parameters", {}) or {}

    selected = solver_info["default"]
    reasons = [solver_info["rationale"]]
    if method.id == "numerics.ode_first_order" and not requested:
        if bool(parameters.get("stiffnessHint")):
            selected = "Radau"
            reasons.append("A stiffness hint requested an implicit solver.")
        elif profile_id in {"strict", "diagnostic"}:
            selected = "DOP853"
            reasons.append("The selected precision profile benefits from a higher-order explicit solver.")
        elif str(inputs.get("model") or "").lower() == "forced_linear":
            selected = "DOP853"
            reasons.append("The oscillatory forcing model benefits from the higher-order explicit method.")
    if method.id == "numerics.linear_system":
        try:
            matrix = np.asarray(inputs.get("matrix"), dtype=float)
            condition = float(np.linalg.cond(matrix))
        except Exception:
            condition = None
        threshold = _finite(governance.get("conditionThreshold"), profile["conditionThreshold"])
        if condition is not None and (not math.isfinite(condition) or condition > threshold):
            selected = "least-squares"
            reasons.append(f"Estimated condition number {condition:.3e} exceeds the governed threshold {threshold:.3e}.")
        else:
            reasons.append("The matrix appears suitable for a direct solve.")
    if requested:
        canonical = next((candidate for candidate in solver_info["allowed"] if candidate.lower() == requested.lower()), None)
        if solver_policy == "manual" and canonical is None:
            raise MethodInputError(f"requestedSolver must be one of: {', '.join(solver_info['allowed'])}.")
        if canonical:
            selected = canonical
            reasons.append("The registered manual solver selection was accepted.")
    return {
        "method": method.id,
        "precisionProfile": profile_id,
        "solverPolicy": solver_policy,
        "recommendedSolver": selected,
        "allowedSolvers": solver_info["allowed"],
        "reasons": reasons,
        "estimatedCost": getattr(method, "estimated_cost", "light"),
    }


def unit_report(payload: Any, method_id: str) -> dict[str, Any]:
    governance = _dict(getattr(payload, "governance", None))
    policy = str(governance.get("unitPolicy") or "warn")
    provided = {str(k): normalize_unit(v) for k, v in (getattr(payload, "units", {}) or {}).items()}
    expected = EXPECTED_UNITS.get(method_id, {})
    missing: list[str] = []
    mismatched: list[dict[str, str]] = []
    for key, expected_unit in expected.items():
        if key not in provided:
            missing.append(key)
        elif normalize_unit(expected_unit) != provided[key]:
            mismatched.append({"field": key, "expected": normalize_unit(expected_unit), "provided": provided[key]})
    status = "not-applicable" if not expected else ("valid" if not missing and not mismatched else "incomplete" if missing and not mismatched else "mismatch")
    report = {"policy": policy, "status": status, "expected": expected, "provided": provided, "missing": missing, "mismatched": mismatched}
    if policy == "strict" and expected and (missing or mismatched):
        details = []
        if missing: details.append("missing units for " + ", ".join(missing))
        if mismatched: details.append("unit mismatches for " + ", ".join(row["field"] for row in mismatched))
        raise MethodInputError("Strict unit validation failed: " + "; ".join(details) + ".")
    return report


def prepare(payload: Any, method: Any) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    governance = _dict(getattr(payload, "governance", None))
    profile_id = str(governance.get("precisionProfile") or "balanced")
    if profile_id not in PROFILES:
        raise MethodInputError("precisionProfile must be fast, balanced, strict, or diagnostic.")
    profile = PROFILES[profile_id]
    recommendation = recommend(payload, method)
    parameters = deepcopy(getattr(payload, "parameters", {}) or {})
    absolute = _finite(governance.get("absoluteTolerance"), _finite(parameters.get("absoluteTolerance"), profile["absoluteTolerance"]))
    relative = _finite(governance.get("relativeTolerance"), _finite(parameters.get("relativeTolerance"), profile["relativeTolerance"]))
    if not (1e-15 <= absolute <= 1e-2) or not (1e-15 <= relative <= 1e-2):
        raise MethodInputError("Governed tolerances must remain between 1e-15 and 1e-2.")
    parameters["absoluteTolerance"] = absolute
    parameters["relativeTolerance"] = relative
    parameters["solver"] = recommendation["recommendedSolver"]
    threshold = _finite(governance.get("conditionThreshold"), profile["conditionThreshold"])
    parameters["conditionThreshold"] = threshold
    parameters["illConditionedPolicy"] = str(governance.get("illConditionedPolicy") or ("reject" if profile_id == "strict" else "least-squares"))
    units = unit_report(payload, method.id)
    warnings: list[str] = []
    if units["policy"] == "warn" and units["status"] in {"incomplete", "mismatch"}:
        warnings.append("Unit metadata is incomplete or inconsistent; review the unit-validation report.")
    if profile_id == "fast":
        warnings.append("The fast profile uses relaxed tolerances and is intended for exploratory analysis.")
    report = {
        "schema": "sc-lab-solver-governance/1.0",
        "version": "0.27.3",
        "precisionProfile": profile_id,
        "floatingPoint": policy_catalog()["precision"],
        "effectiveTolerances": {"absolute": absolute, "relative": relative},
        "conditionThreshold": threshold,
        "recommendation": recommendation,
        "units": units,
        "uncertaintyStandard": str(governance.get("uncertaintyStandard") or "method-default"),
        "referenceComparisonRequested": bool(governance.get("referenceComparison") or profile_id == "diagnostic"),
    }
    return parameters, report, warnings


def diagnostics(method_id: str, outputs: dict[str, Any], governance: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    convergence = "not-reported"
    if "converged" in outputs:
        convergence = "converged" if outputs.get("converged") else "failed"
    elif "success" in outputs:
        convergence = "converged" if outputs.get("success") else "failed"
    residuals: dict[str, Any] = {}
    if "residualNorm" in outputs: residuals["residualNorm"] = outputs["residualNorm"]
    if "residualNorms" in outputs:
        values = [float(v) for v in outputs.get("residualNorms") or []]
        residuals["maximumEigenResidual"] = max(values) if values else None
    condition = outputs.get("conditionNumber")
    threshold = float(governance.get("conditionThreshold") or 1e12)
    if condition is not None and (not math.isfinite(float(condition)) or float(condition) > threshold):
        warnings.append(f"Condition number {float(condition):.3e} exceeds the governed threshold {threshold:.3e}.")
    if convergence == "failed": warnings.append("The registered solver did not report successful convergence.")
    if method_id == "numerics.root_scalar_polynomial" and abs(float(outputs.get("functionValue", 0.0))) > max(governance["effectiveTolerances"].values()):
        warnings.append("The root residual exceeds the requested tolerance scale.")
    if method_id == "numerics.adaptive_quadrature_polynomial":
        estimate = float(outputs.get("absoluteErrorEstimate", 0.0))
        if estimate > governance["effectiveTolerances"]["absolute"]:
            warnings.append("The quadrature error estimate exceeds the requested absolute tolerance.")
    return {"convergence": convergence, "residuals": residuals, "conditionNumber": condition, "warnings": warnings}, warnings


def reference_compare(method_id: str, inputs: dict[str, Any], parameters: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any] | None:
    atol = float(parameters.get("absoluteTolerance", 1e-9)); rtol = float(parameters.get("relativeTolerance", 1e-8))
    if method_id == "numerics.root_scalar_polynomial":
        coefficients = np.asarray(inputs["coefficients"], dtype=float); lower, upper = [float(v) for v in inputs["bracket"]]
        fn = lambda x: float(np.polyval(coefficients, x))
        reference = optimize.root_scalar(fn, bracket=(lower, upper), method="bisect", xtol=atol, rtol=rtol, maxiter=int(parameters.get("maxIterations", 200)))
        difference = abs(float(outputs["root"]) - float(reference.root))
        return {"referenceMethod": "bisect", "referenceValue": float(reference.root), "absoluteDifference": difference, "withinTolerance": difference <= atol + rtol * abs(float(reference.root))}
    if method_id == "numerics.adaptive_quadrature_polynomial":
        exact = float(outputs.get("polynomialExactIntegral")); difference = abs(float(outputs["integral"]) - exact)
        return {"referenceMethod": "analytic-polynomial-antiderivative", "referenceValue": exact, "absoluteDifference": difference, "withinTolerance": difference <= atol + rtol * abs(exact)}
    if method_id == "numerics.ode_first_order":
        alternate = "DOP853" if str(outputs.get("solver")) != "DOP853" else "RK45"
        # Reuse registered model implementation through a small local formulation.
        model=str(inputs.get("model") or "exponential").lower(); y0=float(inputs["initialValue"]); start=float(inputs["startTime"]); end=float(inputs["endTime"])
        if model=="exponential":
            rate=float(parameters.get("rate",0.25)); fn=lambda t,y:[rate*y[0]]
        elif model=="decay":
            rate=float(parameters.get("rate",0.25)); fn=lambda t,y:[-rate*y[0]]
        elif model=="logistic":
            rate=float(parameters.get("rate",0.5)); cap=float(parameters.get("carryingCapacity",100)); fn=lambda t,y:[rate*y[0]*(1-y[0]/cap)]
        else:
            decay=float(parameters.get("decay",0.2)); forcing=float(parameters.get("forcing",1)); frequency=float(parameters.get("frequency",1)); fn=lambda t,y:[-decay*y[0]+forcing*math.sin(frequency*t)]
        ref=integrate.solve_ivp(fn,(start,end),[y0],rtol=rtol,atol=atol,method=alternate)
        reference=float(ref.y[0,-1]); actual=float(outputs["finalValue"]); difference=abs(actual-reference)
        return {"referenceMethod": alternate, "referenceValue": reference, "absoluteDifference": difference, "withinTolerance": difference <= max(atol*10, rtol*10*abs(reference))}
    if method_id == "numerics.linear_system":
        matrix=np.asarray(inputs["matrix"],dtype=float); vector=np.asarray(inputs["vector"],dtype=float)
        reference, *_=np.linalg.lstsq(matrix,vector,rcond=None); actual=np.asarray(outputs["solution"],dtype=float); difference=float(np.linalg.norm(actual-reference))
        return {"referenceMethod":"numpy.linalg.lstsq","referenceValue":reference.tolist(),"differenceNorm":difference,"withinTolerance":difference <= atol + rtol*float(np.linalg.norm(reference))}
    if method_id == "optimization.scalar_bounded" and str(inputs.get("objective") or "quadratic").lower()=="quadratic":
        coefficients=inputs.get("coefficients") or [1,-4,7]; a,b,c=[float(v) for v in coefficients]
        if a>0:
            x=min(max(-b/(2*a),float(inputs["lower"])),float(inputs["upper"])); value=a*x*x+b*x+c; difference=abs(float(outputs["minimum"])-value)
            return {"referenceMethod":"analytic-quadratic-vertex","referenceValue":{"x":x,"minimum":value},"absoluteDifference":difference,"withinTolerance":difference <= atol + rtol*abs(value)}
    return None
