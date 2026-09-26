from __future__ import annotations
from collections import deque
VERSION="0.135.8.5.3"
ROUTE_COUNT=8
TRAVERSALS=("all","upstream","downstream","focus")

def _norm(payload:dict):
    nodes=payload.get("nodes") if isinstance(payload.get("nodes"),list) else []
    edges=payload.get("edges") if isinstance(payload.get("edges"),list) else []
    ids={str(n.get("id")) for n in nodes if isinstance(n,dict) and n.get("id")}
    out=[]
    for i,e in enumerate(edges):
        if not isinstance(e,dict): continue
        a,b=str(e.get("from") or e.get("source") or ""),str(e.get("to") or e.get("target") or "")
        if a in ids and b in ids: out.append({"id":str(e.get("id") or f"edge-{i}"),"from":a,"to":b,"relation":str(e.get("relation") or e.get("type") or "related-to")})
    return ids,out

def _count(ids,edges,selected,traversal,relation):
    if relation=="all": relation_filter=None
    else: relation_filter=relation
    if traversal=="focus" and selected: return 0
    if traversal=="all" or not selected: return sum(1 for e in edges if relation_filter is None or e["relation"]==relation_filter)
    adj={n:[] for n in ids}
    for e in edges:
        if relation_filter is not None and e["relation"]!=relation_filter: continue
        a,b=(e["to"],e["from"]) if traversal=="upstream" else (e["from"],e["to"])
        adj.setdefault(a,[]).append((b,e["id"]))
    seen={selected}; edge_ids=set(); q=deque([selected])
    while q:
        cur=q.popleft()
        for nxt,eid in adj.get(cur,[]):
            edge_ids.add(eid)
            if nxt not in seen: seen.add(nxt); q.append(nxt)
    return len(edge_ids)

def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"context_aware_relationship_options":True,"selected_relationship_persists_across_traversal":True,"zero_match_explicit":True,"impossible_relationship_auto_reset":False,"incremental_rendering_retained":True}

def compatibility_contract(): return {"ok":True,"version":VERSION,"basis":["selected-node","traversal-direction","declared-edge-relation"],"incompatible_unselected_options_disabled":True,"selected_incompatible_option_retained":True,"scientific_relationships_inferred":False}

def relationship_options(payload:dict):
    ids,edges=_norm(payload); selected=str(payload.get("selected_node") or ""); traversal=str(payload.get("traversal") or "all").lower(); current=str(payload.get("relation") or "all")
    if traversal not in TRAVERSALS: traversal="all"
    rels=["all"]+sorted({e["relation"] for e in edges})
    options=[]
    for rel in rels:
        count=_count(ids,edges,selected,traversal,rel)
        options.append({"relation":rel,"count":count,"compatible":rel=="all" or count>0,"disabled":rel!="all" and count==0 and current!=rel})
    item=next((o for o in options if o["relation"]==current),{"relation":current,"count":0,"compatible":False,"disabled":False})
    return {"ok":True,"version":VERSION,"selected_node":selected or None,"traversal":traversal,"relation":current,"current_match_count":item["count"],"current_compatible":current=="all" or item["count"]>0,"zero_match":current!="all" and item["count"]==0,"options":options}

def zero_match_contract(): return {"ok":True,"version":VERSION,"selected_relationship_auto_reset":False,"zero_matching_edges_message":True,"zero_match_state_persisted":True,"dropdown_value_preserved":True}

def persistence_contract(): return {"ok":True,"version":VERSION,"relation_field_persisted":True,"traversal_field_persisted":True,"incompatible_but_valid_relation_preserved":True,"project_store_debounce_ms":220,"presentation_state_only":True}

def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["select-dataset","select-sourced-from-in-all","switch-upstream-retain-sourced-from","switch-downstream-retain-sourced-from-zero-match","verify-zero-match-label","verify-sourced-from-disabled-only-when-not-current","choose-transformed-by-downstream","return-all-relations"],"selector_identity_stable":True,"full_render_count_must_not_increase":True}

def diagnostics_contract(): return {"ok":True,"version":VERSION,"metrics":["relationFilter","relationMatchCount","relationCompatible","zeroMatchRelationshipState","disabledRelationshipCount","relationshipOptions","fullRenderCount","incrementalUpdateCount"]}

def acceptance_report(): return {"ok":True,"version":VERSION,"context_aware_relationship_options":True,"selected_relationship_sticks_across_traversal":True,"zero_match_is_explicit":True,"incompatible_options_are_guarded":True,"relationship_context_full_redraw":False,"legacy_interaction_shutdown_retained":True}
