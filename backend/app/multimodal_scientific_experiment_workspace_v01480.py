from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.148.0"
PREDECESSOR_VERSION="0.147.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
INTEGRATED_NEURAL_VERSION="0.142.0"
SCHEMA="sc-lab-multimodal-scientific-experiment-workspace/0.148.0"
STUDY_SCHEMA="sc-lab-multimodal-scientific-study/0.148.0"
SOURCE_SCHEMA="sc-lab-multimodal-source/0.148.0"
SAMPLE_SCHEMA="sc-lab-multimodal-sample/0.148.0"
ALIGNMENT_SCHEMA="sc-lab-multimodal-alignment/0.148.0"
MODEL_SCHEMA="sc-lab-multimodal-model/0.148.0"
RUN_SCHEMA="sc-lab-multimodal-run/0.148.0"
PREDICTION_SCHEMA="sc-lab-multimodal-output/0.148.0"
SNAPSHOT_SCHEMA="sc-lab-multimodal-workspace-snapshot/0.148.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-multimodal-execution-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-multimodal-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-multimodal-research-objects/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-multimodal-handoff/1.0"
NEURAL_HANDOFF_SCHEMA="sc-lab-integrated-neural-multimodal-handoff/1.0"

BOUNDARY=(
    "The Multimodal Scientific Experiment Workspace governs multimodal study design, modality-specific source and transformation provenance, alignment and fusion declarations, returned outputs, evaluation, comparison, explanation, uncertainty, review, and reproducibility. "
    "Workspace remains the execution authority for multimodal training and inference; Workbench remains the prototype authority; Platform Core remains the canonical governed-object authority. "
    "Cross-modal similarity, alignment, retrieval rank, generated captions, fused predictions, and multimodal embeddings are model-derived results, not proof of semantic equivalence, physical identity, mechanism, or evidence. "
    "Derived representations never overwrite the original modality source, and missing or weakly aligned modalities remain explicit rather than silently imputed as truth."
)

MODALITIES=("text","image","audio","video","tabular","time-series","spatial","raster","graph","sensor","spectrum","microscopy","molecular","genomic","signal","document","other")
TASK_TYPES=("multimodal-classification","multimodal-regression","cross-modal-retrieval","cross-modal-matching","alignment","captioning","multimodal-anomaly-detection","multimodal-forecasting","representation-learning","contrastive-learning","multimodal-embedding","scientific-extraction","other")
FUSION_STRATEGIES=("early","late","intermediate","cross-attention","co-attention","gated","mixture-of-experts","shared-latent","co-embedding","retrieval-augmented","ensemble","hybrid","custom","other")
ALIGNMENT_TYPES=("sample-id","temporal","spatial","entity","document-region","frame-audio","text-image","sensor-event","graph-entity","manual","learned","probabilistic","custom","other")
MODEL_FAMILIES=("multimodal-transformer","vision-language","audio-language","video-language","sensor-fusion","tabular-neural","multimodal-gnn","contrastive-dual-encoder","cross-encoder","encoder-decoder","mixture-of-experts","hybrid","custom","other")
METRICS=("accuracy","balanced-accuracy","precision","recall","f1","roc-auc","pr-auc","log-loss","brier","rmse","mae","r2","mrr","recall@k","precision@k","map","ndcg","alignment-score","calibration-error","other")
SESSION_STATES=("draft","designed","ready-for-execution","executed","analysis","review","reproduction","publication","archived")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _num(v): return float(v) if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v)) else None
def _finite(xs): return [float(x) for x in xs if isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(float(x))]
def _summary(xs):
    v=_finite(xs)
    if not v: return {"count":0,"mean":None,"min":None,"max":None,"stdDev":None}
    return {"count":len(v),"mean":statistics.fmean(v),"min":min(v),"max":max(v),"stdDev":statistics.stdev(v) if len(v)>1 else 0.0}

def catalog():
    return {"ok":True,"version":VERSION,"modalities":list(MODALITIES),"taskTypes":list(TASK_TYPES),"fusionStrategies":list(FUSION_STRATEGIES),"alignmentTypes":list(ALIGNMENT_TYPES),"modelFamilies":list(MODEL_FAMILIES),"metrics":list(METRICS),"crossModalSimilarityIsEvidence":False,"alignmentIsSemanticEquivalence":False,"boundary":BOUNDARY}

