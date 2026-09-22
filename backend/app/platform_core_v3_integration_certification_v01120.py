from __future__ import annotations

import copy
import json
import re
from hashlib import sha256
from typing import Any

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_research_context_v01060 import normalize_research_context

LAB_VERSION = "0.112.0"
FEATURE_VERSION = "0.112.0"
MINIMUM_CORE_RELEASE = "3.0.0"
CORE_CERTIFICATION_CONTRACT = "sc.research.platform-integration-certification.v1"
CORE_UNIFIED_RUNTIME_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
BRIDGE_SCHEMA = "sc-lab-platform-core-v3-integration-certification/0.112.0"
CORE_CERT_BASE = "/v1/research/integration-certification"

LAYER_CATALOG = [
    {"key":"runtime-adapter","version":"0.104.0","health_path":"/v1/platform-core-v3-adapter/health","capabilities":["runtime-contract","capability-registration","handoff-validation"]},
    {"key":"canonical-objects","version":"0.105.0","health_path":"/v1/platform-core-v3-objects/health","capabilities":["object-normalization","reference-first-object-binding","legacy-handoff-mapping"]},
    {"key":"research-context","version":"0.106.0","health_path":"/v1/platform-core-v3-context/health","capabilities":["project-context","session-context","context-continuity"]},
    {"key":"execution-lineage","version":"0.107.0","health_path":"/v1/platform-core-v3-executions/health","capabilities":["execution-normalization","execution-binding","lineage-hash"]},
    {"key":"findings-validation","version":"0.108.0","health_path":"/v1/platform-core-v3-research-intelligence/health","capabilities":["finding-claim-evidence","validation-challenge","replication-record"]},
    {"key":"visual-scene","version":"0.109.0","health_path":"/v1/platform-core-v3-visual-scene/health","capabilities":["visual-binding","scene-contract","renderer-negotiation"]},
    {"key":"scholarly-package","version":"0.110.0","health_path":"/v1/platform-core-v3-scholarly-packages/health","capabilities":["package-binding","scholarly-plan","provenance-manifest"]},
    {"key":"scientific-investigation","version":"0.111.0","health_path":"/v1/platform-core-v3-scientific-investigations/health","capabilities":["investigation-binding","scientific-assets","investigation-continuity"]},
]

CASE_CATALOG = [
    ("runtime-manifest","runtime-adapter","read","runtime-contract","Lab exposes a reference-first Core runtime adapter with automatic Core calls disabled"),
    ("runtime-handoff-boundary","runtime-adapter","handoff","handoff","Core-to-Lab handoffs remain explicit and do not auto-execute scientific work"),
    ("object-normalization","canonical-objects","create","research-object","Lab objects normalize to stable Core-compatible references"),
    ("object-authority","canonical-objects","trace","research-object","Underlying specialist objects remain authoritative in Lab"),
    ("session-project-continuity","research-context","trace","research-context","Project and session references remain stable across bridge operations"),
    ("session-binding-plan","research-context","handoff","research-context","Lab can construct Core session/product-context bindings without auto-submission"),
    ("execution-lineage","execution-lineage","trace","execution","Runtime, method, environment, inputs and outputs remain explicitly traceable"),
    ("execution-boundary","execution-lineage","read","execution","Core records execution lineage but does not execute the computation"),
    ("claim-evidence-declaration","findings-validation","trace","claim","Claims and evidence remain declared research objects rather than inferred truth"),
    ("validation-boundary","findings-validation","read","validation","Validation/replication records do not certify scientific validity automatically"),
    ("visual-binding","visual-scene","handoff","visual","Visual identity and source references bridge into Core without Core rendering"),
    ("scene-authority","visual-scene","trace","scene","Scientific scenes remain renderer-neutral in Core and render-authoritative in Lab"),
    ("package-binding","scholarly-package","handoff","research-package","Reproducibility packages bridge to Core without auto-publication or identifier minting"),
    ("scholarly-provenance","scholarly-package","trace","publication","Citations, datasets, notebooks and provenance remain explicit package references"),
    ("investigation-binding","scientific-investigation","handoff","investigation","Scientific investigations bind to Core using explicit evidence/claim/hypothesis references"),
    ("investigation-boundary","scientific-investigation","read","investigation","Core does not rank evidence, select hypotheses, infer causality, or determine truth"),
    ("cross-layer-roundtrip","cross-layer","snapshot","research-session","One session can preserve references across objects, execution, claims, visuals, packages and investigation"),
    ("immutable-certification-evidence","cross-layer","snapshot","certification","Certification evidence is hashable, revisionable, and snapshot-ready"),
]

