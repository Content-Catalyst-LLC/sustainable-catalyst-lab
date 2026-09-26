from __future__ import annotations
from collections import deque
VERSION="0.135.11.0"
ROUTE_COUNT=10

def _graph(payload:dict):
    nodes=[n for n in (payload.get("nodes") or []) if isinstance(n,dict) and n.get("id")]
    ids={str(n["id"]) for n in nodes}; edges=[]
    for i,e in enumerate(payload.get("edges") or []):
        if not isinstance(e,dict): continue
        a,b=str(e.get("from") or e.get("source") or ""),str(e.get("to") or e.get("target") or "")
        if a not in ids or b not in ids: continue
        meta=e.get("metadata") if isinstance(e.get("metadata"),dict) else {}
        raw=meta.get("evidenceContext",meta.get("evidenceState",e.get("evidenceContext",e.get("evidenceState"))))
        ctx=str(raw or "").lower(); ctx=ctx if ctx in {"supporting","contradicting","neutral"} else "unclassified"
        edges.append({"id":str(e.get("id") or f"edge-{i}"),"from":a,"to":b,"relation":str(e.get("relation") or e.get("type") or "related-to"),"evidence_context":ctx})
    return nodes,edges

def enumerate_paths(payload:dict):
    nodes,edges=_graph(payload); ids={str(n['id']) for n in nodes}; a=str(payload.get('object_a') or ''); b=str(payload.get('object_b') or '')
    mode=str(payload.get('mode') or 'directed'); mode=mode if mode in {'directed','structural'} else 'directed'
    max_hops=max(1,min(12,int(payload.get('max_hops',6)))); max_paths=max(1,min(10,int(payload.get('max_paths',5))))
    if a not in ids or b not in ids: return {"ok":False,"version":VERSION,"error":"object_a/object_b must reference loaded graph nodes"}
    if a==b: return {"ok":True,"version":VERSION,"paths":[{"nodes":[a],"edges":[],"steps":[],"hop_count":0,"evidence":{"supporting":0,"contradicting":0,"neutral":0,"unclassified":0}}],"mode":mode,"max_hops":max_hops,"max_paths":max_paths}
    adj={x:[] for x in ids}
    for e in edges:
        adj[e['from']].append((e['to'],e,'forward'))
        if mode=='structural': adj[e['to']].append((e['from'],e,'reverse'))
    for arr in adj.values(): arr.sort(key=lambda x:(x[1]['relation'],x[1]['id'],x[0]))
    q=deque([(a,[a],[])]); out=[]
    while q and len(out)<max_paths:
        cur,path_nodes,steps=q.popleft()
        if len(steps)>=max_hops: continue
        for nxt,e,orientation in adj.get(cur,[]):
            if nxt in path_nodes: continue
            step={"from":cur,"to":nxt,"edge_id":e['id'],"relation":e['relation'],"orientation":orientation,"evidence_context":e['evidence_context']}
            nn=path_nodes+[nxt]; ns=steps+[step]
            if nxt==b:
                ev={"supporting":0,"contradicting":0,"neutral":0,"unclassified":0}
                for s in ns: ev[s['evidence_context']]+=1
                out.append({"nodes":nn,"edges":[s['edge_id'] for s in ns],"steps":ns,"hop_count":len(ns),"evidence":ev})
                if len(out)>=max_paths: break
            else: q.append((nxt,nn,ns))
    out.sort(key=lambda p:(p['hop_count'],'>'.join(f"{s['relation']}|{s['edge_id']}" for s in p['steps'])))
    return {"ok":True,"version":VERSION,"mode":mode,"max_hops":max_hops,"max_paths":max_paths,"paths":out[:max_paths],"candidate_path_count":len(out[:max_paths]),"declared_relationships_only":True}

def compare_paths(payload:dict):
    result=enumerate_paths(payload)
    if not result.get('ok'): return result
    return {**result,"comparison_is_descriptive":True,"truth_ranking":False,"causal_inference":False,"scientific_preference":False}

def evidence_context(payload:dict):
    result=enumerate_paths(payload)
    if not result.get('ok'): return result
    return {"ok":True,"version":VERSION,"paths":[{"index":i,"evidence":p['evidence']} for i,p in enumerate(result['paths'])],"declared_context_only":True,"inferred_evidence":False}

def context_packet(payload:dict):
    result=compare_paths(payload)
    if not result.get('ok'): return result
    index=max(0,min(len(result['paths'])-1,int(payload.get('selected_path_index',0)))) if result['paths'] else 0
    selected=result['paths'][index] if result['paths'] else None
    return {"ok":True,"version":VERSION,"target":"project-workspace","object_a":payload.get('object_a'),"object_b":payload.get('object_b'),"candidate_paths":result['paths'],"selected_path_index":index,"selected_path":selected,"boundary":"Alternative declared provenance paths only; no truth, causal strength, evidentiary weight, or scientific preference is inferred."}

def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"multiple_declared_paths":True,"declared_evidence_context_only":True,"competing_path_comparison":True,"cross_workspace_comparison_handoff":True}
def path_contract(): return {"ok":True,"version":VERSION,"modes":["directed","structural"],"max_hops_range":[1,12],"max_paths_range":[1,10],"simple_paths_only":True,"deterministic_ordering":True}
def evidence_contract(): return {"ok":True,"version":VERSION,"allowed_declared_states":["supporting","contradicting","neutral","unclassified"],"inferred_evidence":False,"truth_ranking":False}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["set-a-b","enumerate-multiple-paths","select-alternate-path","verify-incremental-highlight","open-comparison-context"],"full_render_count_must_not_increase":True}
def diagnostics_contract(): return {"ok":True,"version":VERSION,"metrics":["candidatePathCount","activePath","enumerations","selectionUpdates","openContextCount"]}
def acceptance_report(): return {"ok":True,"version":VERSION,"multiple_declared_paths":True,"declared_evidence_context_only":True,"full_graph_redraw_for_path_selection":False,"truth_ranking":False,"causal_inference":False,"scientific_preference":False}
