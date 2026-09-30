from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone
from typing import Any

VERSION="0.150.0"
PREDECESSOR_VERSION="0.149.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-integrated-computational-research-laboratory/0.150.0"
SESSION_SCHEMA="sc-lab-integrated-computational-research-session/0.150.0"
PROJECT_SCHEMA="sc-lab-integrated-computational-research-project/0.150.0"
WORKSPACE_REF_SCHEMA="sc-lab-integrated-computational-workspace-ref/0.150.0"
OBJECT_REF_SCHEMA="sc-lab-integrated-computational-object-ref/0.150.0"
SNAPSHOT_SCHEMA="sc-lab-integrated-computational-research-snapshot/0.150.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-integrated-computational-research-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-integrated-computational-research-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-integrated-computational-research-context/1.0"
LIBRARY_HANDOFF_SCHEMA="sc-library-integrated-computational-source-request/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-integrated-computational-handoff/1.0"

BOUNDARY=(
    "The Integrated Computational Research Laboratory links specialized Lab workspaces into one governed research session without replacing their domain-specific contracts or compute boundaries. "
    "Workspace remains the primary execution authority, Workbench remains the prototype authority, Knowledge Library remains the source/document authority, and Platform Core remains the canonical governed-object authority. "
    "Cross-workspace integration does not convert model output, statistical significance, simulation results, graph structure, embeddings, multimodal similarity, benchmark performance, or reproducibility into evidence, causality, scientific validity, deployment readiness, or publication acceptance."
)

WORKSPACES=(
    ("neural","0.142.0","Integrated Neural Research Workspace"),
    ("linguistics","0.143.0","Computational Linguistics Research Workspace"),
    ("statistics-econometrics","0.144.0","Statistical & Econometric Research Workspace"),
    ("simulation","0.145.0","Simulation & Computational Experiment Workspace"),
    ("graph-network","0.146.0","Graph & Network Science Research Workspace"),
    ("graph-ml","0.147.0","Graph Machine Learning Experiment Workspace"),
    ("multimodal","0.148.0","Multimodal Scientific Experiment Workspace"),
    ("validation","0.149.0","Scientific Model Validation & Benchmark Laboratory"),
)
SESSION_STATES=("draft","active","execution","analysis","review","validation","reproduction","publication","archived")
OBJECT_KINDS=("project","study","dataset","source","model","run","result","visualization","claim","finding","review","package","publication","other")
PANEL_ORDER=tuple(x[0] for x in WORKSPACES)


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _stable(obj):
    x=copy.deepcopy(obj)
    if isinstance(x,dict): x.pop("generatedAt",None)
    return x

def workspace_registry():
    return {"ok":True,"version":VERSION,"workspaces":[{"workspaceId":i,"version":v,"title":t,"executionAuthority":"Workspace","canonicalAuthority":"Platform Core"} for i,v,t in WORKSPACES],"panelCount":len(WORKSPACES)}

def catalog():
    return {"ok":True,"version":VERSION,"workspaces":workspace_registry()["workspaces"],"sessionStates":list(SESSION_STATES),"objectKinds":list(OBJECT_KINDS),"panelOrder":list(PANEL_ORDER),"boundary":BOUNDARY}

