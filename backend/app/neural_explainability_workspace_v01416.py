from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.6"
PREDECESSOR_VERSION="0.141.5"
SEARCH_VERSION="0.141.4"
COMPARISON_VERSION="0.141.3"
TELEMETRY_VERSION="0.141.2"
ARCHITECTURE_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-neural-explainability-workspace/0.141.6"
STUDY_SCHEMA="sc-lab-neural-explainability-study/0.141.6"
EXPLANATION_SCHEMA="sc-lab-neural-explanation-result/0.141.6"
SNAPSHOT_SCHEMA="sc-lab-neural-explainability-snapshot/0.141.6"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-neural-explanation-execution-handoff/1.0"
CORE_HANDOFF_SCHEMA="sc-core-neural-explanation-visual-object-handoff/1.0"

BOUNDARY=(
    "Lab structures, compares, visualizes, and audits neural explanation results but does not execute model training, "
    "treat attribution as causation or mechanism, certify an explanation method as faithful, convert saliency or attention into evidence, "
    "or automatically endorse a model. Explanation outputs are method-dependent analytical objects requiring human interpretation."
)
METHOD_FAMILIES=("gradient","integrated-gradients","saliency","grad-cam","occlusion","perturbation","shap","lime","attention","activation","counterfactual","other")
SCOPES=("global","local","layer","feature","token","spatial","temporal","example")
VIEWS=("feature-attribution","saliency-map","activation-map","token-attribution","method-comparison","stability-summary","agreement-matrix","provenance-matrix")


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

def normalize_method(item:Any,index:int=0):
    raw=item if isinstance(item,dict) else {"method":item}
    family=_txt(_get(raw,"family","method","name"),128).lower() or "other"
    if family not in METHOD_FAMILIES: family="other"
    rec={"methodId":_txt(_get(raw,"methodId","id"),256) or f"method-{index+1}","family":family,
         "implementation":_txt(_get(raw,"implementation","implementationRef"),512),"version":_txt(raw.get("version"),128),
         "configuration":_dict(_get(raw,"configuration","parameters",default={})),"scope":_txt(raw.get("scope"),64).lower() or "local",
         "baselinePolicy":_dict(_get(raw,"baselinePolicy","referencePolicy",default={})),"provenance":_dict(raw.get("provenance"))}
    if rec["scope"] not in SCOPES: rec["scope"]="local"
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return rec

def study_spec(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    methods=[normalize_method(x,i) for i,x in enumerate(_list(_get(root,"methods","explanationMethods",default=[])))]
    rec={"schema":STUDY_SCHEMA,"version":VERSION,"recordType":"neural-explainability-study","studyId":_txt(_get(root,"studyId","id"),512) or f"xai-{_fp(methods)[:16]}",
         "title":_txt(root.get("title"),512) or "Neural explainability study","experimentId":_txt(root.get("experimentId"),512),
         "modelRef":_txt(root.get("modelRef"),1024),"checkpointRef":_txt(root.get("checkpointRef"),1024),"datasetRef":_txt(root.get("datasetRef"),1024),
         "splitRef":_txt(root.get("splitRef"),1024),"targetRef":_txt(_get(root,"targetRef","outputRef"),1024),"inputSetRef":_txt(root.get("inputSetRef"),1024),
         "architectureRef":_txt(root.get("architectureRef"),1024),"trainingConfigurationRef":_txt(root.get("trainingConfigurationRef"),1024),
         "environmentRef":_txt(root.get("environmentRef"),1024),"methods":methods,"referenceInputs":_list(_get(root,"referenceInputs","baselines",default=[])),
         "workspaceExecutionAuthority":True,"labExecutesExplanationCompute":False,"causalMechanismInferred":False,"explanationFaithfulnessCertified":False,
         "automaticModelEndorsement":False,"explanationIsEvidence":False,"boundary":BOUNDARY}
    issues=[]
    for k in ("modelRef","checkpointRef","datasetRef","splitRef","targetRef"):
        if not rec.get(k): issues.append(f"missing-{k}")
    if not methods: issues.append("no-explanation-methods")
    rec["issues"]=issues; rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"study":rec,"readyForWorkspaceHandoff":not issues,"boundary":BOUNDARY}