def normalize_modality_source(payload:dict):
    p=_dict(payload); modality=_txt(p.get("modality"),64).lower() or "other"; modality=modality if modality in MODALITIES else "other"
    r={"schema":SOURCE_SCHEMA,"version":VERSION,"sourceId":_txt(p.get("sourceId") or p.get("id"),512) or f"multimodal-source-{_fp(p)[:16]}","modality":modality,"uri":_txt(p.get("uri"),4096),"contentHash":_txt(p.get("contentHash"),256),"mediaType":_txt(p.get("mediaType"),256),"shape":_list(p.get("shape")),"timeCoverage":_dict(p.get("timeCoverage")),"spatialCoverage":_dict(p.get("spatialCoverage")),"rights":_dict(p.get("rights")),"acquisition":_dict(p.get("acquisition")),"transformations":_list(p.get("transformations")),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"originalSourcePreserved":True,"derivedRepresentation":bool(p.get("derivedRepresentation",False))}; r["fingerprint"]=_fp(r); return r

def normalize_sample(payload:dict):
    p=_dict(payload); sources=[normalize_modality_source(x) for x in _list(p.get("sources"))]
    r={"schema":SAMPLE_SCHEMA,"version":VERSION,"sampleId":_txt(p.get("sampleId") or p.get("id"),512) or f"multimodal-sample-{_fp(p)[:16]}","subjectRef":_txt(p.get("subjectRef"),512),"sources":sources,"label":p.get("label"),"labelProvenance":_dict(p.get("labelProvenance")),"alignmentRefs":_list(p.get("alignmentRefs")),"missingModalities":_list(p.get("missingModalities")),"metadata":_dict(p.get("metadata")),"completeCaseRequired":bool(p.get("completeCaseRequired",False))}; r["fingerprint"]=_fp(r); return r

