from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

VERSION = "0.130.0"
ENGINE_VERSION = "11.0.0"
SCHEMA = "sc-lab-scientific-research-project-studio/0.130.0"
SNAPSHOT_SCHEMA = "sc-lab-scientific-research-project-snapshot/0.130.0"
MAX_COMPONENTS = 20000
MAX_RELATIONSHIPS = 50000
MAX_WORKSTREAMS = 500
MAX_MILESTONES = 5000
MAX_REVISIONS = 5000

METHOD_FAMILIES = {
    "project-normalization", "component-registry", "relationship-graph", "workstream-planning",
    "milestone-planning", "project-state", "artifact-indexing", "cross-product-binding",
    "research-session-planning", "handoff-planning", "workspace-composition", "research-timeline",
    "provenance-aggregation", "readiness-review", "project-snapshot", "revision-planning",
    "export-planning", "core-project-binding",
}

FIGURE_FAMILIES = {
    "project-system-map", "research-timeline", "workstream-board", "milestone-roadmap",
    "component-network", "dependency-graph", "dataset-model-lineage", "execution-lineage",
    "claim-evidence-map", "figure-board", "publication-map", "reproduction-status-board",
    "investigation-map", "provenance-graph", "research-readiness-scorecard", "project-state-dashboard",
}

COMPONENT_TYPES = {
    "dataset", "study", "experiment", "model", "execution", "simulation", "analysis", "figure",
    "dashboard", "scene", "claim", "finding", "evidence", "source", "manuscript", "publication",
    "reproduction-package", "replication-study", "investigation", "protocol", "method", "environment",
    "notebook", "workflow", "artifact", "project", "session",
}

class ResearchProjectStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()

def _list(v: Any, label: str, maximum: int) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise ResearchProjectStudioError(f"{label} must be an array.")
    if len(v)>maximum: raise ResearchProjectStudioError(f"{label} exceeds configured maximum of {maximum}.")
    return v

def _refs(v: Any, label: str, maximum: int = MAX_COMPONENTS) -> list[str]:
    return [str(x)[:300] for x in _list(v,label,maximum)]

def schema_info() -> dict[str, Any]:
    return {"ok":True,"schema":SCHEMA,"snapshot_schema":SNAPSHOT_SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,
            "limits":{"components":MAX_COMPONENTS,"relationships":MAX_RELATIONSHIPS,"workstreams":MAX_WORKSTREAMS,"milestones":MAX_MILESTONES,"revisions":MAX_REVISIONS}}

def catalog() -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"method_families":sorted(METHOD_FAMILIES),"figure_families":sorted(FIGURE_FAMILIES),
            "component_types":sorted(COMPONENT_TYPES),"reference_first":True,"automatic_domain_object_mutation":False,
            "automatic_scientific_validity_certification":False,"automatic_core_submission":False}

def manifest() -> dict[str, Any]:
    return {"ok":True,"status":"scientific-research-project-studio-ready","version":VERSION,"engine_version":ENGINE_VERSION,
            "unified_project_workspace":True,"cross_product_references":True,"provenance_aggregation":True,"reproducible_snapshots":True,
            "manuscript_and_publication_planning":True,"reproduction_replication_linkage":True,"investigation_linkage":True,
            "domain_objects_remain_authoritative":True,"automatic_domain_object_mutation":False,"automatic_scientific_inference":False,
            "automatic_scientific_validity_certification":False,"automatic_core_submission":False,"determine_truth":False}

def health() -> dict[str, Any]:
    return {**manifest(),"schema":SCHEMA,"method_family_count":len(METHOD_FAMILIES),"figure_family_count":len(FIGURE_FAMILIES),"api_route_count":32}

