from __future__ import annotations
import copy, hashlib, json
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

VERSION="0.152.0"
PREDECESSOR_VERSION="0.151.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-cross-workspace-research-dependency-graph/0.152.0"
NODE_SCHEMA="sc-lab-research-dependency-node/0.152.0"
EDGE_SCHEMA="sc-lab-research-dependency-edge/0.152.0"
GRAPH_SCHEMA="sc-lab-research-dependency-graph/0.152.0"
CHANGE_SCHEMA="sc-lab-research-dependency-change-event/0.152.0"
STALENESS_SCHEMA="sc-lab-research-staleness-record/0.152.0"
REVIEW_LINK_SCHEMA="sc-lab-research-dependency-review-link/0.152.0"
VALIDATION_LINK_SCHEMA="sc-lab-research-dependency-validation-link/0.152.0"
PUBLICATION_LINK_SCHEMA="sc-lab-research-dependency-publication-link/0.152.0"
SNAPSHOT_SCHEMA="sc-lab-research-dependency-graph-snapshot/0.152.0"
WORKFLOW_HANDOFF_SCHEMA="sc-lab-scientific-workflow-dependency-graph-handoff/1.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-research-dependency-execution-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-research-dependency-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-research-dependency-governed-objects/1.0"
LIBRARY_HANDOFF_SCHEMA="sc-library-research-dependency-source-request/1.0"
GRAPH_STUDIO_HANDOFF_SCHEMA="sc-lab-graph-studio-research-dependency-visualization/1.0"
VALIDATION_HANDOFF_SCHEMA="sc-lab-model-validation-dependency-impact-handoff/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-dependency-graph-handoff/1.0"
INTEGRATED_LAB_HANDOFF_SCHEMA="sc-lab-integrated-computational-dependency-handoff/1.0"

BOUNDARY=(
    "The Cross-Workspace Research Dependency Graph records declared lineage, consumption, production, derivation, validation, review, visualization, publication, and execution dependencies across research workspaces. "
    "A dependency edge is not causal proof, evidentiary support, scientific importance, or a guarantee that changing an upstream object invalidates every downstream object. "
    "Impact and staleness outputs are review candidates, not automatic scientific invalidations. Platform Core remains canonical governed-object authority, Workspace remains primary compute authority, Workbench remains prototype authority, Knowledge Library remains source/document authority, and Lab governs dependency analysis, impact review, interpretation, and reproducibility."
)

WORKSPACES=("neural","linguistics","statistics-econometrics","simulation","graph-network","graph-ml","multimodal","validation","integrated-lab","workflow-orchestration","research-os","library","publication","other")
NODE_TYPES=("source","document","dataset","corpus","feature-set","parameter-set","runtime","environment","notebook","workflow","workflow-stage","analysis","statistical-model","simulation","graph","graph-analysis","ml-model","graph-ml-model","embedding","multimodal-model","prediction","validation-record","benchmark","finding","claim","figure","table","artifact","review","reproduction","publication","other")
EDGE_TYPES=("consumes","produces","derives-from","depends-on","parameterized-by","executed-in","generated-by","transforms","validates","benchmarks","reviews","reproduces","references","visualizes","publishes","supersedes","version-of","contains","aligns-with","links-to","custom")
DEPENDENCY_CLASSES=("computational","data-lineage","methodological","provenance","validation","review","publication","visualization","runtime","environment","reference","organizational","custom")
STALENESS_STATES=("current","candidate-stale","stale-reviewed","revalidation-required","recompute-required","superseded","unknown")
CHANGE_TYPES=("created","modified","replaced","superseded","invalidated","retracted","rerun","revalidated","reproduced","metadata-only","other")
EDGE_CONFIDENCE=("declared","derived","imported","reviewed")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _stable(v):
    x=copy.deepcopy(v)
    if isinstance(x,dict): x.pop("generatedAt",None)
    return x

def authority_registry():
    return {"ok":True,"version":VERSION,"authorities":{"canonicalGovernedObjects":"Platform Core","primaryCompute":"Workspace","prototypeCompute":"Workbench","sourceDocuments":"Knowledge Library","dependencyAnalysis":"Research Lab"},"labExecutesHeavyCompute":False,"dependencyMutationIsAutomatic":False}

def capability_summary():
    return {"ok":True,"version":VERSION,"crossWorkspaceDependencyGraph":True,"persistentLineageObjects":True,"impactAnalysis":True,"stalenessCandidates":True,"revalidationPlanning":True,"recomputePlanning":True,"publicationImpact":True,"graphStudioVisualization":True,"scientificValidityCertified":False}

def graph_schemas():
    return {"ok":True,"version":VERSION,"schemas":[SCHEMA,NODE_SCHEMA,EDGE_SCHEMA,GRAPH_SCHEMA,CHANGE_SCHEMA,STALENESS_SCHEMA,REVIEW_LINK_SCHEMA,VALIDATION_LINK_SCHEMA,PUBLICATION_LINK_SCHEMA,SNAPSHOT_SCHEMA]}

