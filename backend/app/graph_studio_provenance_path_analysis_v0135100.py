from __future__ import annotations
from collections import deque
VERSION="0.135.10.0"
ROUTE_COUNT=9

def _graph(payload:dict):
    nodes=[n for n in (payload.get("nodes") or []) if isinstance(n,dict) and n.get("id")]
    ids={str(n["id"]) for n in nodes}; edges=[]
    for i,e in enumerate(payload.get("edges") or []):
        if not isinstance(e,dict): continue
        a,b=str(e.get("from") or e.get("source") or ""),str(e.get("to") or e.get("target") or "")
        if a in ids and b in ids:
            edges.append({"id":str(e.get("id") or f"edge-{i}"),"from":a,"to":b,"relation":str(e.get("relation") or e.get("type") or "related-to")})
    return nodes,edges

def shortest_path(payload:dict):
    nodes,edges=_graph(payload); ids={str(n['id']) for n in nodes}; a=str(payload.get('object_a') or ''); b=str(payload.get('object_b') or '')
    mode=str(payload.get('mode') or 'directed'); mode=mode if mode in {'directed','structural'} else 'directed'; max_hops=max(1,min(12,int(payload.get('max_hops',6))))
    if a not in ids or b not in ids: return {"ok":False,"version":VERSION,"error":"object_a/object_b must reference loaded graph nodes"}
    if a==b: return {"ok":True,"version":VERSION,"mode":mode,"max_hops":max_hops,"found":True,"nodes":[a],"edges":[],"steps":[],"hop_count":0,"declared_relationships_only":True}
    adj={x:[] for x in ids}
    for e in edges:
        adj[e['from']].append((e['to'],e,'forward'))
        if mode=='structural': adj[e['to']].append((e['from'],e,'reverse'))
    for arr in adj.values(): arr.sort(key=lambda x:(x[1]['relation'],x[1]['id'],x[0]))
    q=deque([(a,0)]); prev={a:None}; via={}
    while q:
        cur,d=q.popleft()
        if d>=max_hops: continue
        for nxt,e,orientation in adj.get(cur,[]):
            if nxt in prev: continue
            prev[nxt]=cur; via[nxt]=(e,orientation)
            if nxt==b: q.clear(); break
            q.append((nxt,d+1))
    if b not in prev: return {"ok":True,"version":VERSION,"mode":mode,"max_hops":max_hops,"found":False,"nodes":[],"edges":[],"steps":[],"hop_count":None,"declared_relationships_only":True}
    path_nodes=[]; steps=[]; cur=b
    while cur is not None:
        path_nodes.append(cur); p=prev[cur]
        if p is not None:
            e,orientation=via[cur]; steps.append({"from":p,"to":cur,"edge_id":e['id'],"relation":e['relation'],"orientation":orientation})
        cur=p
    path_nodes.reverse(); steps.reverse()
    return {"ok":True,"version":VERSION,"mode":mode,"max_hops":max_hops,"found":True,"nodes":path_nodes,"edges":[s['edge_id'] for s in steps],"steps":steps,"hop_count":len(steps),"declared_relationships_only":True}

def compare_objects(payload:dict):
    nodes,_=_graph(payload); by={str(n['id']):n for n in nodes}; a=str(payload.get('object_a') or ''); b=str(payload.get('object_b') or '')
    if a not in by or b not in by: return {"ok":False,"version":VERSION,"error":"comparison objects not found"}
    p=shortest_path(payload)
    return {"ok":True,"version":VERSION,"object_a":by[a],"object_b":by[b],"path":p,"comparison_is_descriptive":True,"ranking":False,"scientific_validity_assessment":False}

def context_packet(payload:dict):
    c=compare_objects(payload)
    if not c.get('ok'): return c
    return {"ok":True,"version":VERSION,"object_a":c['object_a'],"object_b":c['object_b'],"path":c['path'],"target":"project-workspace","declared_relationships_only":True,"scientific_mutation":False,"boundary":"No causal, evidentiary, semantic, or validity inference."}

def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"directed_path_mode":True,"structural_path_mode":True,"bounded_shortest_path":True,"multi_object_comparison":True,"research_context_handoff":True,"full_graph_redraw_for_path":False}
def path_contract(): return {"ok":True,"version":VERSION,"modes":["directed","structural"],"max_hops_range":[1,12],"deterministic_tie_breaking":True,"declared_relationships_only":True,"causal_inference":False,"semantic_inference":False}
def navigation_contract(): return {"ok":True,"version":VERSION,"target":"project-workspace","handoff_storage":"sessionStorage","includes_objects":2,"includes_path":True,"scientific_mutation":False}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["select-object-a","select-object-b","verify-directed-path","switch-structural-mode","verify-path-overlay","open-research-context"],"full_render_count_must_not_increase":True}
def diagnostics_contract(): return {"ok":True,"version":VERSION,"metrics":["anchorA","anchorB","mode","maxHops","pathFound","pathHopCount","pathUpdates","comparisonUpdates","openContextCount"]}
def acceptance_report(): return {"ok":True,"version":VERSION,"directed_path_mode":True,"structural_path_mode":True,"bounded_shortest_path":True,"multi_object_comparison":True,"research_context_handoff":True,"full_graph_redraw_for_path":False,"scientific_mutation":False,"declared_relationships_only":True}
