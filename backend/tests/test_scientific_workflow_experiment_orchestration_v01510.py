from app import scientific_workflow_experiment_orchestration_v01510 as m

def test_health_policy_and_contract():
    h=m.health(); assert h["version"]=="0.151.0" and h["scientificWorkflowExperimentOrchestration"] and h["api_route_count"]==103
    p=m.policy(); assert p["labExecutesHeavyCompute"] is False and p["automaticWorkflowAdvance"] is False and p["humanScientificReviewRequired"] is True

def test_normalized_objects_are_deterministic_and_guarded():
    w=m.normalize_workflow({"title":"Study"}); assert w["fingerprint"]==m.normalize_workflow({"title":"Study"})["fingerprint"] and w["automaticWorkflowAdvance"] is False
    s=m.normalize_stage({"title":"Fit","stageType":"machine-learning","workspaceId":"neural"}); assert s["scientificValidityCertified"] is False and s["executionAuthority"]=="Workspace"
    d=m.normalize_dependency({"fromStageRef":"a","toStageRef":"b","dependencyType":"data"}); assert d["dependencyIsCausalProof"] is False

def test_acyclic_topological_plan_and_cycle_detection():
    p={"stages":[{"stageId":"a"},{"stageId":"b"},{"stageId":"c"}],"dependencies":[{"fromStageRef":"a","toStageRef":"b"},{"fromStageRef":"b","toStageRef":"c"}]}
    x=m.topological_plan(p); assert x["order"]==["a","b","c"] and x["acyclic"] and x["automaticWorkflowAdvance"] is False
    y=m.cycle_audit({"stages":[{"stageId":"a"},{"stageId":"b"}],"dependencies":[{"fromStageRef":"a","toStageRef":"b"},{"fromStageRef":"b","toStageRef":"a"}]}); assert y["acyclic"] is False and set(y["cycleStageRefs"])=={"a","b"}

def test_gate_readiness_requires_explicit_passage():
    p={"stages":[{"stageId":"a"}],"requirements":[{"name":"data","satisfied":True}],"gates":[{"gateId":"g1","gateType":"review","status":"pending"}]}
    r=m.readiness_report(p); assert r["ready"] is False and r["automaticWorkflowAdvance"] is False
    g=m.review_gate({"requirements":[{"name":"review","satisfied":True}]}); assert g["eligible"] is True and g["approved"] is False and g["automaticApproval"] is False

def test_execution_and_authority_boundaries():
    p={"stages":[{"stageId":"a","workspaceId":"simulation","operation":"run","executionAuthority":"Workspace","runtimeRef":"python","environmentRef":"env"}]}
    e=m.execution_plan(p); assert e["automaticDispatch"] is False and e["labExecutesHeavyCompute"] is False
    a=m.authority_audit(p); assert a["clean"] is True and a["authorities"]["primaryCompute"]=="Workspace"

def test_failure_retry_and_recovery_are_plans_not_mutations():
    f=m.failure_report({"failures":[{"stageRef":"a","failureClass":"runtime","message":"x"}]}); assert f["failures"][0]["rootCauseEstablished"] is False
    r=m.retry_plan({"stageRunRef":"sr1","policy":{"strategy":"checkpoint-resume","maxAttempts":3}}); assert r["automaticRetry"] is False and r["retryRepairsMethodology"] is False
    q=m.recovery_plan({"workflowRef":"w1","failedStageRefs":["a"]}); assert q["automaticRecovery"] is False and q["humanReviewRequired"] is True

def test_transition_and_approval_do_not_auto_mutate():
    t=m.transition_request({"workflowRef":"w","stageRef":"s","fromState":"ready","toState":"queued"}); assert t["mutationPerformed"] is False and t["automaticTransition"] is False
    a=m.approval_decision({"approvalType":"scientific-review","subjectRef":"s","decision":"approved"}); assert a["decisionRecorded"] is True and a["workflowMutationPerformed"] is False

def test_lineage_provenance_runtime_and_environment_audits():
    l=m.lineage_graph({"nodes":[{"id":"a"}],"edges":[{"source":"a","target":"b"}]}); assert l["lineageIsCausalProof"] is False
    p=m.provenance_audit({"items":[{"provenance":{"source":"x"}},{}]}); assert p["complete"] is False
    e=m.environment_audit({"stages":[{"stageId":"a","executionAuthority":"Workspace","runtimeRef":"python"}]}); assert e["missingEnvironmentStageRefs"]==["a"]
    r=m.runtime_audit({"stages":[{"stageId":"a","executionAuthority":"Workspace","environmentRef":"env"}]}); assert r["missingRuntimeStageRefs"]==["a"]

def test_change_impact_and_artifact_dependencies():
    x=m.change_impact({"changedRefs":["a"],"dependencies":[{"fromStageRef":"a","toStageRef":"b"},{"fromStageRef":"b","toStageRef":"c"}]}); assert x["impactedStageRefs"]==["b","c"] and x["impactIsScientificInvalidation"] is False
    i=m.artifact_dependency_index({"stages":[{"stageId":"a","outputRefs":["x"]},{"stageId":"b","inputRefs":["x"]}]}); assert i["artifacts"]["x"]["producers"]==["a"] and i["artifactDependencyIsCausalProof"] is False

def test_handoffs_preserve_scientific_boundaries():
    fns=(m.workspace_execution_handoff,m.workbench_handoff,m.core_handoff,m.library_handoff,m.research_os_handoff,m.integrated_lab_handoff,m.neural_handoff,m.linguistics_handoff,m.statistics_handoff,m.simulation_handoff,m.graph_handoff,m.graph_ml_handoff,m.multimodal_handoff,m.validation_handoff)
    for fn in fns:
        h=fn({"workflowRef":"w","stageRef":"s"})["handoff"]; assert h["scientificValidityCertified"] is False and h["publicationAccepted"] is False

def test_snapshot_export_and_reproducibility():
    p={"workflow":{"title":"x"},"stages":[{"stageId":"a"}]}; a=m.workflow_snapshot(p)["snapshot"]; b=m.workflow_snapshot(p)["snapshot"]; assert a["fingerprint"]==b["fingerprint"]
    d=m.workflow_diff({"a":{"x":1},"b":{"x":2}}); assert d["changeCount"]==1 and d["changeIsScientificInvalidation"] is False
    rp=m.reproducibility_package({"workflowRef":"w"})["package"]; assert rp["reproductionCertified"] is False and rp["scientificValidityCertified"] is False

def test_release_gates_acceptance_and_boundaries():
    assert all(m.release_gates()["gates"].values())
    a=m.acceptance_report(); assert a["accepted"]["dependencyGraph"] is True and a["scientificValidityCertified"] is False
    b=m.interpretation_boundary(); assert b["workflowOrderIsScientificNecessity"] is False and b["dependencyEdgeIsCausalProof"] is False and b["gatePassageIsPublicationAcceptance"] is False