def graph_invariants():
    return {"ok":True,"version":VERSION,"invariants":{"nodeIdentityStable":True,"edgeSemanticsExplicit":True,"provenanceRetained":True,"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False,"impactCandidateIsInvalidation":False,"stalenessCandidateIsScientificInvalidation":False,"automaticGraphMutation":False}}

def catalog():
    return {"ok":True,"version":VERSION,"nodeTypes":list(NODE_TYPES),"edgeTypes":list(EDGE_TYPES),"dependencyClasses":list(DEPENDENCY_CLASSES),"stalenessStates":list(STALENESS_STATES),"changeTypes":list(CHANGE_TYPES),"edgeConfidence":list(EDGE_CONFIDENCE),"workspaces":list(WORKSPACES),"boundary":BOUNDARY}

def normalize_node(payload:dict):
    p=_dict(payload); typ=_txt(p.get("nodeType"),128).lower() or "other"; typ=typ if typ in NODE_TYPES else "other"; ws=_txt(p.get("workspaceId"),128).lower() or "other"; ws=ws if ws in WORKSPACES else "other"
    r={"schema":NODE_SCHEMA,"version":VERSION,"nodeId":_txt(p.get("nodeId") or p.get("id") or p.get("objectRef"),512) or f"node-{_fp(p)[:16]}","nodeType":typ,"workspaceId":ws,"objectRef":_txt(p.get("objectRef"),512),"title":_txt(p.get("title"),1024),"versionRef":_txt(p.get("versionRef"),512),"contentHash":_txt(p.get("contentHash"),256),"createdAt":_txt(p.get("createdAt"),128),"updatedAt":_txt(p.get("updatedAt"),128),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"limitations":_list(p.get("limitations")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_edge(payload:dict):
    p=_dict(payload); typ=_txt(p.get("edgeType"),128).lower() or "custom"; typ=typ if typ in EDGE_TYPES else "custom"; cls=_txt(p.get("dependencyClass"),128).lower() or "custom"; cls=cls if cls in DEPENDENCY_CLASSES else "custom"; confidence=_txt(p.get("confidence"),64).lower() or "declared"; confidence=confidence if confidence in EDGE_CONFIDENCE else "declared"
    r={"schema":EDGE_SCHEMA,"version":VERSION,"edgeId":_txt(p.get("edgeId") or p.get("id"),512) or f"edge-{_fp(p)[:16]}","sourceRef":_txt(p.get("sourceRef") or p.get("source"),512),"targetRef":_txt(p.get("targetRef") or p.get("target"),512),"edgeType":typ,"dependencyClass":cls,"confidence":confidence,"required":bool(p.get("required",True)),"workspaceBoundary":bool(p.get("workspaceBoundary",False)),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False}; r["fingerprint"]=_fp(r); return r

def normalize_graph(payload:dict):
    p=_dict(payload); nodes=[normalize_node(x) for x in _list(p.get("nodes")) if isinstance(x,dict)]; edges=[normalize_edge(x) for x in _list(p.get("edges")) if isinstance(x,dict)]
    r={"schema":GRAPH_SCHEMA,"version":VERSION,"graphId":_txt(p.get("graphId") or p.get("id"),512) or f"dependency-graph-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"projectRef":_txt(p.get("projectRef"),512),"nodes":nodes,"edges":edges,"provenance":_dict(p.get("provenance")),"automaticMutation":False,"scientificValidityCertified":False}; r["fingerprint"]=_fp(_stable(r)); return r

def normalize_change_event(payload:dict):
    p=_dict(payload); typ=_txt(p.get("changeType"),128).lower() or "other"; typ=typ if typ in CHANGE_TYPES else "other"; r={"schema":CHANGE_SCHEMA,"version":VERSION,"changeId":_txt(p.get("changeId") or p.get("id"),512) or f"change-{_fp(p)[:16]}","subjectRef":_txt(p.get("subjectRef"),512),"changeType":typ,"previousFingerprint":_txt(p.get("previousFingerprint"),256),"newFingerprint":_txt(p.get("newFingerprint"),256),"occurredAt":_txt(p.get("occurredAt"),128) or _now(),"reason":_txt(p.get("reason"),4096),"provenance":_dict(p.get("provenance")),"scientificInvalidationApplied":False}; r["fingerprint"]=_fp(r); return r

def normalize_staleness_record(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),128).lower() or "candidate-stale"; state=state if state in STALENESS_STATES else "unknown"; r={"schema":STALENESS_SCHEMA,"version":VERSION,"recordId":_txt(p.get("recordId") or p.get("id"),512) or f"stale-{_fp(p)[:16]}","subjectRef":_txt(p.get("subjectRef"),512),"triggerRef":_txt(p.get("triggerRef"),512),"state":state,"pathRefs":_list(p.get("pathRefs")),"reason":_txt(p.get("reason"),4096),"reviewRequired":True,"automaticInvalidation":False,"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def _link(schema:str,payload:dict,kind:str):
    p=_dict(payload); r={"schema":schema,"version":VERSION,"linkId":_txt(p.get("linkId") or p.get("id"),512) or f"{kind}-{_fp(p)[:16]}","subjectRef":_txt(p.get("subjectRef"),512),"linkedRef":_txt(p.get("linkedRef"),512),"status":_txt(p.get("status"),128) or "linked","provenance":_dict(p.get("provenance")),"automaticScientificDecision":False}; r["fingerprint"]=_fp(r); return r

def normalize_review_link(payload:dict): return _link(REVIEW_LINK_SCHEMA,payload,"review")
def normalize_validation_link(payload:dict): return _link(VALIDATION_LINK_SCHEMA,payload,"validation")
def normalize_publication_link(payload:dict): return _link(PUBLICATION_LINK_SCHEMA,payload,"publication")

def _parts(payload:dict):
    p=_dict(payload); nodes=[normalize_node(x) for x in _list(p.get("nodes")) if isinstance(x,dict)]; edges=[normalize_edge(x) for x in _list(p.get("edges")) if isinstance(x,dict)]; nmap={n["nodeId"]:n for n in nodes}; return p,nodes,edges,nmap

def _adj(edges,reverse=False,classes=None,types=None):
    a=defaultdict(list)
    for e in edges:
        if classes and e["dependencyClass"] not in classes: continue
        if types and e["edgeType"] not in types: continue
        s,t=(e["targetRef"],e["sourceRef"]) if reverse else (e["sourceRef"],e["targetRef"]); a[s].append((t,e))
    return a

def graph_state(payload:dict):
    p,n,e,nm=_parts(payload); return {"ok":True,"version":VERSION,"graph":normalize_graph(p),"nodeCount":len(n),"edgeCount":len(e),"workspaceCount":len(set(x["workspaceId"] for x in n)),"automaticGraphMutation":False}

def schema_audit(payload:dict):
    _,nodes,edges,_=_parts(payload); bad_nodes=[n["nodeId"] for n in nodes if n["nodeType"] not in NODE_TYPES]; bad_edges=[e["edgeId"] for e in edges if e["edgeType"] not in EDGE_TYPES or e["dependencyClass"] not in DEPENDENCY_CLASSES]; return {"ok":True,"version":VERSION,"invalidNodeRefs":bad_nodes,"invalidEdgeRefs":bad_edges,"clean":not bad_nodes and not bad_edges}

def provenance_audit(payload:dict):
    _,nodes,edges,_=_parts(payload); missing_nodes=[n["nodeId"] for n in nodes if not n["provenance"]]; missing_edges=[e["edgeId"] for e in edges if not e["provenance"]]; return {"ok":True,"version":VERSION,"missingNodeProvenance":missing_nodes,"missingEdgeProvenance":missing_edges,"complete":not missing_nodes and not missing_edges,"provenanceCompletenessIsScientificValidity":False}

def edge_semantics_audit(payload:dict):
    _,_,edges,_=_parts(payload); ambiguous=[e["edgeId"] for e in edges if e["edgeType"]=="custom" or e["dependencyClass"]=="custom"]; return {"ok":True,"version":VERSION,"ambiguousEdgeRefs":ambiguous,"explicitSemantics":not ambiguous,"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False}

def reference_integrity_audit(payload:dict):
    _,nodes,edges,nm=_parts(payload); missing=[]
    for e in edges:
        if e["sourceRef"] not in nm: missing.append({"edgeRef":e["edgeId"],"missingRef":e["sourceRef"],"role":"source"})
        if e["targetRef"] not in nm: missing.append({"edgeRef":e["edgeId"],"missingRef":e["targetRef"],"role":"target"})
    return {"ok":True,"version":VERSION,"missingReferences":missing,"clean":not missing}

def workspace_membership_audit(payload:dict):
    _,nodes,_,_=_parts(payload); unknown=[n["nodeId"] for n in nodes if n["workspaceId"]=="other"]; return {"ok":True,"version":VERSION,"unknownWorkspaceNodeRefs":unknown,"complete":not unknown}

def authority_audit(payload:dict):
    p=_dict(payload); declared=_dict(p.get("authorities")); expected=authority_registry()["authorities"]; conflicts=[k for k,v in declared.items() if k in expected and v!=expected[k]]; return {"ok":True,"version":VERSION,"conflicts":conflicts,"clean":not conflicts,"authorities":expected,"automaticAuthorityMutation":False}

def duplicate_node_audit(payload:dict):
    _,nodes,_,_=_parts(payload); seen=set(); dup=[]
    for n in nodes:
        if n["nodeId"] in seen: dup.append(n["nodeId"])
        seen.add(n["nodeId"])
    return {"ok":True,"version":VERSION,"duplicateNodeRefs":dup,"clean":not dup}

def duplicate_edge_audit(payload:dict):
    _,_,edges,_=_parts(payload); seen=set(); dup=[]
    for e in edges:
        key=(e["sourceRef"],e["targetRef"],e["edgeType"],e["dependencyClass"])
        if key in seen: dup.append(e["edgeId"])
        seen.add(key)
    return {"ok":True,"version":VERSION,"duplicateEdgeRefs":dup,"clean":not dup}

def self_dependency_audit(payload:dict):
    _,_,edges,_=_parts(payload); refs=[e["edgeId"] for e in edges if e["sourceRef"] and e["sourceRef"]==e["targetRef"]]; return {"ok":True,"version":VERSION,"selfDependencyEdgeRefs":refs,"clean":not refs,"selfDependencyIsCausalProof":False}

def _computational_edges(edges): return [e for e in edges if e["dependencyClass"] in ("computational","data-lineage","runtime","environment") and e["edgeType"] not in ("references","reviews","visualizes","publishes","links-to")]

def _topology(nodes,edges):
    ids=[n["nodeId"] for n in nodes]; indeg={x:0 for x in ids}; out=defaultdict(list)
    for e in _computational_edges(edges):
        s,t=e["sourceRef"],e["targetRef"]
        if s in indeg and t in indeg: out[s].append(t); indeg[t]+=1
    q=deque(sorted(k for k,v in indeg.items() if v==0)); order=[]
    while q:
        x=q.popleft(); order.append(x)
        for y in sorted(out[x]):
            indeg[y]-=1
            if indeg[y]==0: q.append(y)
    cycles=sorted(k for k,v in indeg.items() if v>0); return order,cycles

def computational_cycle_audit(payload:dict):
    _,nodes,edges,_=_parts(payload); order,cycles=_topology(nodes,edges); return {"ok":True,"version":VERSION,"acyclic":not cycles,"topologicalOrder":order,"cycleCandidateRefs":cycles,"cycleCandidateIsScientificInvalidation":False}

def strongly_connected_components(payload:dict):
    _,nodes,edges,_=_parts(payload); ids=[n["nodeId"] for n in nodes]; adj={x:[] for x in ids}; radj={x:[] for x in ids}
    for e in edges:
        s,t=e["sourceRef"],e["targetRef"]
        if s in adj and t in adj: adj[s].append(t); radj[t].append(s)
    seen=set(); order=[]
    def dfs(x):
        seen.add(x)
        for y in adj[x]:
            if y not in seen: dfs(y)
        order.append(x)
    for x in ids:
        if x not in seen: dfs(x)
    seen.clear(); comps=[]
    def rdfs(x,c):
        seen.add(x); c.append(x)
        for y in radj[x]:
            if y not in seen: rdfs(y,c)
    for x in reversed(order):
        if x not in seen:
            c=[]; rdfs(x,c); comps.append(sorted(c))
    return {"ok":True,"version":VERSION,"components":comps,"componentCount":len(comps),"componentIsScientificGroup":False}

def _degree(payload:dict):
    _,nodes,edges,_=_parts(payload); d={n["nodeId"]:{"in":0,"out":0} for n in nodes}
    for e in edges:
        if e["sourceRef"] in d:d[e["sourceRef"]]["out"]+=1
        if e["targetRef"] in d:d[e["targetRef"]]["in"]+=1
    return d

def source_node_summary(payload:dict):
    d=_degree(payload); return {"ok":True,"version":VERSION,"nodeRefs":sorted(k for k,v in d.items() if v["in"]==0),"sourceNodeIsEvidenceSource":False}

def terminal_node_summary(payload:dict):
    d=_degree(payload); return {"ok":True,"version":VERSION,"nodeRefs":sorted(k for k,v in d.items() if v["out"]==0),"terminalNodeIsFinalConclusion":False}

def orphan_node_summary(payload:dict):
    d=_degree(payload); return {"ok":True,"version":VERSION,"nodeRefs":sorted(k for k,v in d.items() if v["in"]==0 and v["out"]==0),"orphanNodeIsInvalid":False}

def degree_summary(payload:dict): return {"ok":True,"version":VERSION,"degrees":_degree(payload),"degreeIsScientificImportance":False}

def _count_field(items,key):
    out={}
    for x in items: out[x[key]]=out.get(x[key],0)+1
    return dict(sorted(out.items()))
def dependency_type_summary(payload:dict):
    _,_,edges,_=_parts(payload); return {"ok":True,"version":VERSION,"counts":_count_field(edges,"dependencyClass"),"countIsScientificImportance":False}
def object_type_summary(payload:dict):
    _,nodes,_,_=_parts(payload); return {"ok":True,"version":VERSION,"counts":_count_field(nodes,"nodeType"),"countIsScientificImportance":False}
def workspace_summary(payload:dict):
    _,nodes,_,_=_parts(payload); return {"ok":True,"version":VERSION,"counts":_count_field(nodes,"workspaceId"),"countIsScientificImportance":False}

def cross_workspace_edge_summary(payload:dict):
    _,_,edges,nm=_parts(payload); items=[]
    for e in edges:
        a,b=nm.get(e["sourceRef"]),nm.get(e["targetRef"])
        if a and b and a["workspaceId"]!=b["workspaceId"]: items.append({"edgeRef":e["edgeId"],"fromWorkspace":a["workspaceId"],"toWorkspace":b["workspaceId"],"edgeType":e["edgeType"]})
    return {"ok":True,"version":VERSION,"edges":items,"count":len(items),"crossWorkspaceEdgeIsScientificIntegrationProof":False}

def cross_workspace_matrix(payload:dict):
    _,_,edges,nm=_parts(payload); m={}
    for e in edges:
        a,b=nm.get(e["sourceRef"]),nm.get(e["targetRef"])
        if a and b:
            k=f'{a["workspaceId"]}->{b["workspaceId"]}'; m[k]=m.get(k,0)+1
    return {"ok":True,"version":VERSION,"matrix":dict(sorted(m.items())),"countIsScientificImportance":False}

def object_type_matrix(payload:dict):
    _,_,edges,nm=_parts(payload); m={}
    for e in edges:
        a,b=nm.get(e["sourceRef"]),nm.get(e["targetRef"])
        if a and b:
            k=f'{a["nodeType"]}->{b["nodeType"]}'; m[k]=m.get(k,0)+1
    return {"ok":True,"version":VERSION,"matrix":dict(sorted(m.items())),"countIsScientificImportance":False}

def dependency_type_matrix(payload:dict):
    _,_,edges,_=_parts(payload); m={}
    for e in edges:
        k=f'{e["dependencyClass"]}:{e["edgeType"]}'; m[k]=m.get(k,0)+1
    return {"ok":True,"version":VERSION,"matrix":dict(sorted(m.items())),"dependencyClassIsCausalClass":False}

def _neighbors(payload,reverse=False):
    p,nodes,edges,_=_parts(payload); ref=_txt(p.get("nodeRef") or p.get("subjectRef"),512); adj=_adj(edges,reverse=reverse); return ref,adj.get(ref,[])
def direct_dependencies(payload:dict):
    ref,items=_neighbors(payload,True); return {"ok":True,"version":VERSION,"nodeRef":ref,"nodeRefs":sorted(x for x,_ in items),"dependencyEdgeIsCausalProof":False}
def direct_dependents(payload:dict):
    ref,items=_neighbors(payload,False); return {"ok":True,"version":VERSION,"nodeRef":ref,"nodeRefs":sorted(x for x,_ in items),"dependencyEdgeIsCausalProof":False}

def _closure(payload,reverse=False):
    p,nodes,edges,_=_parts(payload); start=_txt(p.get("nodeRef") or p.get("subjectRef"),512); adj=_adj(edges,reverse=reverse); seen=set(); q=deque([start]); depth={start:0}
    while q:
        x=q.popleft()
        for y,_ in adj.get(x,[]):
            if y not in seen and y!=start: seen.add(y); depth[y]=depth[x]+1; q.append(y)
    return start,sorted(seen),depth
def upstream_closure(payload:dict):
    s,refs,depth=_closure(payload,True); return {"ok":True,"version":VERSION,"nodeRef":s,"nodeRefs":refs,"depth":depth,"transitiveDependencyIsCausalProof":False}
def downstream_closure(payload:dict):
    s,refs,depth=_closure(payload,False); return {"ok":True,"version":VERSION,"nodeRef":s,"nodeRefs":refs,"depth":depth,"impactCandidates":refs,"automaticInvalidation":False}
def transitive_closure(payload:dict):
    p,nodes,edges,_=_parts(payload); pairs=[]
    for n in nodes:
        _,refs,_=_closure({"nodeRef":n["nodeId"],"nodes":nodes,"edges":edges},False)
        pairs.extend({"sourceRef":n["nodeId"],"targetRef":x} for x in refs)
    return {"ok":True,"version":VERSION,"pairs":pairs,"pairCount":len(pairs),"transitiveDependencyIsCausalProof":False}

def shortest_dependency_path(payload:dict):
    p,nodes,edges,_=_parts(payload); s=_txt(p.get("sourceRef"),512); t=_txt(p.get("targetRef"),512); adj=_adj(edges); q=deque([s]); prev={s:None}
    while q and t not in prev:
        x=q.popleft()
        for y,_ in adj.get(x,[]):
            if y not in prev: prev[y]=x; q.append(y)
    path=[]
    if t in prev:
        x=t
        while x is not None: path.append(x); x=prev[x]
        path.reverse()
    return {"ok":True,"version":VERSION,"sourceRef":s,"targetRef":t,"path":path,"found":bool(path),"shortestPathIsMechanism":False}

def all_dependency_paths(payload:dict):
    p,nodes,edges,_=_parts(payload); s=_txt(p.get("sourceRef"),512); t=_txt(p.get("targetRef"),512); max_paths=max(1,min(100,int(p.get("maxPaths",25) or 25))); max_depth=max(1,min(100,int(p.get("maxDepth",20) or 20))); adj=_adj(edges); paths=[]
    def dfs(x,path):
        if len(paths)>=max_paths or len(path)>max_depth:return
        if x==t: paths.append(path[:]); return
        for y,_ in adj.get(x,[]):
            if y not in path: dfs(y,path+[y])
    if s: dfs(s,[s])
    return {"ok":True,"version":VERSION,"paths":paths,"truncated":len(paths)>=max_paths,"pathIsMechanism":False}

def lineage_chain(payload:dict): return all_dependency_paths(payload)
def provenance_path(payload:dict):
    r=shortest_dependency_path(payload); r["provenancePathIsScientificProof"]=False; return r

def dependency_depth(payload:dict):
    s,refs,depth=_closure(payload,False); return {"ok":True,"version":VERSION,"nodeRef":s,"maxDepth":max(depth.values()) if depth else 0,"depth":depth,"depthIsScientificImportance":False}
def dependency_breadth(payload:dict):
    s,refs,depth=_closure(payload,False); counts={}
    for k,v in depth.items(): counts[v]=counts.get(v,0)+1
    return {"ok":True,"version":VERSION,"nodeRef":s,"breadthByDepth":counts,"breadthIsScientificImportance":False}

def longest_dependency_chain_candidates(payload:dict):
    _,nodes,edges,_=_parts(payload); order,cycles=_topology(nodes,edges)
    if cycles:return {"ok":True,"version":VERSION,"acyclic":False,"chains":[],"longestChainIsScientificImportance":False}
    adj=_adj(_computational_edges(edges)); best={n["nodeId"]:[n["nodeId"]] for n in nodes}
    for x in order:
        for y,_ in adj.get(x,[]):
            cand=best.get(x,[x])+[y]
            if len(cand)>len(best.get(y,[y])):best[y]=cand
    mx=max((len(v) for v in best.values()),default=0); chains=sorted({tuple(v) for v in best.values() if len(v)==mx})
    return {"ok":True,"version":VERSION,"acyclic":True,"chains":[list(x) for x in chains],"length":mx,"longestChainIsScientificImportance":False}

def bridge_workspace_summary(payload:dict): return cross_workspace_edge_summary(payload)
def boundary_crossing_summary(payload:dict): return cross_workspace_matrix(payload)

def _impact(payload:dict,node_type=None):
    p,nodes,edges,nm=_parts(payload); changed=[str(x) for x in _list(p.get("changedRefs"))] or [_txt(p.get("nodeRef") or p.get("subjectRef"),512)]; impacted=set(); depth={};
    for c in changed:
        _,refs,d=_closure({"nodeRef":c,"nodes":nodes,"edges":edges},False)
        for r in refs: impacted.add(r); depth[r]=min(depth.get(r,10**9),d.get(r,0))
    if node_type: impacted={r for r in impacted if nm.get(r,{}).get("nodeType")==node_type}
    return {"ok":True,"version":VERSION,"changedRefs":changed,"impactedRefs":sorted(impacted),"depth":depth,"impactCandidatesOnly":True,"automaticInvalidation":False,"impactIsScientificInvalidation":False}
def change_impact(payload:dict): return _impact(payload)
def blast_radius(payload:dict):
    r=_impact(payload); r["candidateCount"]=len(r["impactedRefs"]); r["blastRadiusIsScientificSeverity"]=False; return r
def affected_outputs(payload:dict): return _impact(payload)
def affected_findings(payload:dict): return _impact(payload,"finding")
def affected_figures(payload:dict): return _impact(payload,"figure")
def affected_publications(payload:dict): return _impact(payload,"publication")
def affected_validation_records(payload:dict): return _impact(payload,"validation-record")

def stale_candidate_report(payload:dict):
    r=_impact(payload); r["records"]=[normalize_staleness_record({"subjectRef":x,"triggerRef":r["changedRefs"][0] if r["changedRefs"] else "","state":"candidate-stale","pathRefs":[]}) for x in r["impactedRefs"]]; r["stalenessCandidateIsScientificInvalidation"]=False; return r

def staleness_propagation_plan(payload:dict):
    r=stale_candidate_report(payload); return {"ok":True,"version":VERSION,"candidateRecords":r["records"],"reviewRequired":True,"automaticPropagation":False,"automaticInvalidation":False}
def revalidation_plan(payload:dict):
    r=_impact(payload,"validation-record"); return {"ok":True,"version":VERSION,"validationRefs":r["impactedRefs"],"actions":[{"validationRef":x,"action":"review-for-revalidation"} for x in r["impactedRefs"]],"automaticRevalidation":False}
def recompute_plan(payload:dict):
    r=_impact(payload); return {"ok":True,"version":VERSION,"candidateStageOrArtifactRefs":r["impactedRefs"],"automaticRecompute":False,"humanReviewRequired":True}
def review_impact_plan(payload:dict):
    r=_impact(payload,"review"); return {"ok":True,"version":VERSION,"reviewRefs":r["impactedRefs"],"automaticReviewInvalidation":False}
def publication_impact_plan(payload:dict):
    r=_impact(payload,"publication"); return {"ok":True,"version":VERSION,"publicationRefs":r["impactedRefs"],"automaticRetraction":False,"publicationImpactIsRetractionDecision":False}

def _typed_impact(payload:dict,label:str):
    r=_impact(payload); r["impactType"]=label; return r
def supersession_impact(payload:dict): return _typed_impact(payload,"supersession")
def version_impact(payload:dict): return _typed_impact(payload,"version")
def parameter_impact(payload:dict): return _typed_impact(payload,"parameter")
def runtime_impact(payload:dict): return _typed_impact(payload,"runtime")
def environment_impact(payload:dict): return _typed_impact(payload,"environment")
def source_impact(payload:dict): return _typed_impact(payload,"source")
def dataset_impact(payload:dict): return _typed_impact(payload,"dataset")
def model_impact(payload:dict): return _typed_impact(payload,"model")
def simulation_impact(payload:dict): return _typed_impact(payload,"simulation")
def graph_impact(payload:dict): return _typed_impact(payload,"graph")
def multimodal_impact(payload:dict): return _typed_impact(payload,"multimodal")
def validation_impact(payload:dict): return _typed_impact(payload,"validation")
def finding_impact(payload:dict): return _typed_impact(payload,"finding")
def artifact_impact(payload:dict): return _typed_impact(payload,"artifact")
def workflow_impact(payload:dict): return _typed_impact(payload,"workflow")

def dependency_diff(payload:dict):
    p=_dict(payload); a=normalize_graph(_dict(p.get("a"))); b=normalize_graph(_dict(p.get("b"))); an={n["nodeId"] for n in a["nodes"]}; bn={n["nodeId"] for n in b["nodes"]}; ae={(e["sourceRef"],e["targetRef"],e["edgeType"],e["dependencyClass"]) for e in a["edges"]}; be={(e["sourceRef"],e["targetRef"],e["edgeType"],e["dependencyClass"]) for e in b["edges"]}; return {"ok":True,"version":VERSION,"addedNodes":sorted(bn-an),"removedNodes":sorted(an-bn),"addedEdges":sorted(be-ae),"removedEdges":sorted(ae-be),"changeIsScientificInvalidation":False}

def snapshot(payload:dict):
    g=normalize_graph(payload); s={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"graph":g,"scientificValidityCertified":False}; s["fingerprint"]=_fp(_stable(s)); return {"ok":True,"version":VERSION,"snapshot":s}
def compare_snapshots(payload:dict):
    p=_dict(payload); a=_dict(p.get("a")); b=_dict(p.get("b")); return {"ok":True,"version":VERSION,"sameFingerprint":_txt(a.get("fingerprint"),256)==_txt(b.get("fingerprint"),256),"aFingerprint":_txt(a.get("fingerprint"),256),"bFingerprint":_txt(b.get("fingerprint"),256),"equalityIsScientificEquivalence":False}
def graph_diff(payload:dict): return dependency_diff(payload)

def dependency_bundle(payload:dict):
    g=normalize_graph(payload); return {"ok":True,"version":VERSION,"bundle":{"schema":SCHEMA,"graph":g,"catalog":catalog(),"authorityRegistry":authority_registry(),"boundary":BOUNDARY,"scientificValidityCertified":False}}

def visual_specification(payload:dict):
    _,nodes,edges,nm=_parts(payload); return {"ok":True,"version":VERSION,"renderer":"graph-studio","nodes":[{"id":n["nodeId"],"label":n["title"] or n["nodeId"],"nodeType":n["nodeType"],"workspaceId":n["workspaceId"]} for n in nodes],"edges":[{"id":e["edgeId"],"source":e["sourceRef"],"target":e["targetRef"],"edgeType":e["edgeType"],"dependencyClass":e["dependencyClass"]} for e in edges],"visualizationIsEvidence":False}
def dependency_dashboard(payload:dict):
    return {"ok":True,"version":VERSION,"panels":{"summary":graph_state(payload),"workspaces":workspace_summary(payload),"types":dependency_type_summary(payload),"impact":_impact(payload) if (_dict(payload).get("changedRefs") or _dict(payload).get("nodeRef")) else None},"dashboardIsScientificConclusion":False}

def _handoff(schema:str,target:str,payload:dict):
    p=_dict(payload); h={"schema":schema,"version":VERSION,"target":target,"graphRef":_txt(p.get("graphRef"),512),"nodeRefs":_list(p.get("nodeRefs")),"edgeRefs":_list(p.get("edgeRefs")),"payload":_dict(p.get("payload")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False,"publicationAccepted":False,"automaticMutation":False}; h["fingerprint"]=_fp(h); return {"ok":True,"version":VERSION,"handoff":h}
def graph_studio_handoff(payload:dict): return _handoff(GRAPH_STUDIO_HANDOFF_SCHEMA,"Graph Studio",payload)
def workflow_orchestration_handoff(payload:dict): return _handoff(WORKFLOW_HANDOFF_SCHEMA,"Scientific Workflow & Experiment Orchestration",payload)
def integrated_lab_handoff(payload:dict): return _handoff(INTEGRATED_LAB_HANDOFF_SCHEMA,"Integrated Computational Research Laboratory",payload)
def workspace_execution_handoff(payload:dict): return _handoff(WORKSPACE_HANDOFF_SCHEMA,"Workspace",payload)
def workbench_handoff(payload:dict): return _handoff(WORKBENCH_HANDOFF_SCHEMA,"Workbench",payload)
def core_handoff(payload:dict): return _handoff(CORE_HANDOFF_SCHEMA,"Platform Core",payload)
def library_handoff(payload:dict): return _handoff(LIBRARY_HANDOFF_SCHEMA,"Knowledge Library",payload)
def validation_handoff(payload:dict): return _handoff(VALIDATION_HANDOFF_SCHEMA,"Scientific Model Validation & Benchmark Laboratory",payload)
def research_os_handoff(payload:dict): return _handoff(RESEARCH_OS_HANDOFF_SCHEMA,"Scientific Research Operating System",payload)
def publication_handoff(payload:dict): return _handoff(PUBLICATION_LINK_SCHEMA,"Publication",payload)

def reproducibility_package(payload:dict):
    g=normalize_graph(payload); package={"schema":"sc-lab-research-dependency-reproducibility-package/0.152.0","version":VERSION,"graph":g,"authorityRegistry":authority_registry(),"boundary":BOUNDARY,"reproductionCertified":False,"scientificValidityCertified":False}; package["fingerprint"]=_fp(_stable(package)); return {"ok":True,"version":VERSION,"package":package}
def export_bundle(payload:dict):
    return {"ok":True,"version":VERSION,"bundle":{"graph":normalize_graph(payload),"snapshot":snapshot(payload)["snapshot"],"catalog":catalog(),"scientificValidityCertified":False}}
def review_packet(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"packet":{"graphRef":_txt(p.get("graphRef"),512),"nodeRefs":_list(p.get("nodeRefs")),"edgeRefs":_list(p.get("edgeRefs")),"questions":_list(p.get("questions")),"humanReviewRequired":True,"automaticApproval":False}}
def impact_review_packet(payload:dict):
    r=_impact(payload); return {"ok":True,"version":VERSION,"packet":{"changedRefs":r["changedRefs"],"impactCandidates":r["impactedRefs"],"humanReviewRequired":True,"automaticInvalidation":False}}

def dependency_query(payload:dict):
    p,nodes,edges,_=_parts(payload); nts=set(_list(p.get("nodeTypes"))); ets=set(_list(p.get("edgeTypes"))); wss=set(_list(p.get("workspaces"))); n=[x for x in nodes if (not nts or x["nodeType"] in nts) and (not wss or x["workspaceId"] in wss)]; ids={x["nodeId"] for x in n}; e=[x for x in edges if (not ets or x["edgeType"] in ets) and x["sourceRef"] in ids and x["targetRef"] in ids]; return {"ok":True,"version":VERSION,"nodes":n,"edges":e,"queryResultIsScientificConclusion":False}
def _subgraph(payload:dict,refs):
    p,nodes,edges,_=_parts(payload); refs=set(str(x) for x in refs); n=[x for x in nodes if x["nodeId"] in refs]; e=[x for x in edges if x["sourceRef"] in refs and x["targetRef"] in refs]; return {"ok":True,"version":VERSION,"nodes":n,"edges":e,"subgraphIsScientificConclusion":False}
def subgraph_extract(payload:dict): return _subgraph(payload,_list(_dict(payload).get("nodeRefs")))
def workspace_subgraph(payload:dict):
    p,nodes,edges,_=_parts(payload); ws=_txt(p.get("workspaceId"),128); return _subgraph(payload,[n["nodeId"] for n in nodes if n["workspaceId"]==ws])
def object_subgraph(payload:dict):
    p,nodes,edges,_=_parts(payload); typ=_txt(p.get("nodeType"),128); return _subgraph(payload,[n["nodeId"] for n in nodes if n["nodeType"]==typ])
def dependency_subgraph(payload:dict):
    p,nodes,edges,_=_parts(payload); cls=_txt(p.get("dependencyClass"),128); refs=set()
    for e in edges:
        if e["dependencyClass"]==cls: refs|={e["sourceRef"],e["targetRef"]}
    return _subgraph(payload,refs)
def lineage_subgraph(payload:dict):
    p=_dict(payload); s=_txt(p.get("nodeRef"),512); _,up,_=_closure(payload,True); _,down,_=_closure(payload,False); return _subgraph(payload,[s]+up+down)
def stale_subgraph(payload:dict):
    r=_impact(payload); return _subgraph(payload,r["impactedRefs"]+r["changedRefs"])

def explain_dependency(payload:dict):
    p=_dict(payload); r=shortest_dependency_path(payload); return {"ok":True,"version":VERSION,"sourceRef":r["sourceRef"],"targetRef":r["targetRef"],"path":r["path"],"explanation":"Declared dependency path only; it does not establish causality, evidence, mechanism, or scientific importance.","causalProof":False,"evidenceProof":False}
def scientific_boundary_audit(payload:dict):
    return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"checks":{"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False,"impactCandidateIsScientificInvalidation":False,"stalenessCandidateIsScientificInvalidation":False,"shortestPathIsMechanism":False,"degreeIsScientificImportance":False,"automaticGraphMutation":False,"automaticRetraction":False},"clean":True}
def release_readiness(payload:dict):
    audits={"schema":schema_audit(payload),"references":reference_integrity_audit(payload),"provenance":provenance_audit(payload),"semantics":edge_semantics_audit(payload),"duplicatesNodes":duplicate_node_audit(payload),"duplicatesEdges":duplicate_edge_audit(payload)}; ready=all(x.get("clean",x.get("complete",False)) for x in audits.values()); return {"ok":True,"version":VERSION,"readyForHumanReview":ready,"audits":audits,"automaticScientificApproval":False}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"api_route_count":120,"nodeTypeCount":len(NODE_TYPES),"edgeTypeCount":len(EDGE_TYPES),"dependencyClassCount":len(DEPENDENCY_CLASSES),"workspaceCount":len(WORKSPACES),"boundary":BOUNDARY}
def policy():
    return {"ok":True,"version":VERSION,"platformCoreCanonicalAuthority":True,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"knowledgeLibrarySourceAuthority":True,"labDependencyAnalysisAuthority":True,"labExecutesHeavyCompute":False,"automaticGraphMutation":False,"automaticStalenessInvalidation":False,"automaticRecompute":False,"automaticRevalidation":False,"automaticRetraction":False,"automaticScientificValidity":False,"humanScientificReviewRequired":True,"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False,"impactCandidateIsScientificInvalidation":False,"reproducibilityIsScientificValidity":False}
def interpretation_boundary():
    return {"ok":True,"version":VERSION,"text":BOUNDARY,"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False,"transitiveDependencyIsCausalProof":False,"shortestPathIsMechanism":False,"degreeIsScientificImportance":False,"crossWorkspaceEdgeIsScientificIntegrationProof":False,"impactCandidateIsScientificInvalidation":False,"stalenessCandidateIsScientificInvalidation":False,"publicationImpactIsRetractionDecision":False,"reproducibilityIsScientificValidity":False}
def release_gates():
    return {"ok":True,"version":VERSION,"gates":{"dependencyObjectModel":True,"explicitEdgeSemantics":True,"crossWorkspaceGraph":True,"referenceIntegrityAudit":True,"provenanceAudit":True,"impactAnalysis":True,"stalenessCandidates":True,"revalidationPlanning":True,"recomputePlanning":True,"publicationImpactPlanning":True,"graphStudioHandoff":True,"workflowOrchestrationHandoff":True,"reproducibilityPackage":True,"humanReviewBoundaries":True}}
def acceptance_report():
    return {"ok":True,"version":VERSION,"accepted":{"crossWorkspaceDependencyGraph":True,"persistentNodeAndEdgeObjects":True,"lineageTraversal":True,"impactAnalysis":True,"stalenessCandidateModel":True,"revalidationAndRecomputePlans":True,"reviewAndPublicationImpact":True,"snapshotAndDiff":True,"graphStudioVisualization":True,"authorityPreservingHandoffs":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"publicationAccepted":False}
def health():
    return {"ok":True,"version":VERSION,"crossWorkspaceResearchDependencyGraph":True,"api_route_count":120,"predecessorVersion":PREDECESSOR_VERSION,"workspaceCount":len(WORKSPACES),"nodeTypeCount":len(NODE_TYPES),"edgeTypeCount":len(EDGE_TYPES),"dependencyClassCount":len(DEPENDENCY_CLASSES),"platformCoreCanonicalAuthority":True,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"knowledgeLibrarySourceAuthority":True,"labDependencyAnalysisAuthority":True,"labExecutesHeavyCompute":False,"automaticGraphMutation":False,"automaticStalenessInvalidation":False,"automaticRecompute":False,"automaticRevalidation":False,"automaticRetraction":False,"automaticScientificValidity":False,"humanScientificReviewRequired":True,"dependencyEdgeIsCausalProof":False,"dependencyEdgeIsEvidence":False,"impactCandidateIsScientificInvalidation":False,"stalenessCandidateIsScientificInvalidation":False}
