from __future__ import annotations
import copy, hashlib, json, math
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.8"
PREDECESSOR_VERSION="0.141.7"
EXPLAINABILITY_VERSION="0.141.6"
ABLATION_VERSION="0.141.5"
SEARCH_VERSION="0.141.4"
COMPARISON_VERSION="0.141.3"
TELEMETRY_VERSION="0.141.2"
ARCHITECTURE_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-reproducible-neural-research-package/0.141.8"
MANIFEST_SCHEMA="sc-lab-neural-research-package-manifest/0.141.8"
COMPONENT_SCHEMA="sc-lab-neural-research-package-component/0.141.8"
SNAPSHOT_SCHEMA="sc-lab-neural-research-package-snapshot/0.141.8"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-neural-reproduction-execution-request/1.0"
CORE_HANDOFF_SCHEMA="sc-core-reproducible-neural-research-package-handoff/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-neural-package-handoff/1.0"

BOUNDARY=(
    "A reproducible neural research package records the materials, configuration, lineage, environment, artifacts, and instructions needed to inspect or attempt reproduction. "
    "Package completeness does not certify scientific validity, methodological quality, causal interpretation, model superiority, successful reproduction, or independent replication. "
    "Workspace remains the execution authority for reruns; Platform Core remains the governed canonical-object authority; human review remains required for scientific conclusions."
)

PACKAGE_SECTIONS=(
    "research-context","data-lineage","model-architecture","training-configuration","execution-environment","training-telemetry",
    "checkpoints-artifacts","model-comparison","hyperparameter-study","ablation-study","explainability","embeddings",
    "provenance-lineage","limitations-review","reproduction-instructions","publication-handoff"
)
ARTIFACT_KINDS=(
    "dataset-reference","split-reference","code-reference","environment-lock","container-image","model-spec","training-config",
    "run-record","metric-series","checkpoint","model-artifact","comparison-matrix","search-study","ablation-result","explanation-artifact",
    "embedding-artifact","visualization","log","seed-record","provenance-record","review-record","publication-object","other"
)
VERIFICATION_STATES=("unverified","declared","hash-verified","runtime-verified","independently-reproduced","independently-replicated")
COMPLETENESS_DIMENSIONS=(
    "identity","research-context","data","code","architecture","training-config","environment","seeds","execution-lineage",
    "metrics","checkpoints","comparisons","search","ablations","explainability","embeddings","limitations","instructions"
)


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=4096): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _num(v):
    if isinstance(v,bool): return None
    if isinstance(v,(int,float)) and math.isfinite(float(v)): return float(v)
    try:
        x=float(v); return x if math.isfinite(x) else None
    except Exception: return None

def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default

def _uniq(xs):
    out=[]; seen=set()
    for x in xs:
        k=_canon(x)
        if k not in seen: seen.add(k); out.append(x)
    return out

def normalize_component(item:Any,index:int=0):
    raw=item if isinstance(item,dict) else {"ref":item}
    kind=_txt(_get(raw,"kind","artifactKind","componentKind"),128).lower() or "other"
    if kind not in ARTIFACT_KINDS: kind="other"
    state=_txt(_get(raw,"verificationState","verification"),64).lower() or "declared"
    if state not in VERIFICATION_STATES: state="declared"
    checksum=_txt(_get(raw,"sha256","checksum","contentHash"),256).lower()
    if checksum.startswith("sha256:"): checksum=checksum.split(":",1)[1]
    rec={
        "schema":COMPONENT_SCHEMA,"version":VERSION,"componentId":_txt(_get(raw,"componentId","id"),512) or f"component-{index+1}",
        "kind":kind,"section":_txt(raw.get("section"),128),"label":_txt(raw.get("label"),512),
        "ref":_txt(_get(raw,"ref","artifactRef","objectRef","uri"),2048),"sha256":checksum,
        "sourceRelease":_txt(raw.get("sourceRelease"),128),"sourceSchema":_txt(raw.get("sourceSchema"),512),
        "producer":_txt(raw.get("producer"),256),"environmentRef":_txt(raw.get("environmentRef"),1024),
        "runRef":_txt(raw.get("runRef"),1024),"experimentRef":_txt(raw.get("experimentRef"),1024),
        "datasetRef":_txt(raw.get("datasetRef"),1024),"splitRef":_txt(raw.get("splitRef"),1024),
        "modelRef":_txt(raw.get("modelRef"),1024),"checkpointRef":_txt(raw.get("checkpointRef"),1024),
        "provenanceRef":_txt(raw.get("provenanceRef"),1024),"dependsOn":[_txt(x,512) for x in _list(raw.get("dependsOn")) if _txt(x,512)],
        "verificationState":state,"metadata":_dict(raw.get("metadata")),
        "scientificValidityCertified":False,"reproductionCertified":state in ("independently-reproduced","independently-replicated"),
        "replicationCertified":state=="independently-replicated",
    }
    if rec["section"] not in PACKAGE_SECTIONS: rec["section"]="provenance-lineage"
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return rec