def normalize_project(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise ResearchProjectStudioError("payload must be an object.")
    project={"schema":SCHEMA,"version":VERSION,"project_ref":str(payload.get("project_ref") or "project:unspecified")[:300],
             "title":str(payload.get("title") or "Scientific research project")[:500],"description":str(payload.get("description") or "")[:5000],
             "status":str(payload.get("status") or "active")[:100],"research_question_refs":_refs(payload.get("research_question_refs"),"research_question_refs",1000),
             "hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs",1000),"owner_refs":_refs(payload.get("owner_refs"),"owner_refs",1000),
             "session_refs":_refs(payload.get("session_refs"),"session_refs",5000),"tags":[str(x)[:100] for x in _list(payload.get("tags"),"tags",1000)],
             "provenance":copy.deepcopy(payload.get("provenance") or {}),"boundaries":{"workspace_is_source_of_truth":False,"project_status_equals_scientific_validity":False,"automatic_inference":False}}
    project["project_hash"]=_hash(project); return {"ok":True,"version":VERSION,"project":project}

def component_registry(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]; seen=set()
    for i,c in enumerate(_list(payload.get("components"),"components",MAX_COMPONENTS)):
        if not isinstance(c,dict): raise ResearchProjectStudioError(f"components[{i}] must be an object.")
        ref=str(c.get("ref") or c.get("component_ref") or f"component:{i}")[:300]
        if ref in seen: raise ResearchProjectStudioError(f"duplicate component ref: {ref}")
        seen.add(ref); typ=str(c.get("type") or "artifact")[:100]
        rows.append({"component_ref":ref,"component_type":typ,"source_product":c.get("source_product"),"source_version":c.get("source_version"),
                     "authority_ref":c.get("authority_ref") or ref,"title":c.get("title"),"state":c.get("state") or "referenced",
                     "immutable_ref":bool(c.get("immutable_ref",True)),"metadata":copy.deepcopy(c.get("metadata") or {})})
    return {"ok":True,"version":VERSION,"components":rows,"component_count":len(rows),"registry_hash":_hash(rows),"project_registry_is_not_domain_authority":True}

def relationship_graph(payload: dict[str, Any]) -> dict[str, Any]:
    nodes=_refs(payload.get("node_refs"),"node_refs",MAX_COMPONENTS); node_set=set(nodes); edges=[]; unresolved=[]
    for i,e in enumerate(_list(payload.get("relationships"),"relationships",MAX_RELATIONSHIPS)):
        if not isinstance(e,dict): raise ResearchProjectStudioError(f"relationships[{i}] must be an object.")
        a=str(e.get("from_ref") or "")[:300]; b=str(e.get("to_ref") or "")[:300]
        if not a or not b: raise ResearchProjectStudioError("each relationship requires from_ref and to_ref.")
        if node_set and (a not in node_set or b not in node_set): unresolved.extend([x for x in (a,b) if x not in node_set])
        edges.append({"relationship_ref":e.get("relationship_ref") or f"relation:{i+1}","from_ref":a,"to_ref":b,"relation":str(e.get("relation") or "related-to")[:100],"declared":True,"metadata":copy.deepcopy(e.get("metadata") or {})})
    graph={"nodes":nodes,"relationships":edges}; return {"ok":True,"version":VERSION,"graph":graph,"graph_hash":_hash(graph),"unresolved_refs":sorted(set(unresolved)),"automatic_relationship_inference":False}

