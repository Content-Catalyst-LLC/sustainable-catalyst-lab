from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone
from typing import Any

VERSION="0.142.0"
PREDECESSOR_VERSION="0.141.8"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
ML_WORKSPACE_VERSION="0.141.0"
SCHEMA="sc-lab-integrated-neural-research-workspace/0.142.0"
SESSION_SCHEMA="sc-lab-integrated-neural-research-session/0.142.0"
SNAPSHOT_SCHEMA="sc-lab-integrated-neural-research-workspace-snapshot/0.142.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-integrated-neural-execution-request/1.0"
CORE_HANDOFF_SCHEMA="sc-core-integrated-neural-research-context/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-integrated-neural-handoff/1.0"
PACKAGE_HANDOFF_SCHEMA="sc-lab-reproducible-neural-package-handoff/1.0"

BOUNDARY=(
    "The Integrated Neural Research Workspace coordinates governed neural research objects and views across the Lab. "
    "It does not execute training, hyperparameter search, embedding extraction, explainability compute, or reproduction. "
    "Workspace remains execution authority; Platform Core remains canonical governed-object authority; human review remains required. "
    "Integrated visibility does not convert predictions, embeddings, explanations, ablation deltas, optimization results, or package completeness into scientific evidence or validity."
)

PANELS=(
    ("experiment","Experiment Design & Runs","0.141.0","machine-learning-experiment-workspace"),
    ("architecture","Architecture & Training","0.141.1","neural-architecture-training-configuration"),
    ("telemetry","Training Curves & Checkpoints","0.141.2","training-curves-metrics-checkpoint-visualization"),
    ("comparison","Model Comparison","0.141.3","model-comparison-experiment-matrix"),
    ("search","Hyperparameter Search","0.141.4","hyperparameter-study-search-results"),
    ("ablation","Ablation Studies","0.141.5","ablation-study-framework"),
    ("explainability","Explainability","0.141.6","neural-explainability-workspace"),
    ("embeddings","Embeddings","0.141.7","embedding-explorer"),
    ("reproducibility","Reproducibility","0.141.8","reproducible-neural-research-package"),
)
PANEL_IDS=tuple(x[0] for x in PANELS)
SESSION_STATES=("draft","active","review","reproduction","publication","archived")
OBJECT_KINDS=("experiment","dataset","split","model","architecture","training-config","run","metric-series","checkpoint","comparison","search-study","trial","ablation-study","explanation","embedding","visualization","package","review","publication","other")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=4096): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _uniq(xs):
    out=[]; seen=set()
    for x in xs:
        k=_canon(x)
        if k not in seen: seen.add(k); out.append(x)
    return out

def module_catalog():
    rows=[]
    for i,(pid,label,version,slug) in enumerate(PANELS):
        rows.append({"panelId":pid,"label":label,"order":i+1,"sourceVersion":version,"sourceSlug":slug,
                     "integrated":True,"executionAuthority":"workspace" if pid in ("experiment","architecture","search","explainability","embeddings","reproducibility") else "lab-analysis",
                     "scientificValidityCertified":False})
    return {"ok":True,"version":VERSION,"panels":rows,"panelCount":len(rows),"boundary":BOUNDARY}

def normalize_object(item:Any,index:int=0):
    raw=item if isinstance(item,dict) else {"ref":item}
    kind=_txt(raw.get("kind"),128).lower() or "other"
    if kind not in OBJECT_KINDS: kind="other"
    panel=_txt(raw.get("panel"),64).lower()
    if panel not in PANEL_IDS: panel="experiment"
    rec={"objectId":_txt(raw.get("objectId") or raw.get("id"),512) or f"object-{index+1}","kind":kind,"panel":panel,
         "ref":_txt(raw.get("ref") or raw.get("objectRef"),2048),"label":_txt(raw.get("label"),512),
         "sourceVersion":_txt(raw.get("sourceVersion"),128),"sourceSchema":_txt(raw.get("sourceSchema"),512),
         "runRef":_txt(raw.get("runRef"),1024),"experimentRef":_txt(raw.get("experimentRef"),1024),
         "datasetRef":_txt(raw.get("datasetRef"),1024),"modelRef":_txt(raw.get("modelRef"),1024),
         "checkpointRef":_txt(raw.get("checkpointRef"),1024),"provenanceRef":_txt(raw.get("provenanceRef"),1024),
         "dependsOn":[_txt(x,512) for x in _list(raw.get("dependsOn")) if _txt(x,512)],"metadata":_dict(raw.get("metadata"))}
    rec["fingerprint"]=_fp(rec)
    return rec

