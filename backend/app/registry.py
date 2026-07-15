from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable

from .methods import core, numerical

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
    example_inputs: dict[str, Any] = None
    example_parameters: dict[str, Any] = None
    recommended_execution: str = "synchronous"
    estimated_cost: str = "light"

    def public(self) -> dict[str, Any]:
        row = asdict(self)
        row.pop("handler", None)
        row["execution_modes"] = self.execution_modes or ["python-core"]
        row["references"] = self.references or []
        row["example_inputs"] = self.example_inputs or {}
        row["example_parameters"] = self.example_parameters or {}
        return row


def _method(id: str, title: str, domain: str, description: str, packages: list[str], inputs: dict[str, Any], outputs: dict[str, Any], assumptions: list[str], handler: Handler, references: list[dict[str, str]] | None = None, example_inputs: dict[str, Any] | None = None, example_parameters: dict[str, Any] | None = None, recommended_execution: str = "synchronous", estimated_cost: str = "light") -> MethodDefinition:
    return MethodDefinition(id=id, version="1.0.0", title=title, domain=domain, description=description, packages=packages, input_schema=inputs, output_schema=outputs, assumptions=assumptions, handler=handler, execution_modes=["python-core", "queued-python-core"], references=references or [], example_inputs=example_inputs or {}, example_parameters=example_parameters or {}, recommended_execution=recommended_execution, estimated_cost=estimated_cost)


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

    _method("numerics.root_scalar_polynomial", "Bracketed polynomial root", "numerical-analysis", "Finds a real polynomial root inside a sign-changing bracket using Brent's method.", ["numpy", "scipy"], {"coefficients":"descending polynomial coefficients", "bracket":"[lower, upper]"}, {"root":"number", "functionValue":"number", "converged":"boolean"}, ["The polynomial changes sign across the supplied bracket."], numerical.polynomial_root_scalar, example_inputs={"coefficients":[1,0,-2],"bracket":[0,2]}, example_parameters={"absoluteTolerance":1e-10,"relativeTolerance":1e-10}),
    _method("numerics.adaptive_quadrature_polynomial", "Adaptive polynomial quadrature", "numerical-analysis", "Integrates a polynomial over finite bounds with adaptive Gauss-Kronrod quadrature and an exact polynomial cross-check.", ["numpy", "scipy"], {"coefficients":"descending polynomial coefficients", "lower":"number", "upper":"number"}, {"integral":"number", "absoluteErrorEstimate":"number", "polynomialExactIntegral":"number"}, ["The integrand is represented by a finite polynomial."], numerical.polynomial_quadrature, example_inputs={"coefficients":[3,0,2],"lower":0,"upper":2}, example_parameters={"absoluteTolerance":1e-10,"relativeTolerance":1e-10}),
    _method("numerics.interpolation", "Interpolation query", "numerical-analysis", "Evaluates linear, monotone PCHIP, or cubic interpolation over ordered observations.", ["numpy", "scipy"], {"x":"strictly increasing numeric[]", "y":"numeric[]", "query":"numeric[]"}, {"values":"numeric[]", "kind":"string"}, ["Observed x values are strictly increasing.", "Extrapolation is disabled unless explicitly requested."], numerical.interpolation_query, example_inputs={"x":[0,1,2,3,4],"y":[0,1,4,9,16],"query":[0.5,1.5,2.5,3.5]}, example_parameters={"kind":"pchip","extrapolate":False}),
    _method("numerics.ode_first_order", "First-order ODE solver", "differential-equations", "Solves governed first-order exponential, decay, logistic, or forced-linear models with adaptive RK45 integration.", ["numpy", "scipy"], {"model":"exponential|decay|logistic|forced_linear", "initialValue":"number", "startTime":"number", "endTime":"number", "points":"integer"}, {"time":"numeric[]", "values":"numeric[]", "finalValue":"number"}, ["Only registered differential-equation families are executed.", "The solver uses adaptive RK45 with bounded output size."], numerical.ode_first_order, example_inputs={"model":"logistic","initialValue":10,"startTime":0,"endTime":20,"points":101}, example_parameters={"rate":0.35,"carryingCapacity":100,"relativeTolerance":1e-7,"absoluteTolerance":1e-9}, recommended_execution="queued", estimated_cost="medium"),
    _method("numerics.eigen_analysis", "Matrix eigen analysis", "linear-algebra", "Computes eigenvalues, eigenvectors, spectral radius, and residual diagnostics for a dense matrix.", ["numpy"], {"matrix":"square numeric[][]"}, {"eigenvalues":"number|complex[]", "eigenvectors":"number|complex[][]", "residualNorms":"numeric[]"}, ["Dense matrices are limited to 50x50.", "Symmetric matrices use a Hermitian solver."], numerical.eigen_analysis, example_inputs={"matrix":[[2,1],[1,2]]}, example_parameters={"symmetricTolerance":1e-10}, estimated_cost="medium"),
    _method("optimization.scalar_bounded", "Bounded scalar minimization", "optimization", "Minimizes a registered one-dimensional objective over finite bounds.", ["numpy", "scipy"], {"objective":"quadratic|quartic|oscillatory", "lower":"number", "upper":"number", "coefficients":"numeric[] optional"}, {"x":"number", "minimum":"number", "success":"boolean"}, ["Only registered objective families are permitted.", "A bounded local optimizer is used."], numerical.bounded_minimize, example_inputs={"objective":"quadratic","lower":-10,"upper":10,"coefficients":[1,-4,7]}, example_parameters={"absoluteTolerance":1e-8,"maxIterations":1000}),
    _method("optimization.linear_program", "Linear programming", "optimization", "Solves a bounded linear objective with optional equality and inequality constraints using HiGHS.", ["numpy", "scipy"], {"objective":"numeric[]", "inequalityMatrix":"numeric[][] optional", "inequalityVector":"numeric[] optional", "equalityMatrix":"numeric[][] optional", "equalityVector":"numeric[] optional", "bounds":"[lower,upper][] optional"}, {"solution":"numeric[]", "objectiveMinimum":"number", "success":"boolean"}, ["The model is linear and continuous.", "Default variable bounds are non-negative."], numerical.linear_program, example_inputs={"objective":[-3,-2],"inequalityMatrix":[[2,1],[1,2]],"inequalityVector":[18,16],"bounds":[[0,None],[0,None]]}, recommended_execution="queued", estimated_cost="medium"),
    _method("signal.fft_spectrum", "FFT spectrum", "signal-processing", "Computes a one-sided amplitude and power spectrum with windowing and detrending.", ["numpy", "scipy"], {"values":"numeric[]", "sampleRate":"Hz > 0"}, {"frequencyHz":"numeric[]", "amplitude":"numeric[]", "peakFrequencyHz":"number"}, ["Samples are evenly spaced.", "Reported amplitudes are window coherent-gain corrected."], numerical.fft_spectrum, example_inputs={"values":[0,1,0,-1,0,1,0,-1,0,1,0,-1,0,1,0,-1],"sampleRate":16}, example_parameters={"window":"hann","detrend":"constant"}, recommended_execution="queued", estimated_cost="medium"),
    _method("uncertainty.monte_carlo_propagation", "Monte Carlo uncertainty propagation", "uncertainty-analysis", "Propagates named normal, uniform, or triangular inputs through a registered algebraic model.", ["numpy", "scipy"], {"model":"linear|product|ratio|power", "distributions":"distribution[]", "samples":"integer"}, {"mean":"number", "standardDeviation":"number", "confidenceInterval":"[number,number]"}, ["Pseudo-random execution is reproducible for a fixed seed.", "Only registered algebraic models are permitted."], numerical.monte_carlo_propagation, example_inputs={"model":"product","samples":20000,"distributions":[{"name":"area","distribution":"normal","mean":10,"stdDev":0.4},{"name":"intensity","distribution":"normal","mean":1000,"stdDev":50}]}, example_parameters={"confidence":0.95}, recommended_execution="queued", estimated_cost="heavy"),
    _method("uncertainty.bootstrap_mean_interval", "Bootstrap mean interval", "uncertainty-analysis", "Computes a seeded nonparametric percentile confidence interval for the sample mean.", ["numpy", "scipy"], {"values":"numeric[]", "resamples":"integer"}, {"sampleMean":"number", "bootstrapStandardError":"number", "confidenceInterval":"[number,number]"}, ["Observations are treated as exchangeable for resampling."], numerical.bootstrap_mean_interval, example_inputs={"values":[12.1,11.8,12.5,12.0,11.9,12.3,12.2,11.7],"resamples":5000}, example_parameters={"confidence":0.95}, recommended_execution="queued", estimated_cost="heavy"),
    _method("sensitivity.local_finite_difference", "Local finite-difference sensitivity", "sensitivity-analysis", "Estimates local partial derivatives and elasticities for a registered algebraic model.", ["numpy"], {"model":"linear|product|ratio|power", "baseline":"named numeric object"}, {"baselineOutput":"number", "sensitivities":"record[]"}, ["Sensitivities are local to the supplied baseline.", "Central differences are used."], numerical.local_sensitivity, example_inputs={"model":"product","baseline":{"efficiency":0.2,"area":10,"irradiance":1000}}, example_parameters={"relativeStep":0.0001,"absoluteStep":1e-8}),
    _method("simulation.parameter_sweep", "Registered parameter sweep", "simulation", "Evaluates a bounded sequence of parameter values for logistic growth, projectile range, photovoltaic output, or Michaelis-Menten kinetics.", ["numpy"], {"model":"logistic_growth|projectile_range|photovoltaic_output|michaelis_menten", "parameter":"string", "values":"numeric[]", "fixed":"object"}, {"rows":"record[]", "minimumOutput":"number", "maximumOutput":"number"}, ["Only registered model families are evaluated.", "The sweep is deterministic."], numerical.parameter_sweep, example_inputs={"model":"logistic_growth","parameter":"rate","values":[0.1,0.2,0.3,0.4,0.5],"fixed":{"initial":10,"carryingCapacity":100,"time":10}}, recommended_execution="queued", estimated_cost="medium"),
    _method("system.controlled_delay", "Controlled worker delay", "system-diagnostics", "Runs a bounded delay for queue, cancellation, timeout, and worker-recovery validation.", [], {"seconds":"number 0..10"}, {"requestedSeconds":"seconds","elapsedSeconds":"seconds"}, ["Diagnostic method only; maximum delay is 10 seconds."], core.controlled_delay),
]

REGISTRY = {method.id: method for method in METHODS}
ALIASES = {"kinetic":"mechanics.kinetic_energy", "projectile":"mechanics.projectile_motion", "pv":"energy.photovoltaic_output", "michaelis":"biology.michaelis_menten", "ode":"numerics.ode_first_order", "fft":"signal.fft_spectrum", "monte-carlo":"uncertainty.monte_carlo_propagation"}


def resolve(method_id: str) -> MethodDefinition:
    canonical = ALIASES.get(method_id, method_id)
    try:
        return REGISTRY[canonical]
    except KeyError as exc:
        raise KeyError(f"Unknown registered compute method: {method_id}") from exc


def catalog() -> list[dict[str, Any]]:
    return [method.public() for method in METHODS]
