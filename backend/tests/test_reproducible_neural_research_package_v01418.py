from app import reproducible_neural_research_package_v01418 as m

C=[
 {"componentId":"dataset","kind":"dataset-reference","section":"data-lineage","ref":"ds:v1","sha256":"a"*64,"sourceRelease":"0.141.0","sourceSchema":"dataset/1","provenanceRef":"prov-ds"},
 {"componentId":"split","kind":"split-reference","section":"data-lineage","ref":"split:test","sha256":"b"*64,"sourceRelease":"0.141.0","sourceSchema":"split/1","provenanceRef":"prov-split","dependsOn":["dataset"]},
 {"componentId":"code","kind":"code-reference","section":"provenance-lineage","ref":"git:abc","sha256":"c"*64,"sourceRelease":"0.141.8","sourceSchema":"code/1","provenanceRef":"prov-code"},
 {"componentId":"model","kind":"model-spec","section":"model-architecture","ref":"model:a","sha256":"d"*64,"sourceRelease":"0.141.1","sourceSchema":"model/1","provenanceRef":"prov-model"},
 {"componentId":"config","kind":"training-config","section":"training-configuration","ref":"cfg:a","sha256":"e"*64,"sourceRelease":"0.141.1","sourceSchema":"config/1","provenanceRef":"prov-config","dependsOn":["model"]},
 {"componentId":"run","kind":"run-record","section":"execution-environment","ref":"run:1","sha256":"f"*64,"sourceRelease":"0.141.0","sourceSchema":"run/1","provenanceRef":"prov-run","environmentRef":"env:1","dependsOn":["dataset","split","code","config"]},
 {"componentId":"metrics","kind":"metric-series","section":"training-telemetry","ref":"metrics:1","sha256":"1"*64,"sourceRelease":"0.141.2","sourceSchema":"metrics/1","provenanceRef":"prov-metrics","runRef":"run:1","dependsOn":["run"]},
 {"componentId":"ckpt","kind":"checkpoint","section":"checkpoints-artifacts","ref":"ckpt:1","sha256":"2"*64,"sourceRelease":"0.141.2","sourceSchema":"checkpoint/1","provenanceRef":"prov-ckpt","runRef":"run:1","dependsOn":["run"]},
 {"componentId":"compare","kind":"comparison-matrix","section":"model-comparison","ref":"cmp:1","sha256":"3"*64,"sourceRelease":"0.141.3","sourceSchema":"comparison/1","provenanceRef":"prov-cmp"},
 {"componentId":"search","kind":"search-study","section":"hyperparameter-study","ref":"search:1","sha256":"4"*64,"sourceRelease":"0.141.4","sourceSchema":"search/1","provenanceRef":"prov-search"},
 {"componentId":"ablation","kind":"ablation-result","section":"ablation-study","ref":"abl:1","sha256":"5"*64,"sourceRelease":"0.141.5","sourceSchema":"ablation/1","provenanceRef":"prov-abl"},
 {"componentId":"explain","kind":"explanation-artifact","section":"explainability","ref":"xai:1","sha256":"6"*64,"sourceRelease":"0.141.6","sourceSchema":"xai/1","provenanceRef":"prov-xai"},
 {"componentId":"embed","kind":"embedding-artifact","section":"embeddings","ref":"emb:1","sha256":"7"*64,"sourceRelease":"0.141.7","sourceSchema":"emb/1","provenanceRef":"prov-emb"},
 {"componentId":"seed","kind":"seed-record","section":"provenance-lineage","ref":"seed:1","sha256":"8"*64,"sourceRelease":"0.141.1","sourceSchema":"seed/1","provenanceRef":"prov-seed"},
]
P={"packageId":"pkg-1","title":"Neural study package","projectRef":"proj-1","researchContext":{"question":"Does the model learn the target under this design?"},"components":C,
   "environment":{"runtime":"python","runtimeVersion":"3.12","dependencies":["torch==x"],"os":"linux"},
   "determinism":{"seeds":{"python":7,"torch":7},"controls":{"deterministicAlgorithms":True}},
   "limitations":["Single dataset"],"reproductionInstructions":[{"step":1,"action":"restore"},{"step":2,"action":"execute"}],
   "neuralReleaseRefs":{"mlWorkspace":"0.141.0","architecture":"0.141.1","telemetry":"0.141.2","comparison":"0.141.3","hyperparameterStudy":"0.141.4","ablation":"0.141.5","explainability":"0.141.6","embeddings":"0.141.7"}}

def test_health_policy():
    h=m.health(); assert h["version"]=="0.141.8" and h["api_route_count"]==36 and h["reproducibleNeuralResearchPackage"] is True
    p=m.policy(); assert p["labExecutesReproduction"] is False and p["automaticReplicationCertification"] is False

def test_manifest_registry():
    x=m.package_manifest(P)["manifest"]; assert x["packageId"]=="pkg-1" and len(x["components"])==len(C)
    r=m.component_registry(P); assert r["count"]==len(C) and r["automaticScientificInterpretation"] is False

def test_dependency_checksum_lineage_audits():
    assert m.dependency_audit(P)["allComplete"] is True
    c=m.checksum_audit(P); assert c["allHashesDeclared"] is True and c["allDeclaredHashFormatsValid"] is True and c["hashDeclarationIsArtifactVerification"] is False
    assert m.lineage_audit(P)["allComplete"] is True

def test_environment_and_determinism_are_not_guarantees():
    e=m.environment_audit(P); assert e["minimumReproductionMetadataPresent"] is True and e["environmentMatchGuaranteesReproduction"] is False
    d=m.seed_determinism_audit(P); assert d["determinismDeclared"] is True and d["determinismGuaranteed"] is False

def test_neural_chain_audit():
    a=m.neural_chain_audit(P); assert a["allDeclared"] is True and a["allMatching"] is True and a["versionMatchIsScientificValidity"] is False

def test_completeness_is_descriptive_not_validity():
    c=m.completeness_report(P); assert c["complete"] is True and c["descriptiveCompletenessFraction"]==1.0
    assert c["packageCompletenessIsScientificValidity"] is False and c["packageCompletenessIsReproduction"] is False

def test_workspace_handoff_and_rerun_boundaries():
    h=m.workspace_reproduction_handoff(P)["handoff"]; assert h["executionAuthority"]=="workspace" and h["automaticExecution"] is False and h["reproductionCertified"] is False
    r=m.rerun_plan({**P,"rerunPlan":{"learningRate":0.001}})["rerunPlan"]; assert r["overridesRequireNewLineage"] is True and r["rerunResultIsIndependentReplication"] is False

def test_evidence_boundaries_and_handoffs():
    b=m.evidence_boundary_audit(P)["boundaries"]; assert b["embeddingProximityIsRelationship"] is False and b["explanationIsCausalProof"] is False and b["ablationDeltaIsCausalEffect"] is False
    c=m.core_handoff(P)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["scientificValidityCertified"] is False
    r=m.research_os_handoff(P)["handoff"]; assert r["automaticPhaseAdvance"] is False

def test_snapshot_determinism_and_diff():
    a=m.snapshot(P)["snapshot"]; b=m.snapshot(P)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"] and a["snapshotId"]==b["snapshotId"]
    d=m.package_diff({"left":P,"right":P}); assert d["samePackageContent"] is True and d["differenceDoesNotImplyScientificSuperiority"] is True

def test_reproducibility_package_not_certification():
    r=m.reproducibility_package(P); p=r["reproducibilityPackage"]
    assert p["completeByDeclaredMetadata"] is True and p["scientificValidityCertified"] is False and p["reproductionCertified"] is False and p["replicationCertified"] is False
