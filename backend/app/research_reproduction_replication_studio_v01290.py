from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

VERSION = "0.129.0"
ENGINE_VERSION = "10.0.0"
SCHEMA = "sc-lab-research-reproduction-replication-studio/0.129.0"
SNAPSHOT_SCHEMA = "sc-lab-reproduction-replication-snapshot/0.129.0"
MAX_ARTIFACTS = 5000
MAX_METRICS = 1000
MAX_DEVIATIONS = 2000
MAX_REPLICATIONS = 500

METHOD_FAMILIES = {
    "artifact-inventory", "input-integrity", "environment-lock", "method-reconstruction",
    "execution-reproduction", "output-comparison", "numerical-tolerance", "figure-reproduction",
    "provenance-reconstruction", "deviation-register", "replication-protocol", "independent-replication",
    "claim-linkage", "reproducibility-matrix", "package-assembly",
}

FIGURE_FAMILIES = {
    "reproduction-status-matrix", "artifact-lineage", "environment-diff", "input-hash-coverage",
    "metric-delta", "tolerance-band", "figure-diff", "deviation-timeline", "replication-comparison",
    "claim-evidence-link", "reproducibility-scorecard", "execution-lineage", "package-contents",
    "reproduction-flow",
}


class ReproductionReplicationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()


def _list(v: Any, label: str, maximum: int) -> list[Any]:
    if v is None:
        return []
    if not isinstance(v, list):
        raise ReproductionReplicationError(f"{label} must be an array.")
    if len(v) > maximum:
        raise ReproductionReplicationError(f"{label} exceeds configured maximum of {maximum}.")
    return v


def _finite(v: Any, label: str) -> float:
    try:
        out = float(v)
    except (TypeError, ValueError) as exc:
        raise ReproductionReplicationError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise ReproductionReplicationError(f"{label} must be finite.")
    return out


def schema_info() -> dict[str, Any]:
    return {"ok": True, "schema": SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION,
            "snapshot_schema": SNAPSHOT_SCHEMA,
            "limits": {"artifacts": MAX_ARTIFACTS, "metrics": MAX_METRICS, "deviations": MAX_DEVIATIONS,
                       "replications": MAX_REPLICATIONS}}


def catalog() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "method_families": sorted(METHOD_FAMILIES),
            "figure_families": sorted(FIGURE_FAMILIES), "automatic_execution": False,
            "automatic_claim_confirmation": False, "automatic_replication_success": False,
            "automatic_scientific_validity_certification": False}


def manifest() -> dict[str, Any]:
    return {"ok": True, "status": "research-reproduction-replication-studio-ready", "version": VERSION,
            "engine_version": ENGINE_VERSION, "reproduction_planning": True, "replication_planning": True,
            "artifact_integrity": True, "environment_locking": True, "result_comparison": True,
            "deviation_register": True, "claim_linkage": True, "package_assembly": True,
            "automatic_execution": False, "automatic_claim_confirmation": False,
            "automatic_replication_success": False, "automatic_scientific_validity_certification": False,
            "automatic_core_submission": False, "determine_truth": False}


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "method_family_count": len(METHOD_FAMILIES),
            "figure_family_count": len(FIGURE_FAMILIES)}


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ReproductionReplicationError("payload must be an object.")
    mode = str(payload.get("mode") or "reproduction").strip().lower()
    if mode not in {"reproduction", "replication"}:
        raise ReproductionReplicationError("mode must be reproduction or replication.")
    study = {
        "schema": SCHEMA, "version": VERSION, "study_ref": str(payload.get("study_ref") or "study:unspecified")[:300],
        "mode": mode, "title": str(payload.get("title") or "Research reproduction / replication")[:500],
        "source_publication_ref": payload.get("source_publication_ref"),
        "original_execution_ref": payload.get("original_execution_ref"),
        "declared_claim_refs": copy.deepcopy(_list(payload.get("claim_refs"), "claim_refs", 1000)),
        "artifact_refs": copy.deepcopy(_list(payload.get("artifact_refs"), "artifact_refs", MAX_ARTIFACTS)),
        "assumptions": copy.deepcopy(payload.get("assumptions") or {}),
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
        "boundaries": {"same_result_equals_same_truth": False, "rerun_confirms_claim": False,
                       "replication_proves_claim": False, "automatic_scientific_validity": False},
    }
    study["study_hash"] = _hash(study)
    return {"ok": True, "version": VERSION, "study": study}