def package_manifest(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    package_id=_txt(_get(root,"packageId","id"),512) or f"neural-package-{_fp(root)[:16]}"
    identity=_dict(root.get("identity")); context=_dict(_get(root,"researchContext","context",default={}))
    components=[normalize_component(x,i) for i,x in enumerate(_list(_get(root,"components","artifacts",default=[])))]
    sections={s:[] for s in PACKAGE_SECTIONS}
    for c in components: sections[c["section"]].append(c["componentId"])
    rec={
        "schema":MANIFEST_SCHEMA,"version":VERSION,"recordType":"reproducible-neural-research-package-manifest",
        "packageId":package_id,"title":_txt(root.get("title"),512) or "Reproducible neural research package",
        "identity":identity,"researchContext":context,"experimentRef":_txt(root.get("experimentRef"),1024),
        "projectRef":_txt(root.get("projectRef"),1024),"studyRef":_txt(root.get("studyRef"),1024),
        "components":components,"sections":sections,"limitations":_list(root.get("limitations")),"review":_dict(root.get("review")),
        "publication":_dict(root.get("publication")),"createdBy":_txt(root.get("createdBy"),512),
        "workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"humanScientificReviewRequired":True,
        "packageCompletenessIsScientificValidity":False,"packageCompletenessIsReproduction":False,"packageCompletenessIsReplication":False,
        "predictionIsEvidence":False,"embeddingProximityIsRelationship":False,"explanationIsCausalProof":False,"ablationDeltaIsCausalEffect":False,
        "boundary":BOUNDARY,
    }
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"manifest":rec,"boundary":BOUNDARY}

def component_registry(payload:dict):
    m=package_manifest(payload)["manifest"]
    rows=[]
    for c in m["components"]:
        rows.append({k:c.get(k) for k in ("componentId","kind","section","ref","sha256","sourceRelease","sourceSchema","verificationState","runRef","datasetRef","modelRef","checkpointRef","provenanceRef")})
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"automaticScientificInterpretation":False,"boundary":BOUNDARY}

def section_inventory(payload:dict):
    m=package_manifest(payload)["manifest"]
    rows=[{"section":s,"componentCount":len(m["sections"].get(s,[])),"componentIds":m["sections"].get(s,[])} for s in PACKAGE_SECTIONS]
    return {"ok":True,"version":VERSION,"rows":rows,"boundary":BOUNDARY}

def dependency_audit(payload:dict):
    m=package_manifest(payload)["manifest"]; ids={c["componentId"] for c in m["components"]}; rows=[]
    for c in m["components"]:
        missing=[d for d in c["dependsOn"] if d not in ids]
        rows.append({"componentId":c["componentId"],"dependencyCount":len(c["dependsOn"]),"missingDependencies":missing,"complete":not missing})
    return {"ok":True,"version":VERSION,"rows":rows,"allComplete":all(r["complete"] for r in rows),"boundary":BOUNDARY}

def checksum_audit(payload:dict):
    m=package_manifest(payload)["manifest"]; rows=[]
    for c in m["components"]:
        h=c.get("sha256",""); valid=(len(h)==64 and all(ch in "0123456789abcdef" for ch in h)) if h else False
        rows.append({"componentId":c["componentId"],"sha256Declared":bool(h),"sha256FormatValid":valid,"verificationState":c["verificationState"]})
    return {"ok":True,"version":VERSION,"rows":rows,"allHashesDeclared":bool(rows) and all(r["sha256Declared"] for r in rows),
            "allDeclaredHashFormatsValid":all((not r["sha256Declared"]) or r["sha256FormatValid"] for r in rows),"hashDeclarationIsArtifactVerification":False,"boundary":BOUNDARY}

