from __future__ import annotations
import copy, hashlib, json, math, statistics
from collections import Counter, deque
from datetime import datetime, timezone
from typing import Any

VERSION="0.146.0"
PREDECESSOR_VERSION="0.145.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-graph-network-science-research-workspace/0.146.0"
STUDY_SCHEMA="sc-lab-network-science-study/0.146.0"
GRAPH_SCHEMA="sc-lab-graph-object/0.146.0"
NODE_SCHEMA="sc-lab-graph-node/0.146.0"
EDGE_SCHEMA="sc-lab-graph-edge/0.146.0"
LAYER_SCHEMA="sc-lab-graph-layer/0.146.0"
TEMPORAL_SLICE_SCHEMA="sc-lab-temporal-network-slice/0.146.0"
SNAPSHOT_SCHEMA="sc-lab-graph-network-workspace-snapshot/0.146.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-graph-network-analysis-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-graph-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-graph-network-research-objects/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-graph-network-handoff/1.0"

BOUNDARY=(
    "The Graph & Network Science Research Workspace governs graph/network study design, node/edge/schema provenance, returned structural analyses, comparison, visualization, null-model state, uncertainty, sensitivity, review, and reproducibility. "
    "Workspace remains the execution authority for large or expensive graph algorithms; Workbench remains the prototype authority; Platform Core remains the canonical governed-object authority. "
    "An edge is only the relationship semantics explicitly declared by its source, graph connectivity is not causal evidence, centrality is not importance in every substantive sense, community detection is not ground-truth grouping, similarity is not an established relationship, and a structural pattern is not automatically a scientific explanation."
)

NETWORK_TYPES=("simple","directed","weighted","multigraph","bipartite","temporal","multilayer","multiplex","signed","attributed","spatial","knowledge","evidence","citation","flow","similarity","dependency","communication","co-occurrence","other")
EDGE_SEMANTICS=("observed","asserted","derived","similarity","correlation","causal-claim","citation","dependency","flow","communication","co-occurrence","alignment","membership","candidate","other")
ANALYSIS_FAMILIES=("structure","connectivity","centrality","community","path","distance","motif","flow","cut","bipartite","temporal","multilayer","null-model","comparison","robustness","uncertainty","sensitivity","spatial","signed","other")
COMMUNITY_METHODS=("connected-components","louvain","leiden","label-propagation","infomap","spectral","modularity","stochastic-block-model","custom","other")
CENTRALITY_METHODS=("degree","in-degree","out-degree","betweenness","closeness","eigenvector","pagerank","katz","harmonic","load","current-flow","custom","other")
NULL_MODELS=("configuration","degree-preserving","erdos-renyi","watts-strogatz","barabasi-albert","edge-swap","label-permutation","temporal-shuffle","weight-shuffle","custom","other")
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


def network_catalog():
    return {"ok":True,"version":VERSION,"networkTypes":list(NETWORK_TYPES),"edgeSemantics":list(EDGE_SEMANTICS),"analysisFamilies":list(ANALYSIS_FAMILIES),"communityMethods":list(COMMUNITY_METHODS),"centralityMethods":list(CENTRALITY_METHODS),"nullModels":list(NULL_MODELS),"automaticRelationshipInference":False,"automaticCausalInference":False,"boundary":BOUNDARY}


