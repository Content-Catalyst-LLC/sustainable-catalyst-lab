from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_research_context_v01060 import normalize_research_context

LAB_VERSION = "0.110.0"
FEATURE_VERSION = "0.110.0"
MINIMUM_CORE_RELEASE = "3.0.0"
BRIDGE_SCHEMA = "sc-lab-platform-core-v3-reproducibility-scholarly-package/0.110.0"
PACKAGE_SCHEMA = "sc-lab-core-v3-research-package/0.110.0"
PLAN_SCHEMA = "sc-lab-core-v3-scholarly-interoperability-plan/0.110.0"
CORE_UNIFIED_RUNTIME_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
CORE_SCHOLARLY_CONTRACT = "sc.research.scholarly-interoperability-packaging.v1"
CORE_PACKAGE_BINDING_ENDPOINT = "/v1/research/unified-runtime/package-bindings"
CORE_SCHOLARLY_BASE_ENDPOINT = "/v1/research/scholarly-packages"

PACKAGE_TYPES = {
    "scholarly_publication", "research_compendium", "replication_package", "data_package",
    "notebook_package", "investigation_package", "mixed_research_package", "other",
}
PACKAGE_PROFILES = {
    "research-compendium", "ro-crate", "replication-package", "data-package",
    "notebook-package", "scholarly-publication", "investigation-package", "custom",
}
CITATION_FORMATS = {"csl-json", "bibtex", "ris", "citation-json", "plain-text"}
IDENTIFIER_SCHEMES = {"doi", "orcid", "ror", "ark", "handle", "isbn", "issn", "url", "urn", "accession", "internal"}
METADATA_STANDARDS = {"datacite", "crossref", "dublin-core", "schema.org", "codemeta", "ro-crate", "custom"}
EXPORT_FORMATS = {"zip", "json", "jsonld", "csv", "bibtex", "ris", "csl-json", "ro-crate", "pdf", "html", "custom"}


class PlatformCoreV3ScholarlyPackageError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 4000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise PlatformCoreV3ScholarlyPackageError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3ScholarlyPackageError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3ScholarlyPackageError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum: int = 5000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3ScholarlyPackageError(f"{label} must be an array.")
    if len(value) > maximum:
        raise PlatformCoreV3ScholarlyPackageError(f"{label} exceeds {maximum} entries.")
    return copy.deepcopy(value)


def _context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ScholarlyPackageError("A package bridge request object is required.")
    raw = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    try:
        return normalize_research_context(raw)["context"]
    except Exception as exc:
        raise PlatformCoreV3ScholarlyPackageError(f"Invalid research context: {exc}", getattr(exc, "status_code", 400)) from exc


def _visibility(context: dict[str, Any], value: Any = None) -> str:
    v = _text(value or context.get("core_visibility") or "internal", "visibility", 20)
    if v not in {"private", "internal", "public"}:
        raise PlatformCoreV3ScholarlyPackageError("visibility must be private, internal, or public.")
    return v


def _ref(item: Any, prefix: str = "lab:artifact") -> str:
    if isinstance(item, str):
        return _text(item, "object reference", 1200)
    if not isinstance(item, dict):
        raise PlatformCoreV3ScholarlyPackageError("Package members must be references or objects.")
    for key in ("object_ref", "objectRef", "resource_ref", "resourceRef", "dataset_ref", "datasetRef", "notebook_ref", "notebookRef", "publication_ref", "publicationRef", "ref"):
        if item.get(key):
            return _text(item[key], "object reference", 1200)
    ident = item.get("id") or item.get("key") or item.get("name")
    if ident:
        return f"{prefix}:{_text(ident, 'object id', 400)}"
    return f"{prefix}:sha256:{_hash(item)}"


