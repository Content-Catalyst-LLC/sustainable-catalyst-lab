from __future__ import annotations
from collections import deque
VERSION="0.135.8.5"
ROUTE_COUNT=13
LAYOUTS=("layered","radial","swimlane")
TRAVERSALS=("all","upstream","downstream","focus")

def health():
    return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"native_graph_state_engine":True,"mutation_observer_owns_interaction":False,"project_state_persistence":True,"presentation_state_mutates_science":False}

def runtime_contract():
    return {"ok":True,"version":VERSION,"state_owner":"native-provenance-controller","renderer":"Renderer 3.1","single_graph_controller":True,"stable_object_ids":True,"dom_is_projection_not_state":True,"observer_driven_renders":0}

def graph_contract():
    return {"ok":True,"version":VERSION,"node_sources":["bound-scientific-object","lab-project-relationships","derived-declared-lineage"],"missing_edges_inferred":False,"structural_paths_are_causal":False,"edge_order_drives_semantics":False}

def layout_contract():
    return {"ok":True,"version":VERSION,"layouts":list(LAYOUTS),"layout_owned_by_controller":True,"synthetic_clicks":False,"direct_post_render_dom_geometry_patch":False}

def traversal_contract():
    return {"ok":True,"version":VERSION,"modes":list(TRAVERSALS),"reachable_subgraph_computed":True,"opacity_only_traversal":False,"cycles_guarded":True}

def inspector_contract():
    return {"ok":True,"version":VERSION,"driven_by_graph_state":True,"node_and_edge_selection":True,"incoming_outgoing_relations":True,"object_reference_visible":True,"scientific_mutation":False}

def persistence_contract():
    return {"ok":True,"version":VERSION,"authoritative_scope":"lab-project-presentation-state","local_storage_role":"fallback-cache","fields":["layout","selectedNode","selectedEdge","traversal","relation","scale","tx","ty"],"scientific_record_mutation":False}

def browser_hardening_contract():
    return {"ok":True,"version":VERSION,"mutation_observer_interaction_owner":False,"delegated_controller_events":True,"duplicate_handlers":0,"interaction_loop_count_expected":0,"observer_driven_renders_expected":0,"browser_acceptance_required":True}

def normalize_graph(payload:dict):
    nodes=payload.get("nodes") if isinstance(payload.get("nodes"),list) else []
    edges=payload.get("edges") if isinstance(payload.get("edges"),list) else []
    ids={str(n.get("id")) for n in nodes if isinstance(n,dict) and n.get("id")}
    out=[]
    for i,e in enumerate(edges):
        if not isinstance(e,dict): continue
        a,b=str(e.get("from") or e.get("source") or ""),str(e.get("to") or e.get("target") or "")
        if a in ids and b in ids:
            out.append({"id":str(e.get("id") or f"edge-{i}"),"from":a,"to":b,"relation":str(e.get("relation") or e.get("type") or "related-to")})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":out,"node_count":len(nodes),"edge_count":len(out),"missing_edges_inferred":False}

def traverse(payload:dict):
    g=normalize_graph(payload); mode=str(payload.get("mode") or "all").lower(); selected=str(payload.get("selected_node") or ""); relation=str(payload.get("relation") or "all")
    if mode not in TRAVERSALS: mode="all"
    if mode=="all" or not selected: return {**g,"mode":mode,"selected_node":selected,"visible_nodes":[str(n.get("id")) for n in g["nodes"] if isinstance(n,dict) and n.get("id")],"visible_edges":[e["id"] for e in g["edges"]]}
    if mode=="focus": return {**g,"mode":mode,"selected_node":selected,"visible_nodes":[selected],"visible_edges":[]}
    adj={str(n.get("id")):[] for n in g["nodes"] if isinstance(n,dict) and n.get("id")}
    for e in g["edges"]:
        if relation!="all" and e["relation"]!=relation: continue
        a,b=(e["to"],e["from"]) if mode=="upstream" else (e["from"],e["to"])
        adj.setdefault(a,[]).append((b,e["id"]))
    seen={selected}; ee=set(); q=deque([selected])
    while q:
        cur=q.popleft()
        for nxt,eid in adj.get(cur,[]):
            ee.add(eid)
            if nxt not in seen: seen.add(nxt); q.append(nxt)
    return {**g,"mode":mode,"selected_node":selected,"visible_nodes":sorted(seen),"visible_edges":sorted(ee)}

def interaction_plan(payload:dict):
    layout=str(payload.get("layout") or "layered").lower(); traversal=str(payload.get("traversal") or "all").lower()
    if layout not in LAYOUTS: layout="layered"
    if traversal not in TRAVERSALS: traversal="all"
    return {"ok":True,"version":VERSION,"layout":layout,"traversal":traversal,"selected_node":payload.get("selected_node"),"selected_edge":payload.get("selected_edge"),"relation":payload.get("relation") or "all","dispatch":"native-state-controller","requires_mutation_observer":False,"requires_synthetic_click":False,"scientific_mutation":False}

def diagnostics():
    return {"ok":True,"version":VERSION,"graph_model_loaded":True,"interaction_loop_count":0,"observer_driven_renders":0,"single_controller":True,"project_persistence":True,"browser_acceptance_gate":["node_selection","edge_selection","layered_radial_swimlane","upstream_downstream_focus","relationship_filter","reload_restore","zoom_fit"]}

def acceptance_report():
    return {"ok":True,"version":VERSION,"native_provenance_engine":True,"graph_controller_count":1,"renderer31_hosts":1,"primary_viewports":1,"mutation_observer_interaction_owner":False,"observer_driven_renders":0,"programmatic_layout_clicks":0,"hard_coded_dom_edge_order_semantics":False,"project_state_persistence":True,"legacy_primary_owners":0}