def workstream_plan(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,w in enumerate(_list(payload.get("workstreams"),"workstreams",MAX_WORKSTREAMS)):
        if not isinstance(w,dict): raise ResearchProjectStudioError(f"workstreams[{i}] must be an object.")
        rows.append({"workstream_ref":w.get("workstream_ref") or f"workstream:{i+1}","title":w.get("title") or f"Workstream {i+1}","owner_refs":_refs(w.get("owner_refs"),"owner_refs",1000),"component_refs":_refs(w.get("component_refs"),"component_refs"),"status":w.get("status") or "planned","dependencies":_refs(w.get("dependencies"),"dependencies",MAX_WORKSTREAMS)})
    return {"ok":True,"version":VERSION,"workstreams":rows,"plan_hash":_hash(rows),"automatic_priority_assignment":False}

def milestone_plan(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,m in enumerate(_list(payload.get("milestones"),"milestones",MAX_MILESTONES)):
        if not isinstance(m,dict): raise ResearchProjectStudioError(f"milestones[{i}] must be an object.")
        rows.append({"milestone_ref":m.get("milestone_ref") or f"milestone:{i+1}","title":m.get("title") or f"Milestone {i+1}","target_date":m.get("target_date"),"status":m.get("status") or "planned","required_refs":_refs(m.get("required_refs"),"required_refs"),"acceptance_criteria":copy.deepcopy(m.get("acceptance_criteria") or [])})
    return {"ok":True,"version":VERSION,"milestones":rows,"plan_hash":_hash(rows),"automatic_completion_certification":False}

def project_state_report(payload: dict[str, Any]) -> dict[str, Any]:
    states=copy.deepcopy(payload.get("states") or {}); allowed={"planned","active","blocked","review","complete","archived","unknown"}
    norm={str(k)[:300]:(str(v).lower() if str(v).lower() in allowed else "unknown") for k,v in states.items()}
    return {"ok":True,"version":VERSION,"states":norm,"state_hash":_hash(norm),"automatic_overall_grade":False,"state_equals_scientific_validity":False}

def _index(payload: dict[str, Any], key: str, type_name: str) -> dict[str, Any]:
    rows=[]
    for i,x in enumerate(_list(payload.get(key),key,MAX_COMPONENTS)):
        if not isinstance(x,dict): raise ResearchProjectStudioError(f"{key}[{i}] must be an object.")
        rows.append({"ref":x.get("ref") or f"{type_name}:{i+1}","title":x.get("title"),"authority_ref":x.get("authority_ref") or x.get("ref"),"source_product":x.get("source_product"),"version":x.get("version"),"status":x.get("status") or "referenced","metadata":copy.deepcopy(x.get("metadata") or {})})
    return {"ok":True,"version":VERSION,"artifact_type":type_name,"items":rows,"count":len(rows),"index_hash":_hash(rows),"index_is_not_domain_authority":True}

def dataset_index(payload): return _index(payload,"datasets","dataset")
def model_index(payload): return _index(payload,"models","model")
def execution_index(payload): return _index(payload,"executions","execution")
def figure_index(payload): return _index(payload,"figures","figure")
def manuscript_index(payload): return _index(payload,"manuscripts","manuscript")
def reproduction_index(payload): return _index(payload,"reproduction_packages","reproduction-package")
def investigation_index(payload): return _index(payload,"investigations","investigation")

def claim_evidence_index(payload: dict[str, Any]) -> dict[str, Any]:
    claims=_index({"claims":payload.get("claims") or []},"claims","claim"); evidence=_index({"evidence":payload.get("evidence") or []},"evidence","evidence")
    links=[]
    for i,l in enumerate(_list(payload.get("links"),"links",MAX_RELATIONSHIPS)):
        if not isinstance(l,dict): raise ResearchProjectStudioError(f"links[{i}] must be an object.")
        links.append({"claim_ref":l.get("claim_ref"),"evidence_ref":l.get("evidence_ref"),"relationship":l.get("relationship") or "supports-or-challenges-declared","declared":True})
    return {"ok":True,"version":VERSION,"claims":claims["items"],"evidence":evidence["items"],"links":links,"index_hash":_hash([claims["items"],evidence["items"],links]),"automatic_evidence_weighting":False,"automatic_claim_status_change":False}

def dependency_graph(payload: dict[str, Any]) -> dict[str, Any]:
    deps=[]
    for i,d in enumerate(_list(payload.get("dependencies"),"dependencies",MAX_RELATIONSHIPS)):
        if not isinstance(d,dict): raise ResearchProjectStudioError(f"dependencies[{i}] must be an object.")
        deps.append({"from_ref":d.get("from_ref"),"requires_ref":d.get("requires_ref"),"dependency_type":d.get("dependency_type") or "declared","hard":bool(d.get("hard",False))})
    graph={"dependencies":deps}; return {"ok":True,"version":VERSION,"graph":graph,"graph_hash":_hash(graph),"automatic_dependency_inference":False}

def cross_product_bindings(payload: dict[str, Any]) -> dict[str, Any]:
    bindings=[]
    for i,b in enumerate(_list(payload.get("bindings"),"bindings",MAX_COMPONENTS)):
        if not isinstance(b,dict): raise ResearchProjectStudioError(f"bindings[{i}] must be an object.")
        bindings.append({"component_ref":b.get("component_ref"),"product":b.get("product"),"object_ref":b.get("object_ref"),"object_type":b.get("object_type"),"version":b.get("version"),"authority":"source-product"})
    return {"ok":True,"version":VERSION,"bindings":bindings,"binding_hash":_hash(bindings),"automatic_remote_mutation":False}

def research_session_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"project_ref":payload.get("project_ref"),"session_ref":payload.get("session_ref") or "session:pending","researcher_refs":_refs(payload.get("researcher_refs"),"researcher_refs",1000),"component_refs":_refs(payload.get("component_refs"),"component_refs"),"objective":payload.get("objective"),"context_ref":payload.get("context_ref"),"registration_mode":"explicit"}
    plan["plan_hash"]=_hash(plan); return {"ok":True,"version":VERSION,"plan":plan,"automatic_session_registration":False}

def handoff_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"project_ref":payload.get("project_ref"),"source_product":payload.get("source_product"),"target_product":payload.get("target_product"),"object_refs":_refs(payload.get("object_refs"),"object_refs"),"context_ref":payload.get("context_ref"),"purpose":payload.get("purpose"),"submission_mode":"explicit"}; plan["handoff_hash"]=_hash(plan)
    return {"ok":True,"version":VERSION,"plan":plan,"automatic_handoff":False,"automatic_execution":False}

