from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.7"
PREDECESSOR_VERSION="0.141.6"
ABLATION_VERSION="0.141.5"
SEARCH_VERSION="0.141.4"
COMPARISON_VERSION="0.141.3"
TELEMETRY_VERSION="0.141.2"
ARCHITECTURE_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-embedding-explorer/0.141.7"
STUDY_SCHEMA="sc-lab-embedding-study/0.141.7"
EMBEDDING_SCHEMA="sc-lab-embedding-vector/0.141.7"
PROJECTION_SCHEMA="sc-lab-embedding-projection/0.141.7"
SNAPSHOT_SCHEMA="sc-lab-embedding-explorer-snapshot/0.141.7"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-embedding-extraction-projection-handoff/1.0"
CORE_HANDOFF_SCHEMA="sc-core-embedding-visual-object-handoff/1.0"

BOUNDARY=(
    "Lab structures, compares, visualizes, and audits embedding spaces but does not execute model training, "
    "silently infer the semantic meaning of vector proximity, treat nearest-neighbor or cluster membership as evidence of a real-world relationship, "
    "or certify a 2D/3D projection as faithful to the original high-dimensional geometry. Projection coordinates are derived analytical views."
)
EMBEDDING_KINDS=("input","token","sentence","document","image","audio","graph-node","entity","multimodal","other")
DISTANCE_METRICS=("cosine","euclidean","manhattan","dot-product")
PROJECTION_METHODS=("pca","tsne","umap","pacmap","random-projection","user-supplied","other")
VIEWS=("projection","neighborhood","distance-matrix","cluster-overlay","label-overlay","drift-comparison","space-comparison","provenance-matrix")


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

def _vector(v):
    out=[]
    if isinstance(v,(list,tuple)):
        for x in v:
            n=_num(x)
            if n is None: return []
            out.append(n)
    return out

def _norm(vec):
    return math.sqrt(sum(x*x for x in vec))

def normalize_embedding(item:Any,index:int=0,study=None):
    raw=item if isinstance(item,dict) else {"embeddingId":item}; study=study or {}
    vec=_vector(_get(raw,"vector","values","embedding",default=[]))
    kind=_txt(_get(raw,"kind","embeddingKind"),64).lower() or "input"
    if kind not in EMBEDDING_KINDS: kind="other"
    rec={
        "schema":EMBEDDING_SCHEMA,"version":VERSION,
        "embeddingId":_txt(_get(raw,"embeddingId","id"),512) or f"embedding-{index+1}",
        "kind":kind,"sourceRef":_txt(_get(raw,"sourceRef","inputRef","objectRef"),1024),
        "label":_txt(raw.get("label"),512),"group":_txt(_get(raw,"group","classLabel","category"),512),
        "vector":vec,"dimension":len(vec),"vectorFingerprint":_fp(vec) if vec else "",
        "modelRef":_txt(raw.get("modelRef"),1024) or study.get("modelRef",""),
        "checkpointRef":_txt(raw.get("checkpointRef"),1024) or study.get("checkpointRef",""),
        "layerRef":_txt(raw.get("layerRef"),1024) or study.get("layerRef",""),
        "datasetRef":_txt(raw.get("datasetRef"),1024) or study.get("datasetRef",""),
        "splitRef":_txt(raw.get("splitRef"),1024) or study.get("splitRef",""),
        "environmentRef":_txt(raw.get("environmentRef"),1024) or study.get("environmentRef",""),
        "extractionConfig":_dict(_get(raw,"extractionConfig","configuration",default={})),
        "normalization":_txt(raw.get("normalization"),128) or study.get("normalization","none"),
        "provenanceRef":_txt(raw.get("provenanceRef"),1024),"metadata":_dict(raw.get("metadata")),
        "semanticRelationshipInferred":False,"embeddingIsEvidence":False,
    }
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return rec