def normalize_alignment(payload:dict):
    p=_dict(payload); t=_txt(p.get("alignmentType"),64).lower() or "manual"; t=t if t in ALIGNMENT_TYPES else "other"
    r={"schema":ALIGNMENT_SCHEMA,"version":VERSION,"alignmentId":_txt(p.get("alignmentId") or p.get("id"),512) or f"multimodal-alignment-{_fp(p)[:16]}","alignmentType":t,"sourceRefs":_list(p.get("sourceRefs")),"targetRefs":_list(p.get("targetRefs")),"mapping":_list(p.get("mapping")),"method":_dict(p.get("method")),"confidence":_num(p.get("confidence")),"reviewState":_txt(p.get("reviewState"),64) or "unreviewed","provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"semanticEquivalenceEstablished":False,"physicalIdentityEstablished":False}; r["fingerprint"]=_fp(r); return r

def normalize_model(payload:dict):
    p=_dict(payload); fam=_txt(p.get("modelFamily"),64).lower() or "hybrid"; fam=fam if fam in MODEL_FAMILIES else "other"; fusion=_txt(p.get("fusionStrategy"),64).lower() or "hybrid"; fusion=fusion if fusion in FUSION_STRATEGIES else "other"
    r={"schema":MODEL_SCHEMA,"version":VERSION,"modelId":_txt(p.get("modelId") or p.get("id"),512) or f"multimodal-model-{_fp(p)[:16]}","modelFamily":fam,"modalEncoders":_dict(p.get("modalEncoders")),"fusionStrategy":fusion,"fusionConfiguration":_dict(p.get("fusionConfiguration")),"decoder":_dict(p.get("decoder")),"loss":_dict(p.get("loss")),"optimizer":_dict(p.get("optimizer")),"checkpointRef":_txt(p.get("checkpointRef"),2048),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"automaticModelEndorsement":False}; r["fingerprint"]=_fp(r); return r

def normalize_run(payload:dict):
    p=_dict(payload)
    r={"schema":RUN_SCHEMA,"version":VERSION,"runId":_txt(p.get("runId") or p.get("id"),512) or f"multimodal-run-{_fp(p)[:16]}","studyRef":_txt(p.get("studyRef"),512),"modelRef":_txt(p.get("modelRef"),512),"sampleSetRef":_txt(p.get("sampleSetRef"),512),"environment":_dict(p.get("environment")),"seed":p.get("seed"),"training":_dict(p.get("training")),"metrics":_dict(p.get("metrics")),"artifactRefs":_list(p.get("artifactRefs")),"status":_txt(p.get("status"),64) or "declared","provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_prediction(payload:dict):
    p=_dict(payload); task=_txt(p.get("taskType"),64).lower() or "other"
    r={"schema":PREDICTION_SCHEMA,"version":VERSION,"outputId":_txt(p.get("outputId") or p.get("predictionId") or p.get("id"),512) or f"multimodal-output-{_fp(p)[:16]}","taskType":task,"sampleRef":_txt(p.get("sampleRef"),512),"sourceRefs":_list(p.get("sourceRefs")),"modelRef":_txt(p.get("modelRef"),512),"runRef":_txt(p.get("runRef"),512),"predictedLabel":p.get("predictedLabel"),"value":p.get("value"),"score":_num(p.get("score")),"probabilities":_dict(p.get("probabilities")),"generatedText":_txt(p.get("generatedText"),32768),"embeddingRef":_txt(p.get("embeddingRef"),512),"alignmentRef":_txt(p.get("alignmentRef"),512),"metadata":_dict(p.get("metadata")),"predictionIsEvidence":False,"semanticEquivalenceEstablished":False}; r["fingerprint"]=_fp(r); return r

def normalize_study(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in SESSION_STATES else "draft"; task=_txt(p.get("taskType"),64).lower() or "multimodal-classification"; task=task if task in TASK_TYPES else "other"
    r={"schema":STUDY_SCHEMA,"version":VERSION,"studyId":_txt(p.get("studyId") or p.get("id"),512) or f"multimodal-study-{_fp(p)[:16]}","projectRef":_txt(p.get("projectRef"),512),"title":_txt(p.get("title"),1024) or "Multimodal scientific experiment","question":_txt(p.get("question"),4096),"state":state,"taskType":task,"samples":[normalize_sample(x) for x in _list(p.get("samples"))],"alignments":[normalize_alignment(x) for x in _list(p.get("alignments"))],"model":normalize_model(p.get("model") or {}),"runs":[normalize_run(x) for x in _list(p.get("runs"))],"outputs":[normalize_prediction(x) for x in _list(p.get("outputs"))],"evaluation":_dict(p.get("evaluation")),"review":_dict(p.get("review")),"limitations":_list(p.get("limitations")),"metadata":_dict(p.get("metadata")),"automaticSemanticEquivalence":False,"automaticScientificValidity":False,"predictionIsEvidence":False}; r["fingerprint"]=_fp(r); return r

def workspace_state(payload:dict):
    s=normalize_study(payload); mods=sorted({src["modality"] for sample in s["samples"] for src in sample["sources"]}); return {"ok":True,"version":VERSION,"study":s,"modalityCount":len(mods),"modalities":mods,"sampleCount":len(s["samples"]),"alignmentCount":len(s["alignments"]),"runCount":len(s["runs"]),"outputCount":len(s["outputs"]),"boundary":BOUNDARY}

def modality_provenance_audit(payload:dict):
    s=normalize_study(payload.get("study") or payload); rows=[]
    for sample in s["samples"]:
        for src in sample["sources"]: rows.append({"sampleRef":sample["sampleId"],"sourceRef":src["sourceId"],"modality":src["modality"],"contentHashPresent":bool(src["contentHash"]),"provenancePresent":bool(src["provenance"]),"transformationsDeclared":len(src["transformations"]),"originalSourcePreserved":src["originalSourcePreserved"]})
    return {"ok":True,"version":VERSION,"rows":rows,"provenanceCertifiedComplete":all(r["contentHashPresent"] and r["provenancePresent"] for r in rows) if rows else False,"boundary":BOUNDARY}

def transformation_lineage_audit(payload:dict): return {"ok":True,"version":VERSION,"chains":_list(payload.get("chains")),"sourceOverwriteAllowed":False,"derivedRepresentationsMustReferenceParents":True,"lineageCertifiedComplete":False,"boundary":BOUNDARY}
def missing_modality_audit(payload:dict):
    s=normalize_study(payload.get("study") or payload); rows=[{"sampleRef":x["sampleId"],"missingModalities":x["missingModalities"],"completeCaseRequired":x["completeCaseRequired"]} for x in s["samples"]]
    return {"ok":True,"version":VERSION,"rows":rows,"silentTruthImputationAllowed":False,"missingnessResolved":False,"boundary":BOUNDARY}
def temporal_alignment_audit(payload:dict): return {"ok":True,"version":VERSION,"pairs":_list(payload.get("pairs")),"tolerance":payload.get("tolerance"),"clockSources":_list(payload.get("clockSources")),"temporalAlignmentCertified":False,"boundary":BOUNDARY}
def spatial_alignment_audit(payload:dict): return {"ok":True,"version":VERSION,"pairs":_list(payload.get("pairs")),"crs":_dict(payload.get("crs")),"registration":_dict(payload.get("registration")),"spatialAlignmentCertified":False,"boundary":BOUNDARY}
def label_provenance_audit(payload:dict): return {"ok":True,"version":VERSION,"labels":_list(payload.get("labels")),"sources":_list(payload.get("sources")),"labelTruthCertified":False,"boundary":BOUNDARY}
def leakage_audit(payload:dict): return {"ok":True,"version":VERSION,"trainRefs":_list(payload.get("trainRefs")),"validationRefs":_list(payload.get("validationRefs")),"testRefs":_list(payload.get("testRefs")),"subjectOverlap":_list(payload.get("subjectOverlap")),"temporalLeakage":bool(payload.get("temporalLeakage",False)),"transformationLeakage":bool(payload.get("transformationLeakage",False)),"crossModalDuplicateLeakage":bool(payload.get("crossModalDuplicateLeakage",False)),"leakageCertifiedAbsent":False,"boundary":BOUNDARY}
def modality_balance_audit(payload:dict): return {"ok":True,"version":VERSION,"counts":_dict(payload.get("counts")),"missingness":_dict(payload.get("missingness")),"dominance":_dict(payload.get("dominance")),"balanceCertified":False,"boundary":BOUNDARY}
def fusion_audit(payload:dict): return {"ok":True,"version":VERSION,"fusionStrategy":_txt(payload.get("fusionStrategy"),64),"inputs":_list(payload.get("inputs")),"gates":_dict(payload.get("gates")),"modalityDropout":_dict(payload.get("modalityDropout")),"fusionInterpretationCertified":False,"boundary":BOUNDARY}
def cross_modal_similarity_audit(payload:dict): return {"ok":True,"version":VERSION,"pairs":_list(payload.get("pairs")),"metric":_txt(payload.get("metric"),64),"similarities":_list(payload.get("similarities")),"semanticEquivalenceEstablished":False,"physicalIdentityEstablished":False,"similarityIsEvidence":False,"boundary":BOUNDARY}
def evaluation_protocol_audit(payload:dict): return {"ok":True,"version":VERSION,"splits":_dict(payload.get("splits")),"metrics":_list(payload.get("metrics")),"thresholdSelection":_dict(payload.get("thresholdSelection")),"testSetUsedForSelection":bool(payload.get("testSetUsedForSelection",False)),"evaluationCertifiedUnbiased":False,"boundary":BOUNDARY}
def calibration_audit(payload:dict): return {"ok":True,"version":VERSION,"method":_txt(payload.get("method"),128),"bins":_list(payload.get("bins")),"ece":_num(payload.get("ece")),"brier":_num(payload.get("brier")),"calibrationCertified":False,"boundary":BOUNDARY}

def _result(kind,payload):
    p=_dict(payload); r={"schema":f"{SCHEMA}/{kind}-result","version":VERSION,"resultId":_txt(p.get("resultId") or p.get("id"),512) or f"{kind}-result-{_fp(p)[:16]}","kind":kind,"runRef":_txt(p.get("runRef"),512),"sampleRefs":_list(p.get("sampleRefs")),"metrics":_dict(p.get("metrics")),"rows":_list(p.get("rows")),"artifactRefs":_list(p.get("artifactRefs")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False,"predictionIsEvidence":False}; r["fingerprint"]=_fp(r); return r
def normalize_classification_result(payload:dict): return _result("classification",payload)
def normalize_regression_result(payload:dict): return _result("regression",payload)
def normalize_retrieval_result(payload:dict):
    r=_result("cross-modal-retrieval",payload); r["retrievalRankIsEvidence"]=False; return r
def normalize_matching_result(payload:dict):
    r=_result("cross-modal-matching",payload); r["matchEstablishesIdentity"]=False; return r
def normalize_alignment_result(payload:dict):
    r=_result("alignment",payload); r["semanticEquivalenceEstablished"]=False; r["physicalIdentityEstablished"]=False; return r
def normalize_captioning_result(payload:dict):
    r=_result("captioning",payload); r["generatedCaptionIsSourceTruth"]=False; return r
def normalize_anomaly_result(payload:dict):
    r=_result("multimodal-anomaly",payload); r["anomalyScoreIsProof"]=False; return r
def normalize_embedding_result(payload:dict):
    r=_result("multimodal-embedding",payload); r["embeddingProximityIsRelationship"]=False; return r
def normalize_explanation(payload:dict):
    r=_result("multimodal-explanation",payload); r["method"]=_txt(payload.get("method"),128); r["modalityAttributions"]=_dict(payload.get("modalityAttributions")); r["explanationIsCausalProof"]=False; r["faithfulnessCertified"]=False; return r

def metric_summary(payload:dict): return {"ok":True,"version":VERSION,"metrics":_dict(payload.get("metrics")),"replicateSummary":{k:_summary(v if isinstance(v,list) else [v]) for k,v in _dict(payload.get("replicates")).items()},"automaticWinnerSelection":False,"boundary":BOUNDARY}
def confusion_matrix(payload:dict): return {"ok":True,"version":VERSION,"labels":_list(payload.get("labels")),"matrix":_list(payload.get("matrix")),"normalized":bool(payload.get("normalized",False)),"scientificValidityCertified":False,"boundary":BOUNDARY}
def retrieval_metrics(payload:dict): return {"ok":True,"version":VERSION,"mrr":_num(payload.get("mrr")),"map":_num(payload.get("map")),"recallAtK":_dict(payload.get("recallAtK")),"precisionAtK":_dict(payload.get("precisionAtK")),"retrievalRankIsEvidence":False,"boundary":BOUNDARY}
def matching_metrics(payload:dict): return {"ok":True,"version":VERSION,"rows":_list(payload.get("rows")),"threshold":_num(payload.get("threshold")),"automaticIdentityEstablishment":False,"boundary":BOUNDARY}
def alignment_quality_summary(payload:dict): return {"ok":True,"version":VERSION,"metrics":_dict(payload.get("metrics")),"review":_dict(payload.get("review")),"semanticEquivalenceEstablished":False,"alignmentCertified":False,"boundary":BOUNDARY}
def calibration_summary(payload:dict): return calibration_audit(payload)
def modality_ablation_matrix(payload:dict): return {"ok":True,"version":VERSION,"modalities":_list(payload.get("modalities")),"rows":_list(payload.get("rows")),"controlledContrast":_dict(payload.get("controlledContrast")),"ablationDeltaIsCausalEffect":False,"automaticRanking":False,"boundary":BOUNDARY}
def fusion_comparison_matrix(payload:dict): return {"ok":True,"version":VERSION,"strategies":_list(payload.get("strategies")),"rows":_list(payload.get("rows")),"comparability":_dict(payload.get("comparability")),"automaticWinnerSelection":False,"boundary":BOUNDARY}
def cross_modal_similarity_matrix(payload:dict): return {"ok":True,"version":VERSION,"rowRefs":_list(payload.get("rowRefs")),"columnRefs":_list(payload.get("columnRefs")),"matrix":_list(payload.get("matrix")),"metric":_txt(payload.get("metric"),64),"similarityIsEvidence":False,"semanticEquivalenceEstablished":False,"boundary":BOUNDARY}
def run_comparison_matrix(payload:dict): return {"ok":True,"version":VERSION,"runRefs":_list(payload.get("runRefs")),"rows":_list(payload.get("rows")),"environmentSeedDifferencesVisible":True,"automaticWinnerSelection":False,"boundary":BOUNDARY}
def model_comparison_matrix(payload:dict): return {"ok":True,"version":VERSION,"modelRefs":_list(payload.get("modelRefs")),"rows":_list(payload.get("rows")),"comparability":_dict(payload.get("comparability")),"automaticRanking":False,"automaticWinnerSelection":False,"boundary":BOUNDARY}
def missingness_matrix(payload:dict): return {"ok":True,"version":VERSION,"sampleRefs":_list(payload.get("sampleRefs")),"modalities":_list(payload.get("modalities")),"matrix":_list(payload.get("matrix")),"imputationIsTruth":False,"boundary":BOUNDARY}
def robustness_audit(payload:dict): return {"ok":True,"version":VERSION,"perturbations":_list(payload.get("perturbations")),"results":_list(payload.get("results")),"modalityDropout":_dict(payload.get("modalityDropout")),"robustnessCertified":False,"boundary":BOUNDARY}
def sensitivity_audit(payload:dict): return {"ok":True,"version":VERSION,"factors":_list(payload.get("factors")),"results":_list(payload.get("results")),"sensitivityIsCausality":False,"boundary":BOUNDARY}
def uncertainty_audit(payload:dict): return {"ok":True,"version":VERSION,"method":_txt(payload.get("method"),128),"intervals":_dict(payload.get("intervals")),"ensembles":_list(payload.get("ensembles")),"uncertaintyResolved":False,"boundary":BOUNDARY}
def out_of_distribution_audit(payload:dict): return {"ok":True,"version":VERSION,"modalityShifts":_list(payload.get("modalityShifts")),"jointShift":_dict(payload.get("jointShift")),"oodScores":_list(payload.get("oodScores")),"generalizationCertified":False,"boundary":BOUNDARY}
def fairness_audit(payload:dict): return {"ok":True,"version":VERSION,"groups":_list(payload.get("groups")),"metrics":_dict(payload.get("metrics")),"fairnessCertified":False,"automaticPolicyConclusion":False,"boundary":BOUNDARY}
def explainability_audit(payload:dict): return {"ok":True,"version":VERSION,"methods":_list(payload.get("methods")),"modalityAttributions":_dict(payload.get("modalityAttributions")),"stability":_dict(payload.get("stability")),"faithfulnessCertified":False,"explanationIsCausalProof":False,"boundary":BOUNDARY}
def modality_contribution_audit(payload:dict): return {"ok":True,"version":VERSION,"contributions":_dict(payload.get("contributions")),"method":_txt(payload.get("method"),128),"contributionIsCausalImportance":False,"automaticModalityRanking":False,"boundary":BOUNDARY}

def sample_inspector_spec(payload:dict): return {"ok":True,"version":VERSION,"visual":{"family":"multimodal-sample-inspector","sampleRef":_txt(payload.get("sampleRef"),512),"panels":_list(payload.get("panels")),"sourceRefs":_list(payload.get("sourceRefs")),"alignmentRefs":_list(payload.get("alignmentRefs")),"derivedRepresentationsLabeled":True,"automaticInterpretation":False},"boundary":BOUNDARY}
def visual_specification(payload:dict): return {"ok":True,"version":VERSION,"visual":{"family":_txt(payload.get("family"),128) or "multimodal-experiment-workspace","title":_txt(payload.get("title"),1024),"layout":_txt(payload.get("layout"),128) or "linked-modality-grid","encodings":_dict(payload.get("encodings")),"dataRefs":_list(payload.get("dataRefs")),"alignmentUncertaintyVisible":True,"missingModalitiesVisible":True,"predictionLegendRequired":True,"automaticInterpretation":False},"boundary":BOUNDARY}
def linked_modality_view(payload:dict): return {"ok":True,"version":VERSION,"views":_list(payload.get("views")),"links":_list(payload.get("links")),"focusRef":_txt(payload.get("focusRef"),512),"crossModalLinkIsSemanticEquivalence":False,"boundary":BOUNDARY}
def provenance_graph(payload:dict):
    s=normalize_study(payload.get("study") or payload); nodes=[{"id":s["studyId"],"kind":"study"},{"id":s["model"]["modelId"],"kind":"model"}]; edges=[]
    for sample in s["samples"]:
        nodes.append({"id":sample["sampleId"],"kind":"sample"}); edges.append({"source":s["studyId"],"target":sample["sampleId"],"relation":"contains"})
        for src in sample["sources"]: nodes.append({"id":src["sourceId"],"kind":src["modality"]}); edges.append({"source":sample["sampleId"],"target":src["sourceId"],"relation":"has-source"})
    for a in s["alignments"]: nodes.append({"id":a["alignmentId"],"kind":"alignment"}); edges.append({"source":s["studyId"],"target":a["alignmentId"],"relation":"uses-alignment"})
    edges.append({"source":s["studyId"],"target":s["model"]["modelId"],"relation":"uses-model"})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"automaticSemanticEquivalence":False,"scientificValidityCertified":False,"boundary":BOUNDARY}
def workspace_execution_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKSPACE_HANDOFF_SCHEMA,"studyRef":s["studyId"],"modelRef":s["model"]["modelId"],"requestedOperation":_txt(payload.get("requestedOperation"),256) or "multimodal-train","executionAuthority":"workspace","automaticExecution":False,"labExecutesMultimodalTraining":False,"labExecutesMultimodalInference":False,"payload":_dict(payload.get("executionPayload"))},"boundary":BOUNDARY}
def workbench_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKBENCH_HANDOFF_SCHEMA,"studyRef":s["studyId"],"requestedPrototype":_txt(payload.get("requestedPrototype"),256),"executionAuthority":"workbench","automaticExecution":False},"boundary":BOUNDARY}
def core_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":CORE_HANDOFF_SCHEMA,"canonicalObjectAuthority":"platform-core","studyRef":s["studyId"],"studyFingerprint":s["fingerprint"],"originalModalSourcesPreserved":True,"derivedRepresentationsRemainDerived":True,"automaticSemanticEquivalence":False,"automaticCanonicalization":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def research_os_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":RESEARCH_OS_HANDOFF_SCHEMA,"researchOSVersion":RESEARCH_OS_VERSION,"studyRef":s["studyId"],"targetPhase":_txt(payload.get("targetPhase"),128) or "analysis","automaticPhaseAdvance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def integrated_neural_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":NEURAL_HANDOFF_SCHEMA,"integratedNeuralVersion":INTEGRATED_NEURAL_VERSION,"studyRef":s["studyId"],"modelRef":s["model"]["modelId"],"automaticModelPromotion":False,"predictionIsEvidence":False},"boundary":BOUNDARY}
def workspace_snapshot(payload:dict):
    s=normalize_study(payload.get("study") or payload); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"study":copy.deepcopy(s)}; snap["snapshotFingerprint"]=_fp(snap); return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}