def workspace_layout(payload: dict[str, Any]) -> dict[str, Any]:
    panels=[]
    for i,p in enumerate(_list(payload.get("panels"),"panels",500)):
        if not isinstance(p,dict): raise ResearchProjectStudioError(f"panels[{i}] must be an object.")
        panels.append({"panel_ref":p.get("panel_ref") or f"panel:{i+1}","panel_type":p.get("panel_type") or "artifact-index","object_refs":_refs(p.get("object_refs"),"object_refs"),"position":copy.deepcopy(p.get("position") or {}),"filters":copy.deepcopy(p.get("filters") or {})})
    return {"ok":True,"version":VERSION,"layout":{"panels":panels},"layout_hash":_hash(panels),"layout_changes_scientific_semantics":False}

def research_timeline(payload: dict[str, Any]) -> dict[str, Any]:
    events=[]
    for i,e in enumerate(_list(payload.get("events"),"events",MAX_MILESTONES*4)):
        if not isinstance(e,dict): raise ResearchProjectStudioError(f"events[{i}] must be an object.")
        events.append({"event_ref":e.get("event_ref") or f"event:{i+1}","time":e.get("time"),"event_type":e.get("event_type") or "project-event","object_refs":_refs(e.get("object_refs"),"object_refs"),"declared":True})
    events=sorted(events,key=lambda x:(str(x.get("time") or ""),str(x["event_ref"])))
    return {"ok":True,"version":VERSION,"events":events,"timeline_hash":_hash(events),"automatic_event_inference":False}

def provenance_aggregate(payload: dict[str, Any]) -> dict[str, Any]:
    records=_list(payload.get("records"),"records",MAX_COMPONENTS); roots=_refs(payload.get("root_refs"),"root_refs")
    bundle={"root_refs":roots,"records":copy.deepcopy(records)}
    return {"ok":True,"version":VERSION,"provenance":bundle,"provenance_hash":_hash(bundle),"aggregation_does_not_replace_source_provenance":True}

def readiness_report(payload: dict[str, Any]) -> dict[str, Any]:
    checks=copy.deepcopy(payload.get("checks") or {}); required=["project","components","provenance","methods","outputs"]
    present={k:bool(checks.get(k)) for k in required}
    return {"ok":True,"version":VERSION,"checks":present,"ready_for_project_review":all(present.values()),"ready_for_scientific_acceptance":False,"automatic_scientific_validity_certification":False}