def _package_kind(raw: dict[str, Any]) -> tuple[str, str, str]:
    schema = str(raw.get("schema") or "")
    explicit_type = str(raw.get("package_type") or raw.get("packageType") or "").strip()
    explicit_profile = str(raw.get("package_profile") or raw.get("packageProfile") or "").strip()
    if explicit_type:
        typ = explicit_type
    elif "research-publication" in schema or raw.get("publicationHash"):
        typ = "scholarly_publication"
    elif "reproducible" in schema or "reproducibility" in schema or raw.get("manifestSha256") or raw.get("packageHash"):
        typ = "replication_package"
    elif raw.get("notebooks") and not raw.get("datasets"):
        typ = "notebook_package"
    elif raw.get("datasets") and not raw.get("notebooks"):
        typ = "data_package"
    else:
        typ = "research_compendium"
    if typ not in PACKAGE_TYPES:
        raise PlatformCoreV3ScholarlyPackageError(f"Unsupported package_type: {typ}")
    if explicit_profile:
        profile = explicit_profile
    else:
        profile = {
            "scholarly_publication": "scholarly-publication", "replication_package": "replication-package",
            "data_package": "data-package", "notebook_package": "notebook-package",
            "investigation_package": "investigation-package",
        }.get(typ, "research-compendium")
    if profile not in PACKAGE_PROFILES:
        raise PlatformCoreV3ScholarlyPackageError(f"Unsupported package_profile: {profile}")
    family = "publication" if typ == "scholarly_publication" else "reproducibility-package" if typ == "replication_package" else "research-package"
    return typ, profile, family