def normalize_session(payload:dict):
    p=payload if isinstance(payload,dict) else {}
    state=_txt(p.get("state"),64).lower() or "draft"
    if state not in SESSION_STATES: state="draft"
    objs=[normalize_object(x,i) for i,x in enumerate(_list(p.get("objects")))]
    active=_txt(p.get("activePanel"),64).lower() or "experiment"
    if active not in PANEL_IDS: active="experiment"
    pinned=[x for x in [_txt(v,512) for v in _list(p.get("pinnedObjectIds"))] if x]
    rec={"schema":SESSION_SCHEMA,"version":VERSION,"sessionId":_txt(p.get("sessionId") or p.get("id"),512) or f"neural-session-{_fp(p)[:16]}",
         "projectRef":_txt(p.get("projectRef"),1024),"studyRef":_txt(p.get("studyRef"),1024),"experimentRef":_txt(p.get("experimentRef"),1024),
         "title":_txt(p.get("title"),512) or "Integrated neural research session","state":state,"activePanel":active,
         "focusedObjectId":_txt(p.get("focusedObjectId"),512),"pinnedObjectIds":_uniq(pinned),"objects":objs,
         "filters":_dict(p.get("filters")),"notes":_list(p.get("notes")),"review":_dict(p.get("review")),"limitations":_list(p.get("limitations")),
         "workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"humanScientificReviewRequired":True,
         "automaticScientificValidity":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    stable={k:v for k,v in rec.items() if k not in ("fingerprint",)}
    rec["fingerprint"]=_fp(stable)
    return rec

def workspace_state(payload:dict):
    s=normalize_session(payload); by={p:0 for p in PANEL_IDS}
    for o in s["objects"]: by[o["panel"]]+=1
    return {"ok":True,"version":VERSION,"session":s,"panelObjectCounts":by,"boundary":BOUNDARY}

def panel_state(payload:dict):
    s=normalize_session(payload); panel=_txt(payload.get("panel"),64).lower() or s["activePanel"]
    if panel not in PANEL_IDS: panel=s["activePanel"]
    rows=[o for o in s["objects"] if o["panel"]==panel]
    return {"ok":True,"version":VERSION,"panel":panel,"objects":rows,"objectCount":len(rows),"focusedObjectId":s["focusedObjectId"],"boundary":BOUNDARY}

def object_index(payload:dict):
    s=normalize_session(payload)
    rows=[{k:o.get(k) for k in ("objectId","kind","panel","ref","label","sourceVersion","runRef","experimentRef","datasetRef","modelRef","checkpointRef","provenanceRef")} for o in s["objects"]]
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"automaticInterpretation":False,"boundary":BOUNDARY}

def lineage_graph(payload:dict):
    s=normalize_session(payload); ids={o["objectId"] for o in s["objects"]}; nodes=[]; edges=[]; missing=[]
    for o in s["objects"]:
        nodes.append({"id":o["objectId"],"kind":o["kind"],"panel":o["panel"],"label":o["label"]})
        for d in o["dependsOn"]:
            edges.append({"source":d,"target":o["objectId"],"relation":"depends-on"})
            if d not in ids: missing.append({"objectId":o["objectId"],"missingDependency":d})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"missingDependencies":missing,"complete":not missing,"lineageGraphIsCausalGraph":False,"boundary":BOUNDARY}