def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"project_ref":payload.get("project_ref"),"project":copy.deepcopy(payload.get("project") or {}),"component_refs":_refs(payload.get("component_refs"),"component_refs"),"relationships":copy.deepcopy(_list(payload.get("relationships"),"relationships",MAX_RELATIONSHIPS)),"workstreams":copy.deepcopy(_list(payload.get("workstreams"),"workstreams",MAX_WORKSTREAMS)),"milestones":copy.deepcopy(_list(payload.get("milestones"),"milestones",MAX_MILESTONES)),"state":copy.deepcopy(payload.get("state") or {}),"provenance_refs":_refs(payload.get("provenance_refs"),"provenance_refs")}
    snap["snapshot_hash"]=_hash(snap); return {"ok":True,"version":VERSION,"snapshot":snap,"immutable_snapshot":True,"automatic_persistence":False}

def revision_plan(payload: dict[str, Any]) -> dict[str, Any]:
    changes=_list(payload.get("changes"),"changes",MAX_REVISIONS); plan={"project_ref":payload.get("project_ref"),"base_snapshot_ref":payload.get("base_snapshot_ref"),"changes":copy.deepcopy(changes),"reason":payload.get("reason"),"author_ref":payload.get("author_ref")}; plan["revision_hash"]=_hash(plan)
    return {"ok":True,"version":VERSION,"plan":plan,"automatic_apply":False,"domain_object_mutation":False}

def export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats=[str(x).lower() for x in _list(payload.get("formats") or ["json"],"formats",20)]
    allowed={"json","zip","pdf","html","markdown","csv","svg","png"}
    if any(x not in allowed for x in formats): raise ResearchProjectStudioError("unsupported export format.")
    plan={"project_ref":payload.get("project_ref"),"snapshot_ref":payload.get("snapshot_ref"),"formats":formats,"include_refs":_refs(payload.get("include_refs"),"include_refs"),"provenance_required":True}
    return {"ok":True,"version":VERSION,"plan":plan,"plan_hash":_hash(plan),"automatic_export_execution":False}

def core_project_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"schema":"sc.research.project-binding.v1","project_ref":payload.get("project_ref"),"session_id":payload.get("session_id"),"context_ref":payload.get("context_ref"),"component_refs":_refs(payload.get("component_refs"),"component_refs"),"snapshot_ref":payload.get("snapshot_ref"),"provenance_ref":payload.get("provenance_ref"),"source_product":"research-lab","source_version":VERSION}
    plan["binding_hash"]=_hash(plan); return {"ok":True,"version":VERSION,"core_plan":plan,"automatic_core_submission":False,"core_becomes_domain_authority":False}

def publication_package_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"project_ref":payload.get("project_ref"),"manuscript_refs":_refs(payload.get("manuscript_refs"),"manuscript_refs"),"figure_refs":_refs(payload.get("figure_refs"),"figure_refs"),"dataset_refs":_refs(payload.get("dataset_refs"),"dataset_refs"),"model_refs":_refs(payload.get("model_refs"),"model_refs"),"reproduction_package_refs":_refs(payload.get("reproduction_package_refs"),"reproduction_package_refs"),"citation_refs":_refs(payload.get("citation_refs"),"citation_refs"),"provenance_ref":payload.get("provenance_ref")}; plan["package_plan_hash"]=_hash(plan)
    return {"ok":True,"version":VERSION,"plan":plan,"automatic_publication":False,"publication_ready_equals_scientifically_valid":False}

def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    boundaries=["Project organization does not change the authority of source scientific objects.","A project status does not certify scientific validity.","References do not imply endorsement, confirmation, or evidentiary weight.","A dependency edge is declared, not inferred.","A claim/evidence link does not automatically change claim status.","A completed milestone does not mean the scientific result is correct.","A reproducible snapshot preserves declared project state; it does not validate the underlying research.","Cross-product bindings are reference-first and do not automatically mutate remote products.","Publication packaging does not constitute peer review or acceptance.","Core plans require explicit submission.","No project view may determine truth or causal validity."]
    return {"ok":True,"version":VERSION,"boundaries":boundaries,"scientific_validity_certified":False,"automatic_inference":False,"automatic_core_submission":False,"determine_truth":False}
