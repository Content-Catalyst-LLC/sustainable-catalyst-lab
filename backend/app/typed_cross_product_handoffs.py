from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

from .research_interoperability import InteroperabilityError, ResearchInteroperabilityLayer

VERSION = "0.38.1"
ADAPTER_SCHEMA = "sc-typed-research-adapter/0.38.1"
ROUTE_SCHEMA = "sc-typed-research-route/0.38.1"
PLAN_SCHEMA = "sc-typed-research-handoff-plan/0.38.1"
CATALOG_SCHEMA = "sc-typed-research-adapter-catalog/0.38.1"

CONTRACTS = {
    "dataset": "sc-research-dataset/1.0",
    "observation-set": "sc-research-observation-set/1.0",
    "workflow": "sc-research-workflow/1.0",
    "workflow-run": "sc-research-workflow-run/1.0",
    "experiment": "sc-research-experiment/1.0",
    "campaign": "sc-research-campaign/1.0",
    "model": "sc-research-model/1.0",
    "surrogate-model": "sc-research-surrogate-model/1.0",
    "artifact": "sc-research-artifact/1.0",
    "evidence-record": "sc-research-evidence/1.0",
    "citation-set": "sc-research-citation-set/1.0",
    "publication": "sc-research-publication/1.0",
    "reproducibility-package": "sc-research-reproducibility-package/1.0",
    "manuscript": "sc-research-manuscript/1.0",
    "decision-packet": "sc-decision-packet/1.0",
    "scenario": "sc-decision-scenario/1.0",
    "indicator-set": "sc-research-indicator-set/1.0",
    "research-brief": "sc-research-brief/1.0",
    "workspace-snapshot": "sc-research-workspace-snapshot/1.0",
}

ALL_TYPES = tuple(CONTRACTS)
BASE_CAPABILITIES = ("sha256-resources", "provenance", "workspace-governance", "typed-route-plan")