FORBIDDEN = {
    "automatic_core_submission", "invoke_product_by_core", "execute_conformance_case_by_core",
    "certify_scientific_validity_by_core", "certify_product_quality_by_core",
    "authorize_product_by_certification_by_core", "rank_products_by_core",
    "infer_missing_evidence_by_core", "infer_reproducibility_by_core",
    "resolve_failed_case_by_core", "determine_truth_by_core",
}

class PlatformCoreV3IntegrationCertificationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()

def _text(v: Any, label: str, maximum: int = 4000, required: bool = True) -> str:
    s=str(v or "").strip()
    if required and not s: raise PlatformCoreV3IntegrationCertificationError(f"{label} is required.")
    if len(s)>maximum: raise PlatformCoreV3IntegrationCertificationError(f"{label} exceeds {maximum} characters.")
    return s

def _dict(v: Any, label: str) -> dict[str, Any]:
    if v is None: return {}
    if not isinstance(v, dict): raise PlatformCoreV3IntegrationCertificationError(f"{label} must be an object.")
    return copy.deepcopy(v)

def _items(v: Any, label: str, maximum: int = 5000) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise PlatformCoreV3IntegrationCertificationError(f"{label} must be an array.")
    if len(v)>maximum: raise PlatformCoreV3IntegrationCertificationError(f"{label} exceeds {maximum} entries.")
    return copy.deepcopy(v)

def _reject_forbidden(payload: dict[str, Any]) -> None:
    bad=sorted(k for k in FORBIDDEN if payload.get(k) not in (None,False))
    if bad:
        raise PlatformCoreV3IntegrationCertificationError("Certification records runtime-contract conformance evidence only; forbidden authority requested: "+", ".join(bad))

def _context(payload: dict[str, Any]) -> dict[str, Any]:
    raw=payload.get("context") if isinstance(payload.get("context"),dict) else payload
    try: return normalize_research_context(raw)["context"]
    except Exception as exc: raise PlatformCoreV3IntegrationCertificationError(f"Invalid research context: {exc}", getattr(exc,"status_code",400)) from exc

def _visibility(v: Any) -> str:
    s=_text(v or "internal","visibility",20)
    if s not in {"private","internal","public"}: raise PlatformCoreV3IntegrationCertificationError("visibility must be private, internal, or public.")
    return "internal" if s=="private" else s

def catalog() -> dict[str, Any]:
    return {
        "ok": True, "schema": BRIDGE_SCHEMA, "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE, "core_contract": CORE_CERTIFICATION_CONTRACT,
        "layer_count": len(LAYER_CATALOG), "case_count": len(CASE_CATALOG),
        "layers": copy.deepcopy(LAYER_CATALOG),
        "cases": [{"case_key":k,"layer":layer,"operation":op,"object_type":obj,"requirement":req,"required":True} for k,layer,op,obj,req in CASE_CATALOG],
        "certification_scope": "platform_runtime_contract_conformance_only",
    }

def build_suite_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise PlatformCoreV3IntegrationCertificationError("A certification request object is required.")
    _reject_forbidden(payload); ctx=_context(payload)
    title=_text(payload.get("title") or "Sustainable Catalyst Lab / Platform Core integration certification","title",1000)
    suite_key=_text(payload.get("suite_key") or f"lab-core-v01120-{_hash({'project':ctx['project_ref'],'title':title})[:12]}","suite_key",400)
    data={
        "suite_key":suite_key,"title":title,"contract_ref":CORE_UNIFIED_RUNTIME_CONTRACT,"contract_version":"1.0","status":"active",
        "required_operations":["create","read","handoff","trace","version","snapshot"],
        "required_capabilities":[f"lab:{x['key']}:{x['version']}" for x in LAYER_CATALOG],
        "visibility":_visibility(payload.get("visibility")),
        "metadata":{"lab_release_version":LAB_VERSION,"product_ref":PRODUCT_REF,"project_ref":ctx["project_ref"],"session_id":ctx["session_id"],"certification_scope":"platform_runtime_contract_conformance_only"},
        "provenance":{"context_ref":ctx["context_ref"],"workflow_ref":ctx.get("workflow_ref"),"project_state_ref":ctx.get("project_state_ref")},
        "created_by":_text(payload.get("created_by") or ctx.get("researcher_ref") or "operator:lab-certification","created_by",1200),
    }
    return {"ok":True,"endpoint":f"{CORE_CERT_BASE}/suites","method":"POST","data":data,"request_body":{"data":data},"automatic_submission":False,"suite_plan_hash":_hash(data)}