def workspace_handoff(payload:dict):
    s=study_spec(payload)
    packet={"schema":WORKSPACE_HANDOFF_SCHEMA,"labRelease":VERSION,"study":s["study"],"executionAuthority":"workspace","labExecutesExplanationCompute":False,
            "ready":s["readyForWorkspaceHandoff"],"causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"automaticModelEndorsement":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def normalize_explanation(item:Any,index:int=0,study=None):
    raw=item if isinstance(item,dict) else {"explanationId":item}; study=study or {}
    method=normalize_method(_get(raw,"method","explanationMethod",default={}),index)
    values=[]
    src=_get(raw,"attributions","values","scores",default=[])
    if isinstance(src,dict):
        values=[{"feature":_txt(k,512),"value":_num(v)} for k,v in src.items()]
    elif isinstance(src,list):
        for j,x in enumerate(src):
            if isinstance(x,dict): values.append({"feature":_txt(_get(x,"feature","name","token","region"),512) or f"feature-{j+1}","value":_num(_get(x,"value","score")),"metadata":_dict(x.get("metadata"))})
            else: values.append({"feature":f"feature-{j+1}","value":_num(x)})
    rec={"schema":EXPLANATION_SCHEMA,"version":VERSION,"explanationId":_txt(_get(raw,"explanationId","id"),512) or f"explanation-{index+1}",
         "method":method,"inputRef":_txt(raw.get("inputRef"),1024),"referenceInputRef":_txt(_get(raw,"referenceInputRef","baselineRef"),1024),
         "targetRef":_txt(_get(raw,"targetRef","outputRef"),1024) or study.get("targetRef","") ,"layerRef":_txt(raw.get("layerRef"),1024),
         "scope":_txt(raw.get("scope"),64).lower() or method["scope"],"attributions":values,"rawArtifactRef":_txt(raw.get("rawArtifactRef"),1024),
         "runId":_txt(raw.get("runId"),512),"modelRef":_txt(raw.get("modelRef"),1024) or study.get("modelRef",""),
         "checkpointRef":_txt(raw.get("checkpointRef"),1024) or study.get("checkpointRef",""),"datasetRef":_txt(raw.get("datasetRef"),1024) or study.get("datasetRef",""),
         "splitRef":_txt(raw.get("splitRef"),1024) or study.get("splitRef",""),"environmentRef":_txt(raw.get("environmentRef"),1024) or study.get("environmentRef",""),
         "provenanceRef":_txt(raw.get("provenanceRef"),1024),"diagnostics":_dict(raw.get("diagnostics")),"metadata":_dict(raw.get("metadata")),
         "causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"explanationIsEvidence":False}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return rec

def normalize_results(payload:dict):
    root=payload if isinstance(payload,dict) else {}; s=study_spec(root)["study"]
    items=_list(_get(root,"explanations","results","explanationResults",default=[])); ex=[normalize_explanation(x,i,s) for i,x in enumerate(items)]
    rec={"schema":"sc-lab-neural-explainability-results/0.141.6","version":VERSION,"studyId":s["studyId"],"studyFingerprint":s["fingerprint"],"explanations":ex,
         "workspaceExecutionAuthority":True,"causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"automaticModelEndorsement":False,"explanationIsEvidence":False,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"results":rec,"boundary":BOUNDARY}

def explanation_registry(payload):
    xs=normalize_results(payload)["results"]["explanations"]
    rows=[{"explanationId":x["explanationId"],"methodId":x["method"]["methodId"],"family":x["method"]["family"],"scope":x["scope"],"inputRef":x["inputRef"],"targetRef":x["targetRef"],"layerRef":x["layerRef"],"runId":x["runId"],"provenanceRef":x["provenanceRef"]} for x in xs]
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"automaticRanking":False,"boundary":BOUNDARY}

def baseline_reference_audit(payload):
    xs=normalize_results(payload)["results"]["explanations"]; rows=[]
    for x in xs:
        fam=x["method"]["family"]; needs=fam in ("integrated-gradients","occlusion","perturbation","shap","lime","counterfactual")
        has=bool(x["referenceInputRef"] or x["method"].get("baselinePolicy"))
        rows.append({"explanationId":x["explanationId"],"family":fam,"referenceRecommended":needs,"referenceDeclared":has,"reviewRequired":bool(needs and not has)})
    return {"ok":True,"version":VERSION,"rows":rows,"allRequiredReferencesDeclared":all(not r["reviewRequired"] for r in rows),"boundary":BOUNDARY}

def provenance_audit(payload):
    xs=normalize_results(payload)["results"]["explanations"]; rows=[]
    for x in xs:
        missing=[k for k in ("modelRef","checkpointRef","datasetRef","splitRef","targetRef","environmentRef") if not x.get(k)]
        rows.append({"explanationId":x["explanationId"],"complete":not missing,"missing":missing,"provenanceRef":x["provenanceRef"]})
    return {"ok":True,"version":VERSION,"rows":rows,"allComplete":all(r["complete"] for r in rows),"boundary":BOUNDARY}

def feature_attribution_matrix(payload):
    xs=normalize_results(payload)["results"]["explanations"]
    feats=sorted({a["feature"] for x in xs for a in x["attributions"] if a.get("feature")})
    rows=[]
    for x in xs:
        vals={a["feature"]:a.get("value") for a in x["attributions"]}; rows.append({"explanationId":x["explanationId"],"methodId":x["method"]["methodId"],"family":x["method"]["family"],"values":{f:vals.get(f) for f in feats}})
    return {"ok":True,"version":VERSION,"matrix":{"features":feats,"rows":rows,"ordering":"lexical-feature-id","automaticImportanceRanking":False},"boundary":BOUNDARY}

def attribution_summary(payload):
    xs=normalize_results(payload)["results"]["explanations"]; rows=[]
    for x in xs:
        vals=[a["value"] for a in x["attributions"] if a.get("value") is not None]
        rows.append({"explanationId":x["explanationId"],"methodId":x["method"]["methodId"],"n":len(vals),"mean":statistics.fmean(vals) if vals else None,
                     "meanAbsolute":statistics.fmean([abs(v) for v in vals]) if vals else None,"min":min(vals) if vals else None,"max":max(vals) if vals else None,
                     "causalMechanismInferred":False})
    return {"ok":True,"version":VERSION,"rows":rows,"descriptiveOnly":True,"boundary":BOUNDARY}

def _vector(x,features):
    d={a["feature"]:a.get("value") for a in x.get("attributions",[])}; return [d.get(f) for f in features]

def method_agreement(payload):
    xs=normalize_results(payload)["results"]["explanations"]; features=sorted({a["feature"] for x in xs for a in x["attributions"]}); rows=[]
    for i,a in enumerate(xs):
        for b in xs[i+1:]:
            va,vb=_vector(a,features),_vector(b,features); pairs=[(x,y) for x,y in zip(va,vb) if x is not None and y is not None]
            if len(pairs)>=2:
                xa=[p[0] for p in pairs]; xb=[p[1] for p in pairs]; ma=statistics.fmean(xa); mb=statistics.fmean(xb)
                num=sum((x-ma)*(y-mb) for x,y in pairs); den=(sum((x-ma)**2 for x in xa)*sum((y-mb)**2 for y in xb))**0.5
                corr=num/den if den else None
            else: corr=None
            rows.append({"left":a["explanationId"],"right":b["explanationId"],"sharedFeatureCount":len(pairs),"pearson":corr,"agreementIsReliabilityCertification":False})
    return {"ok":True,"version":VERSION,"features":features,"rows":rows,"explanationFaithfulnessCertified":False,"boundary":BOUNDARY}

def stability_audit(payload):
    root=payload if isinstance(payload,dict) else {}; xs=normalize_results(root)["results"]["explanations"]; group_key=_txt(root.get("groupBy"),64) or "methodId"; groups={}
    for x in xs:
        key=x["method"]["methodId"] if group_key=="methodId" else (x.get(group_key) or x["method"]["methodId"]); groups.setdefault(key,[]).append(x)
    rows=[]
    for key,g in sorted(groups.items()):
        feats=sorted({a["feature"] for x in g for a in x["attributions"]}); feature_stats={}
        for f in feats:
            vals=[]
            for x in g:
                for a in x["attributions"]:
                    if a["feature"]==f and a.get("value") is not None: vals.append(a["value"])
            feature_stats[f]={"n":len(vals),"mean":statistics.fmean(vals) if vals else None,"stdev":statistics.stdev(vals) if len(vals)>1 else None}
        rows.append({"group":key,"explanationCount":len(g),"featureStats":feature_stats,"stableCertified":False})
    return {"ok":True,"version":VERSION,"rows":rows,"stabilityCertified":False,"boundary":BOUNDARY}

def diagnostic_registry(payload):
    xs=normalize_results(payload)["results"]["explanations"]; rows=[]
    for x in xs:
        rows.append({"explanationId":x["explanationId"],"methodId":x["method"]["methodId"],"diagnostics":x["diagnostics"],"diagnosticsObserved":bool(x["diagnostics"]),"faithfulnessCertified":False})
    return {"ok":True,"version":VERSION,"rows":rows,"boundary":BOUNDARY}

def local_explanation_comparison(payload):
    root=payload if isinstance(payload,dict) else {}; input_ref=_txt(root.get("inputRef"),1024); xs=normalize_results(root)["results"]["explanations"]
    if input_ref: xs=[x for x in xs if x["inputRef"]==input_ref]
    return {"ok":True,"version":VERSION,"inputRef":input_ref,"explanations":xs,"methodAgreement":method_agreement({**root,"explanations":xs}),"automaticConsensus":False,"boundary":BOUNDARY}

def visual_spec(payload):
    root=payload if isinstance(payload,dict) else {}; view=_txt(root.get("view"),64).lower() or "feature-attribution"; view=view if view in VIEWS else "feature-attribution"
    if view in ("feature-attribution","token-attribution","saliency-map","activation-map"): data=feature_attribution_matrix(root)
    elif view=="method-comparison": data=local_explanation_comparison(root)
    elif view=="stability-summary": data=stability_audit(root)
    elif view=="agreement-matrix": data=method_agreement(root)
    else: data=provenance_audit(root)
    spec={"schema":"sc-lab-neural-explainability-visual-spec/0.141.6","version":VERSION,"view":view,"data":data,"rawValuesPreserved":True,"derivedTransformMustBeLabeled":True,
          "causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"automaticConsensus":False,"explanationIsEvidence":False,"boundary":BOUNDARY}
    spec["fingerprint"]=_fp({k:v for k,v in spec.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def core_visual_handoff(payload):
    v=visual_spec(payload)["visualSpec"]; packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"objectType":"NeuralExplanationVisualObject","visualSpec":v,
        "canonicalVisualObjectAuthority":"platform-core","causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"explanationIsEvidence":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def export_bundle(payload):
    r=normalize_results(payload)["results"]; bundle={"schema":"sc-lab-neural-explainability-export/0.141.6","version":VERSION,"results":r,
        "referenceAudit":baseline_reference_audit(payload),"provenanceAudit":provenance_audit(payload),"attributionMatrix":feature_attribution_matrix(payload),
        "agreement":method_agreement(payload),"stability":stability_audit(payload),"causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"explanationIsEvidence":False,"boundary":BOUNDARY}
    bundle["fingerprint"]=_fp({k:v for k,v in bundle.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"bundle":bundle,"boundary":BOUNDARY}

def snapshot(payload):
    stable=export_bundle(payload)["bundle"]; fp=_fp(stable)
    snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"snapshotId":f"xai-snapshot-{fp[:20]}","fingerprint":fp,"content":stable,"createdAt":_now(),"fingerprintExcludesCreatedAt":True}
    return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}

def compare_snapshots(payload):
    root=payload if isinstance(payload,dict) else {}; a=_dict(_get(root,"a","left",default={})); b=_dict(_get(root,"b","right",default={}))
    af=_txt(a.get("fingerprint"),128) or _fp(a.get("content",a)); bf=_txt(b.get("fingerprint"),128) or _fp(b.get("content",b))
    return {"ok":True,"version":VERSION,"same":af==bf,"leftFingerprint":af,"rightFingerprint":bf,"scientificEquivalenceInferred":False,"explanationEquivalenceInferred":False,"boundary":BOUNDARY}

def reproducibility_packet(payload):
    s=snapshot(payload)["snapshot"]; packet={"schema":"sc-lab-neural-explainability-reproducibility-package/0.141.6","version":VERSION,"snapshot":s,
        "requirements":["model/checkpoint lineage","dataset/split lineage","target definition","explanation method/version/configuration","reference or baseline policy when applicable","runtime/environment lineage","raw explanation artifacts","derived visualization transforms"],
        "reproducibilityCertified":False,"scientificValidityCertified":False,"explanationFaithfulnessCertified":False,"causalMechanismCertified":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp({k:v for k,v in packet.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"reproducibilityPacket":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}

def interpretation_boundary(_=None):
    return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"attributionIsCausalEffect":False,"attributionIsMechanism":False,"attentionIsExplanationByDefault":False,
            "saliencyIsEvidence":False,"methodAgreementIsReliabilityCertification":False,"automaticModelEndorsement":False}

def policy():
    return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"labExecutesExplanationCompute":False,"rawExplanationValuesPreserved":True,"derivedTransformsLabeled":True,
            "causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"automaticExplanationRanking":False,"automaticConsensus":False,"automaticModelEndorsement":False,"explanationIsEvidence":False,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"studySchema":STUDY_SCHEMA,"explanationSchema":EXPLANATION_SCHEMA,"workspaceHandoffSchema":WORKSPACE_HANDOFF_SCHEMA,
            "coreHandoffSchema":CORE_HANDOFF_SCHEMA,"methodFamilies":list(METHOD_FAMILIES),"scopes":list(SCOPES),"views":list(VIEWS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":["installed-runtime-integrity-policy-retained","v0.141.5-ablation-line-retained","method-and-version-explicit","reference-policy-audited",
            "raw-values-preserved","derived-transforms-labeled","provenance-audited","no-causal-overclaim","no-faithfulness-certification","no-automatic-model-endorsement","deterministic-snapshot"],"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"api_route_count":31,"neuralExplainabilityWorkspace":True,"ablationStudyFrameworkVersion":PREDECESSOR_VERSION,"hyperparameterStudySearchResultsVersion":SEARCH_VERSION,
            "modelComparisonExperimentMatrixVersion":COMPARISON_VERSION,"trainingCurvesMetricsCheckpointVisualizationVersion":TELEMETRY_VERSION,"neuralArchitectureTrainingConfigurationVersion":ARCHITECTURE_VERSION,
            "machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,
            "workspaceExecutionAuthority":True,"labExecutesExplanationCompute":False,"causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"automaticExplanationRanking":False,
            "automaticConsensus":False,"automaticModelEndorsement":False,"explanationIsEvidence":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"api_route_count":31,"explainabilityStudy":True,"workspaceExecutionHandoff":True,"explanationNormalization":True,"explanationRegistry":True,
            "referenceAudit":True,"provenanceAudit":True,"featureAttributionMatrix":True,"attributionSummary":True,"methodAgreementAudit":True,"stabilityAudit":True,"diagnosticRegistry":True,
            "localExplanationComparison":True,"visualSpecs":True,"coreVisualHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackages":True,
            "causalMechanismInferred":False,"explanationFaithfulnessCertified":False,"automaticModelEndorsement":False,"explanationIsEvidence":False,"boundary":BOUNDARY}