def lineage_audit(payload:dict):
    m=package_manifest(payload)["manifest"]; rows=[]
    for c in m["components"]:
        missing=[k for k in ("sourceRelease","sourceSchema","provenanceRef") if not c.get(k)]
        rows.append({"componentId":c["componentId"],"complete":not missing,"missing":missing,"sourceRelease":c.get("sourceRelease"),"sourceSchema":c.get("sourceSchema")})
    return {"ok":True,"version":VERSION,"rows":rows,"allComplete":all(r["complete"] for r in rows),"lineageCompletenessIsScientificValidity":False,"boundary":BOUNDARY}

def environment_audit(payload:dict):
    root=payload if isinstance(payload,dict) else {}; m=package_manifest(root)["manifest"]
    env=_dict(_get(root,"environment","executionEnvironment",default={}))
    refs=sorted({c["environmentRef"] for c in m["components"] if c.get("environmentRef")})
    fields={k:bool(_get(env,k)) for k in ("runtime","runtimeVersion","os","architecture","dependencies","containerDigest","hardware","accelerator")}
    required=("runtime","runtimeVersion","dependencies")
    return {"ok":True,"version":VERSION,"environment":env,"componentEnvironmentRefs":refs,"fields":fields,
            "minimumReproductionMetadataPresent":all(fields[x] for x in required),"environmentMatchGuaranteesReproduction":False,"boundary":BOUNDARY}

def seed_determinism_audit(payload:dict):
    root=payload if isinstance(payload,dict) else {}; d=_dict(_get(root,"determinism","seedConfiguration",default={}))
    seeds=_dict(d.get("seeds")); controls=_dict(d.get("controls"))
    return {"ok":True,"version":VERSION,"seeds":seeds,"controls":controls,"seedCount":len(seeds),
            "determinismDeclared":bool(d),"determinismGuaranteed":False,"sameSeedGuaranteesSameResult":False,"boundary":BOUNDARY}

def neural_chain_audit(payload:dict):
    root=payload if isinstance(payload,dict) else {}; refs=_dict(_get(root,"neuralReleaseRefs","releaseRefs",default={}))
    expected={
        "mlWorkspace":ML_WORKSPACE_VERSION,"architecture":ARCHITECTURE_VERSION,"telemetry":TELEMETRY_VERSION,"comparison":COMPARISON_VERSION,
        "hyperparameterStudy":SEARCH_VERSION,"ablation":ABLATION_VERSION,"explainability":EXPLAINABILITY_VERSION,"embeddings":PREDECESSOR_VERSION,
    }
    rows=[]
    for name,version in expected.items():
        declared=_txt(refs.get(name),128); rows.append({"component":name,"expectedVersion":version,"declaredVersion":declared,"matches":declared==version if declared else False})
    return {"ok":True,"version":VERSION,"rows":rows,"allDeclared":all(bool(r["declaredVersion"]) for r in rows),
            "allMatching":all(r["matches"] for r in rows),"versionMatchIsScientificValidity":False,"boundary":BOUNDARY}

def completeness_report(payload:dict):
    root=payload if isinstance(payload,dict) else {}; m=package_manifest(root)["manifest"]
    components=m["components"]; kinds={c["kind"] for c in components}; sections={c["section"] for c in components}
    env=environment_audit(root); det=seed_determinism_audit(root)
    rules={
        "identity":bool(m["packageId"] and m["title"]),
        "research-context":bool(m["researchContext"] or m["studyRef"] or m["projectRef"]),
        "data":bool(kinds & {"dataset-reference","split-reference"}),
        "code":"code-reference" in kinds,
        "architecture":"model-spec" in kinds,
        "training-config":"training-config" in kinds,
        "environment":env["minimumReproductionMetadataPresent"] or "environment-lock" in kinds or "container-image" in kinds,
        "seeds":det["determinismDeclared"] or "seed-record" in kinds,
        "execution-lineage":bool(kinds & {"run-record","provenance-record"}),
        "metrics":"metric-series" in kinds,
        "checkpoints":bool(kinds & {"checkpoint","model-artifact"}),
        "comparisons":"model-comparison" in sections or "comparison-matrix" in kinds,
        "search":"hyperparameter-study" in sections or "search-study" in kinds,
        "ablations":"ablation-study" in sections or "ablation-result" in kinds,
        "explainability":"explainability" in sections or "explanation-artifact" in kinds,
        "embeddings":"embeddings" in sections or "embedding-artifact" in kinds,
        "limitations":bool(m["limitations"]),
        "instructions":bool(_list(root.get("reproductionInstructions")) or _dict(root.get("rerunPlan"))),
    }
    missing=[k for k in COMPLETENESS_DIMENSIONS if not rules.get(k,False)]
    score=sum(1 for k in COMPLETENESS_DIMENSIONS if rules.get(k,False))/len(COMPLETENESS_DIMENSIONS)
    return {"ok":True,"version":VERSION,"dimensions":rules,"complete":not missing,"missing":missing,"descriptiveCompletenessFraction":score,
            "packageCompletenessIsScientificValidity":False,"packageCompletenessIsReproduction":False,"packageCompletenessIsReplication":False,"boundary":BOUNDARY}