def normalize_package(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("package") if isinstance(payload.get("package"), dict) else payload
    raw = _dict(raw, "package")
    typ, profile, family = _package_kind(raw)
    pid = _text(raw.get("id") or raw.get("package_key") or raw.get("packageKey"), "package id", 400, required=False)
    title = _text(raw.get("title") or raw.get("name") or typ.replace("_", " ").title(), "title", 1000)
    if not pid:
        pid = f"package-{_hash({'project':context['project_ref'],'title':title,'type':typ})[:20]}"
    package_ref = _text(raw.get("package_ref") or raw.get("packageRef"), "package_ref", 1200, required=False) or f"lab:{family}:{pid}"
    version_ref = raw.get("version_ref") or raw.get("versionRef") or raw.get("packageVersion") or raw.get("version")
    if version_ref is not None:
        version_ref = _text(version_ref, "version_ref", 300)
    content_hash = raw.get("content_hash") or raw.get("contentHash") or raw.get("packageHash") or raw.get("manifestSha256") or raw.get("publicationHash") or raw.get("assemblyHash")
    if content_hash:
        content_hash = _text(content_hash, "content_hash", 128)
    else:
        safe = {k: v for k, v in raw.items() if k not in {"content", "files", "bytes", "binary"}}
        content_hash = _hash(safe)
    member_items = _list(raw.get("member_refs") or raw.get("memberRefs") or raw.get("members") or raw.get("resources"), "members")
    member_refs=[]; seen=set()
    for item in member_items:
        ref=_ref(item)
        if ref not in seen:
            member_refs.append(ref); seen.add(ref)
    metadata = _dict(raw.get("metadata"), "metadata")
    provenance = _dict(raw.get("provenance"), "provenance")
    out = {
        "schema": PACKAGE_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "package_id": pid,
        "package_ref": package_ref,
        "package_type": typ,
        "package_profile": profile,
        "title": title,
        "description": _text(raw.get("description"), "description", 12000, required=False) or None,
        "version_ref": version_ref,
        "content_hash": content_hash,
        "member_refs": member_refs,
        "status": _text(raw.get("status") or "draft", "status", 80),
        "visibility": _visibility(context, raw.get("visibility")),
        "source_publication_ref": raw.get("source_publication_ref") or raw.get("sourcePublicationRef") or (package_ref if typ == "scholarly_publication" else None),
        "source_reproducible_package_ref": raw.get("source_reproducible_package_ref") or raw.get("sourceReproduciblePackageRef") or (package_ref if typ == "replication_package" else None),
        "lab_metadata": metadata,
        "lab_provenance": provenance,
        "citation_count": len(_list(raw.get("citations"), "citations")),
        "identifier_count": len(_list(raw.get("identifiers"), "identifiers")),
        "dataset_count": len(_list(raw.get("datasets"), "datasets")),
        "notebook_count": len(_list(raw.get("notebooks"), "notebooks")),
        "underlying_package_remains_authoritative_in_lab": True,
        "core_certifies_reproducibility": False,
        "core_publishes_package": False,
        "core_mints_identifiers": False,
    }
    out["package_hash"] = _hash(out)
    return {"ok": True, "context": context, "package": out}


def build_core_package_binding(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_package(payload)
    context = normalized["context"]; package = normalized["package"]
    data = {
        "session_id": context["session_id"],
        "package_ref": package["package_ref"],
        "package_type": package["package_type"],
        "version_ref": package["version_ref"],
        "content_hash": package["content_hash"],
        "member_refs": package["member_refs"],
        "visibility": "internal" if package["visibility"] == "private" else package["visibility"],
        "metadata": {
            "source_product_ref": PRODUCT_REF,
            "bridge_schema": BRIDGE_SCHEMA,
            "package_profile": package["package_profile"],
            "title": package["title"],
            "project_ref": context["project_ref"],
            "context_ref": context["context_ref"],
            "underlying_package_remains_authoritative_in_lab": True,
            "lab_package_hash": package["package_hash"],
        },
        "provenance": {
            "source_product_ref": PRODUCT_REF,
            "lab_provenance": package["lab_provenance"],
        },
    }
    return {
        "ok": True, "schema": BRIDGE_SCHEMA, "lab_release_version": LAB_VERSION,
        "core_contract": CORE_UNIFIED_RUNTIME_CONTRACT, "core_endpoint": CORE_PACKAGE_BINDING_ENDPOINT,
        "data": data, "request_body": {"data": data}, "automatic_submission": False,
        "automatic_core_mutation": False, "automatic_reproducibility_certification": False,
    }


def _scholarly_package_data(context: dict[str, Any], package: dict[str, Any], created_by: str = "operator") -> dict[str, Any]:
    return {
        "package_key": package["package_id"], "project_ref": context["project_ref"],
        "package_type": package["package_type"], "title": package["title"],
        "description": package["description"], "package_profile": package["package_profile"],
        "source_publication_ref": package["source_publication_ref"],
        "source_reproducible_package_ref": package["source_reproducible_package_ref"],
        "status": package["status"], "visibility": package["visibility"],
        "metadata": {"source_product_ref": PRODUCT_REF, "lab_package_ref": package["package_ref"], "lab_version_ref": package["version_ref"], "lab_content_hash": package["content_hash"], "lab_metadata": package["lab_metadata"]},
        "provenance": {"source_product_ref": PRODUCT_REF, "context_ref": context["context_ref"], "lab_provenance": package["lab_provenance"]},
        "created_by": created_by,
    }


def build_scholarly_package_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]
    data=_scholarly_package_data(context,package,_text(payload.get("created_by") or payload.get("createdBy") or context.get("researcher_ref") or "operator","created_by",400))
    return {"ok":True,"schema":PLAN_SCHEMA,"core_contract":CORE_SCHOLARLY_CONTRACT,"core_endpoint":f"{CORE_SCHOLARLY_BASE_ENDPOINT}/packages","data":data,"request_body":{"data":data},"automatic_submission":False,"interoperability_state_is_declared_not_certified":True}


def _package_id(payload: dict[str, Any]) -> tuple[str, bool]:
    pid = payload.get("core_package_id") or payload.get("corePackageId")
    return (_text(pid,"core_package_id",400),False) if pid else ("$CORE_PACKAGE_ID",True)


def bridge_citations(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]
    raw=payload.get("package") if isinstance(payload.get("package"),dict) else payload
    package_id,requires=_package_id(payload); rows=[]
    for i,item in enumerate(_list(raw.get("citations"),"citations")):
        if isinstance(item,str): item={"citation_text":item,"citation_format":"plain-text"}
        if not isinstance(item,dict): raise PlatformCoreV3ScholarlyPackageError("citation must be a string or object")
        fmt=str(item.get("citation_format") or item.get("citationFormat") or ("csl-json" if item.get("citation_data") or item.get("citationData") else "plain-text"))
        if fmt not in CITATION_FORMATS: raise PlatformCoreV3ScholarlyPackageError(f"Unsupported citation format: {fmt}")
        cited=_ref(item.get("cited_object_ref") or item.get("citedObjectRef") or item.get("source") or item, "lab:cited-object")
        key=str(item.get("citation_key") or item.get("citationKey") or f"citation-{_hash({'package':package['package_id'],'i':i,'cited':cited})[:20]}")
        data={"citation_key":key,"package_id":package_id,"project_ref":context["project_ref"],"cited_object_ref":cited,"citation_format":fmt,"locator":item.get("locator"),"citation_text":item.get("citation_text") or item.get("citationText"),"citation_data":item.get("citation_data") or item.get("citationData") or {},"visibility":package["visibility"],"provenance":{"source_product_ref":PRODUCT_REF,"context_ref":context["context_ref"]}}
        rows.append({"endpoint":f"{CORE_SCHOLARLY_BASE_ENDPOINT}/citations","data":data,"request_body":{"data":data}})
    return {"ok":True,"schema":PLAN_SCHEMA,"count":len(rows),"operations":rows,"requires_core_package_id":requires,"automatic_submission":False,"core_resolves_citations":False}


def bridge_datasets_notebooks(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]
    raw=payload.get("package") if isinstance(payload.get("package"),dict) else payload; package_id,requires=_package_id(payload); ops=[]
    for kind,endpoint in (("datasets","datasets"),("notebooks","notebooks")):
        for i,item in enumerate(_list(raw.get(kind),kind)):
            item={"ref":item} if isinstance(item,str) else _dict(item,kind[:-1])
            ref=_ref(item,"lab:dataset" if kind=="datasets" else "lab:notebook")
            key=str(item.get("key") or item.get("id") or f"{kind[:-1]}-{_hash({'package':package['package_id'],'ref':ref})[:20]}")
            if kind=="datasets":
                data={"dataset_key":key,"package_id":package_id,"project_ref":context["project_ref"],"dataset_ref":ref,"version_ref":item.get("version_ref") or item.get("versionRef"),"content_hash":item.get("content_hash") or item.get("contentHash"),"media_type":item.get("media_type") or item.get("mediaType"),"schema_ref":item.get("schema_ref") or item.get("schemaRef"),"license_ref":item.get("license_ref") or item.get("licenseRef"),"metadata":item.get("metadata") or {},"visibility":package["visibility"]}
            else:
                data={"notebook_key":key,"package_id":package_id,"project_ref":context["project_ref"],"notebook_ref":ref,"notebook_format":item.get("notebook_format") or item.get("notebookFormat") or "ipynb","version_ref":item.get("version_ref") or item.get("versionRef"),"content_hash":item.get("content_hash") or item.get("contentHash"),"environment_ref":item.get("environment_ref") or item.get("environmentRef"),"execution_ref":item.get("execution_ref") or item.get("executionRef"),"metadata":item.get("metadata") or {},"visibility":package["visibility"]}
            ops.append({"endpoint":f"{CORE_SCHOLARLY_BASE_ENDPOINT}/{endpoint}","data":data,"request_body":{"data":data}})
    return {"ok":True,"schema":PLAN_SCHEMA,"count":len(ops),"operations":ops,"requires_core_package_id":requires,"automatic_submission":False,"core_transforms_datasets":False,"core_executes_notebooks":False}


def build_provenance_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]; package_id,requires=_package_id(payload)
    bindings=[{"object_ref":r,"role":"package-member"} for r in package["member_refs"]]
    raw=payload.get("package") if isinstance(payload.get("package"),dict) else payload
    if raw.get("provenanceBindings"): bindings=_list(raw.get("provenanceBindings"),"provenanceBindings")
    standard=str(payload.get("standard") or raw.get("provenanceStandard") or "ro-crate")
    data={"manifest_key":f"manifest-{_hash({'package':package['package_ref'],'bindings':bindings})[:20]}","package_id":package_id,"project_ref":context["project_ref"],"standard":standard,"standard_version":payload.get("standard_version") or payload.get("standardVersion"),"bindings":bindings,"visibility":package["visibility"],"provenance":{"source_product_ref":PRODUCT_REF,"context_ref":context["context_ref"],"lab_package_hash":package["package_hash"]}}
    return {"ok":True,"schema":PLAN_SCHEMA,"core_endpoint":f"{CORE_SCHOLARLY_BASE_ENDPOINT}/provenance-manifests","data":data,"request_body":{"data":data},"requires_core_package_id":requires,"automatic_submission":False,"lineage_is_declared_not_inferred":True}