def artifact_inventory(payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = _list(payload.get("artifacts"), "artifacts", MAX_ARTIFACTS)
    rows=[]
    for i,a in enumerate(artifacts):
        if not isinstance(a, dict): raise ReproductionReplicationError(f"artifacts[{i}] must be an object.")
        ref=str(a.get("ref") or a.get("artifact_ref") or f"artifact:{i}")[:300]
        declared_hash=a.get("sha256") or a.get("hash")
        rows.append({"artifact_ref":ref,"artifact_type":str(a.get("type") or "unspecified")[:100],
                     "sha256":declared_hash,"uri":a.get("uri"),"required":bool(a.get("required",True)),
                     "available":bool(a.get("available",False)),"hash_declared":bool(declared_hash)})
    required=[r for r in rows if r["required"]]
    available=sum(1 for r in required if r["available"])
    hashed=sum(1 for r in required if r["hash_declared"])
    return {"ok":True,"version":VERSION,"artifacts":rows,"required_count":len(required),
            "required_available_count":available,"required_hashed_count":hashed,
            "availability_fraction":available/len(required) if required else 1.0,
            "hash_coverage_fraction":hashed/len(required) if required else 1.0,
            "inventory_hash":_hash(rows),"artifact_completeness_is_scientific_validity":False}


def input_integrity_report(payload: dict[str, Any]) -> dict[str, Any]:
    checks=_list(payload.get("checks"),"checks",MAX_ARTIFACTS)
    rows=[]
    for i,c in enumerate(checks):
        if not isinstance(c,dict): raise ReproductionReplicationError(f"checks[{i}] must be an object.")
        expected=str(c.get("expected_sha256") or "").lower(); observed=str(c.get("observed_sha256") or "").lower()
        if expected and len(expected)!=64: raise ReproductionReplicationError("expected_sha256 must be a 64-character SHA-256 when provided.")
        if observed and len(observed)!=64: raise ReproductionReplicationError("observed_sha256 must be a 64-character SHA-256 when provided.")
        status="match" if expected and observed and expected==observed else "mismatch" if expected and observed else "incomplete"
        rows.append({"artifact_ref":c.get("artifact_ref"),"status":status,"expected_sha256":expected or None,"observed_sha256":observed or None})
    return {"ok":True,"version":VERSION,"checks":rows,"all_declared_inputs_match":bool(rows) and all(r["status"]=="match" for r in rows),
            "input_match_confirms_scientific_claim":False}


def environment_lock_plan(payload: dict[str, Any]) -> dict[str, Any]:
    env=copy.deepcopy(payload.get("environment") or {})
    lock={"runtime":env.get("runtime"),"runtime_version":env.get("runtime_version"),"os":env.get("os"),
          "architecture":env.get("architecture"),"container_digest":env.get("container_digest"),
          "dependency_lock_ref":env.get("dependency_lock_ref"),"dependency_lock_hash":env.get("dependency_lock_hash"),
          "system_packages":copy.deepcopy(env.get("system_packages") or []),"environment_variables_declared":sorted((env.get("environment_variables") or {}).keys())}
    return {"ok":True,"version":VERSION,"environment_lock":lock,"lock_hash":_hash(lock),"automatic_environment_creation":False,
            "environment_match_guarantees_identical_result":False}


def method_reconstruction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    steps=_list(payload.get("steps"),"steps",1000)
    norm=[]
    for i,s in enumerate(steps):
        if not isinstance(s,dict): raise ReproductionReplicationError(f"steps[{i}] must be an object.")
        norm.append({"order":i+1,"step_ref":s.get("step_ref") or f"method-step:{i+1}","method_ref":s.get("method_ref"),
                     "input_refs":copy.deepcopy(s.get("input_refs") or []),"output_refs":copy.deepcopy(s.get("output_refs") or []),
                     "parameters":copy.deepcopy(s.get("parameters") or {}),"seed":s.get("seed")})
    return {"ok":True,"version":VERSION,"steps":norm,"method_plan_hash":_hash(norm),"automatic_execution":False,
            "method_equivalence_certified":False}


def execution_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"study_ref":payload.get("study_ref"),"environment_lock_ref":payload.get("environment_lock_ref"),
          "method_plan_ref":payload.get("method_plan_ref"),"input_refs":copy.deepcopy(payload.get("input_refs") or []),
          "expected_output_refs":copy.deepcopy(payload.get("expected_output_refs") or []),"seed_policy":payload.get("seed_policy") or "declared-only",
          "execution_policy":"explicit-human-or-runtime-submission"}
    plan["plan_hash"]=_hash(plan)
    return {"ok":True,"version":VERSION,"plan":plan,"automatic_execution":False,"automatic_retry":False,"automatic_core_submission":False}


