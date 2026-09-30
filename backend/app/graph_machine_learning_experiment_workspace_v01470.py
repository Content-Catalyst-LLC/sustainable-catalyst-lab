from __future__ import annotations
import copy, hashlib, json, math, statistics
from collections import Counter
from datetime import datetime, timezone
from typing import Any

VERSION="0.147.0"
PREDECESSOR_VERSION="0.146.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-graph-machine-learning-experiment-workspace/0.147.0"
STUDY_SCHEMA="sc-lab-graph-ml-study/0.147.0"
TASK_SCHEMA="sc-lab-graph-ml-task/0.147.0"
DATASET_SCHEMA="sc-lab-graph-ml-dataset/0.147.0"
SPLIT_SCHEMA="sc-lab-graph-ml-split/0.147.0"
MODEL_SCHEMA="sc-lab-graph-ml-model/0.147.0"
RUN_SCHEMA="sc-lab-graph-ml-run/0.147.0"
PREDICTION_SCHEMA="sc-lab-graph-ml-prediction/0.147.0"
SNAPSHOT_SCHEMA="sc-lab-graph-ml-workspace-snapshot/0.147.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-graph-ml-execution-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-graph-ml-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-graph-ml-research-objects/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-graph-ml-handoff/1.0"

BOUNDARY=(
    "The Graph Machine Learning Experiment Workspace governs graph-ML study design, graph data and label provenance, model/training configuration, returned predictions, evaluation, comparison, explanation, uncertainty, review, and reproducibility. "
    "Workspace remains the execution authority for graph-ML training and inference; Workbench remains the prototype authority; Platform Core remains the canonical governed-object authority. "
    "A predicted node class, edge class, graph class, anomaly score, embedding neighborhood, or candidate link is a model output, not an established fact or evidence edge. "
    "Link prediction never creates an established relationship automatically, graph embeddings do not establish semantic equivalence, and model performance does not certify scientific validity."
)

TASK_TYPES=("node-classification","edge-classification","graph-classification","node-regression","edge-regression","graph-regression","link-prediction","graph-anomaly-detection","node-anomaly-detection","edge-anomaly-detection","graph-embedding","node-embedding","edge-embedding","representation-learning","self-supervised","contrastive","other")
MODEL_FAMILIES=("gcn","graphsage","gat","gin","rgcn","heterogeneous-gnn","temporal-gnn","graph-transformer","message-passing","graph-autoencoder","variational-graph-autoencoder","knowledge-graph-embedding","random-walk-embedding","spectral","matrix-factorization","hybrid","custom","other")
SPLIT_STRATEGIES=("random-node","random-edge","random-graph","stratified","temporal","inductive-node","inductive-graph","cold-start","relation-held-out","subgraph-held-out","cross-validation","custom","other")
NEGATIVE_SAMPLING=("uniform","degree-aware","hard-negative","temporal","type-constrained","closed-world","open-world","external","custom","other")
METRICS=("accuracy","balanced-accuracy","precision","recall","f1","macro-f1","micro-f1","roc-auc","pr-auc","log-loss","brier","mrr","hits@k","map","ndcg","rmse","mae","r2","calibration-error","other")
EXPLANATION_METHODS=("gnnexplainer","pgexplainer","integrated-gradients","saliency","attention","subgraph-mask","feature-mask","counterfactual","prototype","other")
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
    return {"ok":True,"version":VERSION,"taskTypes":list(TASK_TYPES),"modelFamilies":list(MODEL_FAMILIES),"splitStrategies":list(SPLIT_STRATEGIES),"negativeSamplingMethods":list(NEGATIVE_SAMPLING),"metrics":list(METRICS),"explanationMethods":list(EXPLANATION_METHODS),"automaticRelationshipEstablishment":False,"predictionIsEvidence":False,"boundary":BOUNDARY}

def normalize_task(payload:dict):
    p=_dict(payload); t=_txt(p.get("taskType"),64).lower() or "node-classification"; t=t if t in TASK_TYPES else "other"
    r={"schema":TASK_SCHEMA,"version":VERSION,"taskId":_txt(p.get("taskId") or p.get("id"),512) or f"graph-ml-task-{_fp(p)[:16]}","taskType":t,"target":_dict(p.get("target")),"labelSchema":_dict(p.get("labelSchema")),"objective":_dict(p.get("objective")),"metricRefs":_list(p.get("metricRefs")),"limitations":_list(p.get("limitations")),"metadata":_dict(p.get("metadata")),"predictionIsEvidence":False}; r["fingerprint"]=_fp(r); return r

