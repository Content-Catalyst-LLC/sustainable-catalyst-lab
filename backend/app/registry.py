from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable

from .methods import core

Handler = Callable[[dict[str, Any], dict[str, Any], int | None], dict[str, Any]]


@dataclass(frozen=True)
class MethodDefinition:
    id: str
    version: str
    title: str
    domain: str
    description: str
    packages: list[str]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    assumptions: list[str]
    handler: Handler
    execution_modes: list[str] = None
    references: list[dict[str, str]] = None

    def public(self) -> dict[str, Any]:
        row = asdict(self)
        row.pop("handler", None)
        row["execution_modes"] = self.execution_modes or ["python-core"]
        row["references"] = self.references or []
        return row


def _method(id: str, title: str, domain: str, description: str, packages: list[str], inputs: dict[str, Any], outputs: dict[str, Any], assumptions: list[str], handler: Handler, references: list[dict[str, str]] | None = None) -> MethodDefinition:
    return MethodDefinition(id=id, version="1.0.0", title=title, domain=domain, description=description, packages=packages, input_schema=inputs, output_schema=outputs, assumptions=assumptions, handler=handler, execution_modes=["python-core", "queued-python-core"], references=references or [])


METHODS = [
    _method("mechanics.kinetic_energy", "Kinetic energy and momentum", "mechanics", "Computes translational kinetic energy and linear momentum.", ["numpy"], {"mass":"kg > 0","velocity":"m/s"}, {"kineticEnergyJ":"J","momentumKgMs":"kg m/s"}, ["Classical non-relativistic mechanics."], core.kinetic_energy),
    _method("mechanics.projectile_motion", "Projectile motion", "mechanics", "Computes range, maximum height, and flight time without aerodynamic drag.", ["numpy","scipy"], {"speed":"m/s > 0","angleDeg":"degrees","height":"m >= 0"}, {"rangeM":"m","maxHeightM":"m","flightTimeS":"s"}, ["Constant gravitational acceleration.","No aerodynamic drag."], core.projectile_motion),
    _method("energy.photovoltaic_output", "Photovoltaic output", "energy", "Estimates electrical power from irradiance, area, efficiency, and system factor.", ["numpy"], {"irradiance":"W/m2","area":"m2","efficiency":"0..1","systemFactor":"0..1"}, {"powerW":"W"}, ["Uniform irradiance and aggregate system factor."], core.photovoltaic_output),
    _method("biology.michaelis_menten", "Michaelis-Menten kinetics", "biology", "Computes an idealized single-substrate reaction rate.", ["numpy"], {"vmax":">=0","substrate":">=0","km":">0"}, {"rate":"rate units"}, ["Steady-state single-substrate kinetics."], core.michaelis_menten),
    _method("statistics.descriptive", "Descriptive statistics", "statistics", "Produces robust descriptive summaries for a one-dimensional dataset.", ["numpy","pandas","scipy"], {"values":"numeric[]"}, {"count":"integer","mean":"number","median":"number","sampleStdDev":"number","quartiles":"number"}, ["Missing and non-finite values are rejected."], core.descriptive_statistics),
    _method("statistics.linear_regression", "Ordinary least-squares regression", "statistics", "Fits a univariate OLS line and returns diagnostics, predictions, and residuals.", ["numpy","scipy"], {"x":"numeric[]","y":"numeric[]"}, {"slope":"number","intercept":"number","rSquared":"number","predictions":"numeric[]"}, ["Independent observations.","Use domain diagnostics before inferential decisions."], core.linear_regression),
    _method("numerics.linear_system", "Linear system solver", "numerical-analysis", "Solves Ax=b and reports conditioning and residual norm.", ["numpy"], {"matrix":"square numeric[][]","vector":"numeric[]"}, {"solution":"numeric[]","conditionNumber":"number","residualNorm":"number"}, ["Dense CPU solution.","Ill-conditioned matrices are rejected."], core.solve_linear_system),
    _method("numerics.polynomial_roots", "Polynomial roots", "numerical-analysis", "Finds complex roots from descending polynomial coefficients.", ["numpy"], {"coefficients":"numeric[]"}, {"roots":"complex[]"}, ["Coefficients are ordered from highest to lowest power."], core.polynomial_roots),
    _method("numerics.sampled_integration", "Sampled numerical integration", "numerical-analysis", "Integrates sampled y(x) values using trapezoid and Simpson methods.", ["numpy","scipy"], {"x":"strictly increasing numeric[]","y":"numeric[]"}, {"trapezoid":"number","simpson":"number"}, ["Samples represent a single-valued function."], core.sampled_integration),
    _method("simulation.monte_carlo_pi", "Monte Carlo pi benchmark", "simulation", "A seeded Monte Carlo benchmark for validating deterministic execution and provenance.", ["numpy"], {"samples":"integer 100..1000000"}, {"estimate":"number","absoluteError":"number","standardError":"number"}, ["Pseudo-random execution is reproducible for a fixed seed."], core.monte_carlo_pi),
    _method("system.controlled_delay", "Controlled worker delay", "system-diagnostics", "Runs a bounded delay for queue, cancellation, timeout, and worker-recovery validation.", [], {"seconds":"number 0..10"}, {"requestedSeconds":"seconds","elapsedSeconds":"seconds"}, ["Diagnostic method only; maximum delay is 10 seconds."], core.controlled_delay),
]

REGISTRY = {method.id: method for method in METHODS}
ALIASES = {"kinetic":"mechanics.kinetic_energy", "projectile":"mechanics.projectile_motion", "pv":"energy.photovoltaic_output", "michaelis":"biology.michaelis_menten"}


def resolve(method_id: str) -> MethodDefinition:
    canonical = ALIASES.get(method_id, method_id)
    try:
        return REGISTRY[canonical]
    except KeyError as exc:
        raise KeyError(f"Unknown registered compute method: {method_id}") from exc


def catalog() -> list[dict[str, Any]]:
    return [method.public() for method in METHODS]