def missingness_report(payload:dict):
    c=completeness_report(payload); deps=dependency_audit(payload); lineage=lineage_audit(payload); checks=checksum_audit(payload)
    return {"ok":True,"version":VERSION,"missingCompletenessDimensions":c["missing"],
            "componentsWithMissingDependencies":[r["componentId"] for r in deps["rows"] if not r["complete"]],
            "componentsWithIncompleteLineage":[r["componentId"] for r in lineage["rows"] if not r["complete"]],
            "componentsWithoutDeclaredHash":[r["componentId"] for r in checks["rows"] if not r["sha256Declared"]],
            "scientificValidityInferred":False,"boundary":BOUNDARY}

def reproducibility_instructions(payload:dict):
    root=payload if isinstance(payload,dict) else {}; m=package_manifest(root)["manifest"]
    provided=_list(root.get("reproductionInstructions"))
    steps=provided or [
        {"step":1,"action":"materialize-versioned-inputs","authority":"workspace","requiresHumanReview":True},
        {"step":2,"action":"restore-code-and-environment","authority":"workspace","requiresHumanReview":True},
        {"step":3,"action":"restore-training-configuration-and-seeds","authority":"workspace","requiresHumanReview":True},
        {"step":4,"action":"execute-neural-run","authority":"workspace","requiresHumanReview":True},
        {"step":5,"action":"compare-returned-artifact-hashes-and-metrics","authority":"lab","requiresHumanReview":True},
        {"step":6,"action":"record-deviations-limitations-and-review-outcome","authority":"lab","requiresHumanReview":True},
    ]
    return {"ok":True,"version":VERSION,"packageId":m["packageId"],"steps":steps,"automaticExecution":False,
            "successfulExecutionIsScientificReplication":False,"humanReviewRequired":True,"boundary":BOUNDARY}