def normalize_session(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in SESSION_STATES else "draft"
    r={"schema":SESSION_SCHEMA,"version":VERSION,"sessionId":_txt(p.get("sessionId") or p.get("id"),512) or f"session-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"state":state,"projectRef":_txt(p.get("projectRef"),512),"activeWorkspace":_txt(p.get("activeWorkspace"),128) or "neural","workspaceRefs":_list(p.get("workspaceRefs")),"objectRefs":_list(p.get("objectRefs")),"focusRef":_txt(p.get("focusRef"),512),"review":_dict(p.get("review")),"provenance":_dict(p.get("provenance")),"limitations":_list(p.get("limitations")),"automaticWorkflowAdvance":False,"scientificValidityCertified":False,"publicationAccepted":False}; r["fingerprint"]=_fp(r); return r

def normalize_project(payload:dict):
    p=_dict(payload); r={"schema":PROJECT_SCHEMA,"version":VERSION,"projectId":_txt(p.get("projectId") or p.get("id"),512) or f"project-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"researchQuestion":_txt(p.get("researchQuestion"),8192),"hypotheses":_list(p.get("hypotheses")),"workspaceRefs":_list(p.get("workspaceRefs")),"sourceRefs":_list(p.get("sourceRefs")),"datasetRefs":_list(p.get("datasetRefs")),"provenance":_dict(p.get("provenance")),"limitations":_list(p.get("limitations")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_workspace_ref(payload:dict):
    p=_dict(payload); wid=_txt(p.get("workspaceId"),128); known={i:v for i,v,_ in WORKSPACES}; r={"schema":WORKSPACE_REF_SCHEMA,"version":VERSION,"workspaceId":wid,"workspaceVersion":_txt(p.get("workspaceVersion"),64) or known.get(wid,""),"objectRefs":_list(p.get("objectRefs")),"state":_dict(p.get("state")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_object_ref(payload:dict):
    p=_dict(payload); kind=_txt(p.get("kind"),128).lower() or "other"; kind=kind if kind in OBJECT_KINDS else "other"; r={"schema":OBJECT_REF_SCHEMA,"version":VERSION,"ref":_txt(p.get("ref") or p.get("id"),1024),"kind":kind,"workspaceId":_txt(p.get("workspaceId"),128),"sourceVersion":_txt(p.get("sourceVersion"),64),"provenance":_dict(p.get("provenance")),"derived":bool(p.get("derived",False)),"evidenceStatus":_txt(p.get("evidenceStatus"),128) or "unspecified","scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_compute_request(payload:dict):
    p=_dict(payload); r={"version":VERSION,"requestId":_txt(p.get("requestId"),512) or f"compute-{_fp(p)[:16]}","workspaceId":_txt(p.get("workspaceId"),128),"runtime":_txt(p.get("runtime"),128),"operation":_txt(p.get("operation"),512),"inputRefs":_list(p.get("inputRefs")),"parameters":_dict(p.get("parameters")),"executionAuthority":"Workspace","labExecutesHeavyCompute":False,"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_review(payload:dict):
    p=_dict(payload); r={"version":VERSION,"reviewId":_txt(p.get("reviewId"),512) or f"review-{_fp(p)[:16]}","reviewerRefs":_list(p.get("reviewerRefs")),"status":_txt(p.get("status"),128) or "draft","findings":_list(p.get("findings")),"dissent":_list(p.get("dissent")),"scientificValidityCertified":False,"publicationAccepted":False}; r["fingerprint"]=_fp(r); return r

def normalize_publication(payload:dict):
    p=_dict(payload); r={"version":VERSION,"publicationId":_txt(p.get("publicationId"),512) or f"publication-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"artifactRefs":_list(p.get("artifactRefs")),"reviewRefs":_list(p.get("reviewRefs")),"limitations":_list(p.get("limitations")),"publicationAccepted":False,"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def laboratory_state(payload:dict):
    p=_dict(payload); s=normalize_session(_dict(p.get("session") or p)); refs=_list(p.get("workspaceRefs") or s.get("workspaceRefs")); return {"ok":True,"version":VERSION,"session":s,"workspaceCount":len(refs),"activeWorkspace":s["activeWorkspace"],"workspaceRefs":refs,"integrated":True,"scientificValidityCertified":False}

def project_context(payload:dict): return {"ok":True,"version":VERSION,"project":normalize_project(_dict(payload.get("project") if isinstance(payload,dict) else {})),"sessionRef":_txt(_dict(payload).get("sessionRef"),512)}
def workspace_state(payload:dict): return {"ok":True,"version":VERSION,"workspace":normalize_workspace_ref(_dict(payload.get("workspace") if isinstance(payload,dict) else payload)),"scientificValidityCertified":False}
def panel_state(payload:dict):
    p=_dict(payload); wid=_txt(p.get("workspaceId"),128); return {"ok":True,"version":VERSION,"workspaceId":wid,"objects":_list(p.get("objects")),"selectedRef":_txt(p.get("selectedRef"),512),"review":_dict(p.get("review")),"scientificValidityCertified":False}

def object_index(payload:dict):
    p=_dict(payload); objs=[normalize_object_ref(x) for x in _list(p.get("objects")) if isinstance(x,dict)]; return {"ok":True,"version":VERSION,"objects":objs,"count":len(objs),"byWorkspace":{w:sum(1 for o in objs if o["workspaceId"]==w) for w in PANEL_ORDER}}

def lineage_graph(payload:dict):
    p=_dict(payload); nodes=_list(p.get("nodes")); edges=_list(p.get("edges")); return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"nodeCount":len(nodes),"edgeCount":len(edges),"lineageIsCausalProof":False}

def cross_workspace_links(payload:dict):
    p=_dict(payload); links=_list(p.get("links")); return {"ok":True,"version":VERSION,"links":links,"count":len(links),"crossWorkspaceLinkIsEvidence":False,"semanticEquivalenceInferred":False}

def focus_context(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"focusRef":_txt(p.get("focusRef"),512),"workspaceId":_txt(p.get("workspaceId"),128),"linkedRefs":_list(p.get("linkedRefs")),"contextOnly":True}
def linked_view_context(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"sourceView":_txt(p.get("sourceView"),512),"targetViews":_list(p.get("targetViews")),"filters":_dict(p.get("filters")),"selection":_dict(p.get("selection")),"linkedViewDoesNotMutateEvidence":True}
def navigation_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"currentWorkspace":_txt(p.get("currentWorkspace"),128),"nextWorkspace":_txt(p.get("nextWorkspace"),128),"reason":_txt(p.get("reason"),4096),"automaticWorkflowAdvance":False,"humanChoiceRequired":True}
def readiness_report(payload:dict):
    p=_dict(payload); req=_list(p.get("requirements")); missing=[x for x in req if isinstance(x,dict) and not bool(x.get("satisfied"))]; return {"ok":True,"version":VERSION,"requirements":req,"missing":missing,"ready":len(missing)==0,"scientificValidityCertified":False}
def missingness_report(payload:dict):
    p=_dict(payload); refs=_list(p.get("expectedRefs")); present=set(map(str,_list(p.get("presentRefs")))); missing=[x for x in refs if str(x) not in present]; return {"ok":True,"version":VERSION,"expectedCount":len(refs),"missing":missing,"complete":not missing}
def provenance_summary(payload:dict):
    p=_dict(payload); items=_list(p.get("items")); with_prov=sum(1 for x in items if isinstance(x,dict) and x.get("provenance")); return {"ok":True,"version":VERSION,"itemCount":len(items),"withProvenance":with_prov,"missingProvenance":len(items)-with_prov,"provenanceCompletenessIsValidity":False}
def review_state(payload:dict): return {"ok":True,"version":VERSION,"review":normalize_review(_dict(payload.get("review") if isinstance(payload,dict) else payload)),"humanScientificReviewRequired":True}
def review_packet(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"packet":{"sessionRef":_txt(p.get("sessionRef"),512),"objectRefs":_list(p.get("objectRefs")),"workspaceRefs":_list(p.get("workspaceRefs")),"limitations":_list(p.get("limitations")),"openQuestions":_list(p.get("openQuestions")),"generatedAt":_now(),"scientificValidityCertified":False}}

def compute_registry(payload:dict):
    p=_dict(payload); jobs=_list(p.get("jobs")); return {"ok":True,"version":VERSION,"jobs":jobs,"count":len(jobs),"labExecutionAuthority":False}
def runtime_matrix(payload:dict):
    p=_dict(payload); rows=_list(p.get("rows")); return {"ok":True,"version":VERSION,"rows":rows,"executionAuthority":"Workspace","automaticRuntimeSelection":False}
def execution_plan(payload:dict):
    p=_dict(payload); steps=_list(p.get("steps")); return {"ok":True,"version":VERSION,"steps":steps,"stepCount":len(steps),"automaticExecution":False,"executionAuthority":"Workspace"}
def evidence_boundary_audit(payload:dict):
    p=_dict(payload); items=_list(p.get("items")); violations=[]
    for x in items:
        if isinstance(x,dict) and x.get("derived") and str(x.get("evidenceStatus","")) in {"established","fact","evidence"}: violations.append(x.get("ref") or x.get("id"))
    return {"ok":True,"version":VERSION,"violations":violations,"clean":not violations,"derivedOutputAutomaticallyBecomesEvidence":False}
def scientific_boundary_audit(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"claims":_list(p.get("claims")),"boundaries":{"predictionIsEvidence":False,"statisticalSignificanceIsScientificValidity":False,"simulationOutputIsEmpiricalEvidence":False,"graphMetricIsEvidence":False,"crossModalSimilarityIsEvidence":False,"benchmarkPerformanceIsScientificValidity":False,"reproducibilityIsScientificValidity":False}}
def uncertainty_summary(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"uncertainty":_dict(p.get("uncertainty")),"sensitivity":_dict(p.get("sensitivity")),"assumptions":_list(p.get("assumptions")),"uncertaintyDoesNotEstablishValidity":True}
def comparison_matrix(payload:dict):
    p=_dict(payload); rows=_list(p.get("rows")); return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"automaticRanking":False,"automaticWinnerSelection":False,"scientificSuperiorityEstablished":False}
def milestone_summary(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"milestone":"Integrated Computational Research Laboratory","workspaces":workspace_registry()["workspaces"],"projectRef":_txt(p.get("projectRef"),512),"scientificValidityCertified":False,"publicationAccepted":False}

def _handoff(schema:str,target:str,payload:dict):
    p=_dict(payload); h={"schema":schema,"version":VERSION,"target":target,"sessionRef":_txt(p.get("sessionRef"),512),"projectRef":_txt(p.get("projectRef"),512),"objectRefs":_list(p.get("objectRefs")),"context":_dict(p.get("context")),"scientificValidityCertified":False,"deploymentReadinessCertified":False,"publicationAccepted":False}; h["fingerprint"]=_fp(h); return {"ok":True,"version":VERSION,"handoff":h}
def workspace_execution_handoff(payload:dict): return _handoff(WORKSPACE_HANDOFF_SCHEMA,"Workspace",payload)
def workbench_handoff(payload:dict): return _handoff(WORKBENCH_HANDOFF_SCHEMA,"Workbench",payload)
def core_handoff(payload:dict): return _handoff(CORE_HANDOFF_SCHEMA,"Platform Core",payload)
def library_handoff(payload:dict): return _handoff(LIBRARY_HANDOFF_SCHEMA,"Knowledge Library",payload)
def research_os_handoff(payload:dict): return _handoff(RESEARCH_OS_HANDOFF_SCHEMA,"Research OS",payload)
def neural_handoff(payload:dict): return _handoff("sc-lab-integrated-neural-research-handoff/1.0","Integrated Neural Research Workspace",payload)
def linguistics_handoff(payload:dict): return _handoff("sc-lab-computational-linguistics-handoff/1.0","Computational Linguistics Research Workspace",payload)
def statistics_handoff(payload:dict): return _handoff("sc-lab-statistical-econometric-handoff/1.0","Statistical & Econometric Research Workspace",payload)
def simulation_handoff(payload:dict): return _handoff("sc-lab-simulation-experiment-handoff/1.0","Simulation & Computational Experiment Workspace",payload)
def graph_handoff(payload:dict): return _handoff("sc-lab-graph-network-science-handoff/1.0","Graph & Network Science Research Workspace",payload)
def graph_ml_handoff(payload:dict): return _handoff("sc-lab-graph-ml-experiment-handoff/1.0","Graph Machine Learning Experiment Workspace",payload)
def multimodal_handoff(payload:dict): return _handoff("sc-lab-multimodal-experiment-handoff/1.0","Multimodal Scientific Experiment Workspace",payload)
def validation_handoff(payload:dict): return _handoff("sc-lab-model-validation-benchmark-handoff/1.0","Scientific Model Validation & Benchmark Laboratory",payload)

def visual_laboratory_spec(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"spec":{"layout":"integrated-computational-research-laboratory","panels":list(PANEL_ORDER),"activeWorkspace":_txt(p.get("activeWorkspace"),128) or "neural","linkedViews":True,"crossFiltering":True,"provenanceVisible":True,"scientificValidityCertified":False}}
def dashboard_spec(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"dashboard":{"projectRef":_txt(p.get("projectRef"),512),"cards":["research-context","workspace-status","compute","lineage","uncertainty","review","validation","reproducibility"],"automaticRanking":False}}

def workspace_snapshot(payload:dict):
    p=_dict(payload); body={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"session":normalize_session(_dict(p.get("session"))),"project":normalize_project(_dict(p.get("project"))),"workspaceRefs":_list(p.get("workspaceRefs")),"objectRefs":_list(p.get("objectRefs")),"review":_dict(p.get("review")),"limitations":_list(p.get("limitations")),"scientificValidityCertified":False}; body["fingerprint"]=_fp(body); return {"ok":True,"version":VERSION,"snapshot":body}
def compare_snapshots(payload:dict):
    p=_dict(payload); a=_stable(_dict(p.get("a"))); b=_stable(_dict(p.get("b"))); return {"ok":True,"version":VERSION,"equal":_canon(a)==_canon(b),"aFingerprint":_fp(a),"bFingerprint":_fp(b),"scientificValidityCertified":False}
def workspace_diff(payload:dict):
    p=_dict(payload); a=_dict(p.get("a")); b=_dict(p.get("b")); keys=sorted(set(a)|set(b)); changes=[{"key":k,"from":a.get(k),"to":b.get(k)} for k in keys if a.get(k)!=b.get(k)]; return {"ok":True,"version":VERSION,"changes":changes,"changeCount":len(changes)}
def export_bundle(payload:dict):
    p=_dict(payload); body={"version":VERSION,"session":_dict(p.get("session")),"project":_dict(p.get("project")),"workspaceRefs":_list(p.get("workspaceRefs")),"objectRefs":_list(p.get("objectRefs")),"provenance":_dict(p.get("provenance")),"review":_dict(p.get("review")),"limitations":_list(p.get("limitations")),"scientificValidityCertified":False}; return {"ok":True,"version":VERSION,"bundle":body,"fingerprint":_fp(body)}
def reproducibility_package(payload:dict):
    p=_dict(payload); body={"version":VERSION,"sessionRef":_txt(p.get("sessionRef"),512),"projectRef":_txt(p.get("projectRef"),512),"workspaceRefs":_list(p.get("workspaceRefs")),"objectRefs":_list(p.get("objectRefs")),"environmentRefs":_list(p.get("environmentRefs")),"runtimeRefs":_list(p.get("runtimeRefs")),"sourceRefs":_list(p.get("sourceRefs")),"instructions":_list(p.get("instructions")),"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; body["fingerprint"]=_fp(body); return {"ok":True,"version":VERSION,"package":body}
def publication_handoff(payload:dict): return _handoff("sc-lab-integrated-computational-publication-handoff/1.0","Publication Studio",payload)
def handoff_bundle(payload:dict):
    return {"ok":True,"version":VERSION,"handoffs":{"workspace":workspace_execution_handoff(payload)["handoff"],"core":core_handoff(payload)["handoff"],"library":library_handoff(payload)["handoff"],"researchOS":research_os_handoff(payload)["handoff"]},"scientificValidityCertified":False}

def panel_view(workspace_id:str,payload:dict|None=None):
    p=_dict(payload); reg={x[0]:{"version":x[1],"title":x[2]} for x in WORKSPACES}; meta=reg.get(workspace_id,{"version":"","title":workspace_id}); return {"ok":True,"version":VERSION,"workspaceId":workspace_id,"workspaceVersion":meta["version"],"title":meta["title"],"objects":_list(p.get("objects")),"selectedRef":_txt(p.get("selectedRef"),512),"scientificValidityCertified":False}

def contract(): return {"ok":True,"schema":SCHEMA,"version":VERSION,"predecessorVersion":PREDECESSOR_VERSION,"workspaceCount":len(WORKSPACES),"workspaceVersions":{i:v for i,v,_ in WORKSPACES},"integrityBaseline":INTEGRITY_BASELINE,"researchOSVersion":RESEARCH_OS_VERSION,"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"knowledgeLibrarySourceAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesHeavyCompute":False,"automaticWorkflowAdvance":False,"automaticModelPromotion":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"automaticDeploymentReadiness":False,"automaticPublicationAcceptance":False,"humanScientificReviewRequired":True,"derivedOutputIsEvidence":False,"reproducibilityIsScientificValidity":False,"boundary":BOUNDARY}
def interpretation_boundary(): return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"predictionIsEvidence":False,"statisticalSignificanceIsScientificValidity":False,"simulationOutputIsEmpiricalEvidence":False,"graphMetricIsEvidence":False,"crossModalSimilarityIsEvidence":False,"benchmarkPerformanceIsScientificValidity":False,"reproducibilityIsScientificValidity":False}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"eightWorkspaceRegistry":True,"sharedSessionContext":True,"objectIndex":True,"lineageGraph":True,"crossWorkspaceLinks":True,"computeAuthoritySeparated":True,"sourceAuthoritySeparated":True,"canonicalAuthoritySeparated":True,"scientificBoundariesRetained":True,"reviewRequired":True,"snapshots":True,"export":True,"reproducibility":True,"publicationHandoff":True,"predecessorCompatibility":True,"installedRuntimeIntegrity":True}}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"integratedLaboratoryShell":True,"eightWorkspaceRegistry":True,"sharedSessionContext":True,"crossWorkspaceNavigation":True,"lineageAndProvenance":True,"computeAndRuntimeRegistry":True,"scientificBoundaryAudits":True,"reviewAndValidation":True,"reproducibilityPackage":True,"publicationHandoff":True},"scientificValidityCertified":False,"deploymentReadinessCertified":False,"publicationAccepted":False}
def health(): return {"ok":True,"version":VERSION,"integratedComputationalResearchLaboratory":True,"api_route_count":86,"predecessorVersion":PREDECESSOR_VERSION,"workspaceCount":len(WORKSPACES),"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"knowledgeLibrarySourceAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesHeavyCompute":False,"automaticWorkflowAdvance":False,"automaticModelPromotion":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"automaticDeploymentReadiness":False,"automaticPublicationAcceptance":False,"humanScientificReviewRequired":True,"derivedOutputIsEvidence":False,"reproducibilityIsScientificValidity":False}
