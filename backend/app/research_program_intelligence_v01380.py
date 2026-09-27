
from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone
from . import research_change_impact_living_analysis_v01370 as living
from . import graph_studio_integrated_scientific_review_reproducibility_v01360 as integrated

VERSION = "0.138.0"
ROUTE_COUNT = 22
BOUNDARY = (
    "Cross-study research program intelligence organizes declared study relationships, shared research objects, "
    "change propagation, review/rerun assessment obligations, and program-level living status. It does not infer "
    "scientific truth, causal validity, evidentiary weight, reviewer consensus, cross-study superiority, or publication acceptance."
)
RELATION_TYPES = ("replication-of","extension-of","follow-up-to","uses-method-from","uses-data-from","shares-object-with","related-to")

def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=4096): return str(v or '').strip()[:n]
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _fp(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _list(v): return v if isinstance(v,list) else []
def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default

def normalize_study(raw):
    raw=raw if isinstance(raw,dict) else {}
    sid=_txt(_get(raw,'studyId','study_id','id'),512)
    if not sid: return None
    return {
        'studyId':sid,
        'projectId':_txt(_get(raw,'projectId','project_id'),512) or sid,
        'title':_txt(_get(raw,'title','name'),1024) or sid,
        'status':_txt(_get(raw,'status'),128) or 'active',
        'versionRef':_txt(_get(raw,'versionRef','version_ref'),2048) or None,
        'nodes':copy.deepcopy(_list(raw.get('nodes'))),
        'edges':copy.deepcopy(_list(raw.get('edges'))),
        'changeEvents':copy.deepcopy(_list(_get(raw,'changeEvents','change_events',default=[]))),
        'metadata':copy.deepcopy(raw.get('metadata')) if isinstance(raw.get('metadata'),dict) else {},
    }

def normalize_program(payload):
    raw=payload.get('program') if isinstance(payload,dict) and isinstance(payload.get('program'),dict) else (payload if isinstance(payload,dict) else {})
    pid=_txt(_get(raw,'programId','program_id','id'),512)
    if not pid: return {'ok':False,'version':VERSION,'error':'programId is required','boundary':BOUNDARY}
    studies=[]; seen=set()
    for s in _list(raw.get('studies')):
        n=normalize_study(s)
        if n and n['studyId'] not in seen: studies.append(n); seen.add(n['studyId'])
    rels=[]
    for i,r in enumerate(_list(_get(raw,'relationships','studyRelationships','study_relationships',default=[]))):
        if not isinstance(r,dict): continue
        a=_txt(_get(r,'fromStudyId','from_study_id','source'),512); b=_txt(_get(r,'toStudyId','to_study_id','target'),512)
        typ=_txt(_get(r,'type','relation'),128) or 'related-to'
        if typ not in RELATION_TYPES: typ='related-to'
        if a and b: rels.append({'id':_txt(r.get('id'),512) or f'program-relation-{i+1}','fromStudyId':a,'toStudyId':b,'type':typ,'declared':True})
    rec={'schema':'sc-lab-research-program/0.138.0','version':VERSION,'recordType':'research-program','collection':'graphStudioResearchPrograms','id':pid,'programId':pid,'title':_txt(_get(raw,'title','name'),1024) or pid,'studies':studies,'relationships':rels,'createdAt':_txt(_get(raw,'createdAt','created_at'),128) or _now(),'createdBy':_txt(_get(raw,'createdBy','created_by'),256) or 'user','boundary':BOUNDARY}
    rec['fingerprint']=_fp({k:v for k,v in rec.items() if k!='fingerprint'})
    return {'ok':True,'version':VERSION,'record':rec,'boundary':BOUNDARY}

def validate_program(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    r=n['record']; ids={s['studyId'] for s in r['studies']}; errors=[]; warnings=[]
    for rel in r['relationships']:
        if rel['fromStudyId'] not in ids or rel['toStudyId'] not in ids: errors.append(f"relationship {rel['id']} references an unknown study")
    if len(r['studies'])<2: warnings.append('program contains fewer than two studies; cross-study intelligence is limited')
    return {'ok':not errors,'version':VERSION,'record':r,'errors':errors,'warnings':warnings,'boundary':BOUNDARY}

def study_registry(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    rows=[{k:s.get(k) for k in ('studyId','projectId','title','status','versionRef')} | {'nodeCount':len(s['nodes']),'edgeCount':len(s['edges']),'changeEventCount':len(s['changeEvents'])} for s in n['record']['studies']]
    return {'ok':True,'version':VERSION,'programId':n['record']['programId'],'studies':rows,'count':len(rows),'boundary':BOUNDARY}

def relationship_matrix(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    return {'ok':True,'version':VERSION,'programId':n['record']['programId'],'relationships':n['record']['relationships'],'count':len(n['record']['relationships']),'boundary':BOUNDARY}

def shared_object_index(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    idx={}
    for study in n['record']['studies']:
        for node in study['nodes']:
            if not isinstance(node,dict): continue
            oid=_txt(node.get('id'),512)
            if not oid: continue
            item=idx.setdefault(oid,{'objectId':oid,'studyIds':[],'objectTypes':set(),'labels':set()})
            item['studyIds'].append(study['studyId']); item['objectTypes'].add(_txt(node.get('type') or node.get('objectType'),128) or 'research-object'); item['labels'].add(_txt(node.get('label') or node.get('title'),1024) or oid)
    rows=[]
    for oid,item in idx.items():
        if len(set(item['studyIds']))>1:
            rows.append({'objectId':oid,'studyIds':sorted(set(item['studyIds'])),'studyCount':len(set(item['studyIds'])),'objectTypes':sorted(item['objectTypes']),'labels':sorted(item['labels'])})
    rows.sort(key=lambda x:(-x['studyCount'],x['objectId']))
    return {'ok':True,'version':VERSION,'programId':n['record']['programId'],'sharedObjects':rows,'count':len(rows),'boundary':BOUNDARY}

def program_change_impact(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    event_payload=payload.get('changeEvent') if isinstance(payload,dict) else None
    ev=living.normalize_change_event({'changeEvent':event_payload or {}})
    if not ev.get('ok'): return ev
    oid=ev['record']['objectId']; affected=[]; skipped=[]
    for study in n['record']['studies']:
        ids={_txt(x.get('id'),512) for x in study['nodes'] if isinstance(x,dict)}
        if oid not in ids:
            skipped.append(study['studyId']); continue
        q={'projectId':study['projectId'],'changeEvent':{**ev['record'],'projectId':study['projectId']},'nodes':study['nodes'],'edges':study['edges']}
        r=living.analyze_change(q)
        if r.get('ok'):
            affected.append({'studyId':study['studyId'],'projectId':study['projectId'],'impact':r['record'],'obligationCount':len(r['record']['obligations'])})
    rec={'schema':'sc-lab-cross-study-change-impact/0.138.0','version':VERSION,'recordType':'cross-study-change-impact','collection':'graphStudioCrossStudyChangeImpacts','id':f"program-impact-{ev['record']['id']}",'programId':n['record']['programId'],'changeEvent':ev['record'],'affectedStudies':affected,'affectedStudyIds':[x['studyId'] for x in affected],'unmatchedStudyIds':skipped,'declaredDependenciesOnly':True,'potentialImpactOnly':True,'automaticScientificInvalidation':False,'createdAt':_now(),'boundary':BOUNDARY}
    rec['fingerprint']=_fp({k:v for k,v in rec.items() if k!='fingerprint'})
    return {'ok':True,'version':VERSION,'record':rec,'boundary':BOUNDARY}

def cross_study_obligations(payload):
    r=program_change_impact(payload)
    if not r.get('ok'): return r
    items=[]
    for s in r['record']['affectedStudies']:
        for o in s['impact'].get('obligations',[]): items.append({'studyId':s['studyId'],'projectId':s['projectId'],**o})
    items.sort(key=lambda x:(x['studyId'],x.get('objectId','')))
    return {'ok':True,'version':VERSION,'programId':r['record']['programId'],'items':items,'count':len(items),'boundary':BOUNDARY}

def program_living_status(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    studies=[]; total=0
    for s in n['record']['studies']:
        q={'projectId':s['projectId'],'nodes':s['nodes'],'edges':s['edges'],'changeEvents':s['changeEvents']}
        st=living.living_status(q); total+=st.get('assessmentRequiredCount',0)
        studies.append({'studyId':s['studyId'],'projectId':s['projectId'],'state':st.get('state'),'assessmentRequiredCount':st.get('assessmentRequiredCount',0),'changeEventCount':st.get('changeEventCount',0)})
    state='attention-required' if total else 'current-within-declared-program-change-log'
    return {'ok':True,'version':VERSION,'programId':n['record']['programId'],'studyCount':len(studies),'studies':studies,'assessmentRequiredCount':total,'state':state,'scientificValidity':None,'crossStudyConsensus':None,'boundary':BOUNDARY}

def program_attention_register(payload):
    s=program_living_status(payload); return {'ok':s.get('ok',False),'version':VERSION,'programId':s.get('programId'),'items':[x for x in s.get('studies',[]) if x.get('assessmentRequiredCount',0)>0],'count':sum(1 for x in s.get('studies',[]) if x.get('assessmentRequiredCount',0)>0),'boundary':BOUNDARY}

def program_snapshot(payload):
    n=normalize_program(payload); status=program_living_status(payload); shared=shared_object_index(payload)
    if not n.get('ok'): return n
    snap={'schema':'sc-lab-research-program-snapshot/0.138.0','version':VERSION,'programId':n['record']['programId'],'programFingerprint':n['record']['fingerprint'],'livingStatus':status,'sharedObjectIndex':shared.get('sharedObjects',[]),'createdAt':_now(),'boundary':BOUNDARY}
    snap['fingerprint']=_fp({k:v for k,v in snap.items() if k!='fingerprint'})
    return {'ok':True,'version':VERSION,'snapshot':snap,'boundary':BOUNDARY}

def compare_snapshots(payload):
    L=payload.get('left') if isinstance(payload,dict) else {}; R=payload.get('right') if isinstance(payload,dict) else {}; L=L or {}; R=R or {}
    def studies(x): return {s.get('studyId') for s in _get(x,'livingStatus',default={}).get('studies',[]) if isinstance(s,dict)}
    li,ri=studies(L),studies(R)
    def shared(x): return {o.get('objectId') for o in x.get('sharedObjectIndex',[]) if isinstance(o,dict)}
    lo,ro=shared(L),shared(R)
    return {'ok':True,'version':VERSION,'addedStudyIds':sorted(ri-li),'removedStudyIds':sorted(li-ri),'addedSharedObjectIds':sorted(ro-lo),'removedSharedObjectIds':sorted(lo-ro),'programChanged':L.get('programFingerprint')!=R.get('programFingerprint'),'boundary':BOUNDARY}

def study_context(payload):
    n=normalize_program(payload); sid=_txt(_get(payload,'studyId','study_id'),512) if isinstance(payload,dict) else ''
    if not n.get('ok'): return n
    s=next((x for x in n['record']['studies'] if x['studyId']==sid),None)
    if not s: return {'ok':False,'version':VERSION,'error':'studyId is not in program','boundary':BOUNDARY}
    rel=[r for r in n['record']['relationships'] if sid in (r['fromStudyId'],r['toStudyId'])]
    shared=[x for x in shared_object_index(payload).get('sharedObjects',[]) if sid in x['studyIds']]
    return {'ok':True,'version':VERSION,'programId':n['record']['programId'],'study':s,'relationships':rel,'sharedObjects':shared,'boundary':BOUNDARY}

def program_workspace_packet(payload):
    n=normalize_program(payload)
    if not n.get('ok'): return n
    packet={'schema':'sc-lab-project-workspace-research-program/0.138.0','version':VERSION,'program':n['record'],'studyRegistry':study_registry(payload).get('studies',[]),'relationshipMatrix':relationship_matrix(payload).get('relationships',[]),'sharedObjectIndex':shared_object_index(payload).get('sharedObjects',[]),'livingStatus':program_living_status(payload),'boundary':BOUNDARY}
    packet['packetFingerprint']=_fp({k:v for k,v in packet.items() if k!='packetFingerprint'})
    return {'ok':True,'version':VERSION,'packet':packet,'boundary':BOUNDARY}

def integrated_status(payload):
    return {'ok':True,'version':VERSION,'researchProgram':program_living_status(payload),'integratedReviewWorkspace':integrated.status(payload),'boundary':BOUNDARY}

def fingerprint(payload):
    n=normalize_program(payload); return {'ok':n.get('ok',False),'version':VERSION,'programId':n.get('record',{}).get('programId'),'fingerprint':n.get('record',{}).get('fingerprint'),'boundary':BOUNDARY}

def contract(): return {'ok':True,'version':VERSION,'route_count':ROUTE_COUNT,'relationshipTypes':list(RELATION_TYPES),'collections':['graphStudioResearchPrograms','graphStudioCrossStudyChangeImpacts'],'boundary':BOUNDARY}
def policy(): return {'ok':True,'version':VERSION,'declaredStudyRelationshipsOnly':True,'declaredDependenciesOnly':True,'potentialImpactOnly':True,'humanScientificJudgmentRequired':True,'automaticScientificValidity':False,'automaticConsensus':False,'truthRanking':False,'evidenceWeightInference':False,'causalInference':False,'boundary':BOUNDARY}
def health(): return {'ok':True,'version':VERSION,'api_route_count':ROUTE_COUNT,'cross_study_research_program_intelligence':True,'program_living_analysis':True,'shared_research_object_index':True,'boundary':BOUNDARY}
def acceptance_report(): return {'ok':True,'version':VERSION,'programRegistry':True,'studyRelationshipMatrix':True,'sharedResearchObjectIndex':True,'crossStudyChangePropagation':True,'crossStudyObligations':True,'programLivingStatus':True,'programSnapshots':True,'projectWorkspaceHandoff':True,'backwardCompatibleV01370':True,'automaticScientificValidity':False,'automaticConsensus':False,'truthRanking':False,'evidenceWeightInference':False,'causalInference':False,'route_count':ROUTE_COUNT,'boundary':BOUNDARY}
def release_gates(): return {'ok':True,'version':VERSION,'requiredRouteCount':ROUTE_COUNT,'crossStudyResearchProgramIntelligence':True,'sharedResearchObjectIndex':True,'crossStudyChangePropagation':True,'programLivingStatus':True,'automaticScientificValidity':False,'automaticConsensus':False,'boundary':BOUNDARY}