def tolerance_profile(payload: dict[str, Any]) -> dict[str, Any]:
    abs_tol=_finite(payload.get("absolute_tolerance",0.0),"absolute_tolerance")
    rel_tol=_finite(payload.get("relative_tolerance",0.0),"relative_tolerance")
    if abs_tol<0 or rel_tol<0: raise ReproductionReplicationError("tolerances must be non-negative.")
    profile={"absolute_tolerance":abs_tol,"relative_tolerance":rel_tol,"rounding_digits":payload.get("rounding_digits"),
             "nan_policy":str(payload.get("nan_policy") or "explicit-mismatch"),"units":payload.get("units")}
    return {"ok":True,"version":VERSION,"profile":profile,"profile_hash":_hash(profile),"automatic_tolerance_selection":False}


def result_comparison(payload: dict[str, Any]) -> dict[str, Any]:
    expected=_list(payload.get("expected"),"expected",MAX_METRICS); observed=_list(payload.get("observed"),"observed",MAX_METRICS)
    if len(expected)!=len(observed): raise ReproductionReplicationError("expected and observed must have equal length.")
    abs_tol=_finite(payload.get("absolute_tolerance",0.0),"absolute_tolerance"); rel_tol=_finite(payload.get("relative_tolerance",0.0),"relative_tolerance")
    rows=[]
    for i,(a,b) in enumerate(zip(expected,observed)):
        av=_finite(a,"expected value"); bv=_finite(b,"observed value"); delta=bv-av; allowed=max(abs_tol,rel_tol*abs(av)); matched=abs(delta)<=allowed
        rows.append({"index":i,"expected":av,"observed":bv,"delta":delta,"absolute_delta":abs(delta),"allowed_delta":allowed,"within_tolerance":matched})
    return {"ok":True,"version":VERSION,"comparisons":rows,"all_within_tolerance":all(r["within_tolerance"] for r in rows),
            "comparison_hash":_hash(rows),"numerical_match_confirms_claim":False}


def figure_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figures=_list(payload.get("figures"),"figures",1000)
    rows=[]
    for i,f in enumerate(figures):
        if not isinstance(f,dict): raise ReproductionReplicationError(f"figures[{i}] must be an object.")
        rows.append({"figure_ref":f.get("figure_ref") or f"figure:{i+1}","source_data_refs":copy.deepcopy(f.get("source_data_refs") or []),
                     "spec_ref":f.get("spec_ref"),"renderer":f.get("renderer"),"expected_artifact_hash":f.get("expected_artifact_hash"),
                     "comparison_mode":f.get("comparison_mode") or "semantic-plus-pixel-optional"})
    return {"ok":True,"version":VERSION,"figures":rows,"plan_hash":_hash(rows),"automatic_rendering":False,"pixel_identity_required":False}