def build_publication_binding(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]; package_id,requires=_package_id(payload)
    raw=payload.get("publication") if isinstance(payload.get("publication"),dict) else payload.get("package") if isinstance(payload.get("package"),dict) else payload
    publication_ref=_text(raw.get("publication_ref") or raw.get("publicationRef") or (package["package_ref"] if package["package_type"]=="scholarly_publication" else None),"publication_ref",1200)
    object_ref=_text(raw.get("object_ref") or raw.get("objectRef") or publication_ref,"object_ref",1200)
    data={"binding_key":str(raw.get("binding_key") or raw.get("bindingKey") or f"publication-binding-{_hash({'package':package['package_ref'],'object':object_ref})[:20]}"),"package_id":package_id,"project_ref":context["project_ref"],"publication_ref":publication_ref,"object_type":str(raw.get("object_type") or raw.get("objectType") or "publication"),"object_ref":object_ref,"object_version_ref":raw.get("object_version_ref") or raw.get("objectVersionRef") or package["version_ref"],"role":str(raw.get("role") or "primary"),"visibility":package["visibility"],"provenance":{"source_product_ref":PRODUCT_REF,"context_ref":context["context_ref"]}}
    return {"ok":True,"schema":PLAN_SCHEMA,"core_endpoint":f"{CORE_SCHOLARLY_BASE_ENDPOINT}/publication-bindings","data":data,"request_body":{"data":data},"requires_core_package_id":requires,"automatic_submission":False,"automatic_publication":False}


