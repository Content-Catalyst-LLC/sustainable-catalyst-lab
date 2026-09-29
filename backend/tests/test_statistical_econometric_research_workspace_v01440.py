from app import statistical_econometric_research_workspace_v01440 as m

DATASET={"datasetId":"d1","title":"Panel sample","rowCount":120,"entityIdVariable":"firm","timeVariable":"year","variables":[{"name":"y","role":"outcome","dataType":"float"},{"name":"x","role":"treatment","dataType":"float"},{"name":"z","role":"instrument","dataType":"float"}],"provenanceRef":"prov:d1"}
ESTIMAND={"estimandId":"e1","label":"Effect of x on y","population":"sample firms","outcome":"y","treatmentOrExposure":"x","contrast":"one-unit increase","timeHorizon":"annual","identificationStrategy":"instrumental variables","assumptions":["relevance","exclusion"],"causal":True}
SPEC={"specificationId":"s1","estimandRef":"e1","datasetRef":"d1","modelFamily":"iv-2sls","estimator":"2sls","formula":"y ~ x + c | z + c","outcome":"y","predictors":["x"],"controls":["c"],"instruments":["z"],"clusterVariables":["firm"],"covarianceEstimator":"cluster","assumptions":["instrument relevance","instrument exogeneity"],"software":{"runtime":"R","package":"fixest"}}
EST={"estimateId":"r1","specificationRef":"s1","estimandRef":"e1","runRef":"run:1","coefficients":[{"term":"x","estimate":1.2,"stdError":0.4,"statistic":3.0,"pValue":0.004,"confLow":0.4,"confHigh":2.0}],"fit":{"nobs":120,"r2":0.35},"sample":{"n":120},"provenanceRef":"prov:r1"}
P={"sessionId":"sess1","projectRef":"proj:1","state":"analysis","datasets":[DATASET],"estimands":[ESTIMAND],"specifications":[SPEC],"estimates":[EST],"diagnostics":[{"diagnosticId":"dg1","specificationRef":"s1","kind":"first-stage-f","statistic":18.2,"status":"reported"}],"limitations":["observational design"],"review":{"status":"in-review"}}

def test_health_and_contract():
    h=m.health(); assert h["version"]=="0.144.0" and h["api_route_count"]==52 and h["labExecutesStatisticalEstimation"] is False and h["associationIsCausation"] is False
    c=m.contract(); assert c["predecessorVersion"]=="0.143.0" and "iv-2sls" in c["modelFamilies"] and "cluster" in c["covarianceEstimators"]

def test_estimand_specification_estimate_are_separate_objects():
    e=m.normalize_estimand(ESTIMAND); s=m.normalize_specification(SPEC); r=m.normalize_estimate(EST)
    assert e["estimateIsEstimand"] is False and s["estimandRef"]=="e1" and r["estimandRef"]=="e1"
    assert r["scientificValidityCertified"] is False and r["causalEffectCertified"] is False

def test_identification_and_specification_audits():
    assert m.specification_audit({"specification":SPEC})["clean"] is True
    ident=m.identification_audit({"estimand":ESTIMAND,"specification":SPEC}); assert ident["issues"]==[] and ident["causalIdentificationCertified"] is False
    bad=m.identification_audit({"estimand":{**ESTIMAND,"identificationStrategy":"","assumptions":[]},"specification":{**SPEC,"assumptions":[]}}); assert len(bad["issues"])>=2

def test_diagnostics_do_not_prove_assumptions():
    a=m.assumption_audit({"declared":["homoskedasticity"],"diagnostics":[{"kind":"bp","pValue":0.4,"status":"pass"}]}); assert a["assumptionsProven"] is False and a["diagnosticPassIsProof"] is False
    h=m.heteroskedasticity_audit({"diagnostic":{"pValue":0.4,"status":"pass"}}); assert h["computedByLab"] is False and h["assumptionProven"] is False

def test_missingness_panel_and_time_series_audits():
    miss=m.missingness_audit({"variables":[{"variable":"y","n":100,"missing":5}]}); assert abs(miss["rows"][0]["missingRate"]-.05)<1e-9 and miss["missingnessMechanismInferred"] is False
    panel=m.panel_structure_audit({"entityVariable":"firm","timeVariable":"year","entityCount":20,"timeCount":6,"balanced":True}); assert panel["panelStructureDeclared"] is True and panel["panelAssumptionsCertified"] is False
    ts=m.time_series_structure_audit({"timeVariable":"date","frequency":"monthly"}); assert ts["stationarityCertified"] is False and ts["cointegrationCertified"] is False

def test_tables_and_robust_inference_boundaries():
    t=m.coefficient_table({"estimates":[EST]}); assert t["rowCount"]==1 and t["rows"][0]["estimate"]==1.2 and t["statisticalSignificanceIsSubstantiveImportance"] is False
    r=m.robust_inference_summary({"estimates":[{"label":"clustered","covarianceEstimator":"cluster","estimate":1.2,"stdError":.4}]}); assert r["robustStandardErrorsDoNotFixIdentification"] is True

def test_specification_and_robustness_matrices_do_not_pick_winner():
    sm=m.specification_matrix({"specifications":[SPEC,{**SPEC,"specificationId":"s2","controls":["c","w"]}]}); assert len(sm["columns"])==2 and sm["automaticPreferredSpecification"] is None
    rm=m.robustness_matrix({"checks":[{"label":"base","metrics":{"estimate":1.2}},{"label":"alt","metrics":{"estimate":1.0}}]}); assert rm["automaticWinnerSelection"] is False and rm["robustnessIsValidityProof"] is False

def test_model_and_estimand_comparisons_keep_context():
    mc=m.model_comparison({"models":[{"modelRef":"s1","metrics":{"aic":100},"comparability":{"sameSample":True}},{"modelRef":"s2","metrics":{"aic":98},"comparability":{"sameSample":True}}]}); assert mc["automaticRanking"] is False and mc["automaticWinnerSelection"] is False
    ec=m.estimand_comparison({"estimates":[{"estimandRef":"e1","value":1.2,"unit":"USD","population":"A","timeHorizon":"1y"},{"estimandRef":"e2","value":1.0,"unit":"USD","population":"B","timeHorizon":"1y"}]}); assert ec["directlyComparable"] is False

def test_authority_handoffs():
    w=m.workspace_execution_handoff({**P,"requestedOperation":"estimate-iv","specification":SPEC})["handoff"]; assert w["executionAuthority"]=="workspace" and w["automaticExecution"] is False and w["labExecutesEstimation"] is False
    c=m.core_handoff(P)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["automaticCanonicalization"] is False
    r=m.research_os_handoff(P)["handoff"]; assert r["automaticPhaseAdvance"] is False

def test_snapshot_and_reproducibility_boundaries():
    a=m.workspace_snapshot(P)["snapshot"]; b=m.workspace_snapshot(P)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    assert m.compare_snapshots({"left":P,"right":P})["sameWorkspaceState"] is True
    e=m.export_bundle(P); assert e["scientificValidityCertified"] is False
    rp=m.reproducibility_package(P)["package"]; assert rp["reproductionCertified"] is False and rp["replicationCertified"] is False and rp["scientificValidityCertified"] is False

def test_interpretation_boundaries():
    b=m.interpretation_boundary()["boundaries"]
    assert b["coefficientIsEstimand"] is False and b["statisticalSignificanceIsSubstantiveImportance"] is False and b["associationIsCausation"] is False and b["diagnosticPassProvesAssumptions"] is False
