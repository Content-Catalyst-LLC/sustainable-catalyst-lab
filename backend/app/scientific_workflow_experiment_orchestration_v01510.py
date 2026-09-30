from __future__ import annotations
import copy, hashlib, json
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

VERSION="0.151.0"
PREDECESSOR_VERSION="0.150.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-scientific-workflow-experiment-orchestration/0.151.0"
WORKFLOW_SCHEMA="sc-lab-scientific-workflow-definition/0.151.0"
STAGE_SCHEMA="sc-lab-scientific-workflow-stage/0.151.0"
DEPENDENCY_SCHEMA="sc-lab-scientific-workflow-dependency/0.151.0"
GATE_SCHEMA="sc-lab-scientific-workflow-gate/0.151.0"
RUN_SCHEMA="sc-lab-scientific-workflow-run/0.151.0"
STAGE_RUN_SCHEMA="sc-lab-scientific-stage-run/0.151.0"
TRANSITION_SCHEMA="sc-lab-scientific-workflow-transition-request/0.151.0"
EVENT_SCHEMA="sc-lab-scientific-orchestration-event/0.151.0"
CHECKPOINT_SCHEMA="sc-lab-scientific-workflow-checkpoint/0.151.0"
RETRY_POLICY_SCHEMA="sc-lab-scientific-workflow-retry-policy/0.151.0"
APPROVAL_SCHEMA="sc-lab-scientific-workflow-approval/0.151.0"
SNAPSHOT_SCHEMA="sc-lab-scientific-workflow-snapshot/0.151.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-scientific-workflow-execution-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-scientific-workflow-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-scientific-workflow-governed-object/1.0"
LIBRARY_HANDOFF_SCHEMA="sc-library-scientific-workflow-source-request/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-workflow-orchestration-handoff/1.0"
INTEGRATED_LAB_HANDOFF_SCHEMA="sc-lab-integrated-computational-workflow-handoff/1.0"

BOUNDARY=(
    "The Scientific Workflow & Experiment Orchestration workspace coordinates declared research stages, dependencies, gates, execution requests, checkpoints, failures, and recovery without becoming an autonomous scientific decision-maker. "
    "Platform Core remains canonical governed-object authority, Workspace remains primary compute authority, Workbench remains prototype authority, Knowledge Library remains source/document authority, and Lab governs research design, orchestration state, interpretation, review, and reproducibility. "
    "Workflow order is not scientific necessity, successful execution is not scientific validity, dependency edges are not causal proof, gate passage is not publication acceptance, retries do not repair invalid methodology, and no stage advances automatically merely because computation completed."
)

WORKSPACES=("neural","linguistics","statistics-econometrics","simulation","graph-network","graph-ml","multimodal","validation")
WORKFLOW_STATES=("draft","planned","ready","running","blocked","paused","review","completed","failed","cancelled","archived")
STAGE_STATES=("draft","ready","queued","executing","succeeded","failed","blocked","paused","skipped","review","cancelled")
STAGE_TYPES=("source-selection","preprocessing","exploratory-analysis","statistical-analysis","simulation","graph-analysis","machine-learning","graph-ml","multimodal-analysis","validation","sensitivity","robustness","review","reproduction","publication","custom")
DEPENDENCY_TYPES=("data","artifact","control","review","provenance","parameter","environment","runtime","approval","custom")
GATE_TYPES=("human-approval","provenance","data-readiness","validation","review","reproducibility","publication","safety","custom")
FAILURE_CLASSES=("input","dependency","runtime","resource","timeout","numerical","validation","policy","human-review","external","unknown")
RETRY_STRATEGIES=("none","manual","same-runtime","alternate-runtime","checkpoint-resume","recompute-upstream","custom")
APPROVAL_TYPES=("scientific-review","method-review","data-review","validation-review","reproducibility-review","publication-review","operator-approval","custom")
EXECUTION_AUTHORITIES=("Workspace","Workbench","external")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _stable(v):
    x=copy.deepcopy(v)
    if isinstance(x,dict): x.pop("generatedAt",None)
    return x

def workspace_registry():
    return {"ok":True,"version":VERSION,"workspaces":[{"workspaceId":x,"executionAuthority":"Workspace","canonicalAuthority":"Platform Core"} for x in WORKSPACES],"count":len(WORKSPACES)}

def authority_registry():
    return {"ok":True,"version":VERSION,"authorities":{"canonicalGovernedObjects":"Platform Core","primaryCompute":"Workspace","prototypeCompute":"Workbench","sourceDocuments":"Knowledge Library","scientificOrchestration":"Research Lab"},"labExecutesHeavyCompute":False}

def catalog():
    return {"ok":True,"version":VERSION,"workflowStates":list(WORKFLOW_STATES),"stageStates":list(STAGE_STATES),"stageTypes":list(STAGE_TYPES),"dependencyTypes":list(DEPENDENCY_TYPES),"gateTypes":list(GATE_TYPES),"failureClasses":list(FAILURE_CLASSES),"retryStrategies":list(RETRY_STRATEGIES),"approvalTypes":list(APPROVAL_TYPES),"workspaces":list(WORKSPACES),"boundary":BOUNDARY}