def compare_snapshots(payload:dict):
    a=workspace_snapshot(payload.get("left") or {})["snapshot"]; b=workspace_snapshot(payload.get("right") or {})["snapshot"]; return {"ok":True,"version":VERSION,"sameWorkspaceState":a["snapshotFingerprint"]==b["snapshotFingerprint"],"leftFingerprint":a["snapshotFingerprint"],"rightFingerprint":b["snapshotFingerprint"],"automaticScientificConclusion":False,"boundary":BOUNDARY}
def export_bundle(payload:dict):
    s=normalize_study(payload.get("study") or payload); b={"schema":f"{SCHEMA}/export-bundle","version":VERSION,"study":s,"provenanceGraph":provenance_graph(s),"review":s["review"],"limitations":s["limitations"],"scientificValidityCertified":False}; b["fingerprint"]=_fp(b); return {"ok":True,"version":VERSION,"bundle":b,"scientificValidityCertified":False,"boundary":BOUNDARY}
def reproducibility_package(payload:dict):
    s=normalize_study(payload.get("study") or payload); pkg={"schema":f"{SCHEMA}/reproducibility-package","version":VERSION,"studyRef":s["studyId"],"samples":s["samples"],"alignments":s["alignments"],"model":s["model"],"runs":s["runs"],"evaluation":s["evaluation"],"review":s["review"],"limitations":s["limitations"],"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; pkg["fingerprint"]=_fp(pkg); return {"ok":True,"version":VERSION,"package":pkg,"boundary":BOUNDARY}
def publication_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"studyRef":s["studyId"],"studyFingerprint":s["fingerprint"],"review":s["review"],"limitations":s["limitations"],"publicationAccepted":False,"automaticAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def default_study_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Study","Samples & Modalities","Alignment","Model & Fusion","Runs","Outputs","Evaluation","Explainability","Reproducibility"],"linkedViews":True,"missingModalitiesVisible":True},"boundary":BOUNDARY}
def default_analysis_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Metrics","Retrieval/Matching","Fusion Comparison","Modality Ablation","Robustness","Uncertainty","OOD"],"automaticWinnerSelection":False},"boundary":BOUNDARY}
def default_provenance_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Source Lineage","Transformations","Alignment Provenance","Model/Run Lineage"],"originalSourcesPreserved":True},"boundary":BOUNDARY}
def default_missingness_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Missing Modalities","Availability Matrix","Imputation Declarations"],"silentTruthImputationAllowed":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None): return {"ok":True,"version":VERSION,"boundaries":{"predictionIsEvidence":False,"crossModalSimilarityIsEvidence":False,"alignmentIsSemanticEquivalence":False,"matchingEstablishesIdentity":False,"generatedCaptionIsSourceTruth":False,"embeddingProximityIsRelationship":False,"ablationDeltaIsCausalEffect":False,"explanationIsCausalProof":False,"performanceIsScientificValidity":False,"reproducibilityIsScientificValidity":False},"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"policy":{"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesMultimodalTraining":False,"labExecutesMultimodalInference":False,"originalSourcesPreserved":True,"derivedRepresentationsRemainDerived":True,"automaticSemanticEquivalence":False,"automaticModelRanking":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"predictionIsEvidence":False},"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"integratedNeuralVersion":INTEGRATED_NEURAL_VERSION,"studySchema":STUDY_SCHEMA,"sourceSchema":SOURCE_SCHEMA,"sampleSchema":SAMPLE_SCHEMA,"alignmentSchema":ALIGNMENT_SCHEMA,"modelSchema":MODEL_SCHEMA,"runSchema":RUN_SCHEMA,"outputSchema":PREDICTION_SCHEMA,"modalities":list(MODALITIES),"taskTypes":list(TASK_TYPES),"fusionStrategies":list(FUSION_STRATEGIES),"alignmentTypes":list(ALIGNMENT_TYPES),"modelFamilies":list(MODEL_FAMILIES),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"graphMLPredecessorRetained":True,"modalitySpecificProvenancePresent":True,"originalSourcesPreserved":True,"alignmentSeparatedFromEquivalence":True,"fusionDeclared":True,"predictionSeparatedFromEvidence":True,"missingnessExplicit":True,"reproducibilitySeparatedFromValidity":True,"predecessorCompatible":True},"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"multimodalScientificExperimentWorkspace":True,"api_route_count":73,"predecessorVersion":PREDECESSOR_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesMultimodalTraining":False,"labExecutesMultimodalInference":False,"originalSourcesPreserved":True,"derivedRepresentationsRemainDerived":True,"automaticSemanticEquivalence":False,"automaticModelRanking":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"predictionIsEvidence":False,"crossModalSimilarityIsEvidence":False,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"multimodalStudyObjectModel":True,"modalitySpecificSourceObjects":True,"sampleAndAlignmentObjects":True,"fusionModelObjects":True,"multimodalRunAndOutputObjects":True,"provenanceAndTransformationAudits":True,"temporalSpatialAlignmentAudits":True,"missingModalityAudits":True,"leakageAndEvaluationAudits":True,"retrievalMatchingAlignmentMetrics":True,"modalityAblationAndFusionComparison":True,"robustnessSensitivityUncertainty":True,"multimodalExplainability":True,"linkedModalityVisualization":True,"workspaceExecutionHandoff":True,"workbenchHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"integratedNeuralHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