def normalize_dataset(payload:dict):
    p=_dict(payload)
    r={"schema":DATASET_SCHEMA,"version":VERSION,"datasetId":_txt(p.get("datasetId") or p.get("id"),512) or f"graph-ml-dataset-{_fp(p)[:16]}","graphRef":_txt(p.get("graphRef"),512),"graphFingerprint":_txt(p.get("graphFingerprint"),128),"nodeFeatureSchema":_dict(p.get("nodeFeatureSchema")),"edgeFeatureSchema":_dict(p.get("edgeFeatureSchema")),"graphFeatureSchema":_dict(p.get("graphFeatureSchema")),"labelProvenance":_dict(p.get("labelProvenance")),"featureProvenance":_dict(p.get("featureProvenance")),"construction":_dict(p.get("construction")),"timeCoverage":_dict(p.get("timeCoverage")),"limitations":_list(p.get("limitations")),"metadata":_dict(p.get("metadata")),"relationshipSemanticsPreserved":True}; r["fingerprint"]=_fp(r); return r

def normalize_split(payload:dict):
    p=_dict(payload); s=_txt(p.get("strategy"),64).lower() or "random-node"; s=s if s in SPLIT_STRATEGIES else "other"
    r={"schema":SPLIT_SCHEMA,"version":VERSION,"splitId":_txt(p.get("splitId") or p.get("id"),512) or f"graph-ml-split-{_fp(p)[:16]}","strategy":s,"trainRefs":_list(p.get("trainRefs")),"validationRefs":_list(p.get("validationRefs")),"testRefs":_list(p.get("testRefs")),"heldOutNodeRefs":_list(p.get("heldOutNodeRefs")),"heldOutEdgeRefs":_list(p.get("heldOutEdgeRefs")),"heldOutGraphRefs":_list(p.get("heldOutGraphRefs")),"timeBoundary":p.get("timeBoundary"),"negativeSampling":_dict(p.get("negativeSampling")),"seed":p.get("seed"),"metadata":_dict(p.get("metadata")),"leakageCertifiedAbsent":False}; r["fingerprint"]=_fp(r); return r

def normalize_model(payload:dict):
    p=_dict(payload); f=_txt(p.get("modelFamily"),64).lower() or "message-passing"; f=f if f in MODEL_FAMILIES else "other"
    r={"schema":MODEL_SCHEMA,"version":VERSION,"modelId":_txt(p.get("modelId") or p.get("id"),512) or f"graph-ml-model-{_fp(p)[:16]}","modelFamily":f,"architecture":_dict(p.get("architecture")),"messagePassing":_dict(p.get("messagePassing")),"encoder":_dict(p.get("encoder")),"decoder":_dict(p.get("decoder")),"readout":_dict(p.get("readout")),"loss":_dict(p.get("loss")),"optimizer":_dict(p.get("optimizer")),"regularization":_dict(p.get("regularization")),"checkpointRef":_txt(p.get("checkpointRef"),2048),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"automaticModelEndorsement":False}; r["fingerprint"]=_fp(r); return r