def cross_panel_links(payload:dict):
    s=normalize_session(payload); rows=[]
    for o in s["objects"]:
        keys={k:o[k] for k in ("runRef","experimentRef","datasetRef","modelRef","checkpointRef","provenanceRef") if o.get(k)}
        rows.append({"objectId":o["objectId"],"panel":o["panel"],"links":keys})
    return {"ok":True,"version":VERSION,"rows":rows,"crossPanelLinkIsScientificRelationship":False,"boundary":BOUNDARY}

def focus_context(payload:dict):
    s=normalize_session(payload); oid=_txt(payload.get("objectId"),512) or s["focusedObjectId"]
    found=next((o for o in s["objects"] if o["objectId"]==oid),None)
    linked=[]
    if found:
        for o in s["objects"]:
            if o["objectId"]==oid: continue
            if any(found.get(k) and found.get(k)==o.get(k) for k in ("runRef","experimentRef","datasetRef","modelRef","checkpointRef","provenanceRef")):
                linked.append({"objectId":o["objectId"],"panel":o["panel"],"kind":o["kind"]})
    return {"ok":True,"version":VERSION,"focusedObject":found,"linkedObjects":linked,"automaticSemanticInference":False,"boundary":BOUNDARY}

def linked_view_context(payload:dict):
    f=focus_context(payload); panels={x["panel"] for x in f["linkedObjects"]};
    if f["focusedObject"]: panels.add(f["focusedObject"]["panel"])
    return {"ok":True,"version":VERSION,"focusedObject":f["focusedObject"],"linkedPanels":sorted(panels),"linkedObjects":f["linkedObjects"],"selectionPropagatesContextOnly":True,"selectionPropagatesScientificConclusion":False,"boundary":BOUNDARY}

def navigation_plan(payload:dict):
    s=normalize_session(payload); active=s["activePanel"]; idx=PANEL_IDS.index(active)
    return {"ok":True,"version":VERSION,"activePanel":active,"previousPanel":PANEL_IDS[idx-1] if idx>0 else None,"nextPanel":PANEL_IDS[idx+1] if idx+1<len(PANEL_IDS) else None,
            "panelOrder":list(PANEL_IDS),"automaticWorkflowAdvance":False,"boundary":BOUNDARY}

def readiness_report(payload:dict):
    s=normalize_session(payload); present={o["panel"] for o in s["objects"]}
    core=("experiment","architecture")
    missing=[p for p in core if p not in present]
    panels=[{"panel":p,"hasObjects":p in present,"requiredForMinimumWorkspace":p in core} for p in PANEL_IDS]
    return {"ok":True,"version":VERSION,"minimumWorkspaceReady":not missing,"missingMinimumPanels":missing,"panels":panels,
            "readinessIsScientificValidity":False,"readinessIsExecutionApproval":False,"boundary":BOUNDARY}

def missingness_report(payload:dict):
    s=normalize_session(payload); present={o["panel"] for o in s["objects"]}; missing=[p for p in PANEL_IDS if p not in present]
    return {"ok":True,"version":VERSION,"missingPanels":missing,"presentPanels":[p for p in PANEL_IDS if p in present],"missingnessDoesNotInvalidateStudyAutomatically":True,"boundary":BOUNDARY}

def provenance_summary(payload:dict):
    s=normalize_session(payload); rows=[]
    for o in s["objects"]:
        rows.append({"objectId":o["objectId"],"panel":o["panel"],"sourceVersion":o["sourceVersion"],"sourceSchema":o["sourceSchema"],"provenanceRef":o["provenanceRef"],"hasProvenance":bool(o["provenanceRef"])})
    return {"ok":True,"version":VERSION,"rows":rows,"allObjectsHaveProvenance":bool(rows) and all(r["hasProvenance"] for r in rows),"provenanceCompletenessIsScientificValidity":False,"boundary":BOUNDARY}

def review_state(payload:dict):
    s=normalize_session(payload); r=s["review"]
    return {"ok":True,"version":VERSION,"review":{"status":_txt(r.get("status"),64) or "unreviewed","reviewerRefs":_list(r.get("reviewerRefs")),"openIssues":_list(r.get("openIssues")),"decisions":_list(r.get("decisions"))},
            "reviewCompletionIsPublicationAcceptance":False,"reviewCompletionIsScientificValidity":False,"boundary":BOUNDARY}

