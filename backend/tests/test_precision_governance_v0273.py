from __future__ import annotations

import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.compute import ComputeExecutionError, run_compute
from app.main import app
from app.precision import policy_catalog
from app.schemas import ComputeRequest

AUTH={"mode":"test","client":"pytest"}


def test_policy_catalog_has_four_profiles():
    catalog=policy_catalog()
    assert catalog["version"]=="0.27.3"
    assert {row["id"] for row in catalog["profiles"]}=={"fast","balanced","strict","diagnostic"}
    assert catalog["precision"]["machineEpsilon"]==np.finfo(float).eps


def test_root_manual_solver_and_reference_comparison():
    result=run_compute(ComputeRequest(method="numerics.root_scalar_polynomial",inputs={"coefficients":[1,0,-2],"bracket":[0,2]},governance={"precisionProfile":"diagnostic","solverPolicy":"manual","requestedSolver":"ridder","referenceComparison":True}),AUTH)
    assert result.outputs["solver"]=="ridder"
    assert abs(result.outputs["root"]-math.sqrt(2))<1e-10
    assert result.governance["referenceComparison"]["withinTolerance"] is True
    assert result.provenance.solver_governance["precisionProfile"]=="diagnostic"


def test_ode_strict_profile_recommends_dop853():
    result=run_compute(ComputeRequest(method="numerics.ode_first_order",inputs={"model":"exponential","initialValue":2,"startTime":0,"endTime":4,"points":20},parameters={"rate":0.25},units={"startTime":"s","endTime":"seconds"},governance={"precisionProfile":"strict"}),AUTH)
    assert result.outputs["solver"]=="DOP853"
    assert result.governance["units"]["status"]=="valid"


def test_strict_unit_policy_rejects_missing_units():
    with pytest.raises(ComputeExecutionError) as exc:
        run_compute(ComputeRequest(method="mechanics.kinetic_energy",inputs={"mass":2,"velocity":3},governance={"unitPolicy":"strict"}),AUTH)
    assert exc.value.status_code==422
    assert "Strict unit validation" in exc.value.detail


def test_linear_system_falls_back_to_least_squares():
    matrix=[[1,1],[1,1+1e-12]]
    result=run_compute(ComputeRequest(method="numerics.linear_system",inputs={"matrix":matrix,"vector":[2,2+1e-12]},governance={"conditionThreshold":1e8,"illConditionedPolicy":"least-squares"}),AUTH)
    assert result.outputs["illConditioned"] is True
    assert result.outputs["solver"]=="least-squares"
    assert result.warnings


def test_manual_unknown_solver_rejected():
    with pytest.raises(ComputeExecutionError) as exc:
        run_compute(ComputeRequest(method="numerics.root_scalar_polynomial",inputs={"coefficients":[1,0,-2],"bracket":[0,2]},governance={"solverPolicy":"manual","requestedSolver":"newton"}),AUTH)
    assert exc.value.code=="solver_governance_error"


def test_governance_health_and_policies_public_or_signed(monkeypatch):
    monkeypatch.setenv("SC_LAB_COMPUTE_SIGNING_SECRET","")
    with TestClient(app) as client:
        health=client.get("/v1/governance/health")
        assert health.status_code==200 and health.json()["version"]=="0.27.3"


def test_quadrature_exact_reference():
    result=run_compute(ComputeRequest(method="numerics.adaptive_quadrature_polynomial",inputs={"coefficients":[3,0,2],"lower":0,"upper":2},governance={"referenceComparison":True}),AUTH)
    comparison=result.governance["referenceComparison"]
    assert comparison["referenceMethod"]=="analytic-polynomial-antiderivative"
    assert comparison["withinTolerance"] is True