def provenance_reconstruction(payload: dict[str, Any]) -> dict[str, Any]:
    nodes=_list(payload.get("nodes"),"nodes",MAX_ARTIFACTS); edges=_list(payload.get("edges"),"edges",MAX_ARTIFACTS*2)
    node_ids={str(n.get("ref")) for n in nodes if isinstance(n,dict) and n.get("ref")}
    unresolved=[]
    for e in edges:
        if isinstance(e,dict):
            for key in ("from","to"):
                if e.get(key) and str(e[key]) not in node_ids: unresolved.append(str(e[key]))
    graph={"nodes":copy.deepcopy(nodes),"edges":copy.deepcopy(edges)}
    return {"ok":True,"version":VERSION,"graph":graph,"graph_hash":_hash(graph),"unresolved_refs":sorted(set(unresolved)),
            "provenance_complete":len(unresolved)==0,"provenance_complete_equals_validity":False}


def deviation_register(payload: dict[str, Any]) -> dict[str, Any]:
    deviations=_list(payload.get("deviations"),"deviations",MAX_DEVIATIONS)
    rows=[]
    for i,d in enumerate(deviations):
        if not isinstance(d,dict): raise ReproductionReplicationError(f"deviations[{i}] must be an object.")
        rows.append({"deviation_ref":d.get("deviation_ref") or f"deviation:{i+1}","category":d.get("category") or "unspecified",
                     "original":copy.deepcopy(d.get("original")),"reproduction":copy.deepcopy(d.get("reproduction")),
                     "rationale":d.get("rationale"),"expected_impact":d.get("expected_impact"),"review_status":d.get("review_status") or "unreviewed"})
    return {"ok":True,"version":VERSION,"deviations":rows,"deviation_count":len(rows),"register_hash":_hash(rows),"automatic_impact_inference":False}


def replication_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    protocol={"claim_refs":copy.deepcopy(payload.get("claim_refs") or []),"independent_data":bool(payload.get("independent_data",True)),
              "independent_team":bool(payload.get("independent_team",False)),"method_relation":payload.get("method_relation") or "declared",
              "population_relation":payload.get("population_relation") or "declared","predeclared_outcomes":copy.deepcopy(payload.get("predeclared_outcomes") or []),
              "acceptance_criteria":copy.deepcopy(payload.get("acceptance_criteria") or []),"deviation_policy":payload.get("deviation_policy") or "record-all"}
    return {"ok":True,"version":VERSION,"protocol":protocol,"protocol_hash":_hash(protocol),"automatic_success_criteria_selection":False}


def independent_replication_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"protocol_ref":payload.get("protocol_ref"),"dataset_refs":copy.deepcopy(payload.get("dataset_refs") or []),
          "method_refs":copy.deepcopy(payload.get("method_refs") or []),"environment_ref":payload.get("environment_ref"),
          "analysis_plan_ref":payload.get("analysis_plan_ref"),"blinding":payload.get("blinding"),"registered_deviations":copy.deepcopy(payload.get("registered_deviations") or [])}
    return {"ok":True,"version":VERSION,"plan":plan,"plan_hash":_hash(plan),"automatic_execution":False,"automatic_replication_judgment":False}


def replication_result_record(payload: dict[str, Any]) -> dict[str, Any]:
    outcomes=_list(payload.get("outcomes"),"outcomes",MAX_METRICS)
    record={"replication_ref":payload.get("replication_ref"),"protocol_ref":payload.get("protocol_ref"),"outcomes":copy.deepcopy(outcomes),
            "deviation_refs":copy.deepcopy(payload.get("deviation_refs") or []),"execution_ref":payload.get("execution_ref"),
            "researcher_interpretation":payload.get("researcher_interpretation")}
    record["record_hash"]=_hash(record)
    return {"ok":True,"version":VERSION,"record":record,"automatic_success_label":False,"automatic_claim_confirmation":False}