def normalize_workflow(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in WORKFLOW_STATES else "draft"
    r={"schema":WORKFLOW_SCHEMA,"version":VERSION,"workflowId":_txt(p.get("workflowId") or p.get("id"),512) or f"workflow-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"researchQuestion":_txt(p.get("researchQuestion"),8192),"state":state,"stageRefs":_list(p.get("stageRefs")),"dependencyRefs":_list(p.get("dependencyRefs")),"gateRefs":_list(p.get("gateRefs")),"projectRef":_txt(p.get("projectRef"),512),"sessionRef":_txt(p.get("sessionRef"),512),"provenance":_dict(p.get("provenance")),"limitations":_list(p.get("limitations")),"automaticWorkflowAdvance":False,"scientificValidityCertified":False,"publicationAccepted":False}; r["fingerprint"]=_fp(r); return r

def normalize_stage(payload:dict):
    p=_dict(payload); typ=_txt(p.get("stageType"),128).lower() or "custom"; typ=typ if typ in STAGE_TYPES else "custom"; state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in STAGE_STATES else "draft"; auth=_txt(p.get("executionAuthority"),64) or "Workspace"; auth=auth if auth in EXECUTION_AUTHORITIES else "Workspace"
    r={"schema":STAGE_SCHEMA,"version":VERSION,"stageId":_txt(p.get("stageId") or p.get("id"),512) or f"stage-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"stageType":typ,"state":state,"workspaceId":_txt(p.get("workspaceId"),128),"operation":_txt(p.get("operation"),512),"executionAuthority":auth,"inputRefs":_list(p.get("inputRefs")),"outputRefs":_list(p.get("outputRefs")),"dependencyRefs":_list(p.get("dependencyRefs")),"gateRefs":_list(p.get("gateRefs")),"runtimeRef":_txt(p.get("runtimeRef"),512),"environmentRef":_txt(p.get("environmentRef"),512),"parameters":_dict(p.get("parameters")),"provenance":_dict(p.get("provenance")),"limitations":_list(p.get("limitations")),"automaticAdvance":False,"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_dependency(payload:dict):
    p=_dict(payload); typ=_txt(p.get("dependencyType"),128).lower() or "custom"; typ=typ if typ in DEPENDENCY_TYPES else "custom"
    r={"schema":DEPENDENCY_SCHEMA,"version":VERSION,"dependencyId":_txt(p.get("dependencyId") or p.get("id"),512) or f"dep-{_fp(p)[:16]}","fromStageRef":_txt(p.get("fromStageRef"),512),"toStageRef":_txt(p.get("toStageRef"),512),"dependencyType":typ,"required":bool(p.get("required",True)),"artifactRefs":_list(p.get("artifactRefs")),"conditions":_dict(p.get("conditions")),"provenance":_dict(p.get("provenance")),"dependencyIsCausalProof":False}; r["fingerprint"]=_fp(r); return r

def normalize_gate(payload:dict):
    p=_dict(payload); typ=_txt(p.get("gateType"),128).lower() or "custom"; typ=typ if typ in GATE_TYPES else "custom"
    r={"schema":GATE_SCHEMA,"version":VERSION,"gateId":_txt(p.get("gateId") or p.get("id"),512) or f"gate-{_fp(p)[:16]}","gateType":typ,"stageRef":_txt(p.get("stageRef"),512),"requirements":_list(p.get("requirements")),"reviewerRefs":_list(p.get("reviewerRefs")),"status":_txt(p.get("status"),128) or "pending","humanApprovalRequired":bool(p.get("humanApprovalRequired",typ in ("human-approval","review","publication"))),"automaticApproval":False,"scientificValidityCertified":False,"publicationAccepted":False}; r["fingerprint"]=_fp(r); return r

def normalize_run(payload:dict):
    p=_dict(payload); r={"schema":RUN_SCHEMA,"version":VERSION,"runId":_txt(p.get("runId") or p.get("id"),512) or f"run-{_fp(p)[:16]}","workflowRef":_txt(p.get("workflowRef"),512),"state":_txt(p.get("state"),128) or "planned","stageRunRefs":_list(p.get("stageRunRefs")),"startedAt":_txt(p.get("startedAt"),128),"completedAt":_txt(p.get("completedAt"),128),"provenance":_dict(p.get("provenance")),"executionSuccessIsScientificValidity":False}; r["fingerprint"]=_fp(r); return r

def normalize_stage_run(payload:dict):
    p=_dict(payload); r={"schema":STAGE_RUN_SCHEMA,"version":VERSION,"stageRunId":_txt(p.get("stageRunId") or p.get("id"),512) or f"stage-run-{_fp(p)[:16]}","stageRef":_txt(p.get("stageRef"),512),"state":_txt(p.get("state"),128) or "queued","attempt":int(p.get("attempt",1) or 1),"executionRef":_txt(p.get("executionRef"),512),"checkpointRefs":_list(p.get("checkpointRefs")),"artifactRefs":_list(p.get("artifactRefs")),"failure":_dict(p.get("failure")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_transition_request(payload:dict):
    p=_dict(payload); r={"schema":TRANSITION_SCHEMA,"version":VERSION,"requestId":_txt(p.get("requestId") or p.get("id"),512) or f"transition-{_fp(p)[:16]}","workflowRef":_txt(p.get("workflowRef"),512),"stageRef":_txt(p.get("stageRef"),512),"fromState":_txt(p.get("fromState"),128),"toState":_txt(p.get("toState"),128),"requestedBy":_txt(p.get("requestedBy"),512),"reason":_txt(p.get("reason"),4096),"approved":False,"automaticTransition":False}; r["fingerprint"]=_fp(r); return r

def normalize_event(payload:dict):
    p=_dict(payload); r={"schema":EVENT_SCHEMA,"version":VERSION,"eventId":_txt(p.get("eventId") or p.get("id"),512) or f"event-{_fp(p)[:16]}","eventType":_txt(p.get("eventType"),128),"workflowRef":_txt(p.get("workflowRef"),512),"stageRef":_txt(p.get("stageRef"),512),"occurredAt":_txt(p.get("occurredAt"),128) or _now(),"details":_dict(p.get("details")),"provenance":_dict(p.get("provenance"))}; r["fingerprint"]=_fp(r); return r

def normalize_checkpoint(payload:dict):
    p=_dict(payload); r={"schema":CHECKPOINT_SCHEMA,"version":VERSION,"checkpointId":_txt(p.get("checkpointId") or p.get("id"),512) or f"checkpoint-{_fp(p)[:16]}","stageRunRef":_txt(p.get("stageRunRef"),512),"artifactRefs":_list(p.get("artifactRefs")),"runtimeRef":_txt(p.get("runtimeRef"),512),"environmentRef":_txt(p.get("environmentRef"),512),"createdAt":_txt(p.get("createdAt"),128) or _now(),"provenance":_dict(p.get("provenance")),"checkpointIsEndorsedResult":False}; r["fingerprint"]=_fp(r); return r

def normalize_retry_policy(payload:dict):
    p=_dict(payload); strategy=_txt(p.get("strategy"),128).lower() or "manual"; strategy=strategy if strategy in RETRY_STRATEGIES else "manual"; r={"schema":RETRY_POLICY_SCHEMA,"version":VERSION,"policyId":_txt(p.get("policyId") or p.get("id"),512) or f"retry-{_fp(p)[:16]}","strategy":strategy,"maxAttempts":max(0,int(p.get("maxAttempts",1) or 1)),"retryableFailureClasses":_list(p.get("retryableFailureClasses")),"requiresApproval":bool(p.get("requiresApproval",True)),"automaticRetry":False}; r["fingerprint"]=_fp(r); return r

def normalize_approval(payload:dict):
    p=_dict(payload); typ=_txt(p.get("approvalType"),128).lower() or "custom"; typ=typ if typ in APPROVAL_TYPES else "custom"; r={"schema":APPROVAL_SCHEMA,"version":VERSION,"approvalId":_txt(p.get("approvalId") or p.get("id"),512) or f"approval-{_fp(p)[:16]}","approvalType":typ,"subjectRef":_txt(p.get("subjectRef"),512),"reviewerRefs":_list(p.get("reviewerRefs")),"decision":_txt(p.get("decision"),128) or "pending","rationale":_txt(p.get("rationale"),8192),"automaticApproval":False,"scientificValidityCertified":False,"publicationAccepted":False}; r["fingerprint"]=_fp(r); return r

def workflow_state(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"workflow":normalize_workflow(_dict(p.get("workflow") or p)),"stages":[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)],"dependencies":[normalize_dependency(x) for x in _list(p.get("dependencies")) if isinstance(x,dict)],"gates":[normalize_gate(x) for x in _list(p.get("gates")) if isinstance(x,dict)],"automaticWorkflowAdvance":False,"scientificValidityCertified":False}

def workflow_graph(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; deps=[normalize_dependency(x) for x in _list(p.get("dependencies")) if isinstance(x,dict)]; return {"ok":True,"version":VERSION,"nodes":[{"id":x["stageId"],"stageType":x["stageType"],"workspaceId":x["workspaceId"]} for x in stages],"edges":[{"source":x["fromStageRef"],"target":x["toStageRef"],"dependencyType":x["dependencyType"],"required":x["required"]} for x in deps],"dependencyEdgeIsCausalProof":False}

def _topology(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; ids=[x["stageId"] for x in stages]; deps=[normalize_dependency(x) for x in _list(p.get("dependencies")) if isinstance(x,dict) and x.get("required",True)]; indeg={x:0 for x in ids}; adj=defaultdict(list); unknown=[]
    for d in deps:
        a,b=d["fromStageRef"],d["toStageRef"]
        if a not in indeg or b not in indeg: unknown.append(d["dependencyId"]); continue
        adj[a].append(b); indeg[b]+=1
    q=deque(sorted([x for x,v in indeg.items() if v==0])); order=[]
    while q:
        x=q.popleft(); order.append(x)
        for y in sorted(adj[x]):
            indeg[y]-=1
            if indeg[y]==0:q.append(y)
    cycle=[x for x,v in indeg.items() if v>0]
    return order,cycle,unknown

def cycle_audit(payload:dict):
    order,cycle,unknown=_topology(payload); return {"ok":True,"version":VERSION,"acyclic":not cycle,"cycleStageRefs":cycle,"unknownDependencyRefs":unknown,"plannedStageRefs":order,"scientificValidityCertified":False}

def topological_plan(payload:dict):
    order,cycle,unknown=_topology(payload); return {"ok":True,"version":VERSION,"order":order,"acyclic":not cycle,"cycleStageRefs":cycle,"unknownDependencyRefs":unknown,"automaticWorkflowAdvance":False,"workflowOrderIsScientificNecessity":False}

def dependency_audit(payload:dict):
    p=_dict(payload); deps=[normalize_dependency(x) for x in _list(p.get("dependencies")) if isinstance(x,dict)]; issues=[]
    for d in deps:
        if not d["fromStageRef"] or not d["toStageRef"]: issues.append({"dependencyId":d["dependencyId"],"issue":"missing-stage-ref"})
        if d["fromStageRef"]==d["toStageRef"] and d["fromStageRef"]: issues.append({"dependencyId":d["dependencyId"],"issue":"self-dependency"})
    return {"ok":True,"version":VERSION,"dependencies":deps,"issues":issues,"clean":not issues,"dependencyEdgeIsCausalProof":False}

def gate_audit(payload:dict):
    p=_dict(payload); gates=[normalize_gate(x) for x in _list(p.get("gates")) if isinstance(x,dict)]; pending=[x for x in gates if x["status"] not in ("passed","approved")]; return {"ok":True,"version":VERSION,"gates":gates,"pending":pending,"allPassed":not pending,"automaticGateApproval":False,"gatePassageIsScientificValidity":False}

def readiness_report(payload:dict):
    p=_dict(payload); reqs=_list(p.get("requirements")); missing=[x for x in reqs if isinstance(x,dict) and not bool(x.get("satisfied"))]; gates=gate_audit(p); cyc=cycle_audit(p); ready=not missing and gates["allPassed"] and cyc["acyclic"] and not cyc["unknownDependencyRefs"]; return {"ok":True,"version":VERSION,"ready":ready,"missing":missing,"pendingGates":gates["pending"],"cycleStageRefs":cyc["cycleStageRefs"],"unknownDependencyRefs":cyc["unknownDependencyRefs"],"automaticWorkflowAdvance":False}

def blocker_report(payload:dict):
    p=_dict(payload); blockers=[]
    blockers.extend([{"type":"requirement","item":x} for x in _list(p.get("requirements")) if isinstance(x,dict) and not bool(x.get("satisfied"))])
    blockers.extend([{"type":"gate","item":x} for x in gate_audit(p)["pending"]])
    c=cycle_audit(p); blockers.extend([{"type":"cycle","stageRef":x} for x in c["cycleStageRefs"]]); blockers.extend([{"type":"unknown-dependency","dependencyRef":x} for x in c["unknownDependencyRefs"]])
    return {"ok":True,"version":VERSION,"blockers":blockers,"blocked":bool(blockers)}

def stage_status_matrix(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; return {"ok":True,"version":VERSION,"rows":[{"stageId":x["stageId"],"stageType":x["stageType"],"workspaceId":x["workspaceId"],"state":x["state"],"executionAuthority":x["executionAuthority"],"automaticAdvance":False} for x in stages]}

def execution_plan(payload:dict):
    p=_dict(payload); topo=topological_plan(p); stages={normalize_stage(x)["stageId"]:normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)}; ordered=[stages[x] for x in topo["order"] if x in stages]; return {"ok":True,"version":VERSION,"orderedStages":ordered,"acyclic":topo["acyclic"],"blocked":not topo["acyclic"],"automaticDispatch":False,"labExecutesHeavyCompute":False}

def execution_queue(payload:dict):
    plan=execution_plan(payload); return {"ok":True,"version":VERSION,"items":[{"stageId":x["stageId"],"workspaceId":x["workspaceId"],"operation":x["operation"],"executionAuthority":x["executionAuthority"],"dispatchState":"planned"} for x in plan["orderedStages"]],"automaticDispatch":False}

def compute_request_registry(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"requests":_list(p.get("requests")),"count":len(_list(p.get("requests"))),"executionAuthority":"Workspace","labExecutesHeavyCompute":False}

def authority_audit(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; violations=[{"stageId":x["stageId"],"issue":"lab-heavy-compute-authority"} for x in stages if x["executionAuthority"] not in EXECUTION_AUTHORITIES]; return {"ok":True,"version":VERSION,"violations":violations,"clean":not violations,"authorities":authority_registry()["authorities"]}

def cross_workspace_plan(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; transitions=[]
    for a,b in zip(stages,stages[1:]):
        if a["workspaceId"]!=b["workspaceId"]: transitions.append({"fromStageRef":a["stageId"],"toStageRef":b["stageId"],"fromWorkspace":a["workspaceId"],"toWorkspace":b["workspaceId"],"automaticHandoff":False})
    return {"ok":True,"version":VERSION,"transitions":transitions,"automaticWorkflowAdvance":False}

def input_output_contract(payload:dict):
    p=_dict(payload); s=normalize_stage(_dict(p.get("stage") or p)); return {"ok":True,"version":VERSION,"stageRef":s["stageId"],"inputs":s["inputRefs"],"outputs":s["outputRefs"],"parameters":s["parameters"],"provenanceRequired":True,"automaticEvidencePromotion":False}

def artifact_dependency_index(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; idx={}
    for s in stages:
        for r in s["inputRefs"]: idx.setdefault(str(r),{"consumers":[],"producers":[]})["consumers"].append(s["stageId"])
        for r in s["outputRefs"]: idx.setdefault(str(r),{"consumers":[],"producers":[]})["producers"].append(s["stageId"])
    return {"ok":True,"version":VERSION,"artifacts":idx,"artifactDependencyIsCausalProof":False}

def lineage_graph(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"nodes":_list(p.get("nodes")),"edges":_list(p.get("edges")),"lineageIsCausalProof":False,"provenanceRequired":True}

def provenance_audit(payload:dict):
    p=_dict(payload); items=_list(p.get("items")); missing=[i for i,x in enumerate(items) if not isinstance(x,dict) or not _dict(x.get("provenance"))]; return {"ok":True,"version":VERSION,"itemCount":len(items),"missingProvenanceIndexes":missing,"complete":not missing,"provenanceCompletenessIsScientificValidity":False}

def environment_audit(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; missing=[x["stageId"] for x in stages if x["executionAuthority"] in ("Workspace","Workbench") and not x["environmentRef"]]; return {"ok":True,"version":VERSION,"missingEnvironmentStageRefs":missing,"complete":not missing,"environmentRecordedIsScientificValidity":False}

def runtime_audit(payload:dict):
    p=_dict(payload); stages=[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)]; missing=[x["stageId"] for x in stages if x["executionAuthority"] in ("Workspace","Workbench") and not x["runtimeRef"]]; return {"ok":True,"version":VERSION,"missingRuntimeStageRefs":missing,"complete":not missing,"runtimeRecordedIsScientificValidity":False}

def resource_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"stageResources":_list(p.get("stageResources")),"budgets":_dict(p.get("budgets")),"automaticResourceAllocation":False,"scientificValidityCertified":False}

def concurrency_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"groups":_list(p.get("groups")),"maxConcurrent":max(1,int(p.get("maxConcurrent",1) or 1)),"automaticDispatch":False,"parallelismImpliesIndependence":False}

def checkpoint_registry(payload:dict):
    p=_dict(payload); cps=[normalize_checkpoint(x) for x in _list(p.get("checkpoints")) if isinstance(x,dict)]; return {"ok":True,"version":VERSION,"checkpoints":cps,"count":len(cps),"checkpointIsEndorsedResult":False}

def failure_report(payload:dict):
    p=_dict(payload); failures=[]
    for x in _list(p.get("failures")):
        if not isinstance(x,dict): continue
        cls=_txt(x.get("failureClass"),128).lower() or "unknown"; cls=cls if cls in FAILURE_CLASSES else "unknown"; failures.append({"stageRef":_txt(x.get("stageRef"),512),"failureClass":cls,"message":_txt(x.get("message"),4096),"rootCauseEstablished":False})
    return {"ok":True,"version":VERSION,"failures":failures,"count":len(failures),"failurePatternIsEstablishedRootCause":False}

def retry_plan(payload:dict):
    p=_dict(payload); policy=normalize_retry_policy(_dict(p.get("policy"))); return {"ok":True,"version":VERSION,"policy":policy,"stageRunRef":_txt(p.get("stageRunRef"),512),"recommendedAction":policy["strategy"],"automaticRetry":False,"approvalRequired":True,"retryRepairsMethodology":False}

def recovery_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"workflowRef":_txt(p.get("workflowRef"),512),"failedStageRefs":_list(p.get("failedStageRefs")),"checkpointRefs":_list(p.get("checkpointRefs")),"upstreamRecomputeRefs":_list(p.get("upstreamRecomputeRefs")),"actions":_list(p.get("actions")),"automaticRecovery":False,"humanReviewRequired":True}

def resume_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"workflowRef":_txt(p.get("workflowRef"),512),"resumeFromStageRef":_txt(p.get("resumeFromStageRef"),512),"checkpointRef":_txt(p.get("checkpointRef"),512),"automaticResume":False,"approvalRequired":True}

def pause_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"workflowRef":_txt(p.get("workflowRef"),512),"stageRefs":_list(p.get("stageRefs")),"reason":_txt(p.get("reason"),4096),"mutationPerformed":False}

def cancellation_plan(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"workflowRef":_txt(p.get("workflowRef"),512),"stageRefs":_list(p.get("stageRefs")),"preserveArtifactRefs":_list(p.get("preserveArtifactRefs")),"mutationPerformed":False,"scientificValidityCertified":False}

def transition_request(payload:dict): return {"ok":True,"version":VERSION,"request":normalize_transition_request(payload),"mutationPerformed":False,"automaticTransition":False}
def transition_audit(payload:dict):
    p=_dict(payload); req=normalize_transition_request(_dict(p.get("request") or p)); gates=gate_audit(p); return {"ok":True,"version":VERSION,"request":req,"pendingGates":gates["pending"],"eligibleForHumanReview":gates["allPassed"],"transitionApplied":False,"automaticTransition":False}

def approval_queue(payload:dict):
    p=_dict(payload); items=[normalize_approval(x) for x in _list(p.get("approvals")) if isinstance(x,dict)]; return {"ok":True,"version":VERSION,"approvals":items,"pending":[x for x in items if x["decision"]=="pending"],"automaticApproval":False}

def approval_decision(payload:dict):
    p=_dict(payload); a=normalize_approval(p); return {"ok":True,"version":VERSION,"approval":a,"decisionRecorded":bool(a["decision"] and a["decision"]!="pending"),"automaticApproval":False,"workflowMutationPerformed":False}

def _gate_result(kind:str,payload:dict):
    p=_dict(payload); reqs=_list(p.get("requirements")); missing=[x for x in reqs if isinstance(x,dict) and not bool(x.get("satisfied"))]; return {"ok":True,"version":VERSION,"gateType":kind,"requirements":reqs,"missing":missing,"eligible":not missing,"approved":False,"automaticApproval":False,"scientificValidityCertified":False,"publicationAccepted":False}
def review_gate(payload:dict): return _gate_result("review",payload)
def validation_gate(payload:dict): return _gate_result("validation",payload)
def reproducibility_gate(payload:dict): return _gate_result("reproducibility",payload)
def publication_gate(payload:dict): return _gate_result("publication",payload)

def change_impact(payload:dict):
    p=_dict(payload); changed=set(str(x) for x in _list(p.get("changedRefs"))); deps=_list(p.get("dependencies")); impacted=set()
    frontier=set(changed)
    while frontier:
        nxt=set()
        for d in deps:
            if not isinstance(d,dict): continue
            if str(d.get("fromStageRef")) in frontier and str(d.get("toStageRef")) not in impacted: nxt.add(str(d.get("toStageRef")))
        impacted|=nxt; frontier=nxt
    return {"ok":True,"version":VERSION,"changedRefs":sorted(changed),"impactedStageRefs":sorted(x for x in impacted if x),"impactIsScientificInvalidation":False}

def event_timeline(payload:dict):
    p=_dict(payload); events=[normalize_event(x) for x in _list(p.get("events")) if isinstance(x,dict)]; events=sorted(events,key=lambda x:(x["occurredAt"],x["eventId"])); return {"ok":True,"version":VERSION,"events":events,"count":len(events),"timelineOrderIsCausalProof":False}

def run_summary(payload:dict):
    p=_dict(payload); r=normalize_run(_dict(p.get("run") or p)); stage_runs=[normalize_stage_run(x) for x in _list(p.get("stageRuns")) if isinstance(x,dict)]; counts={s:sum(1 for x in stage_runs if x["state"]==s) for s in STAGE_STATES}; return {"ok":True,"version":VERSION,"run":r,"stageRuns":stage_runs,"counts":counts,"executionSuccessIsScientificValidity":False}

def workflow_summary(payload:dict):
    p=_dict(payload); state=workflow_state(p); ready=readiness_report(p); return {"ok":True,"version":VERSION,"workflow":state["workflow"],"stageCount":len(state["stages"]),"dependencyCount":len(state["dependencies"]),"gateCount":len(state["gates"]),"ready":ready["ready"],"automaticWorkflowAdvance":False,"scientificValidityCertified":False}

def comparison_matrix(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"rows":_list(p.get("rows")),"columns":_list(p.get("columns")),"values":_list(p.get("values")),"automaticRanking":False,"automaticWinnerSelection":False}

def uncertainty_summary(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"sources":_list(p.get("sources")),"assumptions":_list(p.get("assumptions")),"intervals":_list(p.get("intervals")),"uncertaintyEliminated":False,"scientificValidityCertified":False}

def visual_workflow_spec(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"renderer":"workflow-dag","nodes":_list(p.get("nodes")),"edges":_list(p.get("edges")),"gates":_list(p.get("gates")),"statusLegend":list(STAGE_STATES),"visualizationIsEvidence":False}

def dashboard_spec(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"cards":_list(p.get("cards")),"workflowRef":_txt(p.get("workflowRef"),512),"panels":["workflow","stages","dependencies","gates","execution","failures","review","provenance"],"automaticScientificValidity":False}

def workflow_snapshot(payload:dict):
    p=_dict(payload); body={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"workflow":normalize_workflow(_dict(p.get("workflow"))),"stages":[normalize_stage(x) for x in _list(p.get("stages")) if isinstance(x,dict)],"dependencies":[normalize_dependency(x) for x in _list(p.get("dependencies")) if isinstance(x,dict)],"gates":[normalize_gate(x) for x in _list(p.get("gates")) if isinstance(x,dict)],"runs":_list(p.get("runs")),"events":_list(p.get("events")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False}; body["fingerprint"]=_fp(body); return {"ok":True,"version":VERSION,"snapshot":body}

def compare_snapshots(payload:dict):
    p=_dict(payload); a=_stable(_dict(p.get("a"))); b=_stable(_dict(p.get("b"))); return {"ok":True,"version":VERSION,"equal":_canon(a)==_canon(b),"aFingerprint":_fp(a),"bFingerprint":_fp(b),"scientificValidityCertified":False}

def workflow_diff(payload:dict):
    p=_dict(payload); a=_dict(p.get("a")); b=_dict(p.get("b")); keys=sorted(set(a)|set(b)); changes=[{"key":k,"from":a.get(k),"to":b.get(k)} for k in keys if a.get(k)!=b.get(k)]; return {"ok":True,"version":VERSION,"changes":changes,"changeCount":len(changes),"changeIsScientificInvalidation":False}

def export_bundle(payload:dict):
    p=_dict(payload); body={"version":VERSION,"workflow":_dict(p.get("workflow")),"stages":_list(p.get("stages")),"dependencies":_list(p.get("dependencies")),"gates":_list(p.get("gates")),"runs":_list(p.get("runs")),"events":_list(p.get("events")),"provenance":_dict(p.get("provenance")),"review":_dict(p.get("review")),"limitations":_list(p.get("limitations")),"scientificValidityCertified":False}; return {"ok":True,"version":VERSION,"bundle":body,"fingerprint":_fp(body)}

def reproducibility_package(payload:dict):
    p=_dict(payload); body={"version":VERSION,"workflowRef":_txt(p.get("workflowRef"),512),"snapshotRef":_txt(p.get("snapshotRef"),512),"stageRefs":_list(p.get("stageRefs")),"artifactRefs":_list(p.get("artifactRefs")),"sourceRefs":_list(p.get("sourceRefs")),"runtimeRefs":_list(p.get("runtimeRefs")),"environmentRefs":_list(p.get("environmentRefs")),"checkpointRefs":_list(p.get("checkpointRefs")),"instructions":_list(p.get("instructions")),"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; body["fingerprint"]=_fp(body); return {"ok":True,"version":VERSION,"package":body}

def _handoff(schema:str,target:str,payload:dict):
    p=_dict(payload); body={"schema":schema,"version":VERSION,"target":target,"workflowRef":_txt(p.get("workflowRef"),512),"stageRef":_txt(p.get("stageRef"),512),"objectRefs":_list(p.get("objectRefs")),"artifactRefs":_list(p.get("artifactRefs")),"parameters":_dict(p.get("parameters")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False,"deploymentReadinessCertified":False,"publicationAccepted":False}; body["fingerprint"]=_fp(body); return {"ok":True,"version":VERSION,"handoff":body}
def publication_handoff(payload:dict): return _handoff("sc-lab-scientific-workflow-publication-handoff/1.0","Publication Studio",payload)
def workspace_execution_handoff(payload:dict): return _handoff(WORKSPACE_HANDOFF_SCHEMA,"Workspace",payload)
def workbench_handoff(payload:dict): return _handoff(WORKBENCH_HANDOFF_SCHEMA,"Workbench",payload)
def core_handoff(payload:dict): return _handoff(CORE_HANDOFF_SCHEMA,"Platform Core",payload)
def library_handoff(payload:dict): return _handoff(LIBRARY_HANDOFF_SCHEMA,"Knowledge Library",payload)
def research_os_handoff(payload:dict): return _handoff(RESEARCH_OS_HANDOFF_SCHEMA,"Research OS",payload)
def integrated_lab_handoff(payload:dict): return _handoff(INTEGRATED_LAB_HANDOFF_SCHEMA,"Integrated Computational Research Laboratory",payload)
def neural_handoff(payload:dict): return _handoff("sc-lab-neural-workflow-handoff/1.0","neural",payload)
def linguistics_handoff(payload:dict): return _handoff("sc-lab-linguistics-workflow-handoff/1.0","linguistics",payload)
def statistics_handoff(payload:dict): return _handoff("sc-lab-statistics-workflow-handoff/1.0","statistics-econometrics",payload)
def simulation_handoff(payload:dict): return _handoff("sc-lab-simulation-workflow-handoff/1.0","simulation",payload)
def graph_handoff(payload:dict): return _handoff("sc-lab-graph-workflow-handoff/1.0","graph-network",payload)
def graph_ml_handoff(payload:dict): return _handoff("sc-lab-graph-ml-workflow-handoff/1.0","graph-ml",payload)
def multimodal_handoff(payload:dict): return _handoff("sc-lab-multimodal-workflow-handoff/1.0","multimodal",payload)
def validation_handoff(payload:dict): return _handoff("sc-lab-validation-workflow-handoff/1.0","validation",payload)
def stage_handoff(payload:dict): return _handoff("sc-lab-stage-orchestration-handoff/1.0",_txt(_dict(payload).get("target"),128) or "Workspace",payload)
def workflow_handoff(payload:dict): return _handoff("sc-lab-workflow-orchestration-handoff/1.0",_txt(_dict(payload).get("target"),128) or "Integrated Laboratory",payload)
def handoff_bundle(payload:dict):
    return {"ok":True,"version":VERSION,"handoffs":{"workspace":workspace_execution_handoff(payload)["handoff"],"core":core_handoff(payload)["handoff"],"library":library_handoff(payload)["handoff"],"researchOS":research_os_handoff(payload)["handoff"],"integratedLab":integrated_lab_handoff(payload)["handoff"]},"automaticWorkflowAdvance":False,"scientificValidityCertified":False}

def contract(): return {"ok":True,"schema":SCHEMA,"version":VERSION,"predecessorVersion":PREDECESSOR_VERSION,"integrityBaseline":INTEGRITY_BASELINE,"researchOSVersion":RESEARCH_OS_VERSION,"workflowSchema":WORKFLOW_SCHEMA,"stageSchema":STAGE_SCHEMA,"dependencySchema":DEPENDENCY_SCHEMA,"gateSchema":GATE_SCHEMA,"runSchema":RUN_SCHEMA,"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"platformCoreCanonicalAuthority":True,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"knowledgeLibrarySourceAuthority":True,"labScientificOrchestrationAuthority":True,"labExecutesHeavyCompute":False,"automaticWorkflowAdvance":False,"automaticDispatch":False,"automaticGateApproval":False,"automaticRetry":False,"automaticScientificDecision":False,"automaticEvidencePromotion":False,"automaticModelPromotion":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"automaticPublicationAcceptance":False,"humanScientificReviewRequired":True,"dependencyEdgeIsCausalProof":False,"workflowOrderIsScientificNecessity":False,"executionSuccessIsScientificValidity":False,"reproducibilityIsScientificValidity":False,"boundary":BOUNDARY}
def interpretation_boundary(): return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"workflowOrderIsScientificNecessity":False,"dependencyEdgeIsCausalProof":False,"executionSuccessIsScientificValidity":False,"successfulStageIsScientificValidity":False,"retryRepairsMethodology":False,"gatePassageIsPublicationAcceptance":False,"reproducibilityIsScientificValidity":False}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"workflowObjectModel":True,"stageDependencyGateModel":True,"acyclicPlanning":True,"crossWorkspaceOrchestration":True,"explicitAuthorities":True,"explicitTransitionRequests":True,"humanApprovalGates":True,"failureRecoveryPlanning":True,"checkpointLineage":True,"provenanceAudits":True,"snapshots":True,"reproducibility":True,"publicationHandoff":True,"predecessorCompatibility":True,"installedRuntimeIntegrity":True}}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"scientificWorkflowObjects":True,"experimentStageObjects":True,"dependencyGraph":True,"approvalGates":True,"deterministicTopologicalPlanning":True,"crossWorkspaceHandoffs":True,"failureRecoveryPlanning":True,"checkpointRegistry":True,"provenanceAndEnvironmentAudits":True,"reproducibilityPackage":True,"publicationHandoff":True},"scientificValidityCertified":False,"deploymentReadinessCertified":False,"publicationAccepted":False}
def health(): return {"ok":True,"version":VERSION,"scientificWorkflowExperimentOrchestration":True,"api_route_count":103,"predecessorVersion":PREDECESSOR_VERSION,"workspaceCount":len(WORKSPACES),"platformCoreCanonicalAuthority":True,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"knowledgeLibrarySourceAuthority":True,"labScientificOrchestrationAuthority":True,"labExecutesHeavyCompute":False,"automaticWorkflowAdvance":False,"automaticDispatch":False,"automaticGateApproval":False,"automaticRetry":False,"automaticScientificDecision":False,"automaticScientificValidity":False,"automaticPublicationAcceptance":False,"humanScientificReviewRequired":True,"dependencyEdgeIsCausalProof":False,"workflowOrderIsScientificNecessity":False,"executionSuccessIsScientificValidity":False}
