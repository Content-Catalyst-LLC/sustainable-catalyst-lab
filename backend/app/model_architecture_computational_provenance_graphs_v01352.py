from __future__ import annotations
import copy, json, math
from collections import defaultdict, deque
from hashlib import sha256
from typing import Any

VERSION='0.135.2'; ENGINE_VERSION='16.2.0'
SCHEMA='sc-lab-model-architecture-computational-provenance-graphs/0.135.2'
SNAPSHOT_SCHEMA='sc-lab-model-architecture-computational-provenance-graph-snapshot/0.135.2'
MAX_NODES=5000; MAX_EDGES=15000; MAX_PATH_DEPTH=64
NODE_TYPES={'dataset','source','transform','feature','prior','parameter','hyperparameter','model','solver','inference','execution','uncertainty','output','figure','diagnostic','assumption','evidence','claim','core-object','publication'}
EDGE_TYPES={'derived-from','sourced-from','transformed-by','binds','parameterizes','conditions','depends-on','executes','produces','quantifies','diagnoses','visualizes','supports','challenges','references','lineage-of','exports-to','registered-as'}
VIEW_MODES={'architecture','provenance','execution','evidence'}; LAYOUT_MODES={'layered','swimlane','radial'}; GRAPH_STATES={'bound','declared','unbound','external','derived'}
TYPE_LAYER={'source':0,'dataset':1,'transform':2,'feature':3,'prior':3,'parameter':3,'hyperparameter':3,'model':4,'solver':5,'inference':5,'execution':6,'uncertainty':7,'output':7,'diagnostic':8,'figure':8,'assumption':8,'evidence':9,'claim':10,'publication':11,'core-object':11}

class ModelArchitectureProvenanceGraphError(ValueError):
    def __init__(self,detail,status_code=400): super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _list(v,label,limit):
    if v is None:return []
    if not isinstance(v,list): raise ModelArchitectureProvenanceGraphError(f'{label} must be an array.')
    if len(v)>limit: raise ModelArchitectureProvenanceGraphError(f'{label} exceeds configured maximum of {limit}.')
    return v
def _refs(v,label): return [str(x)[:500] for x in _list(v,label,MAX_NODES)]
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise ModelArchitectureProvenanceGraphError(f'{label} is required.')
    return s[:500]

def schema_info(): return {'ok':True,'schema':SCHEMA,'snapshot_schema':SNAPSHOT_SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,'node_types':sorted(NODE_TYPES),'edge_types':sorted(EDGE_TYPES),'view_modes':sorted(VIEW_MODES),'layout_modes':sorted(LAYOUT_MODES),'limits':{'nodes':MAX_NODES,'edges':MAX_EDGES,'path_depth':MAX_PATH_DEPTH}}
def catalog(): return {'ok':True,'version':VERSION,'node_types':sorted(NODE_TYPES),'node_type_count':len(NODE_TYPES),'edge_types':sorted(EDGE_TYPES),'edge_type_count':len(EDGE_TYPES),'view_modes':sorted(VIEW_MODES),'layout_modes':sorted(LAYOUT_MODES),'graph_states':sorted(GRAPH_STATES),'fabricated_scientific_values':False,'automatic_model_inference':False,'automatic_provenance_inference':False,'automatic_causal_inference':False,'automatic_evidence_weighting':False,'automatic_core_submission':False}
def manifest(): return {'ok':True,'status':'model-architecture-computational-provenance-graphs-ready','version':VERSION,'engine_version':ENGINE_VERSION,'interactive_architecture_graph':True,'computational_provenance_graph':True,'execution_trace_graph':True,'uncertainty_flow_graph':True,'evidence_lineage_graph':True,'upstream_downstream_traversal':True,'cycle_orphan_audits':True,'layered_swimlane_radial_layouts':True,'reference_first':True,'v01351_visual_experience_bridge':True,'platform_core_reference_bridge':True,'automatic_model_inference':False,'automatic_scientific_interpretation':False,'automatic_evidence_promotion':False,'automatic_core_submission':False}
def health(): return {**manifest(),'schema':SCHEMA,'node_type_count':20,'edge_type_count':18,'view_mode_count':4,'layout_mode_count':3,'api_route_count':40}