def workspace_reproduction_handoff(payload:dict):
    m=package_manifest(payload)["manifest"]; instructions=reproducibility_instructions(payload)
    packet={"schema":WORKSPACE_HANDOFF_SCHEMA,"labRelease":VERSION,"packageId":m["packageId"],"packageFingerprint":m["fingerprint"],
            "manifest":m,"instructions":instructions["steps"],"executionAuthority":"workspace","automaticExecution":False,
            "reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False,"humanReviewRequired":True,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def rerun_plan(payload:dict):
    root=payload if isinstance(payload,dict) else {}; h=workspace_reproduction_handoff(root)["handoff"]
    requested=_dict(root.get("rerunPlan")); plan={"packageId":h["packageId"],"workspaceRequest":h,"requestedOverrides":requested,
        "overridesRequireNewLineage":bool(requested),"automaticPromotionOfRerun":False,"rerunResultIsIndependentReplication":False,"boundary":BOUNDARY}
    plan["fingerprint"]=_fp(plan); return {"ok":True,"version":VERSION,"rerunPlan":plan,"boundary":BOUNDARY}

def verification_checklist(payload:dict):
    checks=[
        "package-manifest-fingerprint","component-dependency-audit","component-checksum-audit","lineage-audit","environment-audit",
        "seed-determinism-audit","neural-release-chain-audit","completeness-report","limitations-present","reproduction-instructions-present",
        "rerun-output-comparison","human-scientific-review"
    ]
    return {"ok":True,"version":VERSION,"checks":checks,"automaticCertification":False,"scientificValidityCertified":False,
            "reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}

def evidence_boundary_audit(payload:dict):
    return {"ok":True,"version":VERSION,"boundaries":{
        "predictionIsEvidence":False,"embeddingProximityIsRelationship":False,"explanationIsCausalProof":False,"ablationDeltaIsCausalEffect":False,
        "metricSuperiorityIsScientificSuperiority":False,"packageCompletenessIsScientificValidity":False,"rerunSuccessIsIndependentReplication":False,
        "reproducibilityIsCorrectness":False},"allGuardrailsExplicit":True,"boundary":BOUNDARY}

def package_summary(payload:dict):
    m=package_manifest(payload)["manifest"]; c=completeness_report(payload)
    return {"ok":True,"version":VERSION,"packageId":m["packageId"],"title":m["title"],"componentCount":len(m["components"]),
            "populatedSections":[s for s,ids in m["sections"].items() if ids],"descriptiveCompletenessFraction":c["descriptiveCompletenessFraction"],
            "missingDimensions":c["missing"],"scientificValidityCertified":False,"reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}

def export_manifest(payload:dict):
    m=package_manifest(payload)["manifest"]
    export={"schema":SCHEMA,"version":VERSION,"manifest":m,"summary":package_summary(payload),"completeness":completeness_report(payload),
            "dependencyAudit":dependency_audit(payload),"lineageAudit":lineage_audit(payload),"checksumAudit":checksum_audit(payload),
            "environmentAudit":environment_audit(payload),"determinismAudit":seed_determinism_audit(payload),
            "evidenceBoundaryAudit":evidence_boundary_audit(payload),"reproductionInstructions":reproducibility_instructions(payload),
            "scientificValidityCertified":False,"reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}
    export["fingerprint"]=_fp({k:v for k,v in export.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"exportManifest":export,"boundary":BOUNDARY}

def core_handoff(payload:dict):
    e=export_manifest(payload)["exportManifest"]
    packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"canonicalObjectAuthority":"platform-core","objectType":"reproducible-neural-research-package",
            "packageId":e["manifest"]["packageId"],"packageFingerprint":e["fingerprint"],"manifest":e["manifest"],
            "scientificValidityCertified":False,"reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def research_os_handoff(payload:dict):
    e=export_manifest(payload)["exportManifest"]
    packet={"schema":RESEARCH_OS_HANDOFF_SCHEMA,"labRelease":VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"packageId":e["manifest"]["packageId"],
            "packageFingerprint":e["fingerprint"],"suggestedPhase":"reproduction","automaticPhaseAdvance":False,"publicationAcceptance":False,
            "scientificValidityCertified":False,"humanReviewRequired":True,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def publication_handoff(payload:dict):
    e=export_manifest(payload)["exportManifest"]
    packet={"schema":"sc-lab-neural-research-publication-handoff/0.141.8","version":VERSION,"packageId":e["manifest"]["packageId"],
            "packageFingerprint":e["fingerprint"],"publication":e["manifest"].get("publication",{}),"limitations":e["manifest"].get("limitations",[]),
            "review":e["manifest"].get("review",{}),"publicationReadyCertified":False,"automaticPublication":False,"humanReviewRequired":True,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def snapshot(payload:dict):
    e=export_manifest(payload)["exportManifest"]
    stable=copy.deepcopy(e); stable.pop("createdAt",None)
    fp=_fp(stable)
    rec={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"snapshotId":f"nrp-{fp[:20]}","packageId":e["manifest"]["packageId"],
         "packageFingerprint":e["fingerprint"],"snapshotFingerprint":fp,"exportManifest":e,"scientificValidityCertified":False,
         "reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}
    return {"ok":True,"version":VERSION,"snapshot":rec,"boundary":BOUNDARY}

def compare_snapshots(payload:dict):
    root=payload if isinstance(payload,dict) else {}; left=_dict(root.get("left")); right=_dict(root.get("right"))
    lfp=_txt(_get(left,"snapshotFingerprint","fingerprint"),256); rfp=_txt(_get(right,"snapshotFingerprint","fingerprint"),256)
    return {"ok":True,"version":VERSION,"sameSnapshot":bool(lfp and rfp and lfp==rfp),"leftFingerprint":lfp,"rightFingerprint":rfp,
            "differenceDoesNotImplyScientificInvalidity":True,"boundary":BOUNDARY}

def package_diff(payload:dict):
    root=payload if isinstance(payload,dict) else {}; left=package_manifest(_dict(root.get("left")))["manifest"]; right=package_manifest(_dict(root.get("right")))["manifest"]
    li={c["componentId"]:c for c in left["components"]}; ri={c["componentId"]:c for c in right["components"]}
    added=sorted(set(ri)-set(li)); removed=sorted(set(li)-set(ri)); changed=sorted(k for k in set(li)&set(ri) if li[k]["fingerprint"]!=ri[k]["fingerprint"])
    return {"ok":True,"version":VERSION,"added":added,"removed":removed,"changed":changed,"samePackageContent":not (added or removed or changed),
            "differenceDoesNotImplyScientificSuperiority":True,"boundary":BOUNDARY}

def reproducibility_package(payload:dict):
    e=export_manifest(payload)["exportManifest"]; c=e["completeness"]
    packet={"schema":SCHEMA,"version":VERSION,"packageId":e["manifest"]["packageId"],"manifest":e["manifest"],"exportManifest":e,
            "workspaceReproductionHandoff":workspace_reproduction_handoff(payload)["handoff"],"coreHandoff":core_handoff(payload)["handoff"],
            "researchOSHandoff":research_os_handoff(payload)["handoff"],"verificationChecklist":verification_checklist(payload)["checks"],
            "completeByDeclaredMetadata":c["complete"],"scientificValidityCertified":False,"reproductionCertified":False,"replicationCertified":False,
            "publicationAccepted":False,"humanReviewRequired":True,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"reproducibilityPackage":packet,"packageCompletenessIsScientificValidity":False,
            "packageCompletenessIsReproduction":False,"packageCompletenessIsReplication":False,"boundary":BOUNDARY}

def interpretation_boundary(payload=None):
    return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"packageCompletenessIsScientificValidity":False,"packageCompletenessIsReproduction":False,
            "packageCompletenessIsReplication":False,"rerunSuccessIsIndependentReplication":False,"predictionIsEvidence":False,
            "embeddingProximityIsRelationship":False,"explanationIsCausalProof":False,"ablationDeltaIsCausalEffect":False}

def policy():
    return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"humanScientificReviewRequired":True,
            "labExecutesTraining":False,"labExecutesReproduction":False,"automaticScientificValidity":False,"automaticReproductionCertification":False,
            "automaticReplicationCertification":False,"automaticPublicationAcceptance":False,"packageCompletenessIsScientificValidity":False,
            "predictionIsEvidence":False,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"manifestSchema":MANIFEST_SCHEMA,"componentSchema":COMPONENT_SCHEMA,"snapshotSchema":SNAPSHOT_SCHEMA,
            "workspaceHandoffSchema":WORKSPACE_HANDOFF_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"researchOSHandoffSchema":RESEARCH_OS_HANDOFF_SCHEMA,
            "packageSections":list(PACKAGE_SECTIONS),"artifactKinds":list(ARTIFACT_KINDS),"verificationStates":list(VERIFICATION_STATES),
            "completenessDimensions":list(COMPLETENESS_DIMENSIONS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":[
        "installed-runtime-integrity-policy-retained","v0.141.7-embedding-line-retained","all-neural-package-components-versioned",
        "component-dependencies-auditable","component-checksums-declarable","lineage-auditable","environment-metadata-auditable",
        "seed-determinism-metadata-auditable","neural-release-chain-auditable","package-completeness-separate-from-validity",
        "workspace-reproduction-authority-explicit","platform-core-canonical-authority-explicit","human-review-required",
        "no-automatic-reproduction-certification","no-automatic-replication-certification","deterministic-package-snapshot"
    ],"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"api_route_count":36,"reproducibleNeuralResearchPackage":True,"embeddingExplorerVersion":PREDECESSOR_VERSION,
            "neuralExplainabilityWorkspaceVersion":EXPLAINABILITY_VERSION,"ablationStudyFrameworkVersion":ABLATION_VERSION,
            "hyperparameterStudySearchResultsVersion":SEARCH_VERSION,"modelComparisonExperimentMatrixVersion":COMPARISON_VERSION,
            "trainingCurvesMetricsCheckpointVisualizationVersion":TELEMETRY_VERSION,"neuralArchitectureTrainingConfigurationVersion":ARCHITECTURE_VERSION,
            "machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,
            "manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,
            "labExecutesTraining":False,"labExecutesReproduction":False,"automaticScientificValidity":False,"automaticReproductionCertification":False,
            "automaticReplicationCertification":False,"packageCompletenessIsScientificValidity":False,"predictionIsEvidence":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"api_route_count":36,"packageManifest":True,"componentRegistry":True,"sectionInventory":True,
            "dependencyAudit":True,"checksumAudit":True,"lineageAudit":True,"environmentAudit":True,"seedDeterminismAudit":True,"neuralChainAudit":True,
            "completenessReport":True,"missingnessReport":True,"reproductionInstructions":True,"workspaceReproductionHandoff":True,"rerunPlan":True,
            "verificationChecklist":True,"evidenceBoundaryAudit":True,"exportManifest":True,"coreHandoff":True,"researchOSHandoff":True,
            "publicationHandoff":True,"deterministicSnapshots":True,"packageDiff":True,"reproducibilityPackage":True,
            "packageCompletenessIsScientificValidity":False,"reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}