def study_spec(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    metric=_txt(_get(root,"distanceMetric","metric"),64).lower() or "cosine"
    if metric not in DISTANCE_METRICS: metric="cosine"
    rec={
        "schema":STUDY_SCHEMA,"version":VERSION,"recordType":"embedding-study",
        "studyId":_txt(_get(root,"studyId","id"),512) or f"embedding-study-{_fp(root)[:16]}",
        "title":_txt(root.get("title"),512) or "Embedding exploration study",
        "experimentId":_txt(root.get("experimentId"),512),"modelRef":_txt(root.get("modelRef"),1024),
        "checkpointRef":_txt(root.get("checkpointRef"),1024),"layerRef":_txt(root.get("layerRef"),1024),
        "datasetRef":_txt(root.get("datasetRef"),1024),"splitRef":_txt(root.get("splitRef"),1024),
        "environmentRef":_txt(root.get("environmentRef"),1024),"embeddingKind":_txt(root.get("embeddingKind"),64).lower() or "input",
        "normalization":_txt(root.get("normalization"),128) or "none","distanceMetric":metric,
        "extractionConfig":_dict(root.get("extractionConfig")),"projectionRequests":_list(root.get("projectionRequests")),
        "workspaceExecutionAuthority":True,"labExecutesEmbeddingExtraction":False,"labExecutesDimensionalityReduction":False,
        "semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,"embeddingIsEvidence":False,"boundary":BOUNDARY,
    }
    if rec["embeddingKind"] not in EMBEDDING_KINDS: rec["embeddingKind"]="other"
    issues=[]
    for k in ("modelRef","checkpointRef","datasetRef","splitRef"):
        if not rec.get(k): issues.append(f"missing-{k}")
    rec["issues"]=issues; rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"study":rec,"readyForWorkspaceHandoff":not issues,"boundary":BOUNDARY}

def workspace_handoff(payload:dict):
    s=study_spec(payload)
    packet={"schema":WORKSPACE_HANDOFF_SCHEMA,"labRelease":VERSION,"study":s["study"],"executionAuthority":"workspace",
            "labExecutesEmbeddingExtraction":False,"labExecutesDimensionalityReduction":False,"ready":s["readyForWorkspaceHandoff"],
            "semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def normalize_results(payload:dict):
    root=payload if isinstance(payload,dict) else {}; s=study_spec(root)["study"]
    items=_list(_get(root,"embeddings","vectors","results",default=[])); xs=[normalize_embedding(x,i,s) for i,x in enumerate(items)]
    rec={"schema":"sc-lab-embedding-results/0.141.7","version":VERSION,"studyId":s["studyId"],"studyFingerprint":s["fingerprint"],
         "embeddings":xs,"workspaceExecutionAuthority":True,"semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,
         "automaticClusterMeaning":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"results":rec,"boundary":BOUNDARY}

def vector_registry(payload):
    xs=normalize_results(payload)["results"]["embeddings"]
    rows=[{k:x.get(k) for k in ("embeddingId","kind","sourceRef","label","group","dimension","modelRef","checkpointRef","layerRef","datasetRef","splitRef","provenanceRef","vectorFingerprint")} for x in xs]
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"automaticSemanticInterpretation":False,"boundary":BOUNDARY}

def provenance_audit(payload):
    xs=normalize_results(payload)["results"]["embeddings"]; rows=[]
    for x in xs:
        missing=[k for k in ("modelRef","checkpointRef","datasetRef","splitRef","environmentRef") if not x.get(k)]
        rows.append({"embeddingId":x["embeddingId"],"complete":not missing,"missing":missing})
    return {"ok":True,"version":VERSION,"rows":rows,"allComplete":all(r["complete"] for r in rows),"boundary":BOUNDARY}

def dimensionality_audit(payload):
    xs=normalize_results(payload)["results"]["embeddings"]; dims=sorted(set(x["dimension"] for x in xs if x["dimension"]>0))
    invalid=[x["embeddingId"] for x in xs if x["dimension"]<=0]
    return {"ok":True,"version":VERSION,"dimensions":dims,"consistent":len(dims)<=1 and not invalid,"invalidEmbeddingIds":invalid,
            "comparableForDistance":len(dims)==1 and not invalid,"boundary":BOUNDARY}

def _distance(a,b,metric):
    if len(a)!=len(b) or not a: return None
    if metric=="euclidean": return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
    if metric=="manhattan": return sum(abs(x-y) for x,y in zip(a,b))
    if metric=="dot-product": return sum(x*y for x,y in zip(a,b))
    na,nb=_norm(a),_norm(b)
    if na==0 or nb==0: return None
    return 1.0 - sum(x*y for x,y in zip(a,b))/(na*nb)