def _node(raw,i):
    if not isinstance(raw,dict): raise ModelArchitectureProvenanceGraphError(f'nodes[{i}] must be an object.')
    t=str(raw.get('node_type') or raw.get('type') or 'output').lower(); state=str(raw.get('state') or 'declared').lower()
    if t not in NODE_TYPES: raise ModelArchitectureProvenanceGraphError(f'nodes[{i}].node_type invalid.')
    if state not in GRAPH_STATES: raise ModelArchitectureProvenanceGraphError(f'nodes[{i}].state invalid.')
    nid=str(raw.get('node_id') or raw.get('ref') or f'node:{i}:{_hash(raw)[:12]}')[:500]
    return {'node_id':nid,'node_type':t,'label':str(raw.get('label') or raw.get('title') or nid)[:500],'state':state,'object_ref':raw.get('object_ref') or raw.get('ref'),'project_ref':raw.get('project_ref'),'session_ref':raw.get('session_ref'),'scientific_value':raw.get('scientific_value') if 'scientific_value' in raw else None,'scientific_value_declared':'scientific_value' in raw,'metadata':copy.deepcopy(raw.get('metadata') if isinstance(raw.get('metadata'),dict) else {}),'source_index':i}
def _edge(raw,i,node_ids):
    if not isinstance(raw,dict): raise ModelArchitectureProvenanceGraphError(f'edges[{i}] must be an object.')
    a=_req(raw.get('source'),f'edges[{i}].source'); b=_req(raw.get('target'),f'edges[{i}].target'); t=str(raw.get('edge_type') or raw.get('type') or 'depends-on').lower()
    if a not in node_ids or b not in node_ids: raise ModelArchitectureProvenanceGraphError(f'edges[{i}] references unknown node(s).')
    if t not in EDGE_TYPES: raise ModelArchitectureProvenanceGraphError(f'edges[{i}].edge_type invalid.')
    return {'edge_id':str(raw.get('edge_id') or f'edge:{_hash([a,b,t,i])[:16]}')[:500],'source':a,'target':b,'edge_type':t,'label':str(raw.get('label') or t)[:500],'declared':bool(raw.get('declared',True)),'metadata':copy.deepcopy(raw.get('metadata') if isinstance(raw.get('metadata'),dict) else {})}
def normalize_graph(payload):
    if not isinstance(payload,dict): raise ModelArchitectureProvenanceGraphError('payload must be an object.')
    nodes=[_node(x,i) for i,x in enumerate(_list(payload.get('nodes'),'nodes',MAX_NODES))]; ids=[n['node_id'] for n in nodes]
    if len(ids)!=len(set(ids)): raise ModelArchitectureProvenanceGraphError('node_id values must be unique.')
    edges=[_edge(x,i,set(ids)) for i,x in enumerate(_list(payload.get('edges'),'edges',MAX_EDGES))]; eids=[e['edge_id'] for e in edges]
    if len(eids)!=len(set(eids)): raise ModelArchitectureProvenanceGraphError('edge_id values must be unique.')
    view=str(payload.get('view_mode') or 'architecture').lower(); layout=str(payload.get('layout_mode') or 'layered').lower()
    if view not in VIEW_MODES or layout not in LAYOUT_MODES: raise ModelArchitectureProvenanceGraphError('invalid view_mode or layout_mode.')
    g={'graph_ref':str(payload.get('graph_ref') or f'architecture-graph:{_hash(payload)[:16]}')[:500],'project_ref':payload.get('project_ref'),'session_ref':payload.get('session_ref'),'view_mode':view,'layout_mode':layout,'nodes':nodes,'edges':edges,'node_count':len(nodes),'edge_count':len(edges),'reference_first':True,'automatic_model_inference':False,'automatic_provenance_inference':False,'fabricated_scientific_values':False}; g['graph_hash']=_hash(g)
    return {'ok':True,'version':VERSION,'graph':g}
def _g(p): return normalize_graph(p)['graph']
def _map(g): return {n['node_id']:n for n in g['nodes']}
def _adj(g,reverse=False):
    out=defaultdict(list)
    for e in g['edges']:
        a,b=(e['target'],e['source']) if reverse else (e['source'],e['target']); out[a].append((b,e))
    return out

def build_model_architecture(p):
    g=_g(p); layers=defaultdict(list)
    for n in g['nodes']: layers[TYPE_LAYER.get(n['node_type'],7)].append(n['node_id'])
    return {'ok':True,'version':VERSION,'graph':g,'layers':[{'layer':k,'node_ids':sorted(v)} for k,v in sorted(layers.items())],'automatic_model_inference':False}
