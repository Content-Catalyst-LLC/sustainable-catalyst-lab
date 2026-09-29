from app import simulation_computational_experiment_workspace_v01450 as m
MODEL={"modelId":"m1","title":"Reservoir model","simulationFamily":"ode","equations":["dS/dt=inflow-outflow"],"stateVariables":[{"name":"S","unit":"m3"}],"parameters":[{"name":"k","role":"uncertain-input","unit":"1/day","bounds":{"min":0.1,"max":0.5}}],"numericalMethod":"rk45","solver":{"rtol":1e-6},"timeDomain":{"start":0,"stop":365,"step":1},"initialConditions":{"S":100},"assumptions":["well mixed"],"codeRef":"git:abc","environmentRef":"env:1"}
SCENARIO={"scenarioId":"s1","label":"Baseline","modelRef":"m1","parameterOverrides":{"k":0.2},"seed":42}
RUN={"runId":"r1","modelRef":"m1","scenarioRef":"s1","status":"completed","seed":42,"outputs":{"peak":120.0,"mean":100.0},"series":[{"name":"storage","time":[0,1,2],"values":[100,104,101]}],"runtime":{"language":"python"},"provenanceRef":"prov:r1"}
EXP={"experimentId":"e1","projectRef":"p1","title":"Reservoir simulation","question":"How does storage respond?","experimentFamily":"scenario-comparison","state":"analysis","model":MODEL,"scenarios":[SCENARIO],"runs":[RUN],"verification":{"status":"reviewed"},"validation":{"status":"pending"},"limitations":["simplified inflow"],"review":{"status":"in-review"}}

def test_health_contract_catalog():
    h=m.health(); assert h["version"]=="0.145.0" and h["api_route_count"]==56 and h["labExecutesSimulation"] is False and h["modeledOutputIsEvidence"] is False
    c=m.contract(); assert c["predecessorVersion"]=="0.144.0" and "agent-based" in c["simulationFamilies"] and "rk45" in c["numericalMethods"]
    assert m.simulation_catalog()["automaticScenarioSelection"] is False

def test_object_model_separates_modeled_output_from_evidence():
    model=m.normalize_model(MODEL); s=m.normalize_scenario(SCENARIO); r=m.normalize_run(RUN); e=m.normalize_experiment(EXP)
    assert model["scientificValidityCertified"] is False and s["scenarioIsPrediction"] is False
    assert r["modeledOutput"] is True and r["observationalEvidence"] is False and e["automaticScientificValidity"] is False

def test_design_and_parameter_audits():
    assert m.design_audit(EXP)["clean"] is True
    p=m.parameter_audit({"parameters":MODEL["parameters"]}); assert p["issues"]==[] and p["automaticDistributionInference"] is False
    bad=m.design_audit({"model":{"simulationFamily":"ode"}}); assert len(bad["issues"])>=2

def test_verification_validation_and_calibration_are_separate():
    v=m.verification_audit({"checks":[{"kind":"unit-test","status":"pass"}],"implementationVerified":True}); assert v["verificationIsValidation"] is False and v["scientificValidityCertified"] is False
    val=m.validation_audit({"validationDataRef":"dataset:obs","metrics":{"rmse":2.0},"intendedUse":"planning"}); assert val["validationIsVerification"] is False and val["scientificValidityCertified"] is False
    cal=m.calibration_audit({"method":"least-squares","targets":["flow"]}); assert cal["calibrationIsValidation"] is False and cal["independentValidationCertified"] is False

def test_numerical_and_convergence_audits_do_not_certify_science():
    n=m.numerical_method_audit({"numericalMethod":"rk45","solver":{"rtol":1e-6}}); assert n["numericalMethod"]=="rk45" and n["methodAppropriatenessCertified"] is False
    c=m.convergence_audit({"metricValues":[1.2,1.1,1.05],"resolutionLevels":[10,20,40],"converged":True}); assert c["convergenceDeclared"] is True and c["convergenceCertified"] is False and c["scientificValidityCertified"] is False

def test_sensitivity_uncertainty_boundaries():
    s=m.sensitivity_audit({"method":"sobol","indices":[{"parameter":"k","S1":0.7}]}); assert s["parameterImportanceIsCausalEffect"] is False and s["automaticRanking"] is False
    u=m.uncertainty_audit({"sources":["k"],"propagationMethod":"monte-carlo"}); assert u["uncertaintyResolved"] is False

def test_outputs_ensemble_and_matrices_no_auto_winner():
    o=m.output_series({"series":RUN["series"]}); assert o["series"][0]["summary"]["count"]==3 and o["observationalEvidence"] is False
    ens=m.ensemble_summary({"runs":[{"metrics":{"peak":1.0}},{"metrics":{"peak":3.0}}]}); assert ens["metricSummaries"]["peak"]["mean"]==2.0 and ens["automaticScenarioSelection"] is False
    sm=m.scenario_matrix({"scenarios":[{"scenarioRef":"s1","metrics":{"peak":2}},{"scenarioRef":"s2","metrics":{"peak":1}}]}); assert sm["automaticPreferredScenario"] is None and sm["automaticRanking"] is False
    pm=m.parameter_sweep_matrix({"axes":["k"],"rows":[{"k":.1,"y":2}]}); assert pm["automaticOptimumSelection"] is False

def test_authority_handoffs():
    w=m.workspace_execution_handoff({"experiment":EXP,"requestedOperation":"ensemble"})["handoff"]; assert w["executionAuthority"]=="workspace" and w["automaticExecution"] is False and w["labExecutesSimulation"] is False
    wb=m.workbench_handoff({"experiment":EXP,"requestedPrototype":"solver-prototype"})["handoff"]; assert wb["executionAuthority"]=="workbench" and wb["automaticExecution"] is False
    c=m.core_handoff(EXP)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["automaticCanonicalization"] is False
    r=m.research_os_handoff(EXP)["handoff"]; assert r["automaticPhaseAdvance"] is False

def test_snapshot_reproducibility_and_publication_boundaries():
    a=m.workspace_snapshot(EXP)["snapshot"]; b=m.workspace_snapshot(EXP)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    assert m.compare_snapshots({"left":EXP,"right":EXP})["sameWorkspaceState"] is True
    ex=m.export_bundle(EXP); assert ex["scientificValidityCertified"] is False
    rp=m.reproducibility_package(EXP)["package"]; assert rp["reproductionCertified"] is False and rp["replicationCertified"] is False and rp["scientificValidityCertified"] is False
    ph=m.publication_handoff(EXP)["handoff"]; assert ph["publicationAccepted"] is False and ph["automaticAcceptance"] is False

def test_interpretation_boundaries():
    b=m.interpretation_boundary()["boundaries"]
    assert b["simulationOutputIsObservationalEvidence"] is False and b["verificationIsValidation"] is False and b["numericalConvergenceIsScientificValidity"] is False and b["sensitivityIsCausality"] is False