def distance_matrix(payload):
    r=normalize_results(payload)["results"]; xs=r["embeddings"]
    metric=_txt(_get(payload,"distanceMetric","metric"),64).lower() or study_spec(payload)["study"]["distanceMetric"]
    if metric not in DISTANCE_METRICS: metric="cosine"
    audit=dimensionality_audit(payload)
    rows=[]
    for a in xs:
        row={"embeddingId":a["embeddingId"],"values":{}}
        for b in xs: row["values"][b["embeddingId"]]=_distance(a["vector"],b["vector"],metric) if audit["comparableForDistance"] else None
        rows.append(row)
    return {"ok":True,"version":VERSION,"metric":metric,"rows":rows,"comparable":audit["comparableForDistance"],
            "semanticRelationshipInferred":False,"distanceIsEvidence":False,"boundary":BOUNDARY}

def neighborhood_query(payload):
    r=normalize_results(payload)["results"]; xs=r["embeddings"]
    target_id=_txt(_get(payload,"targetEmbeddingId","embeddingId"),512); k=max(1,min(100,int(_get(payload,"k",default=10) or 10)))
    metric=_txt(_get(payload,"distanceMetric","metric"),64).lower() or study_spec(payload)["study"]["distanceMetric"]
    if metric not in DISTANCE_METRICS: metric="cosine"
    target=next((x for x in xs if x["embeddingId"]==target_id),None)
    out=[]
    if target:
        for x in xs:
            if x["embeddingId"]==target_id: continue
            d=_distance(target["vector"],x["vector"],metric)
            if d is not None: out.append({"embeddingId":x["embeddingId"],"label":x["label"],"group":x["group"],"distance":d})
        reverse=metric=="dot-product"; out=sorted(out,key=lambda z:z["distance"],reverse=reverse)[:k]
    return {"ok":True,"version":VERSION,"targetEmbeddingId":target_id,"metric":metric,"neighbors":out,
            "nearestNeighborIsRelationship":False,"semanticRelationshipInferred":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}

def normalize_projection(item:Any,index:int=0):
    raw=item if isinstance(item,dict) else {}
    method=_txt(_get(raw,"method","projectionMethod"),64).lower() or "user-supplied"
    if method not in PROJECTION_METHODS: method="other"
    coords=[]
    for j,p in enumerate(_list(_get(raw,"points","coordinates",default=[]))):
        if isinstance(p,dict):
            xyz=[_num(p.get("x")),_num(p.get("y")),_num(p.get("z"))]
            coords.append({"embeddingId":_txt(_get(p,"embeddingId","id"),512) or f"embedding-{j+1}","x":xyz[0],"y":xyz[1],"z":xyz[2],"metadata":_dict(p.get("metadata"))})
    rec={"schema":PROJECTION_SCHEMA,"version":VERSION,"projectionId":_txt(_get(raw,"projectionId","id"),512) or f"projection-{index+1}",
         "method":method,"dimensions":int(_get(raw,"dimensions",default=2) or 2),"parameters":_dict(raw.get("parameters")),"seed":_get(raw,"seed"),
         "points":coords,"sourceEmbeddingSetRef":_txt(raw.get("sourceEmbeddingSetRef"),1024),"provenanceRef":_txt(raw.get("provenanceRef"),1024),
         "derivedRepresentation":True,"projectionFaithfulnessCertified":False,"semanticRelationshipInferred":False}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return rec

def projection_registry(payload):
    items=_list(_get(payload,"projections","projectionResults",default=[])); ps=[normalize_projection(x,i) for i,x in enumerate(items)]
    return {"ok":True,"version":VERSION,"projections":ps,"count":len(ps),"derivedRepresentation":True,"projectionFaithfulnessCertified":False,"boundary":BOUNDARY}

def projection_audit(payload):
    ps=projection_registry(payload)["projections"]; rows=[]
    for p in ps:
        missing=[]
        if not p["method"]: missing.append("method")
        if not p["points"]: missing.append("points")
        if p["method"] in ("tsne","umap","pacmap","random-projection") and p["seed"] is None: missing.append("seed")
        rows.append({"projectionId":p["projectionId"],"complete":not missing,"missing":missing,"derivedRepresentation":True})
    return {"ok":True,"version":VERSION,"rows":rows,"allComplete":all(r["complete"] for r in rows),"projectionFaithfulnessCertified":False,"boundary":BOUNDARY}