def claim_linkage_report(payload: dict[str, Any]) -> dict[str, Any]:
    links=_list(payload.get("links"),"links",MAX_ARTIFACTS)
    rows=[]
    for i,l in enumerate(links):
        if not isinstance(l,dict): raise ReproductionReplicationError(f"links[{i}] must be an object.")
        rows.append({"claim_ref":l.get("claim_ref"),"original_evidence_refs":copy.deepcopy(l.get("original_evidence_refs") or []),
                     "reproduction_output_refs":copy.deepcopy(l.get("reproduction_output_refs") or []),"replication_output_refs":copy.deepcopy(l.get("replication_output_refs") or []),
                     "researcher_assessment":l.get("researcher_assessment")})
    return {"ok":True,"version":VERSION,"links":rows,"linkage_hash":_hash(rows),"automatic_evidentiary_weighting":False,"automatic_claim_status_change":False}


def reproducibility_matrix(payload: dict[str, Any]) -> dict[str, Any]:
    dimensions=payload.get("dimensions") or {}
    defaults=("inputs","environment","methods","parameters","randomness","outputs","figures","provenance","documentation")
    rows=[]
    for d in defaults:
        val=dimensions.get(d,"unknown") if isinstance(dimensions,dict) else "unknown"
        if isinstance(val,bool): val="available" if val else "missing"
        rows.append({"dimension":d,"status":str(val)})
    counts={s:sum(1 for r in rows if r["status"]==s) for s in sorted({r["status"] for r in rows})}
    return {"ok":True,"version":VERSION,"matrix":rows,"counts":counts,"matrix_hash":_hash(rows),"automatic_score":False,"automatic_grade":False}


def package_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    items=_list(payload.get("items"),"items",MAX_ARTIFACTS)
    normalized=[]
    for i,x in enumerate(items):
        if not isinstance(x,dict): raise ReproductionReplicationError(f"items[{i}] must be an object.")
        normalized.append({"ref":x.get("ref") or f"item:{i+1}","type":x.get("type") or "artifact","sha256":x.get("sha256"),"required":bool(x.get("required",True))})
    pkg={"package_ref":payload.get("package_ref") or "reproduction-package","items":normalized,"study_ref":payload.get("study_ref"),
         "snapshot_ref":payload.get("snapshot_ref"),"license":payload.get("license"),"citation":payload.get("citation")}
    return {"ok":True,"version":VERSION,"package":pkg,"package_hash":_hash(pkg),"automatic_publication":False,"scientific_validity_certified":False}


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figs=[{"figure_type":f,"purpose":"reproduction / replication review","publication_profile":payload.get("publication_profile") or "research-report"} for f in sorted(FIGURE_FAMILIES)]
    return {"ok":True,"version":VERSION,"figures":figs,"figure_count":len(figs),"automatic_claim_encoding":False}


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    studio={"schema":SCHEMA,"version":VERSION,"study_ref":payload.get("study_ref"),"mode":payload.get("mode") or "reproduction",
            "artifact_inventory_ref":payload.get("artifact_inventory_ref"),"environment_lock_ref":payload.get("environment_lock_ref"),
            "method_plan_ref":payload.get("method_plan_ref"),"execution_refs":copy.deepcopy(payload.get("execution_refs") or []),
            "comparison_refs":copy.deepcopy(payload.get("comparison_refs") or []),"deviation_register_ref":payload.get("deviation_register_ref"),
            "replication_refs":copy.deepcopy(payload.get("replication_refs") or []),"claim_refs":copy.deepcopy(payload.get("claim_refs") or [])}
    studio["studio_hash"]=_hash(studio)
    return {"ok":True,"version":VERSION,"studio":studio,"automatic_execution":False,"automatic_claim_confirmation":False}


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"studio":copy.deepcopy(payload.get("studio") or {}),"study_ref":payload.get("study_ref"),
          "artifact_inventory_ref":payload.get("artifact_inventory_ref"),"environment_lock_ref":payload.get("environment_lock_ref"),
          "method_plan_ref":payload.get("method_plan_ref"),"execution_refs":copy.deepcopy(payload.get("execution_refs") or []),
          "deviation_register_ref":payload.get("deviation_register_ref"),"package_ref":payload.get("package_ref")}
    return {"ok":True,"version":VERSION,"snapshot":snap,"snapshot_hash":_hash(snap),"automatic_persistence":False}


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats=payload.get("formats") or ["json","zip","html","pdf"]
    return {"ok":True,"version":VERSION,"formats":formats,"include_manifest":True,"include_hashes":True,"include_environment_lock":True,
            "include_deviation_register":True,"include_claim_links":True,"automatic_publication":False}


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"session_id":payload.get("session_id"),"object_type":"research-reproduction-replication-package",
          "object_ref":payload.get("analysis_id") or payload.get("study_ref") or "reproduction:unspecified",
          "snapshot_ref":payload.get("snapshot_ref"),"package_ref":payload.get("package_ref"),"claim_refs":copy.deepcopy(payload.get("claim_refs") or []),
          "execution_refs":copy.deepcopy(payload.get("execution_refs") or []),"replication_refs":copy.deepcopy(payload.get("replication_refs") or [])}
    return {"ok":True,"version":VERSION,"core_plan":plan,"plan_hash":_hash(plan),"automatic_core_submission":False,"automatic_claim_status_change":False}