def build_product_plan(payload: dict[str, Any]) -> dict[str, Any]:
    _reject_forbidden(payload); suite_id=_text(payload.get("suite_id") or payload.get("suiteId"),"suite_id",400)
    data={
        "product_key":"sustainable-catalyst-lab","suite_id":suite_id,"product_ref":PRODUCT_REF,"product_version":LAB_VERSION,
        "runtime_binding_ref":"lab:runtime:scientific-compute:0.104.0",
        "declared_capabilities":[c for layer in LAYER_CATALOG for c in layer["capabilities"]],
        "declared_object_types":["dataset","model","experiment","workflow","execution","evidence","claim","finding","visual","scene","research-package","publication","investigation"],
        "visibility":_visibility(payload.get("visibility")),
        "metadata":{"integration_layers":[x["key"] for x in LAYER_CATALOG],"minimum_core_release":MINIMUM_CORE_RELEASE,"lab_release_version":LAB_VERSION},
    }
    return {"ok":True,"endpoint":f"{CORE_CERT_BASE}/products","method":"POST","data":data,"request_body":{"data":data},"automatic_submission":False,"product_plan_hash":_hash(data)}

def build_case_plans(payload: dict[str, Any]) -> dict[str, Any]:
    _reject_forbidden(payload); suite_id=_text(payload.get("suite_id") or payload.get("suiteId"),"suite_id",400); vis=_visibility(payload.get("visibility"))
    cases=[]
    for key,layer,op,obj,req in CASE_CATALOG:
        data={"case_key":key,"suite_id":suite_id,"operation":op,"object_type":obj,"requirement":req,"expected_evidence":["declared-result","reference-trace","boundary-assertion"],"required":True,"visibility":vis,"metadata":{"layer":layer,"lab_release_version":LAB_VERSION}}
        cases.append({"endpoint":f"{CORE_CERT_BASE}/cases","method":"POST","data":data,"request_body":{"data":data}})
    return {"ok":True,"count":len(cases),"cases":cases,"automatic_submission":False,"catalog_hash":_hash([x["data"] for x in cases])}

def build_run_plan(payload: dict[str, Any]) -> dict[str, Any]:
    _reject_forbidden(payload)
    data={"run_key":_text(payload.get("run_key") or f"lab-v01120-{_hash(payload)[:12]}","run_key",400),"suite_id":_text(payload.get("suite_id"),"suite_id",400),"product_id":_text(payload.get("product_id"),"product_id",400),"executed_by":_text(payload.get("executed_by") or "lab:conformance-harness","executed_by",1200),"environment_ref":_text(payload.get("environment_ref") or "lab:environment:production","environment_ref",1200),"visibility":_visibility(payload.get("visibility")),"metadata":{"lab_release_version":LAB_VERSION,"does_not_invoke_product":True,"does_not_certify_scientific_validity":True}}
    return {"ok":True,"endpoint":f"{CORE_CERT_BASE}/runs","method":"POST","data":data,"request_body":{"data":data},"automatic_submission":False,"automatic_product_invocation":False,"run_plan_hash":_hash(data)}