def build_validation_record(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]; package_id,requires=_package_id(payload)
    raw=_dict(payload.get("validation"),"validation") if payload.get("validation") is not None else {}
    validator_ref=_text(raw.get("validator_ref") or raw.get("validatorRef") or context.get("researcher_ref") or "lab:validator:declared","validator_ref",1200)
    vtype=_text(raw.get("validation_type") or raw.get("validationType") or "manifest-integrity","validation_type",120)
    data={"validation_key":str(raw.get("validation_key") or raw.get("validationKey") or f"validation-{_hash({'package':package['package_ref'],'type':vtype,'validator':validator_ref})[:20]}"),"package_id":package_id,"project_ref":context["project_ref"],"validator_ref":validator_ref,"validation_type":vtype,"status":str(raw.get("status") or "recorded"),"evidence":_list(raw.get("evidence"),"validation evidence"),"report_ref":raw.get("report_ref") or raw.get("reportRef"),"visibility":package["visibility"],"provenance":{"source_product_ref":PRODUCT_REF,"context_ref":context["context_ref"],"declared_not_certified":True}}
    return {"ok":True,"schema":PLAN_SCHEMA,"core_endpoint":f"{CORE_SCHOLARLY_BASE_ENDPOINT}/validations","data":data,"request_body":{"data":data},"requires_core_package_id":requires,"automatic_submission":False,"core_certifies_reproducibility":False,"core_validates_scientific_content":False}