def normalize_node(payload:dict,index:int=0):
    p=_dict(payload)
    rec={"schema":NODE_SCHEMA,"version":VERSION,"nodeId":_txt(p.get("nodeId") or p.get("id"),512) or f"node-{index+1}-{_fp(p)[:12]}","label":_txt(p.get("label"),1024),"nodeType":_txt(p.get("nodeType") or p.get("type"),256),"attributes":_dict(p.get("attributes")),"sourceRef":_txt(p.get("sourceRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"time":p.get("time"),"layerRef":_txt(p.get("layerRef"),512),"metadata":_dict(p.get("metadata")),"scientificValidityCertified":False}
    rec["fingerprint"]=_fp(rec); return rec


def normalize_edge(payload:dict,index:int=0):
    p=_dict(payload); sem=_txt(p.get("semantics") or p.get("relationshipType"),64).lower() or "other"; sem=sem if sem in EDGE_SEMANTICS else "other"
    weight=_num(p.get("weight"))
    rec={"schema":EDGE_SCHEMA,"version":VERSION,"edgeId":_txt(p.get("edgeId") or p.get("id"),512) or f"edge-{index+1}-{_fp(p)[:12]}","source":_txt(p.get("source"),512),"target":_txt(p.get("target"),512),"semantics":sem,"directed":bool(p.get("directed",False)),"weight":weight,"sign":_num(p.get("sign")),"attributes":_dict(p.get("attributes")),"sourceRef":_txt(p.get("sourceRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"time":p.get("time"),"layerRef":_txt(p.get("layerRef"),512),"relationshipEstablished":bool(p.get("relationshipEstablished",False)) if sem in ("observed","asserted","citation","dependency","flow","communication","membership") else False,"candidateOnly":sem in ("candidate","similarity","correlation","derived"),"metadata":_dict(p.get("metadata"))}
    rec["fingerprint"]=_fp(rec); return rec


def normalize_layer(payload:dict,index:int=0):
    p=_dict(payload); rec={"schema":LAYER_SCHEMA,"version":VERSION,"layerId":_txt(p.get("layerId") or p.get("id"),512) or f"layer-{index+1}-{_fp(p)[:12]}","label":_txt(p.get("label"),1024),"semantics":_txt(p.get("semantics"),512),"nodeFilter":_dict(p.get("nodeFilter")),"edgeFilter":_dict(p.get("edgeFilter")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata"))}; rec["fingerprint"]=_fp(rec); return rec


def normalize_temporal_slice(payload:dict,index:int=0):
    p=_dict(payload); rec={"schema":TEMPORAL_SLICE_SCHEMA,"version":VERSION,"sliceId":_txt(p.get("sliceId") or p.get("id"),512) or f"slice-{index+1}-{_fp(p)[:12]}","label":_txt(p.get("label"),1024),"start":p.get("start"),"end":p.get("end"),"nodeRefs":[_txt(x,512) for x in _list(p.get("nodeRefs")) if _txt(x,512)],"edgeRefs":[_txt(x,512) for x in _list(p.get("edgeRefs")) if _txt(x,512)],"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata"))}; rec["fingerprint"]=_fp(rec); return rec


def normalize_graph(payload:dict):
    p=_dict(payload); nt=_txt(p.get("networkType"),64).lower() or "simple"; nt=nt if nt in NETWORK_TYPES else "other"
    nodes=[normalize_node(x,i) for i,x in enumerate(_list(p.get("nodes")))]; edges=[normalize_edge(x,i) for i,x in enumerate(_list(p.get("edges")))]; ids={n["nodeId"] for n in nodes}
    rec={"schema":GRAPH_SCHEMA,"version":VERSION,"graphId":_txt(p.get("graphId") or p.get("id"),512) or f"graph-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"networkType":nt,"directed":bool(p.get("directed", nt=="directed")),"multigraph":bool(p.get("multigraph",nt=="multigraph")),"weighted":bool(p.get("weighted",nt=="weighted" or any(e["weight"] is not None for e in edges))),"nodes":nodes,"edges":edges,"layers":[normalize_layer(x,i) for i,x in enumerate(_list(p.get("layers")))],"temporalSlices":[normalize_temporal_slice(x,i) for i,x in enumerate(_list(p.get("temporalSlices")))],"nodeCount":len(nodes),"edgeCount":len(edges),"danglingEndpointCount":sum(1 for e in edges if e["source"] not in ids or e["target"] not in ids),"sourceRef":_txt(p.get("sourceRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"construction":_dict(p.get("construction")),"limitations":[_txt(x,4096) for x in _list(p.get("limitations")) if _txt(x,4096)],"metadata":_dict(p.get("metadata")),"automaticRelationshipInference":False,"scientificValidityCertified":False}
    rec["fingerprint"]=_fp(rec); return rec


def normalize_study(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in SESSION_STATES else "draft"
    fam=_txt(p.get("analysisFamily"),64).lower() or "structure"; fam=fam if fam in ANALYSIS_FAMILIES else "other"
    rec={"schema":STUDY_SCHEMA,"version":VERSION,"studyId":_txt(p.get("studyId") or p.get("id"),512) or f"graph-study-{_fp(p)[:16]}","projectRef":_txt(p.get("projectRef"),512),"title":_txt(p.get("title"),1024) or "Graph & network science study","question":_txt(p.get("question"),4096),"state":state,"analysisFamily":fam,"graph":normalize_graph(p.get("graph") or {}),"analysisResults":_dict(p.get("analysisResults")),"nullModel":_dict(p.get("nullModel")),"sensitivity":_dict(p.get("sensitivity")),"uncertainty":_dict(p.get("uncertainty")),"review":_dict(p.get("review")),"limitations":[_txt(x,4096) for x in _list(p.get("limitations")) if _txt(x,4096)],"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"automaticCausalInference":False,"automaticScientificValidity":False}
    rec["fingerprint"]=_fp(rec); return rec


def workspace_state(payload:dict):
    s=normalize_study(payload.get("study") if isinstance(payload.get("study"),dict) else payload); g=s["graph"]
    return {"ok":True,"version":VERSION,"study":s,"summary":{"nodeCount":g["nodeCount"],"edgeCount":g["edgeCount"],"layerCount":len(g["layers"]),"temporalSliceCount":len(g["temporalSlices"]),"scientificValidityCertified":False},"boundary":BOUNDARY}


def schema_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); issues=[]
    if not g["nodes"]: issues.append("nodes-missing")
    if g["danglingEndpointCount"]: issues.append("dangling-edge-endpoints")
    if g["weighted"] and any(e["weight"] is None for e in g["edges"]): issues.append("weighted-graph-has-unweighted-edges")
    return {"ok":True,"version":VERSION,"issues":issues,"clean":not issues,"nodeCount":g["nodeCount"],"edgeCount":g["edgeCount"],"scientificValidityCertified":False,"boundary":BOUNDARY}


def provenance_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); missingNodes=[n["nodeId"] for n in g["nodes"] if not n["provenanceRef"] and not n["sourceRef"]]; missingEdges=[e["edgeId"] for e in g["edges"] if not e["provenanceRef"] and not e["sourceRef"]]
    return {"ok":True,"version":VERSION,"missingNodeProvenance":missingNodes,"missingEdgeProvenance":missingEdges,"complete":not missingNodes and not missingEdges,"provenanceCompletenessIsScientificValidity":False,"boundary":BOUNDARY}


def relationship_semantics_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); counts=Counter(e["semantics"] for e in g["edges"]); candidate=[e["edgeId"] for e in g["edges"] if e["candidateOnly"]]
    return {"ok":True,"version":VERSION,"semanticsCounts":dict(counts),"candidateEdgeRefs":candidate,"candidateEdgesAreEstablishedRelationships":False,"similarityIsRelationship":False,"automaticRelationshipInference":False,"boundary":BOUNDARY}


def directedness_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); mixed=sum(1 for e in g["edges"] if e["directed"]!=g["directed"])
    return {"ok":True,"version":VERSION,"graphDirected":g["directed"],"mixedDirectednessCount":mixed,"directednessAdequacyCertified":False,"boundary":BOUNDARY}


def weight_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); vals=[e["weight"] for e in g["edges"] if e["weight"] is not None]
    return {"ok":True,"version":VERSION,"weighted":g["weighted"],"weightedEdgeCount":len(vals),"weightSummary":_summary(vals),"weightMeaning":_txt(payload.get("weightMeaning"),1024),"weightSemanticsCertified":False,"boundary":BOUNDARY}


def multiplex_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); refs=Counter(e["layerRef"] for e in g["edges"] if e["layerRef"])
    return {"ok":True,"version":VERSION,"layerCount":len(g["layers"]),"edgeCountByLayer":dict(refs),"multiplex":g["networkType"] in ("multilayer","multiplex") or len(refs)>1,"crossLayerSemanticsCertified":False,"boundary":BOUNDARY}


def temporal_audit(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); timedNodes=sum(1 for n in g["nodes"] if n["time"] is not None); timedEdges=sum(1 for e in g["edges"] if e["time"] is not None)
    return {"ok":True,"version":VERSION,"temporal":g["networkType"]=="temporal" or bool(g["temporalSlices"]) or timedNodes>0 or timedEdges>0,"timedNodeCount":timedNodes,"timedEdgeCount":timedEdges,"sliceCount":len(g["temporalSlices"]),"temporalCausalityInferred":False,"boundary":BOUNDARY}


def _adj(g, directed=False):
    ids=[n["nodeId"] for n in g["nodes"]]; a={x:set() for x in ids}
    for e in g["edges"]:
        s,t=e["source"],e["target"]
        if s in a and t in a:
            a[s].add(t)
            if not directed: a[t].add(s)
    return a


def connectivity_summary(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); a=_adj(g,False); seen=set(); comps=[]
    for n in a:
        if n in seen: continue
        q=[n]; seen.add(n); c=[]
        while q:
            u=q.pop(); c.append(u)
            for v in a[u]:
                if v not in seen: seen.add(v); q.append(v)
        comps.append(c)
    return {"ok":True,"version":VERSION,"componentCount":len(comps),"componentSizes":[len(c) for c in comps],"largestComponentSize":max([len(c) for c in comps],default=0),"connected":len(comps)<=1 if a else False,"connectivityIsCausalEvidence":False,"boundary":BOUNDARY}


def degree_summary(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); ids=[n["nodeId"] for n in g["nodes"]]; deg=Counter({x:0 for x in ids}); indeg=Counter({x:0 for x in ids}); outdeg=Counter({x:0 for x in ids})
    for e in g["edges"]:
        s,t=e["source"],e["target"]
        if s in deg: outdeg[s]+=1; deg[s]+=1
        if t in deg: indeg[t]+=1; deg[t]+=1
        if not g["directed"]:
            if t in deg: outdeg[t]+=1
            if s in deg: indeg[s]+=1
    rows=[{"nodeRef":n,"degree":deg[n],"inDegree":indeg[n],"outDegree":outdeg[n]} for n in ids]
    return {"ok":True,"version":VERSION,"rows":rows,"degreeSummary":_summary([r["degree"] for r in rows]),"automaticImportanceInference":False,"boundary":BOUNDARY}


def density_summary(payload:dict):
    g=normalize_graph(payload.get("graph") or payload); n=g["nodeCount"]; m=g["edgeCount"]
    denom=n*(n-1) if g["directed"] else n*(n-1)/2; density=(m/denom if denom else 0.0)
    return {"ok":True,"version":VERSION,"nodeCount":n,"edgeCount":m,"directed":g["directed"],"density":density,"densityIsEvidence":False,"boundary":BOUNDARY}


def component_summary(payload:dict): return connectivity_summary(payload)

def centrality_summary(payload:dict):
    rows=_list(payload.get("rows")); method=_txt(payload.get("method"),64).lower() or "degree"; method=method if method in CENTRALITY_METHODS else "other"; vals=[r.get("value") for r in rows if isinstance(r,dict)]
    return {"ok":True,"version":VERSION,"method":method,"rows":rows,"valueSummary":_summary(vals),"automaticImportanceRanking":False,"centralityIsSubstantiveImportance":False,"boundary":BOUNDARY}


def path_summary(payload:dict):
    vals=_finite(payload.get("pathLengths") or []); return {"ok":True,"version":VERSION,"pathLengthSummary":_summary(vals),"sourceRef":_txt(payload.get("sourceRef"),512),"targetRef":_txt(payload.get("targetRef"),512),"pathRefs":_list(payload.get("pathRefs")),"pathImpliesCausality":False,"boundary":BOUNDARY}

def distance_matrix(payload:dict): return {"ok":True,"version":VERSION,"nodeRefs":_list(payload.get("nodeRefs")),"matrix":_list(payload.get("matrix")),"distanceDefinition":_txt(payload.get("distanceDefinition"),512),"automaticSemanticInference":False,"boundary":BOUNDARY}

def community_summary(payload:dict):
    method=_txt(payload.get("method"),64).lower() or "other"; method=method if method in COMMUNITY_METHODS else "other"; assignments=_dict(payload.get("assignments")); counts=Counter(str(v) for v in assignments.values())
    return {"ok":True,"version":VERSION,"method":method,"communityCount":len(counts),"sizes":dict(counts),"assignments":assignments,"modularity":_num(payload.get("modularity")),"communityIsGroundTruthGroup":False,"automaticLabelInterpretation":False,"boundary":BOUNDARY}

def assortativity_summary(payload:dict): return {"ok":True,"version":VERSION,"coefficient":_num(payload.get("coefficient")),"attribute":_txt(payload.get("attribute"),256),"associationIsCausation":False,"boundary":BOUNDARY}
def clustering_summary(payload:dict): return {"ok":True,"version":VERSION,"globalCoefficient":_num(payload.get("globalCoefficient")),"localValues":_list(payload.get("localValues")),"localSummary":_summary([x.get("value") for x in _list(payload.get("localValues")) if isinstance(x,dict)]),"clusteringIsCommunityTruth":False,"boundary":BOUNDARY}
def motif_summary(payload:dict): return {"ok":True,"version":VERSION,"motifs":_list(payload.get("motifs")),"nullModelRef":_txt(payload.get("nullModelRef"),512),"motifEnrichmentIsMechanism":False,"boundary":BOUNDARY}
def core_periphery_summary(payload:dict): return {"ok":True,"version":VERSION,"coreRefs":_list(payload.get("coreRefs")),"peripheryRefs":_list(payload.get("peripheryRefs")),"score":_num(payload.get("score")),"coreLabelIsSubstantiveImportance":False,"boundary":BOUNDARY}
def rich_club_summary(payload:dict): return {"ok":True,"version":VERSION,"coefficients":_list(payload.get("coefficients")),"normalized":bool(payload.get("normalized",False)),"richClubIsEliteStatus":False,"boundary":BOUNDARY}
def flow_summary(payload:dict): return {"ok":True,"version":VERSION,"sourceRef":_txt(payload.get("sourceRef"),512),"targetRef":_txt(payload.get("targetRef"),512),"value":_num(payload.get("value")),"edgeFlows":_list(payload.get("edgeFlows")),"flowIsCausalEffect":False,"boundary":BOUNDARY}
def cut_summary(payload:dict): return {"ok":True,"version":VERSION,"cutValue":_num(payload.get("cutValue")),"cutEdges":_list(payload.get("cutEdges")),"partition":_dict(payload.get("partition")),"cutIsNaturalBoundary":False,"boundary":BOUNDARY}
def bridge_articulation_summary(payload:dict): return {"ok":True,"version":VERSION,"bridgeEdgeRefs":_list(payload.get("bridgeEdgeRefs")),"articulationNodeRefs":_list(payload.get("articulationNodeRefs")),"structuralCriticalityIsRealWorldCriticality":False,"boundary":BOUNDARY}
def bipartite_summary(payload:dict): return {"ok":True,"version":VERSION,"leftNodeRefs":_list(payload.get("leftNodeRefs")),"rightNodeRefs":_list(payload.get("rightNodeRefs")),"projection":_dict(payload.get("projection")),"projectedEdgeIsOriginalRelationship":False,"boundary":BOUNDARY}
def multilayer_summary(payload:dict): return {"ok":True,"version":VERSION,"layers":_list(payload.get("layers")),"interlayerEdges":_list(payload.get("interlayerEdges")),"coupling":_dict(payload.get("coupling")),"crossLayerEquivalenceInferred":False,"boundary":BOUNDARY}
def temporal_network_summary(payload:dict): return {"ok":True,"version":VERSION,"slices":_list(payload.get("slices")),"nodePersistence":_dict(payload.get("nodePersistence")),"edgePersistence":_dict(payload.get("edgePersistence")),"turnover":_dict(payload.get("turnover")),"temporalOrderIsCausality":False,"boundary":BOUNDARY}


def null_model_audit(payload:dict):
    model=_txt(payload.get("nullModel"),64).lower() or "other"; model=model if model in NULL_MODELS else "other"
    return {"ok":True,"version":VERSION,"nullModel":model,"preservedProperties":_list(payload.get("preservedProperties")),"randomizationCount":payload.get("randomizationCount"),"seed":payload.get("seed"),"nullModelAdequacyCertified":False,"pValueIsMechanism":False,"boundary":BOUNDARY}
def randomization_plan(payload:dict): return {"ok":True,"version":VERSION,"nullModel":_txt(payload.get("nullModel"),64) or "configuration","replicates":payload.get("replicates"),"seedPolicy":_dict(payload.get("seedPolicy")),"preservedProperties":_list(payload.get("preservedProperties")),"executionAuthority":"workspace","automaticExecution":False,"boundary":BOUNDARY}
def network_comparison(payload:dict): return {"ok":True,"version":VERSION,"leftRef":_txt(payload.get("leftRef"),512),"rightRef":_txt(payload.get("rightRef"),512),"metrics":_dict(payload.get("metrics")),"differences":_dict(payload.get("differences")),"comparability":_dict(payload.get("comparability")),"automaticWinnerSelection":False,"boundary":BOUNDARY}
def metric_matrix(payload:dict): return {"ok":True,"version":VERSION,"networkRefs":_list(payload.get("networkRefs")),"metricKeys":_list(payload.get("metricKeys")),"rows":_list(payload.get("rows")),"automaticRanking":False,"boundary":BOUNDARY}
def node_metric_matrix(payload:dict): return {"ok":True,"version":VERSION,"nodeRefs":_list(payload.get("nodeRefs")),"metricKeys":_list(payload.get("metricKeys")),"rows":_list(payload.get("rows")),"automaticImportanceRanking":False,"boundary":BOUNDARY}
def edge_metric_matrix(payload:dict): return {"ok":True,"version":VERSION,"edgeRefs":_list(payload.get("edgeRefs")),"metricKeys":_list(payload.get("metricKeys")),"rows":_list(payload.get("rows")),"automaticRelationshipStrengthInference":False,"boundary":BOUNDARY}
def community_comparison(payload:dict): return {"ok":True,"version":VERSION,"left":_dict(payload.get("left")),"right":_dict(payload.get("right")),"agreementMetrics":_dict(payload.get("agreementMetrics")),"communityAgreementIsTruth":False,"boundary":BOUNDARY}
def temporal_comparison(payload:dict): return {"ok":True,"version":VERSION,"periods":_list(payload.get("periods")),"metrics":_list(payload.get("metrics")),"changePoints":_list(payload.get("changePoints")),"changePointIsCausalEvent":False,"boundary":BOUNDARY}
def sensitivity_audit(payload:dict): return {"ok":True,"version":VERSION,"perturbations":_list(payload.get("perturbations")),"metricChanges":_list(payload.get("metricChanges")),"structuralSensitivityIsCausality":False,"automaticRanking":False,"boundary":BOUNDARY}
def uncertainty_audit(payload:dict): return {"ok":True,"version":VERSION,"uncertainNodes":_list(payload.get("uncertainNodes")),"uncertainEdges":_list(payload.get("uncertainEdges")),"sampling":_dict(payload.get("sampling")),"metricIntervals":_dict(payload.get("metricIntervals")),"uncertaintyResolved":False,"boundary":BOUNDARY}


def visual_specification(payload:dict): return {"ok":True,"version":VERSION,"visual":{"family":_txt(payload.get("family"),128) or "network-workspace","title":_txt(payload.get("title"),1024),"layout":_txt(payload.get("layout"),128) or "force-directed","encodings":_dict(payload.get("encodings")),"layers":_list(payload.get("layers")),"dataRefs":_list(payload.get("dataRefs")),"edgeSemanticsLegendRequired":True,"derivedLayoutLabelRequired":True,"automaticInterpretation":False},"boundary":BOUNDARY}

def provenance_graph(payload:dict):
    s=normalize_study(payload.get("study") or payload); g=s["graph"]; nodes=[{"id":s["studyId"],"kind":"study"},{"id":g["graphId"],"kind":"graph"}]; edges=[{"source":s["studyId"],"target":g["graphId"],"relation":"analyzes"}]
    for n in g["nodes"]: nodes.append({"id":n["nodeId"],"kind":"node"}); edges.append({"source":g["graphId"],"target":n["nodeId"],"relation":"contains-node"})
    for e in g["edges"]: nodes.append({"id":e["edgeId"],"kind":"edge"}); edges.append({"source":g["graphId"],"target":e["edgeId"],"relation":"contains-edge"})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"automaticRelationshipInference":False,"scientificValidityCertified":False,"boundary":BOUNDARY}

def workspace_execution_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKSPACE_HANDOFF_SCHEMA,"studyRef":s["studyId"],"graphRef":s["graph"]["graphId"],"studyFingerprint":s["fingerprint"],"requestedOperation":_txt(payload.get("requestedOperation"),256) or "graph-analysis","executionAuthority":"workspace","automaticExecution":False,"labExecutesLargeGraphAlgorithms":False,"payload":_dict(payload.get("executionPayload"))},"boundary":BOUNDARY}
def workbench_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKBENCH_HANDOFF_SCHEMA,"studyRef":s["studyId"],"graphRef":s["graph"]["graphId"],"requestedPrototype":_txt(payload.get("requestedPrototype"),256),"executionAuthority":"workbench","automaticExecution":False},"boundary":BOUNDARY}
def core_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":CORE_HANDOFF_SCHEMA,"canonicalObjectAuthority":"platform-core","studyRef":s["studyId"],"graphRef":s["graph"]["graphId"],"studyFingerprint":s["fingerprint"],"automaticCanonicalization":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def research_os_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":RESEARCH_OS_HANDOFF_SCHEMA,"researchOSVersion":RESEARCH_OS_VERSION,"studyRef":s["studyId"],"targetPhase":_txt(payload.get("targetPhase"),128) or "analysis","automaticPhaseAdvance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def workspace_snapshot(payload:dict):
    s=normalize_study(payload.get("study") or payload); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"study":copy.deepcopy(s)}; snap["snapshotFingerprint"]=_fp(snap); return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}