def cluster_overlay(payload):
    xs=normalize_results(payload)["results"]["embeddings"]
    assignments=_dict(_get(payload,"clusterAssignments","clusters",default={}))
    rows=[{"embeddingId":x["embeddingId"],"cluster":assignments.get(x["embeddingId"]),"label":x["label"],"group":x["group"]} for x in xs]
    return {"ok":True,"version":VERSION,"rows":rows,"clusterMeaningInferred":False,"clusterMembershipIsEvidence":False,"boundary":BOUNDARY}

def label_overlay(payload):
    xs=normalize_results(payload)["results"]["embeddings"]
    return {"ok":True,"version":VERSION,"rows":[{"embeddingId":x["embeddingId"],"label":x["label"],"group":x["group"]} for x in xs],"boundary":BOUNDARY}

def drift_comparison(payload):
    before=_list(_get(payload,"beforeEmbeddings",default=[])); after=_list(_get(payload,"afterEmbeddings",default=[])); metric=_txt(_get(payload,"distanceMetric","metric"),64).lower() or "cosine"
    b={normalize_embedding(x,i)["embeddingId"]:normalize_embedding(x,i) for i,x in enumerate(before)}; a={normalize_embedding(x,i)["embeddingId"]:normalize_embedding(x,i) for i,x in enumerate(after)}
    rows=[]
    for eid in sorted(set(b)&set(a)):
        d=_distance(b[eid]["vector"],a[eid]["vector"],metric); rows.append({"embeddingId":eid,"distance":d})
    vals=[r["distance"] for r in rows if r["distance"] is not None]
    return {"ok":True,"version":VERSION,"metric":metric,"rows":rows,"meanDistance":statistics.fmean(vals) if vals else None,
            "driftCauseInferred":False,"semanticChangeCertified":False,"boundary":BOUNDARY}

def embedding_space_comparison(payload):
    left=payload.get("left") if isinstance(payload,dict) else {}; right=payload.get("right") if isinstance(payload,dict) else {}
    la=dimensionality_audit(left or {}); ra=dimensionality_audit(right or {})
    ls=study_spec(left or {})["study"]; rs=study_spec(right or {})["study"]
    dimensions={k:{"left":ls.get(k),"right":rs.get(k),"match":ls.get(k)==rs.get(k)} for k in ("modelRef","checkpointRef","layerRef","datasetRef","splitRef","normalization","distanceMetric")}
    return {"ok":True,"version":VERSION,"dimensions":dimensions,"leftDimensionAudit":la,"rightDimensionAudit":ra,
            "directlyComparable":all(v["match"] for v in dimensions.values()) and la["comparableForDistance"] and ra["comparableForDistance"],
            "automaticSuperiorityJudgment":False,"boundary":BOUNDARY}

def visual_spec(payload):
    view=_txt(_get(payload,"view","viewType"),64).lower() or "projection"
    if view not in VIEWS: view="projection"
    spec={"schema":"sc-lab-embedding-visual-spec/0.141.7","version":VERSION,"view":view,
          "sourceStudyFingerprint":study_spec(payload)["study"]["fingerprint"],"distanceMetric":study_spec(payload)["study"]["distanceMetric"],
          "derivedProjection":view=="projection","rawVectorsPreserved":True,"semanticRelationshipInferred":False,
          "projectionFaithfulnessCertified":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
    spec["fingerprint"]=_fp(spec); return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def core_visual_handoff(payload):
    v=visual_spec(payload)["visualSpec"]
    packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"visualSpec":v,"canonicalVisualObjectAuthority":"platform-core",
            "semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def export_bundle(payload):
    bundle={"schema":"sc-lab-embedding-explorer-export/0.141.7","version":VERSION,"study":study_spec(payload)["study"],
            "results":normalize_results(payload)["results"],"vectorRegistry":vector_registry(payload)["rows"],"provenanceAudit":provenance_audit(payload),
            "dimensionAudit":dimensionality_audit(payload),"visualSpec":visual_spec(payload)["visualSpec"],"boundary":BOUNDARY}
    bundle["fingerprint"]=_fp(bundle); return {"ok":True,"version":VERSION,"bundle":bundle,"boundary":BOUNDARY}

def snapshot(payload):
    stable={"study":study_spec(payload)["study"],"results":normalize_results(payload)["results"],"projections":projection_registry(payload)["projections"]}
    fp=_fp(stable); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"snapshotId":f"embedding-snapshot-{fp[:20]}","fingerprint":fp,"content":stable,
                            "semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
    return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}