def normalize_run(payload:dict):
    p=_dict(payload)
    r={"schema":RUN_SCHEMA,"version":VERSION,"runId":_txt(p.get("runId") or p.get("id"),512) or f"graph-ml-run-{_fp(p)[:16]}","taskRef":_txt(p.get("taskRef"),512),"datasetRef":_txt(p.get("datasetRef"),512),"splitRef":_txt(p.get("splitRef"),512),"modelRef":_txt(p.get("modelRef"),512),"environment":_dict(p.get("environment")),"seed":p.get("seed"),"training":_dict(p.get("training")),"metrics":_dict(p.get("metrics")),"artifactRefs":_list(p.get("artifactRefs")),"status":_txt(p.get("status"),64) or "declared","provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_prediction(payload:dict):
    p=_dict(payload); task=_txt(p.get("taskType"),64).lower() or "other"; score=_num(p.get("score")); candidate_edge=task=="link-prediction" or bool(p.get("candidateEdge",False))
    r={"schema":PREDICTION_SCHEMA,"version":VERSION,"predictionId":_txt(p.get("predictionId") or p.get("id"),512) or f"graph-ml-prediction-{_fp(p)[:16]}","taskType":task,"subjectRef":_txt(p.get("subjectRef"),512),"sourceNodeRef":_txt(p.get("sourceNodeRef"),512),"targetNodeRef":_txt(p.get("targetNodeRef"),512),"predictedLabel":p.get("predictedLabel"),"score":score,"probabilities":_dict(p.get("probabilities")),"threshold":_num(p.get("threshold")),"modelRef":_txt(p.get("modelRef"),512),"runRef":_txt(p.get("runRef"),512),"candidateOnly":candidate_edge,"relationshipEstablished":False if candidate_edge else None,"evidenceEdgeCreated":False,"predictionIsEvidence":False,"metadata":_dict(p.get("metadata"))}; r["fingerprint"]=_fp(r); return r

def normalize_study(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in SESSION_STATES else "draft"
    r={"schema":STUDY_SCHEMA,"version":VERSION,"studyId":_txt(p.get("studyId") or p.get("id"),512) or f"graph-ml-study-{_fp(p)[:16]}","projectRef":_txt(p.get("projectRef"),512),"title":_txt(p.get("title"),1024) or "Graph machine learning experiment","question":_txt(p.get("question"),4096),"state":state,"graphStudyRef":_txt(p.get("graphStudyRef"),512),"task":normalize_task(p.get("task") or {}),"dataset":normalize_dataset(p.get("dataset") or {}),"split":normalize_split(p.get("split") or {}),"model":normalize_model(p.get("model") or {}),"runs":[normalize_run(x) for x in _list(p.get("runs"))],"predictions":[normalize_prediction(x) for x in _list(p.get("predictions"))],"evaluation":_dict(p.get("evaluation")),"explainability":_dict(p.get("explainability")),"review":_dict(p.get("review")),"limitations":_list(p.get("limitations")),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"automaticRelationshipEstablishment":False,"automaticScientificValidity":False}; r["fingerprint"]=_fp(r); return r

def workspace_state(payload:dict):
    s=normalize_study(payload.get("study") if isinstance(payload.get("study"),dict) else payload)
    return {"ok":True,"version":VERSION,"study":s,"summary":{"taskType":s["task"]["taskType"],"runCount":len(s["runs"]),"predictionCount":len(s["predictions"]),"state":s["state"]},"automaticScientificValidity":False,"boundary":BOUNDARY}

def graph_schema_audit(payload:dict):
    p=_dict(payload); required=["graphRef","nodeFeatureSchema","edgeFeatureSchema"]; missing=[x for x in required if not p.get(x)]
    return {"ok":True,"version":VERSION,"missingFields":missing,"clean":not missing,"schemaAdequacyCertified":False,"boundary":BOUNDARY}
def provenance_audit(payload:dict):
    p=_dict(payload); fields=("graphRef","labelProvenance","featureProvenance"); missing=[x for x in fields if not p.get(x)]
    return {"ok":True,"version":VERSION,"missingProvenance":missing,"complete":not missing,"scientificValidityCertified":False,"boundary":BOUNDARY}
def split_leakage_audit(payload:dict):
    s=normalize_split(payload); a=set(map(str,s["trainRefs"])); b=set(map(str,s["validationRefs"])); c=set(map(str,s["testRefs"])); overlap=sorted((a&b)|(a&c)|(b&c))
    return {"ok":True,"version":VERSION,"overlapRefs":overlap,"possibleLeakage":bool(overlap),"leakageCertifiedAbsent":False,"boundary":BOUNDARY}
def label_provenance_audit(payload:dict): return {"ok":True,"version":VERSION,"labelProvenance":_dict(payload.get("labelProvenance")),"missingSource":not bool(_dict(payload.get("labelProvenance")).get("sourceRef")),"labelsAreGroundTruthByDefault":False,"boundary":BOUNDARY}
def negative_sampling_audit(payload:dict):
    p=_dict(payload); method=_txt(p.get("method"),64).lower() or "other"; method=method if method in NEGATIVE_SAMPLING else "other"
    return {"ok":True,"version":VERSION,"method":method,"knownPositiveExclusion":bool(p.get("knownPositiveExclusion",False)),"temporalValidityDeclared":bool(p.get("temporalValidityDeclared",False)),"absenceIsNegativeLabel":False,"samplingAdequacyCertified":False,"boundary":BOUNDARY}
def candidate_edge_audit(payload:dict):
    rows=[normalize_prediction(x) for x in _list(payload.get("predictions"))]; candidates=[x for x in rows if x["candidateOnly"]]
    return {"ok":True,"version":VERSION,"candidateCount":len(candidates),"allRelationshipEstablishedFalse":all(x["relationshipEstablished"] is False for x in candidates),"evidenceEdgesCreated":False,"boundary":BOUNDARY}
def class_balance_audit(payload:dict):
    labels=_list(payload.get("labels")); counts=Counter(map(str,labels)); return {"ok":True,"version":VERSION,"counts":dict(counts),"classCount":len(counts),"imbalanceResolved":False,"boundary":BOUNDARY}
def feature_leakage_audit(payload:dict): return {"ok":True,"version":VERSION,"features":_list(payload.get("features")),"targetDerivedFeatures":_list(payload.get("targetDerivedFeatures")),"possibleLeakage":bool(_list(payload.get("targetDerivedFeatures"))),"leakageCertifiedAbsent":False,"boundary":BOUNDARY}
def temporal_leakage_audit(payload:dict): return {"ok":True,"version":VERSION,"timeAware":bool(payload.get("timeAware",False)),"futureInformationRefs":_list(payload.get("futureInformationRefs")),"possibleTemporalLeakage":bool(_list(payload.get("futureInformationRefs"))),"temporalValidityCertified":False,"boundary":BOUNDARY}
def transductive_inductive_audit(payload:dict):
    mode=_txt(payload.get("mode"),64).lower() or "unspecified"; return {"ok":True,"version":VERSION,"mode":mode,"heldOutEntityRefs":_list(payload.get("heldOutEntityRefs")),"evaluationScopeExplicit":mode in ("transductive","inductive"),"generalizationBeyondDeclaredScope":False,"boundary":BOUNDARY}
def evaluation_protocol_audit(payload:dict): return {"ok":True,"version":VERSION,"metrics":_list(payload.get("metrics")),"thresholdSelection":_dict(payload.get("thresholdSelection")),"testSetTouchedDuringSelection":bool(payload.get("testSetTouchedDuringSelection",False)),"evaluationValidityCertified":False,"boundary":BOUNDARY}

def _result(kind,payload):
    p=_dict(payload); r={"ok":True,"version":VERSION,"resultType":kind,"runRef":_txt(p.get("runRef"),512),"taskRef":_txt(p.get("taskRef"),512),"rows":_list(p.get("rows")),"metrics":_dict(p.get("metrics")),"provenance":_dict(p.get("provenance")),"automaticScientificValidity":False,"predictionIsEvidence":False,"boundary":BOUNDARY}; r["fingerprint"]=_fp({k:v for k,v in r.items() if k not in ("ok","boundary")}); return r
def normalize_node_classification_result(payload:dict): return _result("node-classification",payload)
def normalize_edge_classification_result(payload:dict): return _result("edge-classification",payload)
def normalize_graph_classification_result(payload:dict): return _result("graph-classification",payload)
def normalize_graph_regression_result(payload:dict): return _result("graph-regression",payload)
def normalize_anomaly_result(payload:dict): return _result("anomaly",payload)
def normalize_embedding_result(payload:dict):
    r=_result("embedding",payload); r["embeddingProximityIsRelationship"]=False; return r
def normalize_gnn_explanation(payload:dict):
    p=_dict(payload); method=_txt(p.get("method"),64).lower() or "other"; method=method if method in EXPLANATION_METHODS else "other"
    r=_result("gnn-explanation",payload); r.update({"method":method,"targetRef":_txt(p.get("targetRef"),512),"subgraph":_dict(p.get("subgraph")),"featureAttributions":_list(p.get("featureAttributions")),"explanationIsCausalProof":False,"explanationFaithfulnessCertified":False}); return r
def normalize_link_prediction_result(payload:dict):
    r=_result("link-prediction",payload); r["candidates"]=[normalize_prediction(dict(x,taskType="link-prediction",candidateEdge=True)) for x in _list(payload.get("candidates"))]; r["relationshipsEstablished"]=False; r["evidenceEdgesCreated"]=False; return r

def metric_summary(payload:dict): return {"ok":True,"version":VERSION,"metrics":_dict(payload.get("metrics")),"replicateSummary":{k:_summary(v if isinstance(v,list) else [v]) for k,v in _dict(payload.get("replicates")).items()},"automaticWinnerSelection":False,"boundary":BOUNDARY}
def confusion_matrix(payload:dict): return {"ok":True,"version":VERSION,"labels":_list(payload.get("labels")),"matrix":_list(payload.get("matrix")),"normalized":bool(payload.get("normalized",False)),"scientificValidityCertified":False,"boundary":BOUNDARY}
def threshold_sweep(payload:dict): return {"ok":True,"version":VERSION,"rows":_list(payload.get("rows")),"selectedThreshold":payload.get("selectedThreshold"),"automaticThresholdSelection":False,"boundary":BOUNDARY}
def calibration_summary(payload:dict): return {"ok":True,"version":VERSION,"bins":_list(payload.get("bins")),"ece":_num(payload.get("ece")),"brier":_num(payload.get("brier")),"calibrationCertified":False,"boundary":BOUNDARY}
def ranking_metrics(payload:dict): return {"ok":True,"version":VERSION,"mrr":_num(payload.get("mrr")),"map":_num(payload.get("map")),"hitsAtK":_dict(payload.get("hitsAtK")),"rankingMetricIsEvidence":False,"boundary":BOUNDARY}
def candidate_link_table(payload:dict): return {"ok":True,"version":VERSION,"rows":[dict(normalize_prediction(dict(x,taskType="link-prediction",candidateEdge=True)),candidateOnly=True,relationshipEstablished=False,evidenceEdgeCreated=False) for x in _list(payload.get("rows"))],"automaticRelationshipEstablishment":False,"boundary":BOUNDARY}
def node_prediction_table(payload:dict): return {"ok":True,"version":VERSION,"rows":_list(payload.get("rows")),"predictedNodeClassIsFact":False,"boundary":BOUNDARY}
def edge_prediction_table(payload:dict): return {"ok":True,"version":VERSION,"rows":_list(payload.get("rows")),"predictedEdgeClassIsFact":False,"boundary":BOUNDARY}
def graph_prediction_table(payload:dict): return {"ok":True,"version":VERSION,"rows":_list(payload.get("rows")),"predictedGraphClassIsFact":False,"boundary":BOUNDARY}
def anomaly_table(payload:dict): return {"ok":True,"version":VERSION,"rows":_list(payload.get("rows")),"anomalyScoreIsProofOfAnomaly":False,"boundary":BOUNDARY}
def embedding_comparison(payload:dict): return {"ok":True,"version":VERSION,"spaces":_list(payload.get("spaces")),"metrics":_dict(payload.get("metrics")),"alignment":_dict(payload.get("alignment")),"embeddingProximityIsRelationship":False,"automaticWinnerSelection":False,"boundary":BOUNDARY}
def model_comparison_matrix(payload:dict): return {"ok":True,"version":VERSION,"modelRefs":_list(payload.get("modelRefs")),"metricKeys":_list(payload.get("metricKeys")),"rows":_list(payload.get("rows")),"comparability":_dict(payload.get("comparability")),"automaticRanking":False,"automaticWinnerSelection":False,"boundary":BOUNDARY}
def run_comparison_matrix(payload:dict): return {"ok":True,"version":VERSION,"runRefs":_list(payload.get("runRefs")),"rows":_list(payload.get("rows")),"seedEnvironmentDifferencesVisible":True,"automaticWinnerSelection":False,"boundary":BOUNDARY}
def graph_split_comparison(payload:dict): return {"ok":True,"version":VERSION,"splitRefs":_list(payload.get("splitRefs")),"rows":_list(payload.get("rows")),"crossSplitComparabilityCertified":False,"automaticRanking":False,"boundary":BOUNDARY}
def robustness_audit(payload:dict): return {"ok":True,"version":VERSION,"perturbations":_list(payload.get("perturbations")),"results":_list(payload.get("results")),"robustnessCertified":False,"boundary":BOUNDARY}
def sensitivity_audit(payload:dict): return {"ok":True,"version":VERSION,"factors":_list(payload.get("factors")),"results":_list(payload.get("results")),"sensitivityIsCausality":False,"boundary":BOUNDARY}
def uncertainty_audit(payload:dict): return {"ok":True,"version":VERSION,"method":_txt(payload.get("method"),128),"intervals":_dict(payload.get("intervals")),"ensembles":_list(payload.get("ensembles")),"uncertaintyResolved":False,"boundary":BOUNDARY}
def out_of_distribution_audit(payload:dict): return {"ok":True,"version":VERSION,"shiftTests":_list(payload.get("shiftTests")),"oodScores":_list(payload.get("oodScores")),"generalizationCertified":False,"boundary":BOUNDARY}
def fairness_audit(payload:dict): return {"ok":True,"version":VERSION,"groups":_list(payload.get("groups")),"metrics":_dict(payload.get("metrics")),"fairnessCertified":False,"automaticPolicyConclusion":False,"boundary":BOUNDARY}
def explainability_audit(payload:dict): return {"ok":True,"version":VERSION,"methods":_list(payload.get("methods")),"stability":_dict(payload.get("stability")),"fidelity":_dict(payload.get("fidelity")),"explanationFaithfulnessCertified":False,"explanationIsCausalProof":False,"boundary":BOUNDARY}

def visual_specification(payload:dict): return {"ok":True,"version":VERSION,"visual":{"family":_txt(payload.get("family"),128) or "graph-ml-workspace","title":_txt(payload.get("title"),1024),"layout":_txt(payload.get("layout"),128) or "linked-network-model-view","encodings":_dict(payload.get("encodings")),"dataRefs":_list(payload.get("dataRefs")),"candidateEdgeStylingRequired":True,"predictionLegendRequired":True,"automaticInterpretation":False},"boundary":BOUNDARY}
def provenance_graph(payload:dict):
    s=normalize_study(payload.get("study") or payload); nodes=[{"id":s["studyId"],"kind":"study"},{"id":s["task"]["taskId"],"kind":"task"},{"id":s["dataset"]["datasetId"],"kind":"dataset"},{"id":s["split"]["splitId"],"kind":"split"},{"id":s["model"]["modelId"],"kind":"model"}]; edges=[{"source":s["studyId"],"target":n["id"],"relation":"contains"} for n in nodes[1:]]
    for run in s["runs"]: nodes.append({"id":run["runId"],"kind":"run"}); edges.append({"source":s["model"]["modelId"],"target":run["runId"],"relation":"executed-as"})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"automaticRelationshipEstablishment":False,"scientificValidityCertified":False,"boundary":BOUNDARY}
def workspace_execution_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKSPACE_HANDOFF_SCHEMA,"studyRef":s["studyId"],"taskRef":s["task"]["taskId"],"datasetRef":s["dataset"]["datasetId"],"splitRef":s["split"]["splitId"],"modelRef":s["model"]["modelId"],"requestedOperation":_txt(payload.get("requestedOperation"),256) or "graph-ml-train","executionAuthority":"workspace","automaticExecution":False,"labExecutesGraphMLTraining":False,"payload":_dict(payload.get("executionPayload"))},"boundary":BOUNDARY}
def workbench_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKBENCH_HANDOFF_SCHEMA,"studyRef":s["studyId"],"requestedPrototype":_txt(payload.get("requestedPrototype"),256),"executionAuthority":"workbench","automaticExecution":False},"boundary":BOUNDARY}
def core_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":CORE_HANDOFF_SCHEMA,"canonicalObjectAuthority":"platform-core","studyRef":s["studyId"],"studyFingerprint":s["fingerprint"],"candidatePredictionsRemainCandidates":True,"automaticRelationshipEstablishment":False,"automaticCanonicalization":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def research_os_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":RESEARCH_OS_HANDOFF_SCHEMA,"researchOSVersion":RESEARCH_OS_VERSION,"studyRef":s["studyId"],"targetPhase":_txt(payload.get("targetPhase"),128) or "analysis","automaticPhaseAdvance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def workspace_snapshot(payload:dict):
    s=normalize_study(payload.get("study") or payload); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"study":copy.deepcopy(s)}; snap["snapshotFingerprint"]=_fp(snap); return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}