def review_packet(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"reviewPacket":{"schema":"sc-lab-integrated-neural-review-packet/0.142.0","sessionFingerprint":s["fingerprint"],"objectCount":len(s["objects"]),"limitations":s["limitations"],"review":s["review"],"panels":module_catalog()["panels"],"humanDecisionRequired":True,"scientificValidityCertified":False},"boundary":BOUNDARY}

def module_handoff(payload:dict):
    s=normalize_session(payload); target=_txt(payload.get("targetPanel"),64).lower()
    if target not in PANEL_IDS: target=s["activePanel"]
    return {"ok":True,"version":VERSION,"handoff":{"schema":"sc-lab-neural-panel-handoff/0.142.0","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"targetPanel":target,"focusedObjectId":s["focusedObjectId"],"pinnedObjectIds":s["pinnedObjectIds"],"automaticExecution":False,"automaticInterpretation":False},"boundary":BOUNDARY}

def workspace_execution_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":WORKSPACE_HANDOFF_SCHEMA,"executionAuthority":"workspace","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"experimentRef":s["experimentRef"],"requestedOperation":_txt(payload.get("requestedOperation"),128),"objectRefs":[o["ref"] for o in s["objects"] if o["ref"]],"automaticExecution":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def core_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":CORE_HANDOFF_SCHEMA,"canonicalObjectAuthority":"platform-core","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"objectRefs":[o["ref"] for o in s["objects"] if o["ref"]],"provenanceRefs":[o["provenanceRef"] for o in s["objects"] if o["provenanceRef"]],"automaticCanonicalization":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def research_os_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":RESEARCH_OS_HANDOFF_SCHEMA,"researchOSVersion":RESEARCH_OS_VERSION,"sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"requestedPhase":_txt(payload.get("requestedPhase"),128) or "analysis","automaticPhaseAdvance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def package_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":PACKAGE_HANDOFF_SCHEMA,"packageLayerVersion":PREDECESSOR_VERSION,"sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"objectRefs":[o["ref"] for o in s["objects"] if o["ref"]],"packageCompletenessCertified":False,"reproductionCertified":False,"replicationCertified":False},"boundary":BOUNDARY}

def publication_handoff(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"handoff":{"schema":"sc-lab-integrated-neural-publication-handoff/0.142.0","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"review":s["review"],"limitations":s["limitations"],"automaticPublicationAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def visual_workspace_spec(payload:dict):
    s=normalize_session(payload); counts=workspace_state(payload)["panelObjectCounts"]
    return {"ok":True,"version":VERSION,"visualSpec":{"schema":"sc-lab-integrated-neural-workspace-visual/0.142.0","layout":"linked-nine-panel-workspace","activePanel":s["activePanel"],"panelOrder":list(PANEL_IDS),"panelObjectCounts":counts,"focusedObjectId":s["focusedObjectId"],"pinnedObjectIds":s["pinnedObjectIds"],"provenanceVisible":True,"limitationsVisible":True,"derivedViewsLabeled":True,"automaticRanking":False},"boundary":BOUNDARY}

def workspace_snapshot(payload:dict):
    s=normalize_session(payload); stable=copy.deepcopy(s); stable.pop("fingerprint",None)
    fp=_fp(stable)
    return {"ok":True,"version":VERSION,"snapshot":{"schema":SNAPSHOT_SCHEMA,"snapshotId":f"neural-workspace-snapshot-{fp[:16]}","sessionId":s["sessionId"],"sessionFingerprint":s["fingerprint"],"snapshotFingerprint":fp,"state":stable,"scientificValidityCertified":False},"boundary":BOUNDARY}

def compare_snapshots(payload:dict):
    left=workspace_snapshot(_dict(payload.get("left")))["snapshot"]; right=workspace_snapshot(_dict(payload.get("right")))["snapshot"]
    return {"ok":True,"version":VERSION,"sameWorkspaceState":left["snapshotFingerprint"]==right["snapshotFingerprint"],"left":left["snapshotFingerprint"],"right":right["snapshotFingerprint"],"differenceDoesNotImplyScientificSuperiority":True,"boundary":BOUNDARY}

def workspace_diff(payload:dict):
    l=normalize_session(_dict(payload.get("left"))); r=normalize_session(_dict(payload.get("right")))
    li={o["objectId"]:o for o in l["objects"]}; ri={o["objectId"]:o for o in r["objects"]}
    added=sorted(set(ri)-set(li)); removed=sorted(set(li)-set(ri)); changed=sorted(k for k in set(li)&set(ri) if li[k]["fingerprint"]!=ri[k]["fingerprint"])
    return {"ok":True,"version":VERSION,"addedObjectIds":added,"removedObjectIds":removed,"changedObjectIds":changed,"sameWorkspaceContent":not (added or removed or changed) and l["fingerprint"]==r["fingerprint"],"differenceDoesNotImplyScientificSuperiority":True,"boundary":BOUNDARY}

def export_bundle(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"export":{"schema":"sc-lab-integrated-neural-workspace-export/0.142.0","session":s,"moduleCatalog":module_catalog()["panels"],"lineage":lineage_graph(payload),"readiness":readiness_report(payload),"provenance":provenance_summary(payload),"review":review_state(payload),"fingerprint":_fp({"session":s,"catalog":module_catalog()["panels"]})},"scientificValidityCertified":False,"boundary":BOUNDARY}

def reproducibility_summary(payload:dict):
    s=normalize_session(payload); present={o["panel"] for o in s["objects"]}
    return {"ok":True,"version":VERSION,"summary":{"sessionFingerprint":s["fingerprint"],"reproducibilityPanelPresent":"reproducibility" in present,"packageLayerVersion":PREDECESSOR_VERSION,"workspaceExecutionAuthority":True,"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None):
    return {"ok":True,"version":VERSION,"boundaries":{"predictionIsEvidence":False,"embeddingProximityIsRelationship":False,"explanationIsCausalProof":False,"ablationDeltaIsCausalEffect":False,"optimizationWinnerIsScientificWinner":False,"metricDifferenceIsScientificSuperiority":False,"packageCompletenessIsScientificValidity":False,"workspaceIntegrationIsValidity":False,"reviewCompletionIsPublicationAcceptance":False},"boundary":BOUNDARY}

def policy():
    return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labCoordinatesResearch":True,"labExecutesTraining":False,"labExecutesSearch":False,"labExecutesExplainabilityCompute":False,"labExecutesEmbeddingExtraction":False,"labExecutesReproduction":False,"automaticWorkflowAdvance":False,"automaticModelPromotion":False,"automaticScientificValidity":False,"automaticPublicationAcceptance":False,"predictionIsEvidence":False,"humanScientificReviewRequired":True,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"sessionSchema":SESSION_SCHEMA,"snapshotSchema":SNAPSHOT_SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"integrityBaseline":INTEGRITY_BASELINE,"panels":module_catalog()["panels"],"sessionStates":list(SESSION_STATES),"objectKinds":list(OBJECT_KINDS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":{"predecessorPackageLayerRetained":True,"allNineNeuralPanelsIntegrated":True,"sharedSessionContext":True,"crossPanelFocusContext":True,"lineageVisible":True,"provenanceVisible":True,"limitationsVisible":True,"workspaceExecutionBoundaryPreserved":True,"platformCoreAuthorityPreserved":True,"integrityRepairRetained":True,"automaticScientificValidity":False},"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"integratedNeuralResearchWorkspace":True,"panelCount":len(PANELS),"api_route_count":39,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"integrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesTraining":False,"automaticScientificValidity":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"accepted":True,"sharedSessionContext":True,"ninePanelWorkspace":True,"objectIndex":True,"lineageGraph":True,"crossPanelLinks":True,"focusContext":True,"linkedViewContext":True,"readinessReport":True,"reviewPacket":True,"workspaceHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"packageHandoff":True,"publicationHandoff":True,"visualWorkspaceSpec":True,"deterministicSnapshots":True,"exportBundle":True,"integrityRepairRetained":True,"scientificValidityCertified":False,"boundary":BOUNDARY}