def _view(p,types,flag,val=True):
    g=_g(p); nodes=[n for n in g['nodes'] if n['node_type'] in types]; keep={n['node_id'] for n in nodes}; edges=[e for e in g['edges'] if e['source'] in keep and e['target'] in keep]; return {'ok':True,'version':VERSION,'graph':{**g,'nodes':nodes,'edges':edges},flag:val}
def build_provenance_graph(p): return _view(p,{'source','dataset','transform','feature','model','execution','uncertainty','output','figure','evidence','core-object','publication'},'provenance_is_declared_not_inferred')
def build_execution_trace(p): return _view(p,{'solver','inference','execution','output','diagnostic','figure'},'execution_status_inferred',False)
def build_uncertainty_graph(p): return _view(p,{'prior','parameter','hyperparameter','model','inference','execution','uncertainty','output','figure'},'uncertainty_semantics_preserved')
def build_evidence_lineage(p): return _view(p,{'output','figure','diagnostic','assumption','evidence','claim','publication','core-object'},'automatic_evidence_weighting',False)
def build_core_lineage(p):
    g=_g(p); core=[n for n in g['nodes'] if n['node_type']=='core-object']; return {'ok':True,'version':VERSION,'core_nodes':core,'core_node_count':len(core),'lab_mutates_core':False,'reference_first':True}
def dependency_graph(p):
    g=_g(p); allowed={'depends-on','parameterizes','conditions','executes','produces'}; return {'ok':True,'version':VERSION,'nodes':g['nodes'],'edges':[e for e in g['edges'] if e['edge_type'] in allowed],'automatic_dependency_inference':False}
def subgraph(p):
    g=_g(p); ids=set(_refs(p.get('node_ids'),'node_ids')); nodes=[n for n in g['nodes'] if n['node_id'] in ids]; keep={n['node_id'] for n in nodes}; edges=[e for e in g['edges'] if e['source'] in keep and e['target'] in keep]; return {'ok':True,'version':VERSION,'graph':{**g,'nodes':nodes,'edges':edges,'node_count':len(nodes),'edge_count':len(edges)}}
def node_detail(p):
    g=_g(p); nid=_req(p.get('node_id'),'node_id'); n=_map(g).get(nid)
    if not n: raise ModelArchitectureProvenanceGraphError('node_id not found.',404)
    inc=[e for e in g['edges'] if nid in (e['source'],e['target'])]; return {'ok':True,'version':VERSION,'node':n,'incident_edges':inc,'incident_edge_count':len(inc)}
def edge_detail(p):
    g=_g(p); eid=_req(p.get('edge_id'),'edge_id'); e=next((x for x in g['edges'] if x['edge_id']==eid),None)
    if not e: raise ModelArchitectureProvenanceGraphError('edge_id not found.',404)
    return {'ok':True,'version':VERSION,'edge':e,'source':_map(g)[e['source']],'target':_map(g)[e['target']]}
def path_trace(p):
    g=_g(p); source=_req(p.get('source'),'source'); target=_req(p.get('target'),'target'); adj=_adj(g); q=deque([source]); prev={source:None}; pe={}
    while q:
        cur=q.popleft()
        if cur==target: break
        for nxt,e in adj.get(cur,[]):
            if nxt not in prev: prev[nxt]=cur; pe[nxt]=e; q.append(nxt)
    if target not in prev:return {'ok':True,'version':VERSION,'found':False,'path':[],'edges':[]}
    nodes=[]; edges=[]; cur=target
    while cur is not None:
        nodes.append(cur)
        if cur in pe: edges.append(pe[cur])
        cur=prev[cur]
    return {'ok':True,'version':VERSION,'found':True,'path':list(reversed(nodes)),'edges':list(reversed(edges)),'path_length':len(edges)}
def _trace(p,reverse):
    g=_g(p); start=_req(p.get('node_id'),'node_id'); adj=_adj(g,reverse); seen={start}; q=deque([(start,0)]); rows=[]; limit=min(MAX_PATH_DEPTH,max(1,int(p.get('max_depth') or MAX_PATH_DEPTH)))
    if start not in _map(g): raise ModelArchitectureProvenanceGraphError('node_id not found.',404)
    while q:
        cur,d=q.popleft()
        if d>=limit: continue
        for nxt,e in sorted(adj.get(cur,[]),key=lambda t:t[0]):
            rows.append({'from':cur,'to':nxt,'edge_id':e['edge_id'],'edge_type':e['edge_type'],'depth':d+1})
            if nxt not in seen:seen.add(nxt);q.append((nxt,d+1))
    return {'ok':True,'version':VERSION,'node_id':start,'reachable_node_ids':sorted(seen-{start}),'trace':rows}