def build_case_result_plan(payload: dict[str, Any]) -> dict[str, Any]:
    _reject_forbidden(payload); status=_text(payload.get("status") or "not_run","status",40)
    if status not in {"pass","fail","blocked","not_run","not_applicable"}: raise PlatformCoreV3IntegrationCertificationError("unsupported case-result status")
    data={"run_id":_text(payload.get("run_id"),"run_id",400),"case_id":_text(payload.get("case_id"),"case_id",400),"status":status,"observed_behavior":_text(payload.get("observed_behavior"),"observed_behavior",8000,False) or None,"evidence_refs":[_text(x,"evidence_ref",1200) for x in _items(payload.get("evidence_refs"),"evidence_refs")],"executed_by":_text(payload.get("executed_by") or "lab:conformance-harness","executed_by",1200),"visibility":_visibility(payload.get("visibility")),"metadata":_dict(payload.get("metadata"),"metadata")}
    return {"ok":True,"endpoint":f"{CORE_CERT_BASE}/case-results","method":"POST","data":data,"request_body":{"data":data},"automatic_submission":False,"scientific_validity_assessed":False}

def _check_plan(kind: str, endpoint: str, payload: dict[str, Any], required: list[str]) -> dict[str, Any]:
    _reject_forbidden(payload); data={k:copy.deepcopy(payload[k]) for k in payload if k not in FORBIDDEN and k not in {"automatic_submission"}}
    for key in required: _text(data.get(key),key,4000)
    data.setdefault("visibility",_visibility(payload.get("visibility")))
    data.setdefault("metadata",{}); data["metadata"]={**_dict(data.get("metadata"),"metadata"),"lab_release_version":LAB_VERSION,"certification_scope":"runtime_contract_conformance_only"}
    return {"ok":True,"kind":kind,"endpoint":f"{CORE_CERT_BASE}/{endpoint}","method":"POST","data":data,"request_body":{"data":data},"automatic_submission":False,"scientific_validity_assessed":False,"record_hash":_hash(data)}

def build_exchange_check_plan(payload): return _check_plan("exchange-check","exchange-checks",payload,["run_id","source_product_ref","target_product_ref","exchange_ref","status"])
def build_trace_check_plan(payload): return _check_plan("trace-check","trace-checks",payload,["run_id","object_ref","status"])
def build_reproduction_check_plan(payload): return _check_plan("reproduction-check","reproduction-checks",payload,["run_id","project_ref","status"])
def build_evidence_plan(payload): return _check_plan("certification-evidence","evidence",payload,["evidence_key","run_id","evidence_type","evidence_ref"])
def build_finding_plan(payload): return _check_plan("certification-finding","findings",payload,["finding_key","run_id","category","statement"])

def assess_roundtrip(payload: dict[str, Any]) -> dict[str, Any]:
    _reject_forbidden(payload); results=_items(payload.get("results"),"results",1000)
    by_key={_text(x.get("case_key"),"case_key",400):_text(x.get("status") or "not_run","status",40) for x in results if isinstance(x,dict)}
    required=[x[0] for x in CASE_CATALOG]; missing=[k for k in required if k not in by_key]; nonpassing=[k for k in required if k in by_key and by_key[k]!="pass"]
    declared=(not missing and not nonpassing)
    state={"required_case_count":len(required),"observed_case_count":len(by_key),"missing_required_cases":missing,"nonpassing_required_cases":nonpassing,"declared_conformance":declared}
    return {"ok":True,"schema":"sc-lab-platform-core-v3-certification-assessment/0.112.0",**state,"assessment_hash":_hash(state),"scientific_validity_certified":False,"product_quality_certified":False,"truth_determined":False,"automatic_remediation":False}