def compare_snapshots(payload:dict):
    a=workspace_snapshot(payload.get("left") or {})["snapshot"]; b=workspace_snapshot(payload.get("right") or {})["snapshot"]; return {"ok":True,"version":VERSION,"sameWorkspaceState":a["snapshotFingerprint"]==b["snapshotFingerprint"],"leftFingerprint":a["snapshotFingerprint"],"rightFingerprint":b["snapshotFingerprint"],"automaticScientificConclusion":False,"boundary":BOUNDARY}
def export_bundle(payload:dict):
    s=normalize_study(payload.get("study") or payload); b={"schema":f"{SCHEMA}/export-bundle","version":VERSION,"study":s,"provenanceGraph":provenance_graph(s),"review":s["review"],"limitations":s["limitations"],"scientificValidityCertified":False}; b["fingerprint"]=_fp(b); return {"ok":True,"version":VERSION,"bundle":b,"scientificValidityCertified":False,"boundary":BOUNDARY}
def reproducibility_package(payload:dict):
    s=normalize_study(payload.get("study") or payload); pkg={"schema":f"{SCHEMA}/reproducibility-package","version":VERSION,"studyRef":s["studyId"],"task":s["task"],"dataset":s["dataset"],"split":s["split"],"model":s["model"],"runs":s["runs"],"evaluation":s["evaluation"],"explainability":s["explainability"],"review":s["review"],"limitations":s["limitations"],"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; pkg["fingerprint"]=_fp(pkg); return {"ok":True,"version":VERSION,"package":pkg,"boundary":BOUNDARY}
def publication_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"studyRef":s["studyId"],"studyFingerprint":s["fingerprint"],"review":s["review"],"limitations":s["limitations"],"publicationAccepted":False,"automaticAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None): return {"ok":True,"version":VERSION,"boundaries":{"predictionIsEvidence":False,"candidateLinkIsEstablishedRelationship":False,"predictedClassIsFact":False,"anomalyScoreIsProof":False,"embeddingProximityIsRelationship":False,"attentionIsExplanationByDefault":False,"explanationIsCausalProof":False,"performanceIsScientificValidity":False,"reproducibilityIsScientificValidity":False},"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"policy":{"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesGraphMLTraining":False,"labExecutesGraphMLInference":False,"candidatePredictionsRemainCandidates":True,"automaticRelationshipEstablishment":False,"automaticModelRanking":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"predictionIsEvidence":False},"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"studySchema":STUDY_SCHEMA,"taskSchema":TASK_SCHEMA,"datasetSchema":DATASET_SCHEMA,"splitSchema":SPLIT_SCHEMA,"modelSchema":MODEL_SCHEMA,"runSchema":RUN_SCHEMA,"predictionSchema":PREDICTION_SCHEMA,"taskTypes":list(TASK_TYPES),"modelFamilies":list(MODEL_FAMILIES),"splitStrategies":list(SPLIT_STRATEGIES),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"graphScienceFoundationRetained":True,"executionAuthoritySeparated":True,"graphSpecificLeakageAuditsPresent":True,"candidateLinksNotEstablished":True,"predictionsSeparatedFromEvidence":True,"reproducibilitySeparatedFromValidity":True,"predecessorCompatible":True},"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"graphMachineLearningExperimentWorkspace":True,"api_route_count":65,"predecessorVersion":PREDECESSOR_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesGraphMLTraining":False,"labExecutesGraphMLInference":False,"candidatePredictionsRemainCandidates":True,"automaticRelationshipEstablishment":False,"automaticModelRanking":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"graphMLStudyObjectModel":True,"taskDatasetSplitModelRunObjects":True,"graphSpecificLeakageAudits":True,"nodeEdgeGraphPredictionObjects":True,"linkPredictionCandidateObjects":True,"anomalyAndEmbeddingObjects":True,"GNNExplanationObjects":True,"evaluationAndCalibrationObjects":True,"modelRunSplitComparison":True,"robustnessSensitivityUncertainty":True,"visualSpecification":True,"workspaceExecutionHandoff":True,"workbenchHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