def upstream_trace(p): return _trace(p,True)
def downstream_trace(p): return _trace(p,False)
def impact_path(p):
    out=downstream_trace(p); out['impact_is_structural_not_causal']=True; out['automatic_causal_inference']=False; return out
def orphan_report(p):
    g=_g(p); degree=defaultdict(int)
    for e in g['edges']: degree[e['source']]+=1; degree[e['target']]+=1
    rows=[n for n in g['nodes'] if degree[n['node_id']]==0]; return {'ok':True,'version':VERSION,'orphan_nodes':rows,'orphan_count':len(rows),'automatic_deletion':False}
def cycle_audit(p):
    g=_g(p); adj=_adj(g); color={n['node_id']:0 for n in g['nodes']}; stack=[]; cycles=[]
    def dfs(u):
        color[u]=1; stack.append(u)
        for v,_ in adj.get(u,[]):
            if color.get(v,0)==0: dfs(v)
            elif color.get(v)==1 and v in stack:
                c=stack[stack.index(v):]+[v]
                if c not in cycles: cycles.append(c)
        stack.pop(); color[u]=2
    for u in sorted(color):
        if color[u]==0: dfs(u)
    return {'ok':True,'version':VERSION,'cycles':cycles,'cycle_count':len(cycles),'cycle_means_error':False}
def graph_statistics(p):
    g=_g(p); nt=defaultdict(int); et=defaultdict(int); deg=defaultdict(int)
    for n in g['nodes']: nt[n['node_type']]+=1
    for e in g['edges']: et[e['edge_type']]+=1; deg[e['source']]+=1; deg[e['target']]+=1
    return {'ok':True,'version':VERSION,'node_count':len(g['nodes']),'edge_count':len(g['edges']),'nodes_by_type':dict(sorted(nt.items())),'edges_by_type':dict(sorted(et.items())),'max_degree':max(deg.values(),default=0),'scientific_interpretation':False}
def _layout(p,mode):
    g=_g(p); groups=defaultdict(list)
    for n in g['nodes']: groups[TYPE_LAYER.get(n['node_type'],7)].append(n)
    pos={}
    if mode=='radial':
        ordered=sorted(g['nodes'],key=lambda n:(TYPE_LAYER.get(n['node_type'],7),n['node_id'])); total=max(1,len(ordered))
        for i,n in enumerate(ordered):
            a=2*math.pi*i/total; r=120+TYPE_LAYER.get(n['node_type'],7)*18; pos[n['node_id']]={'x':round(400+r*math.cos(a),3),'y':round(260+r*math.sin(a),3),'layer':TYPE_LAYER.get(n['node_type'],7)}
    else:
        for layer,rows in sorted(groups.items()):
            for i,n in enumerate(sorted(rows,key=lambda n:n['node_id'])): pos[n['node_id']]={'x':90+layer*150 if mode=='layered' else 100+i*170,'y':80+i*88 if mode=='layered' else 70+layer*92,'layer':layer}
    return {'ok':True,'version':VERSION,'layout':mode,'positions':pos,'presentation_only':True}