def compare_snapshots(payload:dict):
    a=workspace_snapshot(payload.get("left") or {})["snapshot"]; b=workspace_snapshot(payload.get("right") or {})["snapshot"]; return {"ok":True,"version":VERSION,"sameWorkspaceState":a["snapshotFingerprint"]==b["snapshotFingerprint"],"leftFingerprint":a["snapshotFingerprint"],"rightFingerprint":b["snapshotFingerprint"],"automaticScientificConclusion":False,"boundary":BOUNDARY}
def export_bundle(payload:dict):
    s=normalize_study(payload.get("study") or payload); bundle={"schema":f"{SCHEMA}/export-bundle","version":VERSION,"study":s,"provenanceGraph":provenance_graph(s),"review":s["review"],"limitations":s["limitations"],"scientificValidityCertified":False}; bundle["fingerprint"]=_fp(bundle); return {"ok":True,"version":VERSION,"bundle":bundle,"scientificValidityCertified":False,"boundary":BOUNDARY}
def reproducibility_package(payload:dict):
    s=normalize_study(payload.get("study") or payload); pkg={"schema":f"{SCHEMA}/reproducibility-package","version":VERSION,"studyRef":s["studyId"],"graph":s["graph"],"analysisResults":s["analysisResults"],"nullModel":s["nullModel"],"sensitivity":s["sensitivity"],"uncertainty":s["uncertainty"],"review":s["review"],"limitations":s["limitations"],"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; pkg["fingerprint"]=_fp(pkg); return {"ok":True,"version":VERSION,"package":pkg,"boundary":BOUNDARY}
def publication_handoff(payload:dict):
    s=normalize_study(payload.get("study") or payload); return {"ok":True,"version":VERSION,"handoff":{"studyRef":s["studyId"],"studyFingerprint":s["fingerprint"],"review":s["review"],"limitations":s["limitations"],"publicationAccepted":False,"automaticAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None): return {"ok":True,"version":VERSION,"boundaries":{"edgeIsOnlyDeclaredSemantics":True,"connectivityIsCausality":False,"centralityIsUniversalImportance":False,"communityIsGroundTruthGroup":False,"similarityIsEstablishedRelationship":False,"structuralPatternIsScientificExplanation":False,"nullModelSignificanceIsMechanism":False,"graphMetricIsEvidence":False,"reproducibilityIsScientificValidity":False},"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"policy":{"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesLargeGraphAlgorithms":False,"labComputesDescriptiveGraphSummaries":True,"explicitEdgeSemantics":True,"automaticRelationshipInference":False,"automaticCausalInference":False,"automaticCommunityInterpretation":False,"automaticNodeImportanceRanking":False,"automaticScientificValidity":False,"graphMetricIsEvidence":False},"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"studySchema":STUDY_SCHEMA,"graphSchema":GRAPH_SCHEMA,"nodeSchema":NODE_SCHEMA,"edgeSchema":EDGE_SCHEMA,"layerSchema":LAYER_SCHEMA,"temporalSliceSchema":TEMPORAL_SLICE_SCHEMA,"networkTypes":list(NETWORK_TYPES),"edgeSemantics":list(EDGE_SEMANTICS),"analysisFamilies":list(ANALYSIS_FAMILIES),"communityMethods":list(COMMUNITY_METHODS),"centralityMethods":list(CENTRALITY_METHODS),"nullModels":list(NULL_MODELS),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"executionAuthoritySeparated":True,"edgeSemanticsExplicit":True,"structuralMetricsSeparatedFromEvidence":True,"communityInterpretationNotAutomatic":True,"causalInferenceDisabled":True,"reproducibilitySeparatedFromValidity":True,"predecessorCompatible":True},"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"graphNetworkScienceResearchWorkspace":True,"api_route_count":61,"predecessorVersion":PREDECESSOR_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesLargeGraphAlgorithms":False,"labComputesDescriptiveGraphSummaries":True,"explicitEdgeSemantics":True,"automaticRelationshipInference":False,"automaticCausalInference":False,"automaticCommunityInterpretation":False,"automaticNodeImportanceRanking":False,"automaticScientificValidity":False,"graphMetricIsEvidence":False,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"graphNodeEdgeObjectModel":True,"explicitRelationshipSemantics":True,"structuralSummaries":True,"centralityCommunityPathObjects":True,"motifFlowCutObjects":True,"bipartiteTemporalMultilayerObjects":True,"nullModelAndRandomizationObjects":True,"networkComparisonMatrices":True,"sensitivityUncertaintyAudits":True,"visualSpecification":True,"workspaceExecutionHandoff":True,"workbenchHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"graphMetricIsEvidence":False,"boundary":BOUNDARY}