def build_scholarly_interoperability_plan(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_package(payload); context=normalized["context"]; package=normalized["package"]
    package_op=build_scholarly_package_envelope(payload)
    citations=bridge_citations(payload); descriptors=bridge_datasets_notebooks(payload); provenance=build_provenance_manifest(payload)
    ops=[{"name":"create-package","endpoint":package_op["core_endpoint"],"data":package_op["data"],"request_body":package_op["request_body"]}]
    ops.extend({"name":"citation","endpoint":x["endpoint"],"data":x["data"],"request_body":x["request_body"]} for x in citations["operations"])
    ops.extend({"name":"descriptor","endpoint":x["endpoint"],"data":x["data"],"request_body":x["request_body"]} for x in descriptors["operations"])
    ops.append({"name":"provenance-manifest","endpoint":provenance["core_endpoint"],"data":provenance["data"],"request_body":provenance["request_body"]})
    raw=payload.get("package") if isinstance(payload.get("package"),dict) else payload
    if package["package_type"]=="scholarly_publication" or raw.get("publication_ref") or raw.get("publicationRef"):
        pub=build_publication_binding(payload); ops.append({"name":"publication-binding","endpoint":pub["core_endpoint"],"data":pub["data"],"request_body":pub["request_body"]})
    return {"ok":True,"schema":PLAN_SCHEMA,"lab_release_version":LAB_VERSION,"core_contract":CORE_SCHOLARLY_CONTRACT,"project_ref":context["project_ref"],"package_ref":package["package_ref"],"operation_count":len(ops),"operations":ops,"execution_order":["create-package","then operations containing $CORE_PACKAGE_ID"],"requires_core_package_id_after_create":len(ops)>1,"automatic_submission":False,"automatic_publication":False,"automatic_identifier_minting":False,"automatic_reproducibility_certification":False}


def map_legacy_package(payload: dict[str, Any]) -> dict[str, Any]:
    context=_context(payload)
    raw=payload.get("package") if isinstance(payload.get("package"),dict) else payload.get("legacy_package") if isinstance(payload.get("legacy_package"),dict) else payload
    schema=str(raw.get("schema") or "")
    supported=("sc-lab-reproducibility-package/0.37.0","sc-lab-reproducible-model-package/0.50.0","sc-lab-reproducibility-bundle/0.28.2","sc-lab-research-publication/0.37.0","sc-lab-research-assembly/0.37.1")
    if schema not in supported and not any(token in schema for token in ("reproduc", "publication", "assembly")):
        raise PlatformCoreV3ScholarlyPackageError("Unsupported legacy Lab package/publication schema.")
    wrapped={"context":context,"package":raw}
    return {"ok":True,"schema":BRIDGE_SCHEMA,"legacy_schema":schema,"normalized":normalize_package(wrapped)["package"],"core_package_binding":build_core_package_binding(wrapped),"scholarly_plan":build_scholarly_interoperability_plan(wrapped),"automatic_submission":False,"automatic_execution":False,"automatic_publication":False,"automatic_certification":False}


def manifest() -> dict[str, Any]:
    return {"ok":True,"status":"reproducibility-scholarly-package-bridge-ready","schema":BRIDGE_SCHEMA,"lab_release_version":LAB_VERSION,"minimum_core_release":MINIMUM_CORE_RELEASE,"product_ref":PRODUCT_REF,"core_unified_runtime_contract":CORE_UNIFIED_RUNTIME_CONTRACT,"core_scholarly_contract":CORE_SCHOLARLY_CONTRACT,"core_package_binding_endpoint":CORE_PACKAGE_BINDING_ENDPOINT,"core_scholarly_base_endpoint":CORE_SCHOLARLY_BASE_ENDPOINT,"supported_package_types":sorted(PACKAGE_TYPES),"supported_package_profiles":sorted(PACKAGE_PROFILES),"boundaries":{"lab_is_underlying_package_authority":True,"core_records_package_refs_and_interoperability_metadata":True,"automatic_core_submission":False,"automatic_core_mutation":False,"core_mints_identifiers":False,"core_publishes_packages":False,"core_resolves_citations":False,"core_executes_notebooks":False,"core_transforms_datasets":False,"core_certifies_reproducibility":False,"core_validates_scientific_content":False,"core_infers_authorship":False,"core_determines_truth":False},"scientific_investigation_runtime_integration_deferred_to":"0.111.0"}


def health() -> dict[str, Any]:
    m=manifest()
    return {"ok":True,"status":m["status"],"schema":"sc-lab-platform-core-v3-reproducibility-scholarly-package-health/0.110.0","lab_release_version":LAB_VERSION,"minimum_core_release":MINIMUM_CORE_RELEASE,"product_ref":PRODUCT_REF,"core_package_binding_endpoint":CORE_PACKAGE_BINDING_ENDPOINT,"core_scholarly_contract":CORE_SCHOLARLY_CONTRACT,"automatic_core_submission":False,"automatic_publication":False,"automatic_reproducibility_certification":False,"package_type_count":len(PACKAGE_TYPES),"package_profile_count":len(PACKAGE_PROFILES)}