# Each adapter declares executable acceptance rules. The route planner does not
# call remote products; it prepares a canonical, validated envelope for the
# existing v0.38.0 governed exchange engine.
ADAPTERS: dict[str, dict[str, Any]] = {
    "sustainable-catalyst-lab": {
        "displayName": "Sustainable Catalyst Lab", "role": "scientific-compute-authority",
        "accepts": ALL_TYPES, "emits": ALL_TYPES, "binding": "lab-resource",
        "capabilities": ("scientific-compute", "experiments", "reproducibility", "artifacts"),
    },
    "decision-studio": {
        "displayName": "Decision Studio", "role": "decision-intelligence-authority",
        "accepts": ("dataset", "observation-set", "workflow-run", "experiment", "model", "evidence-record", "citation-set", "scenario", "indicator-set", "research-brief", "decision-packet", "workspace-snapshot"),
        "emits": ("decision-packet", "scenario", "research-brief", "evidence-record", "workspace-snapshot"),
        "binding": "decision-evidence-input", "capabilities": ("decision-packets", "scenarios", "evidence-linking"),
    },
    "catalyst-data": {
        "displayName": "Catalyst Data", "role": "data-authority",
        "accepts": ("dataset", "observation-set", "indicator-set", "evidence-record", "artifact"),
        "emits": ("dataset", "observation-set", "indicator-set", "evidence-record"),
        "binding": "dataset-record", "capabilities": ("dataset-registry", "observations", "quality-review"),
    },
    "catalyst-analytics-r": {
        "displayName": "Catalyst AnalyticsR", "role": "statistical-analysis-authority",
        "accepts": ("dataset", "observation-set", "indicator-set", "workflow", "workflow-run", "experiment", "model", "scenario"),
        "emits": ("workflow-run", "model", "artifact", "evidence-record", "research-brief", "scenario"),
        "binding": "analysis-input", "capabilities": ("statistical-analysis", "modeling", "uncertainty"),
    },
    "catalyst-canvas": {
        "displayName": "Catalyst Canvas", "role": "research-framing-authority",
        "accepts": ("evidence-record", "citation-set", "research-brief", "scenario", "workspace-snapshot", "dataset"),
        "emits": ("research-brief", "scenario", "evidence-record", "workspace-snapshot"),
        "binding": "canvas-evidence", "capabilities": ("personas", "journeys", "assumptions", "evidence-ledger"),
    },
    "sustainable-catalyst-workbench": {
        "displayName": "Sustainable Catalyst Workbench", "role": "interactive-compute-authority",
        "accepts": ("dataset", "observation-set", "workflow", "workflow-run", "experiment", "model", "surrogate-model", "artifact", "indicator-set"),
        "emits": ("workflow", "workflow-run", "experiment", "model", "artifact", "dataset", "evidence-record"),
        "binding": "workbench-session", "capabilities": ("symbolic-compute", "unit-aware-compute", "visualization"),
    },
    "site-intelligence": {
        "displayName": "Site Intelligence", "role": "public-intelligence-authority",
        "accepts": ("dataset", "observation-set", "indicator-set", "scenario", "research-brief", "evidence-record", "publication"),
        "emits": ("dataset", "observation-set", "indicator-set", "scenario", "research-brief", "evidence-record"),
        "binding": "intelligence-source", "capabilities": ("observatories", "geospatial-analysis", "monitoring"),
    },
    "knowledge-library": {
        "displayName": "Knowledge Library", "role": "institutional-knowledge-authority",
        "accepts": ("publication", "manuscript", "reproducibility-package", "artifact", "evidence-record", "citation-set", "research-brief", "dataset"),
        "emits": ("publication", "evidence-record", "citation-set", "research-brief", "dataset"),
        "binding": "library-source-record", "capabilities": ("citations", "collections", "source-discovery", "publication-preservation"),
    },
    "research-librarian": {
        "displayName": "Research Librarian", "role": "research-guidance-authority",
        "accepts": ("evidence-record", "citation-set", "research-brief", "publication", "dataset"),
        "emits": ("evidence-record", "citation-set", "research-brief"),
        "binding": "research-guidance-context", "capabilities": ("source-routing", "citation-guidance", "scope-control"),
    },
    "catalyst-finance": {
        "displayName": "Catalyst Finance", "role": "financial-decision-authority",
        "accepts": ("dataset", "indicator-set", "scenario", "decision-packet", "research-brief", "evidence-record"),
        "emits": ("dataset", "indicator-set", "scenario", "decision-packet", "research-brief", "evidence-record"),
        "binding": "financial-analysis-input", "capabilities": ("financial-modeling", "forecasting", "decision-support"),
    },
    "catalyst-grit": {
        "displayName": "Catalyst Grit", "role": "human-systems-resilience-authority",
        "accepts": ("dataset", "indicator-set", "scenario", "evidence-record", "research-brief"),
        "emits": ("dataset", "indicator-set", "scenario", "evidence-record", "research-brief"),
        "binding": "resilience-evidence-input", "capabilities": ("resilience-assessment", "human-systems", "scenario-analysis"),
    },
    "catalyst-narrative-risk": {
        "displayName": "Catalyst Narrative Risk", "role": "narrative-risk-authority",
        "accepts": ("evidence-record", "citation-set", "scenario", "research-brief", "publication", "dataset"),
        "emits": ("evidence-record", "citation-set", "scenario", "research-brief", "publication"),
        "binding": "narrative-evidence-input", "capabilities": ("claim-mapping", "narrative-analysis", "evidence-ledger"),
    },
    "global-impact-catalyst": {
        "displayName": "Global Impact Catalyst", "role": "impact-assessment-authority",
        "accepts": ("dataset", "indicator-set", "scenario", "evidence-record", "research-brief", "decision-packet"),
        "emits": ("dataset", "indicator-set", "scenario", "evidence-record", "research-brief", "decision-packet"),
        "binding": "impact-evidence-input", "capabilities": ("impact-assessment", "indicator-frameworks", "scenario-analysis"),
    },
}

ALIASES = {
    "lab": "sustainable-catalyst-lab", "workbench": "sustainable-catalyst-workbench",
    "analyticsr": "catalyst-analytics-r", "catalyst-analyticsr": "catalyst-analytics-r",
    "library": "knowledge-library", "decision-studio-platform": "decision-studio",
}


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _product(value: Any) -> str:
    product = str(value or "").strip().lower()
    product = ALIASES.get(product, product)
    if product not in ADAPTERS:
        raise InteroperabilityError(f"No typed cross-product adapter is registered for '{product or 'unknown'}'.", 404)
    return product