def compatibility_report(readiness: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(readiness,dict): raise PlatformCoreV3IntegrationCertificationError("Core certification readiness object is required.")
    version=str(readiness.get("version") or readiness.get("release") or "0.0.0")
    m=re.fullmatch(r"(\d+)\.(\d+)\.(\d+)",version)
    version_ok=bool(m and tuple(map(int,m.groups())) >= (3,0,0))
    required_true=["certification_suite_registry_by_core","certification_product_registry_by_core","conformance_case_registry_by_core","conformance_run_registry_by_core","conformance_result_registry_by_core","exchange_check_registry_by_core","trace_check_registry_by_core","reproduction_check_registry_by_core","certification_evidence_registry_by_core","certification_finding_registry_by_core","revision_history_by_core","immutable_certification_snapshots_by_core"]
    required_false=["invoke_product_by_core","execute_conformance_case_by_core","certify_scientific_validity_by_core","certify_product_quality_by_core","authorize_product_by_certification_by_core","rank_products_by_core","infer_missing_evidence_by_core","infer_reproducibility_by_core","resolve_failed_case_by_core","determine_truth_by_core"]
    missing_true=[k for k in required_true if readiness.get(k) is not True]; wrong_false=[k for k in required_false if readiness.get(k) is not False]
    contract_ok=readiness.get("contract") in {CORE_CERTIFICATION_CONTRACT,None}
    compatible=version_ok and contract_ok and not missing_true and not wrong_false
    return {"ok":True,"status":"compatible" if compatible else "incompatible","compatible":compatible,"detected_core_release":version,"minimum_core_release":MINIMUM_CORE_RELEASE,"contract":readiness.get("contract"),"missing_required_capabilities":missing_true,"violated_boundaries":wrong_false,"scientific_validity_certified":False,"truth_determined":False}

def build_full_submission_plan(payload: dict[str, Any]) -> dict[str, Any]:
    _reject_forbidden(payload); ctx=_context(payload)
    suite=build_suite_plan({**payload,"context":ctx}); placeholder="<core-suite-id>"; product=build_product_plan({"suite_id":placeholder,"visibility":payload.get("visibility")}); cases=build_case_plans({"suite_id":placeholder,"visibility":payload.get("visibility")})
    plan=[{"step":1,"name":"create-suite","operation":suite},{"step":2,"name":"register-product","depends_on":["create-suite"],"operation":product},{"step":3,"name":"register-conformance-cases","depends_on":["create-suite"],"operation":cases},{"step":4,"name":"create-run","depends_on":["register-product","register-conformance-cases"],"endpoint":f"{CORE_CERT_BASE}/runs"},{"step":5,"name":"record-case-results-and-checks","depends_on":["create-run"],"endpoints":[f"{CORE_CERT_BASE}/case-results",f"{CORE_CERT_BASE}/exchange-checks",f"{CORE_CERT_BASE}/trace-checks",f"{CORE_CERT_BASE}/reproduction-checks"]},{"step":6,"name":"record-evidence-findings","depends_on":["record-case-results-and-checks"],"endpoints":[f"{CORE_CERT_BASE}/evidence",f"{CORE_CERT_BASE}/findings"]},{"step":7,"name":"snapshot-suite","depends_on":["record-evidence-findings"],"endpoint":f"{CORE_CERT_BASE}/snapshots"}]
    return {"ok":True,"schema":"sc-lab-platform-core-v3-certification-submission-plan/0.112.0","context":ctx,"steps":plan,"automatic_submission":False,"automatic_product_invocation":False,"automatic_case_execution":False,"automatic_scientific_certification":False,"automatic_truth_determination":False,"plan_hash":_hash(plan)}

def manifest() -> dict[str, Any]:
    return {"ok":True,"status":"platform-core-integration-certification-ready","schema":BRIDGE_SCHEMA,"lab_release_version":LAB_VERSION,"minimum_core_release":MINIMUM_CORE_RELEASE,"product_ref":PRODUCT_REF,"core_contract":CORE_CERTIFICATION_CONTRACT,"core_certification_base":CORE_CERT_BASE,"certified_layer_count":len(LAYER_CATALOG),"conformance_case_count":len(CASE_CATALOG),"certification_scope":"platform_runtime_contract_conformance_only","boundaries":{"core_records_certification_evidence":True,"lab_constructs_conformance_plans":True,"automatic_core_submission":False,"core_invokes_lab_product":False,"core_executes_conformance_cases":False,"core_certifies_scientific_validity":False,"core_certifies_product_quality":False,"core_authorizes_product":False,"core_ranks_products":False,"core_infers_reproducibility":False,"core_resolves_failures":False,"core_determines_truth":False}}

def health() -> dict[str, Any]:
    m=manifest(); return {"ok":True,"status":m["status"],"schema":"sc-lab-platform-core-v3-integration-certification-health/0.112.0","lab_release_version":LAB_VERSION,"minimum_core_release":MINIMUM_CORE_RELEASE,"core_contract":CORE_CERTIFICATION_CONTRACT,"certified_layer_count":len(LAYER_CATALOG),"conformance_case_count":len(CASE_CATALOG),"automatic_core_submission":False,"automatic_product_invocation":False,"automatic_case_execution":False,"automatic_scientific_certification":False,"automatic_truth_determination":False,"serviceVersion":"1.0.0"}