def build_execution_lineage_plan(payload: dict[str, Any]) -> dict[str, Any]:
    lineage={"session_id":payload.get("session_id"),"source_execution_ref":payload.get("source_execution_ref"),
             "reproduction_execution_refs":copy.deepcopy(payload.get("reproduction_execution_refs") or []),
             "replication_execution_refs":copy.deepcopy(payload.get("replication_execution_refs") or []),
             "environment_refs":copy.deepcopy(payload.get("environment_refs") or []),"dataset_refs":copy.deepcopy(payload.get("dataset_refs") or [])}
    return {"ok":True,"version":VERSION,"lineage":lineage,"lineage_hash":_hash(lineage),"automatic_execution":False,"automatic_certification":False}


def readiness_report(payload: dict[str, Any]) -> dict[str, Any]:
    requirements={"artifact_inventory":bool(payload.get("artifact_inventory_ref")),"environment_lock":bool(payload.get("environment_lock_ref")),
                  "method_plan":bool(payload.get("method_plan_ref")),"declared_outputs":bool(payload.get("expected_output_refs")),
                  "tolerance_profile":bool(payload.get("tolerance_profile_ref")),"provenance":bool(payload.get("provenance_ref"))}
    missing=[k for k,v in requirements.items() if not v]
    return {"ok":True,"version":VERSION,"requirements":requirements,"missing":missing,"ready_for_execution_review":not missing,
            "ready_for_scientific_acceptance":False,"automatic_waiver":False}


def reproduction_status_report(payload: dict[str, Any]) -> dict[str, Any]:
    domains=("artifacts","inputs","environment","methods","execution","outputs","figures","provenance","deviations","replication")
    supplied=payload.get("status") or {}
    rows=[{"domain":d,"status":str(supplied.get(d,"not-reviewed")) if isinstance(supplied,dict) else "not-reviewed"} for d in domains]
    return {"ok":True,"version":VERSION,"status":rows,"status_hash":_hash(rows),"automatic_overall_grade":False,
            "automatic_scientific_acceptance":False,"automatic_claim_confirmation":False}


def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    boundaries={
        "rerun_success_confirms_scientific_claim":False,
        "numerical_match_proves_original_correct":False,
        "replication_match_proves_causality":False,
        "replication_difference_falsifies_claim_automatically":False,
        "environment_match_guarantees_identical_result":False,
        "artifact_completeness_certifies_validity":False,
        "automatic_replication_success_label":False,
        "automatic_evidentiary_weighting":False,
        "automatic_claim_status_change":False,
        "automatic_scientific_validity_certification":False,
        "automatic_core_submission":False,
        "determine_truth":False,
    }
    return {"ok":True,"version":VERSION,"boundaries":boundaries,"scientific_validity_certified":False}