def _entity(value: Any) -> str:
    entity = str(value or "").strip().lower()
    if entity not in CONTRACTS:
        raise InteroperabilityError("The typed handoff entity type is not supported.")
    return entity


def _clean_resource(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InteroperabilityError("A resource object is required.")
    # The governed interoperability layer performs the authoritative safety,
    # size, identifier, and SHA-256 validation before a handoff is persisted.
    return copy.deepcopy(value)


def _adapter_record(product_id: str) -> dict[str, Any]:
    item = ADAPTERS[product_id]
    record = {
        "schema": ADAPTER_SCHEMA, "version": VERSION, "productId": product_id,
        "displayName": item["displayName"], "role": item["role"],
        "accepts": list(item["accepts"]), "emits": list(item["emits"]),
        "defaultBinding": item["binding"], "capabilities": list(item["capabilities"]),
        "contracts": {entity: CONTRACTS[entity] for entity in sorted(set(item["accepts"]) | set(item["emits"]))},
        "safety": {"remoteCallbacks": False, "arbitraryCode": False, "embeddedRestrictedData": False},
    }
    record["adapterHash"] = _hash(record)
    return record


def policies() -> dict[str, Any]:
    return {
        "ok": True, "schema": "sc-typed-cross-product-handoff-policy/0.38.1", "version": VERSION,
        "adapterCount": len(ADAPTERS), "routeMode": "deterministic-local-planning",
        "capabilities": {
            "executableAdapterRegistry": True, "productPairRoutePlanning": True,
            "contractInference": True, "targetBindingNormalization": True,
            "canonicalHandoffCreation": True, "profileAwareSealing": True,
            "dryRunValidation": True, "routePlanHashes": True,
            "remoteCallbacks": False, "arbitraryCode": False, "embeddedRestrictedData": False,
        },
    }


class TypedCrossProductHandoffs:
    def __init__(self, interoperability: ResearchInteroperabilityLayer):
        self.interoperability = interoperability

    def catalog(self, product_id: str = "") -> dict[str, Any]:
        if product_id:
            pid = _product(product_id)
            return {"ok": True, "adapter": _adapter_record(pid)}
        adapters = [_adapter_record(pid) for pid in sorted(ADAPTERS)]
        body = {"schema": CATALOG_SCHEMA, "version": VERSION, "adapters": adapters, "count": len(adapters)}
        body["catalogHash"] = _hash(body)
        return {"ok": True, **body}

    def route_catalog(self, source_product: str = "", target_product: str = "", entity_type: str = "") -> dict[str, Any]:
        source_ids = [_product(source_product)] if source_product else sorted(ADAPTERS)
        target_ids = [_product(target_product)] if target_product else sorted(ADAPTERS)
        entity_ids = [_entity(entity_type)] if entity_type else list(CONTRACTS)
        routes: list[dict[str, Any]] = []
        for source in source_ids:
            for target in target_ids:
                if source == target:
                    continue
                for entity in entity_ids:
                    if entity in ADAPTERS[source]["emits"] and entity in ADAPTERS[target]["accepts"]:
                        routes.append(self._route(source, target, entity))
        return {"ok": True, "schema": "sc-typed-research-route-catalog/0.38.1", "version": VERSION, "routes": routes, "count": len(routes)}

    def _route(self, source: str, target: str, entity: str) -> dict[str, Any]:
        target_adapter = ADAPTERS[target]
        route = {
            "schema": ROUTE_SCHEMA, "version": VERSION,
            "id": f"{source}--{entity}--{target}", "sourceProduct": source, "targetProduct": target,
            "entityType": entity, "contractVersion": CONTRACTS[entity],
            "targetBinding": target_adapter["binding"],
            "requiredCapabilities": list(BASE_CAPABILITIES),
            "targetCapabilities": list(target_adapter["capabilities"]),
            "mapping": {
                "resource.id": "resource.id", "resource.title": "resource.title",
                "resource.sha256": "resource.sha256", "resource.mediaType": "resource.mediaType",
                "resource.metadata": "resource.metadata", "provenance": "provenance",
            },
            "delivery": {"mode": "governed-envelope", "automaticRemoteDelivery": False, "requiresReceipt": True},
        }
        route["routeHash"] = _hash(route)
        return route

    def plan(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self.interoperability._workspace(workspace_id, actor_id, "viewer", True)
        body = copy.deepcopy(payload or {})
        source = _product(body.get("sourceProduct") or "sustainable-catalyst-lab")
        target = _product(body.get("targetProduct"))
        entity = _entity(body.get("entityType"))
        errors: list[str] = []
        warnings: list[str] = []
        if entity not in ADAPTERS[source]["emits"]:
            errors.append(f"{ADAPTERS[source]['displayName']} does not emit {entity} resources.")
        if entity not in ADAPTERS[target]["accepts"]:
            errors.append(f"{ADAPTERS[target]['displayName']} does not accept {entity} resources.")
        resource = _clean_resource(body.get("resource") or {})
        for required in ("id", "sha256"):
            if not resource.get(required): errors.append(f"resource.{required} is required.")
        if not resource.get("title"): warnings.append("resource.title is recommended for human review.")
        route = self._route(source, target, entity)
        contract = str(body.get("contractVersion") or route["contractVersion"]).strip().lower()
        if contract != route["contractVersion"]:
            errors.append(f"The adapter route requires contract {route['contractVersion']}.")
        metadata = copy.deepcopy(resource.get("metadata") or {})
        if not isinstance(metadata, dict): errors.append("resource.metadata must be an object.")
        else:
            metadata.update({
                "typedRouteId": route["id"], "typedRouteHash": route["routeHash"],
                "targetBinding": route["targetBinding"], "sourceProduct": source, "targetProduct": target,
            })
        normalized_resource = {**resource, "metadata": metadata}
        required_caps = sorted(set(route["requiredCapabilities"]) | {str(v).strip() for v in body.get("requiredCapabilities", []) if str(v).strip()})
        handoff = {
            "id": str(body.get("id") or "").strip(), "sourceProduct": source, "targetProduct": target,
            "entityType": entity, "contractVersion": route["contractVersion"],
            "resource": normalized_resource, "provenance": copy.deepcopy(body.get("provenance") or {}),
            "requiredCapabilities": required_caps,
            "externalId": str(body.get("externalId") or "").strip() or None,
        }
        if not handoff["id"]: errors.append("id is required.")
        plan = {
            "schema": PLAN_SCHEMA, "version": VERSION, "workspaceId": workspace_id,
            "valid": not errors, "errors": errors, "warnings": warnings,
            "route": route, "handoff": handoff,
            "sourceAdapterHash": _adapter_record(source)["adapterHash"],
            "targetAdapterHash": _adapter_record(target)["adapterHash"],
            "safety": {"remoteCallbacks": False, "arbitraryCode": False, "embeddedRestrictedData": False},
        }
        plan["planHash"] = _hash(plan)
        return {"ok": not errors, "plan": plan}

    def create(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        planned = self.plan(workspace_id, payload, actor_id)
        plan = planned["plan"]
        if not plan["valid"]:
            raise InteroperabilityError("Typed handoff validation failed: " + "; ".join(plan["errors"]), 422)
        source_profile = str((payload or {}).get("sourceProfileId") or "").strip()
        target_profile = str((payload or {}).get("targetProfileId") or "").strip()
        if (source_profile or target_profile) and not (source_profile and target_profile):
            raise InteroperabilityError("Both sourceProfileId and targetProfileId are required for profile-aware sealing.")
        result = self.interoperability.create_handoff(workspace_id, plan["handoff"], actor_id)
        response: dict[str, Any] = {"ok": True, "plan": plan, "handoff": result["handoff"]}
        if source_profile and target_profile:
            sealed = self.interoperability.seal_handoff(workspace_id, result["handoff"]["id"], {"sourceProfileId": source_profile, "targetProfileId": target_profile}, actor_id)
            response["handoff"] = sealed["handoff"]
            response["sealed"] = True
        else:
            response["sealed"] = False
        return response

    def health(self) -> dict[str, Any]:
        routes = self.route_catalog(source_product="sustainable-catalyst-lab")
        return {
            "ok": True, "status": "ready", "version": VERSION,
            "schema": "sc-typed-cross-product-handoff-health/0.38.1",
            "adapterCount": len(ADAPTERS), "labOutboundRouteCount": routes["count"],
            "catalogHash": self.catalog()["catalogHash"], "capabilities": policies()["capabilities"],
        }
