from __future__ import annotations
from collections import deque
VERSION="0.135.9.0"
ROUTE_COUNT=10

def _graph(payload:dict):
    nodes=[n for n in (payload.get("nodes") or []) if isinstance(n,dict) and n.get("id")]
    ids={str(n["id"]) for n in nodes}
    edges=[]
    for i,e in enumerate(payload.get("edges") or []):
        if not isinstance(e,dict): continue
        a,b=str(e.get("from") or e.get("source") or ""),str(e.get("to") or e.get("target") or "")
        if a in ids and b in ids:
            edges.append({"id":str(e.get("id") or f"edge-{i}"),"from":a,"to":b,"relation":str(e.get("relation") or e.get("type") or "related-to")})
    return nodes,edges

def neighborhood(payload:dict):
    nodes,edges=_graph(payload); selected=str(payload.get("selected_node") or ""); depth=max(0,min(2,int(payload.get("depth",1))))
    if not selected or selected not in {str(n['id']) for n in nodes}: return {"ok":True,"version":VERSION,"depth":depth,"nodes":[],"edges":[]}
    adj={str(n['id']):[] for n in nodes}
    for e in edges:
        adj[e['from']].append((e['to'],e)); adj[e['to']].append((e['from'],e))
    seen={selected}; q=deque([(selected,0)])
    while q:
        cur,d=q.popleft()
        if d>=depth: continue
        for nxt,_ in adj.get(cur,[]):
            if nxt not in seen: seen.add(nxt); q.append((nxt,d+1))
    visible_edges=[e for e in edges if e['from'] in seen and e['to'] in seen]
    return {"ok":True,"version":VERSION,"depth":depth,"nodes":sorted(seen),"edges":[e['id'] for e in visible_edges],"declared_relationships_only":True}

def object_summary(payload:dict):
    nodes,edges=_graph(payload); selected=str(payload.get("selected_node") or ""); node=next((n for n in nodes if str(n.get('id'))==selected),None)
    if not node: return {"ok":False,"version":VERSION,"error":"selected node not found"}
    incoming=[e for e in edges if e['to']==selected]; outgoing=[e for e in edges if e['from']==selected]
    return {"ok":True,"version":VERSION,"node":node,"incoming":incoming,"outgoing":outgoing,"incoming_count":len(incoming),"outgoing_count":len(outgoing)}

def relation_summary(payload:dict):
    nodes,edges=_graph(payload); selected=str(payload.get("selected_node") or "")
    rel=[]
    for e in edges:
        if e['from']==selected: rel.append({"direction":"outgoing","relation":e['relation'],"other":e['to'],"edge_id":e['id']})
        elif e['to']==selected: rel.append({"direction":"incoming","relation":e['relation'],"other":e['from'],"edge_id":e['id']})
    return {"ok":True,"version":VERSION,"selected_node":selected or None,"relationships":rel}

def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"one_hop_neighborhood":True,"two_hop_neighborhood":True,"rich_object_inspector":True,"related_object_selection":True,"cross_workspace_navigation":True,"full_graph_redraw_for_scope":False}
def inspector_contract(): return {"ok":True,"version":VERSION,"fields":["object-id","object-ref","type","collection","status","updated","method","source-id","incoming-count","outgoing-count"],"project_metadata_optional":True,"scientific_inference":False}
def navigation_contract(): return {"ok":True,"version":VERSION,"target":"project-workspace","handoff_storage":"sessionStorage","focus_record_id":True,"full_page_runtime_navigation_supported":True,"scientific_mutation":False}
def scope_contract(): return {"ok":True,"version":VERSION,"scopes":["1-hop","2-hop","full"],"undirected_declared_neighborhood_for_exploration":True,"causal_path_claim":False,"incremental_visibility_update":True}
def persistence_contract(): return {"ok":True,"version":VERSION,"scope_is_presentation_state":True,"project_records_unchanged":True,"relationship_records_unchanged":True}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["select-dataset","choose-1-hop","verify-unrelated-node-dimmed","choose-related-object","verify-inspector-updates","choose-full","verify-all-restored","open-project-workspace-handoff"],"full_render_count_must_not_increase":True}
def diagnostics_contract(): return {"ok":True,"version":VERSION,"metrics":["scope","visibleNodes","visibleEdges","selectedNode","selectedEdge","scopeUpdates","openProjectCount"]}
def acceptance_report(): return {"ok":True,"version":VERSION,"dynamic_project_graph":True,"declared_relationships_only":True,"one_hop_neighborhood":True,"two_hop_neighborhood":True,"rich_object_inspector":True,"related_object_selection":True,"cross_workspace_navigation":True,"full_graph_redraw_for_scope":False,"mutation_observer_interaction_owner":False}