def compare_snapshots(payload):
    a=_get(payload,"left","a",default={}); b=_get(payload,"right","b",default={})
    afp=_txt(_get(a,"fingerprint",default="")); bfp=_txt(_get(b,"fingerprint",default=""))
    return {"ok":True,"version":VERSION,"same":bool(afp and afp==bfp),"leftFingerprint":afp,"rightFingerprint":bfp,"automaticInterpretation":False,"boundary":BOUNDARY}

def reproducibility_packet(payload):
    s=snapshot(payload)["snapshot"]
    packet={"schema":"sc-lab-embedding-explorer-reproducibility/0.141.7","version":VERSION,"snapshot":s,
            "studyFingerprint":s["content"]["study"]["fingerprint"],"resultFingerprint":s["content"]["results"]["fingerprint"],
            "projectionFingerprints":[p["fingerprint"] for p in s["content"]["projections"]],"reproducibilityCertified":False,
            "semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"reproducibilityPacket":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}

def interpretation_boundary(payload=None):
    return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"nearestNeighborIsRelationship":False,"clusterMembershipIsMeaning":False,
            "projectionFaithfulnessCertified":False,"semanticRelationshipInferred":False,"embeddingIsEvidence":False}

def policy():
    return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"labExecutesEmbeddingExtraction":False,"labExecutesDimensionalityReduction":False,
            "nearestNeighborIsRelationship":False,"clusterMeaningInferred":False,"semanticRelationshipInferred":False,
            "projectionFaithfulnessCertified":False,"automaticModelEndorsement":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"studySchema":STUDY_SCHEMA,"embeddingSchema":EMBEDDING_SCHEMA,"projectionSchema":PROJECTION_SCHEMA,
            "workspaceHandoffSchema":WORKSPACE_HANDOFF_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"embeddingKinds":list(EMBEDDING_KINDS),
            "distanceMetrics":list(DISTANCE_METRICS),"projectionMethods":list(PROJECTION_METHODS),"views":list(VIEWS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":["installed-runtime-integrity-policy-retained","v0.141.6-explainability-line-retained","vector-source-provenance-explicit",
            "distance-metric-explicit","projection-method-and-parameters-explicit","projection-derived-state-labeled","dimension-consistency-audited",
            "no-neighbor-semantic-overclaim","no-cluster-meaning-inference","no-projection-faithfulness-certification","deterministic-snapshot"],"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"api_route_count":33,"embeddingExplorer":True,"neuralExplainabilityWorkspaceVersion":PREDECESSOR_VERSION,
            "ablationStudyFrameworkVersion":ABLATION_VERSION,"hyperparameterStudySearchResultsVersion":SEARCH_VERSION,"modelComparisonExperimentMatrixVersion":COMPARISON_VERSION,
            "trainingCurvesMetricsCheckpointVisualizationVersion":TELEMETRY_VERSION,"neuralArchitectureTrainingConfigurationVersion":ARCHITECTURE_VERSION,
            "machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,
            "manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"labExecutesEmbeddingExtraction":False,
            "labExecutesDimensionalityReduction":False,"nearestNeighborIsRelationship":False,"clusterMeaningInferred":False,
            "semanticRelationshipInferred":False,"projectionFaithfulnessCertified":False,"automaticModelEndorsement":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"api_route_count":33,"embeddingStudy":True,"workspaceExecutionHandoff":True,"embeddingNormalization":True,
            "vectorRegistry":True,"provenanceAudit":True,"dimensionalityAudit":True,"distanceMatrix":True,"neighborhoodQuery":True,"projectionRegistry":True,
            "projectionAudit":True,"clusterOverlay":True,"labelOverlay":True,"driftComparison":True,"spaceComparison":True,"visualSpecs":True,"coreVisualHandoff":True,
            "deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackages":True,"semanticRelationshipInferred":False,
            "projectionFaithfulnessCertified":False,"automaticModelEndorsement":False,"embeddingIsEvidence":False,"boundary":BOUNDARY}