def layered_layout(p): return _layout(p,'layered')
def swimlane_layout(p): return _layout(p,'swimlane')
def radial_layout(p): return _layout(p,'radial')
def visual_encoding_plan(p): return {'ok':True,'version':VERSION,'encoding':{'node_shape':'node_type','node_border':'state','edge_pattern':'edge_type','selection':'interaction-state','scientific_value_encoding':'only-when-explicitly-declared'},'presentation_only':True,'fabricated_scientific_values':False}
def interaction_contract(p): return {'ok':True,'version':VERSION,'interactions':['select-node','select-edge','pan','zoom','focus-path','upstream','downstream','toggle-layer','open-object'],'selection_mutates_scientific_record':False,'navigation_only':True}
def linked_selection_plan(p): return {'ok':True,'version':VERSION,'selection_ref':p.get('selection_ref'),'linked_view_refs':_refs(p.get('linked_view_refs'),'linked_view_refs'),'automatic_join_inference':False,'selection_is_presentation_state':True}
def timeline_overlay_plan(p): return {'ok':True,'version':VERSION,'execution_refs':_refs(p.get('execution_refs'),'execution_refs'),'event_refs':_refs(p.get('event_refs'),'event_refs'),'requires_explicit_timestamps':True,'automatic_time_inference':False}
def assumption_overlay_plan(p): return {'ok':True,'version':VERSION,'assumption_refs':_refs(p.get('assumption_refs'),'assumption_refs'),'states_are_referenced_not_recomputed':True,'automatic_method_rejection':False}
def diagnostic_overlay_plan(p): return {'ok':True,'version':VERSION,'diagnostic_refs':_refs(p.get('diagnostic_refs'),'diagnostic_refs'),'diagnostic_values_must_be_bound':True,'automatic_validity_judgment':False}
def evidence_overlay_plan(p): return {'ok':True,'version':VERSION,'evidence_refs':_refs(p.get('evidence_refs'),'evidence_refs'),'claim_refs':_refs(p.get('claim_refs'),'claim_refs'),'automatic_evidence_weighting':False,'automatic_claim_status_change':False}
def project_binding(p): return {'ok':True,'version':VERSION,'project_ref':p.get('project_ref'),'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'reference_first':True,'source_objects_remain_authoritative':True}
def session_binding(p): return {'ok':True,'version':VERSION,'session_ref':p.get('session_ref'),'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'selection_state':copy.deepcopy(p.get('selection_state') if isinstance(p.get('selection_state'),dict) else {}),'scientific_objects_mutated':False}
def handoff_plan(p): return {'ok':True,'version':VERSION,'destination':str(p.get('destination') or 'platform-core'),'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'object_refs':_refs(p.get('object_refs'),'object_refs'),'automatic_submission':False}
def export_plan(p): return {'ok':True,'version':VERSION,'formats':[str(x).lower() for x in _list(p.get('formats') or ['json','svg'],'formats',20)],'include_graph_spec':True,'include_object_refs':True,'include_layout':bool(p.get('include_layout',True)),'scientific_values_only_if_declared':True}
def build_snapshot(p):
    g=_g(p); body={'schema':SNAPSHOT_SCHEMA,'version':VERSION,'graph':g,'selection':copy.deepcopy(p.get('selection') if isinstance(p.get('selection'),dict) else {}),'presentation':copy.deepcopy(p.get('presentation') if isinstance(p.get('presentation'),dict) else {})}; body['snapshot_hash']=_hash(body); return {'ok':True,'version':VERSION,'snapshot':body}
def revision_plan(p): return {'ok':True,'version':VERSION,'base_snapshot_ref':p.get('base_snapshot_ref'),'operations':copy.deepcopy(_list(p.get('operations'),'operations',1000)),'automatic_source_object_mutation':False,'requires_explicit_apply':True}
def core_object_plan(p): return {'ok':True,'version':VERSION,'object_type':'visual-research-graph','graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'scientific_object_refs':_refs(p.get('scientific_object_refs'),'scientific_object_refs'),'lab_owns_graph_rendering':True,'core_owns_canonical_research_objects':True,'automatic_core_submission':False,'reference_first':True}
def readiness_report(p):
    g=_g(p); warn=[]; unbound=[n['node_id'] for n in g['nodes'] if n['state']=='unbound']
    if not g['nodes']:warn.append('No graph nodes are declared.')
    if g['nodes'] and not g['edges']:warn.append('Nodes are present but no relationships are declared.')
    if unbound:warn.append(f'{len(unbound)} node(s) remain unbound.')
    return {'ok':True,'version':VERSION,'ready_for_visualization':bool(g['nodes']),'warnings':warn,'unbound_node_ids':unbound,'scientific_validity_certified':False}
def interpretation_boundaries_report(p=None): return {'ok':True,'version':VERSION,'fabricate_scientific_values':False,'infer_undeclared_model_structure':False,'infer_undeclared_provenance':False,'automatic_causal_inference':False,'automatic_evidence_weighting':False,'automatic_claim_status_change':False,'automatic_scientific_interpretation':False,'automatic_scientific_validity_certification':False,'automatic_core_submission':False,'determine_truth':False}
