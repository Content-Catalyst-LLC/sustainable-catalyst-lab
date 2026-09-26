from __future__ import annotations
from collections import deque
import hashlib, json

VERSION = "0.135.16.0"
ROUTE_COUNT = 16
MAX_NODES = 5000
MAX_EDGES = 20000
MAX_DEPTH = 12
DIRECTIONS = ("downstream", "upstream", "both")
REVISION_ACTIONS = ("revise-method", "revise-data", "revise-figure", "rerun-analysis", "add-evidence", "clarify-claim", "follow-up", "manual-revision")
BOUNDARY = "Impact analysis follows declared graph dependencies only. A node marked potentially affected is not thereby invalid, false, unsupported, causally changed, or scientifically inferior; human review is required."

def _text(v, limit=4096): return str(v or "").strip()[:limit]
def _raw_graph(payload):
    if not isinstance(payload, dict): return {}
    for k in ("graph","dependencyGraph","dependency_graph","record"):
        if isinstance(payload.get(k), dict): return payload[k]
    return payload

def _fp(obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def normalize_graph(payload):
    raw=_raw_graph(payload)
    if not isinstance(raw,dict): return {"ok":False,"version":VERSION,"error":"dependency graph must be an object"}
    nodes=[]; seen=set()
    for i,n in enumerate((raw.get("nodes") or [])[:MAX_NODES]):
        if not isinstance(n,dict): continue
        nid=_text(n.get("id"),512)
        if not nid or nid in seen: continue
        seen.add(nid)
        nodes.append({"id":nid,"label":_text(n.get("label") or n.get("title") or nid,1024),"type":_text(n.get("type") or n.get("objectType") or "research-object",128),"object_ref":_text(n.get("objectRef",n.get("object_ref")) or nid,2048),"collection":_text(n.get("collection"),256) or None,"version_ref":_text(n.get("versionRef",n.get("version_ref")),1024) or None})
    ids={n["id"] for n in nodes}; edges=[]; edge_ids=set(); dangling=[]
    for i,e in enumerate((raw.get("edges") or [])[:MAX_EDGES]):
        if not isinstance(e,dict): continue
        a=_text(e.get("from") or e.get("source"),512); b=_text(e.get("to") or e.get("target"),512)
        eid=_text(e.get("id"),512) or f"dependency-edge-{i+1}"
        if not a or not b: continue
        if a not in ids or b not in ids:
            dangling.append({"id":eid,"from":a,"to":b}); continue
        if eid in edge_ids: continue
        edge_ids.add(eid)
        edges.append({"id":eid,"from":a,"to":b,"relation":_text(e.get("relation") or e.get("type") or "depends-on",256),"declared":True})
    rec={"schema":"sc-lab-graph-studio-scientific-dependency-graph/0.135.16.0","version":VERSION,"record_type":"graph-studio-scientific-dependency-graph","nodes":nodes,"edges":edges,"dangling_edges":dangling,"boundary":BOUNDARY}
    rec["graph_fingerprint"]=_fp({"nodes":nodes,"edges":edges})
    return {"ok":True,"version":VERSION,"record":rec,"node_count":len(nodes),"edge_count":len(edges),"dangling_edge_count":len(dangling)}

def _cycle_nodes(nodes, edges):
    adj={n["id"]:[] for n in nodes}
    for e in edges: adj[e["from"]].append(e["to"])
    state={}; stack=[]; cyc=set()
    def dfs(v):
        state[v]=1; stack.append(v)
        for w in adj.get(v,[]):
            if state.get(w,0)==0: dfs(w)
            elif state.get(w)==1:
                try: idx=stack.index(w); cyc.update(stack[idx:])
                except ValueError: cyc.add(w)
        stack.pop(); state[v]=2
    for v in adj:
        if state.get(v,0)==0: dfs(v)
    return sorted(cyc)

def validate_graph(payload):
    n=normalize_graph(payload)
    if not n.get("ok"): return n
    r=n["record"]; cycles=_cycle_nodes(r["nodes"],r["edges"])
    return {"ok":not r["dangling_edges"],"version":VERSION,"graph_fingerprint":r["graph_fingerprint"],"node_count":len(r["nodes"]),"edge_count":len(r["edges"]),"dangling_edges":r["dangling_edges"],"cycle_node_ids":cycles,"cycle_count":len(cycles),"warnings":(["cycles detected; traversal remains bounded"] if cycles else [])+(["dangling edges detected"] if r["dangling_edges"] else []),"declared_dependencies_only":True}

def _traverse(payload, direction):
    n=normalize_graph(payload)
    if not n.get("ok"): return n
    r=n["record"]; ids={x["id"] for x in r["nodes"]}; seed=_text(payload.get("seedId",payload.get("seed_id")),512); depth=max(1,min(MAX_DEPTH,int(payload.get("maxDepth",payload.get("max_depth",6)) or 6)))
    if seed not in ids: return {"ok":False,"version":VERSION,"error":"seedId must reference a loaded graph node"}
    adj={i:[] for i in ids}
    for e in r["edges"]:
        a,b=(e["to"],e["from"]) if direction=="upstream" else (e["from"],e["to"])
        adj[a].append((b,e))
    for arr in adj.values(): arr.sort(key=lambda x:(x[1]["relation"],x[1]["id"],x[0]))
    q=deque([(seed,0)]); dist={seed:0}; parent={}; via={}
    while q:
        cur,d=q.popleft()
        if d>=depth: continue
        for nxt,e in adj.get(cur,[]):
            nd=d+1
            if nxt not in dist or nd<dist[nxt]:
                dist[nxt]=nd; parent[nxt]=cur; via[nxt]=e; q.append((nxt,nd))
    affected=[]
    by={x["id"]:x for x in r["nodes"]}
    edge_ids=set(); paths=[]
    for nid,d in sorted(dist.items(), key=lambda x:(x[1],x[0])):
        if nid==seed: continue
        cur=nid; steps=[]
        while cur!=seed and cur in parent:
            p=parent[cur]; e=via[cur]; steps.append({"from":p,"to":cur,"edge_id":e["id"],"relation":e["relation"]}); edge_ids.add(e["id"]); cur=p
        steps.reverse(); paths.append({"target_id":nid,"hop_count":d,"steps":steps})
        affected.append({**by[nid],"hop_count":d,"impact_class":"direct" if d==1 else "transitive","direction":direction})
    return {"ok":True,"version":VERSION,"seed_id":seed,"direction":direction,"max_depth":depth,"affected":affected,"affected_node_ids":[x["id"] for x in affected],"affected_edge_ids":sorted(edge_ids),"paths":paths,"direct_count":sum(x["hop_count"]==1 for x in affected),"transitive_count":sum(x["hop_count"]>1 for x in affected),"declared_dependencies_only":True,"potential_impact_only":True,"boundary":BOUNDARY}

def downstream(payload): return _traverse(payload,"downstream")
def upstream(payload): return _traverse(payload,"upstream")

def direct(payload):
    p=dict(payload or {}); p["maxDepth"]=1
    d=_traverse(p,_text(p.get("direction"),32) or "downstream")
    return d

def impact(payload):
    direction=_text(payload.get("direction"),32) or "both"
    if direction not in DIRECTIONS: return {"ok":False,"version":VERSION,"error":"direction must be downstream, upstream, or both"}
    if direction!="both": return _traverse(payload,direction)
    down=_traverse(payload,"downstream"); up=_traverse(payload,"upstream")
    if not down.get("ok"): return down
    if not up.get("ok"): return up
    return {"ok":True,"version":VERSION,"seed_id":down["seed_id"],"direction":"both","max_depth":down["max_depth"],"downstream":down,"upstream":up,"potentially_affected_node_ids":down["affected_node_ids"],"dependency_node_ids":up["affected_node_ids"],"affected_edge_ids":sorted(set(down["affected_edge_ids"]+up["affected_edge_ids"])),"declared_dependencies_only":True,"potential_impact_only":True,"boundary":BOUNDARY}

def impact_paths(payload):
    r=impact(payload)
    if not r.get("ok"): return r
    if r["direction"]=="both": return {"ok":True,"version":VERSION,"seed_id":r["seed_id"],"downstream_paths":r["downstream"]["paths"],"upstream_paths":r["upstream"]["paths"],"boundary":BOUNDARY}
    return {"ok":True,"version":VERSION,"seed_id":r["seed_id"],"paths":r["paths"],"boundary":BOUNDARY}

def summary(payload):
    r=impact(payload)
    if not r.get("ok"): return r
    if r["direction"]=="both":
        affected=r["downstream"]["affected"]; dependencies=r["upstream"]["affected"]
    else:
        affected=r["affected"] if r["direction"]=="downstream" else []; dependencies=r["affected"] if r["direction"]=="upstream" else []
    by_type={}
    for x in affected: by_type[x["type"]]=by_type.get(x["type"],0)+1
    return {"ok":True,"version":VERSION,"seed_id":r["seed_id"],"potentially_affected_count":len(affected),"upstream_dependency_count":len(dependencies),"direct_affected_count":sum(x["hop_count"]==1 for x in affected),"transitive_affected_count":sum(x["hop_count"]>1 for x in affected),"potentially_affected_by_type":by_type,"potential_impact_only":True}

def snapshot(payload):
    n=normalize_graph(payload)
    if not n.get("ok"): return n
    r=impact(payload)
    if not r.get("ok"): return r
    snap={"schema":"sc-lab-graph-studio-revision-impact-snapshot/0.135.16.0","version":VERSION,"id":_text(payload.get("snapshotId",payload.get("snapshot_id")),256) or "revision-impact-snapshot","seed_id":r["seed_id"],"direction":r["direction"],"max_depth":r["max_depth"],"graph_fingerprint":n["record"]["graph_fingerprint"],"impact":r,"boundary":BOUNDARY}
    snap["fingerprint"]=_fp(snap)
    return {"ok":True,"version":VERSION,"snapshot":snap}

def compare_snapshots(payload):
    if not isinstance(payload,dict): return {"ok":False,"version":VERSION,"error":"payload must be an object"}
    L=payload.get("left") or {}; R=payload.get("right") or {}
    def ids(s):
        imp=s.get("impact") if isinstance(s,dict) else {}
        if imp.get("direction")=="both": return set(imp.get("potentially_affected_node_ids") or [])
        return set(imp.get("affected_node_ids") or [])
    li,ri=ids(L),ids(R)
    return {"ok":True,"version":VERSION,"left_fingerprint":L.get("fingerprint"),"right_fingerprint":R.get("fingerprint"),"added_potentially_affected_node_ids":sorted(ri-li),"removed_potentially_affected_node_ids":sorted(li-ri),"unchanged_potentially_affected_node_ids":sorted(li&ri),"graph_changed":L.get("graph_fingerprint")!=R.get("graph_fingerprint"),"interpretation":"descriptive change in declared dependency reachability only"}

def revision_analysis(payload):
    action=_text(payload.get("revisionAction",payload.get("revision_action")),64) or "manual-revision"
    if action not in REVISION_ACTIONS: return {"ok":False,"version":VERSION,"error":"unsupported revisionAction"}
    r=impact(payload)
    if not r.get("ok"): return r
    s=summary(payload)
    rec={"schema":"sc-lab-graph-studio-revision-impact-analysis/0.135.16.0","version":VERSION,"recordType":"graph-studio-revision-impact-analysis","collection":"graphStudioRevisionImpactAnalyses","id":_text(payload.get("id"),256) or "revision-impact-analysis","revisionAction":action,"revisionRef":_text(payload.get("revisionRef",payload.get("revision_ref")),2048) or None,"annotationId":_text(payload.get("annotationId",payload.get("annotation_id")),512) or None,"seedId":r["seed_id"],"direction":r["direction"],"maxDepth":r["max_depth"],"impact":r,"summary":s,"createdAt":_text(payload.get("createdAt",payload.get("created_at")),128) or None,"author":_text(payload.get("author"),256) or "user","boundary":BOUNDARY}
    rec["fingerprint"]=_fp(rec)
    return {"ok":True,"version":VERSION,"record":rec}

def impact_packet(payload):
    x=revision_analysis(payload)
    if not x.get("ok"): return x
    return {"ok":True,"version":VERSION,"target":"project-workspace","analysis":x["record"],"graphValidation":validate_graph(payload),"boundary":BOUNDARY}

def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"revision_impact_graph":True,"scientific_dependency_analysis":True,"direct_and_transitive_impact":True,"upstream_downstream_traversal":True,"impact_snapshots":True,"project_workspace_handoff":True,"backward_compatible_v0135150":True}
def contract(): return {"ok":True,"version":VERSION,"directions":list(DIRECTIONS),"revision_actions":list(REVISION_ACTIONS),"max_nodes":MAX_NODES,"max_edges":MAX_EDGES,"max_depth":MAX_DEPTH,"project_collection":"graphStudioRevisionImpactAnalyses","declared_dependencies_only":True,"potential_impact_only":True,"automatic_invalidation":False,"causal_inference":False,"truth_ranking":False}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["select-revision-seed","analyze-downstream-impact","inspect-direct-transitive-impact","save-impact-analysis","open-impact-context"],"full_render_count_must_not_increase":True}
def acceptance_report(): return {"ok":True,"version":VERSION,"revision_impact_graph":True,"scientific_dependency_analysis":True,"direct_and_transitive_impact":True,"upstream_downstream_traversal":True,"cycle_detection":True,"dangling_reference_detection":True,"project_persistence_explicit":True,"cross_workspace_impact_handoff":True,"full_graph_redraw_for_impact":False,"automatic_scientific_invalidation":False,"causal_inference":False,"truth_ranking":False,"evidence_weight_inference":False,"scientific_preference":False,"backward_compatible_v0135150":True}
