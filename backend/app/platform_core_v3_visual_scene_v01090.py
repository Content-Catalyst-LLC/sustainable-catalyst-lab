from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_research_context_v01060 import normalize_research_context
from .scientific_scene_v0770 import normalize_scene as normalize_scene_v0770
from .advanced_scientific_scene_v0880 import normalize_scene as normalize_scene_v0880, scene_descriptor as advanced_scene_descriptor
from .linked_views_v0790 import normalize_composition
from .uncertainty_ensemble_distribution_v0820 import normalize_layer as normalize_uncertainty_layer
from .gpu_renderer_architecture_v0840 import renderer_registry as lab_renderer_registry, negotiate_renderer as lab_negotiate_renderer
from .webgpu_scientific_renderer_v0870 import renderer_descriptor as webgpu_renderer_descriptor

LAB_VERSION = "0.109.0"
FEATURE_VERSION = "0.109.0"
MINIMUM_CORE_RELEASE = "3.0.0"
BRIDGE_SCHEMA = "sc-lab-platform-core-v3-visual-reasoning-scientific-scene/0.109.0"
VISUAL_SCHEMA = "sc-lab-core-v3-visual-binding/0.109.0"
SCENE_BRIDGE_SCHEMA = "sc-lab-core-v3-scientific-scene-bridge/0.109.0"
LINKED_VIEW_SCHEMA = "sc-lab-core-v3-linked-view-bridge/0.109.0"
UNCERTAINTY_VISUAL_SCHEMA = "sc-lab-core-v3-uncertainty-visual-bridge/0.109.0"
CORE_UNIFIED_RUNTIME_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
CORE_VISUAL_SCENE_CONTRACT = "sc.visual-runtime.scene.v1"
CORE_UNIFIED_VISUAL_REASONING_CONTRACT = "sc.visual-runtime.unified-reasoning.v1"
CORE_CROSS_PRODUCT_VISUAL_CONTRACT = "sc.visual-runtime.cross-product-integration.v1"
CORE_VISUAL_BINDING_ENDPOINT = "/v1/research/unified-runtime/visual-bindings"

VISUAL_TYPES = {
    "scientific-scene", "scientific-figure", "linked-views", "uncertainty-view",
    "visualization", "renderer-plan", "scientific-dashboard", "visual-explanation",
}


class PlatformCoreV3VisualSceneError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 2000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise PlatformCoreV3VisualSceneError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3VisualSceneError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3VisualSceneError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum: int = 2000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3VisualSceneError(f"{label} must be an array.")
    if len(value) > maximum:
        raise PlatformCoreV3VisualSceneError(f"{label} exceeds {maximum} entries.")
    return copy.deepcopy(value)


def _refs(value: Any, label: str = "source_refs", maximum: int = 2000) -> list[str]:
    items = _list(value, label, maximum)
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        ref = item
        if isinstance(item, dict):
            ref = item.get("object_ref") or item.get("objectRef") or item.get("source_ref") or item.get("sourceRef") or item.get("ref") or item.get("id")
        text = _text(ref, label, 1200)
        if text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3VisualSceneError("A bridge request object is required.")
    raw = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    try:
        return normalize_research_context(raw)["context"]
    except Exception as exc:
        raise PlatformCoreV3VisualSceneError(f"Invalid research context: {exc}", getattr(exc, "status_code", 400)) from exc


def _visibility(context: dict[str, Any], value: Any = None) -> str:
    v = _text(value or context.get("core_visibility") or "internal", "visibility", 20)
    if v not in {"private", "internal", "public"}:
        raise PlatformCoreV3VisualSceneError("visibility must be private, internal, or public.")
    return "internal" if v == "private" else v


def _scene_kind(scene: dict[str, Any]) -> str:
    schema = str(scene.get("schema") or "")
    if schema.startswith("sc-lab-advanced-scientific-scene/") or "nodes" in scene:
        return "advanced-scene"
    if schema.startswith("sc-lab-scientific-scene/") or "objects" in scene:
        return "scientific-scene"
    if scene.get("contract") == CORE_VISUAL_SCENE_CONTRACT:
        return "core-scene"
    raise PlatformCoreV3VisualSceneError("scene must be a Lab v0.77/v0.88 scientific scene or a Core scene contract.")


def normalize_visual(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("visual") if isinstance(payload.get("visual"), dict) else payload
    visual_type = _text(raw.get("visual_type") or raw.get("visualType") or raw.get("type") or "visualization", "visual_type", 80)
    if visual_type not in VISUAL_TYPES:
        raise PlatformCoreV3VisualSceneError(f"Unsupported visual_type: {visual_type}")
    raw_id = _text(raw.get("id") or raw.get("visual_id") or raw.get("visualId"), "visual id", 240, required=False)
    title = _text(raw.get("title") or visual_type.replace("-", " ").title(), "visual title", 600)
    scene_ref = _text(raw.get("scene_ref") or raw.get("sceneRef"), "scene_ref", 1200, required=False) or None
    view_ref = _text(raw.get("view_ref") or raw.get("viewRef"), "view_ref", 1200, required=False) or None
    source_refs = _refs(raw.get("source_refs") or raw.get("sourceRefs"), "source_refs")
    renderer = _text(raw.get("renderer") or raw.get("renderer_id") or raw.get("rendererId"), "renderer", 160, required=False) or None
    renderer_version = _text(raw.get("renderer_version") or raw.get("rendererVersion"), "renderer_version", 80, required=False) or None
    metadata = _dict(raw.get("metadata"), "metadata")
    provenance = _dict(raw.get("provenance"), "provenance")
    key_material = {"project": context["project_ref"], "type": visual_type, "title": title, "scene_ref": scene_ref, "view_ref": view_ref, "source_refs": source_refs}
    visual_id = raw_id or f"visual-{_hash(key_material)[:20]}"
    visual_ref = _text(raw.get("visual_ref") or raw.get("visualRef"), "visual_ref", 1200, required=False) or f"lab:visual:{visual_id}"
    out = {
        "schema": VISUAL_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "visual_id": visual_id,
        "visual_ref": visual_ref,
        "visual_type": visual_type,
        "title": title,
        "scene_ref": scene_ref,
        "view_ref": view_ref,
        "source_refs": source_refs,
        "renderer": renderer,
        "renderer_version": renderer_version,
        "metadata": metadata,
        "provenance": provenance,
        "underlying_visual_remains_authoritative_in_lab": True,
        "core_renders_visual": False,
        "core_infers_truth_from_visual": False,
    }
    out["visual_hash"] = _hash(out)
    return {"ok": True, "context": context, "visual": out}


def normalize_scene(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("scene") if isinstance(payload.get("scene"), dict) else payload
    kind = _scene_kind(raw)
    try:
        if kind == "advanced-scene":
            scene = normalize_scene_v0880(raw)
        elif kind == "scientific-scene":
            scene = normalize_scene_v0770(raw)
        else:
            required = ("scene", "layers", "nodes", "edges", "views", "bindings")
            missing = [k for k in required if k not in raw]
            if missing:
                raise PlatformCoreV3VisualSceneError("Core scene contract missing: " + ", ".join(missing))
            scene = copy.deepcopy(raw)
    except PlatformCoreV3VisualSceneError:
        raise
    except Exception as exc:
        raise PlatformCoreV3VisualSceneError(f"Invalid scientific scene: {exc}", getattr(exc, "status_code", 422)) from exc
    scene_id = _text(scene.get("id") or (scene.get("scene") or {}).get("id") or f"scene-{_hash(scene)[:20]}", "scene id", 240)
    scene_ref = f"lab:scientific-scene:{scene_id}"
    out = {
        "schema": SCENE_BRIDGE_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "scene_kind": kind,
        "scene_ref": scene_ref,
        "core_scene_contract": CORE_VISUAL_SCENE_CONTRACT,
        "lab_scene": scene,
        "renderer_preference": scene.get("rendererPreference") or scene.get("renderer"),
        "scene_fingerprint": scene.get("fingerprint") or _hash(scene),
        "underlying_scene_remains_authoritative_in_lab": True,
        "core_performs_layout": False,
        "core_renders_scene": False,
        "core_performs_gpu_work": False,
    }
    out["bridge_hash"] = _hash({k: v for k, v in out.items() if k != "lab_scene"})
    return {"ok": True, "context": context, "scene": out}


def build_core_scene_contract(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_scene(payload)
    context = normalized["context"]
    bridge = normalized["scene"]
    scene = bridge["lab_scene"]
    kind = bridge["scene_kind"]
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    views: list[dict[str, Any]] = []
    layers = [{"id": "scientific-content", "title": "Scientific content", "visible": True, "source_product": PRODUCT_REF}]
    if kind == "advanced-scene":
        for node in scene.get("nodes", []):
            nid = str(node.get("id"))
            source_ref = str(node.get("sourceObjectId") or nid)
            nodes.append({"id": nid, "kind": node.get("type"), "label": node.get("name"), "layer_id": "scientific-content", "source_ref": source_ref, "visible": node.get("visible") is not False, "metadata": {"transform": node.get("transform"), "geometry": node.get("geometry"), "material_id": node.get("materialId")}})
            bindings.append({"binding_key": f"node:{nid}", "node_id": nid, "source_product": PRODUCT_REF, "source_ref": source_ref, "provenance": node.get("provenance") or {}})
            for child in node.get("children", []):
                edges.append({"id": f"contains:{nid}:{child}", "source": nid, "target": child, "relation": "contains", "declared_not_inferred": True})
        for camera in scene.get("cameras", []):
            views.append({"id": str(camera.get("id")), "kind": "camera", "state": camera})
    elif kind == "scientific-scene":
        for obj in scene.get("objects", []):
            nid = str(obj.get("id"))
            nodes.append({"id": nid, "kind": obj.get("type"), "label": obj.get("title"), "layer_id": "scientific-content", "source_ref": nid, "visible": obj.get("visible") is not False, "metadata": {"style": obj.get("style"), "opacity": obj.get("opacity")}})
            bindings.append({"binding_key": f"object:{nid}", "node_id": nid, "source_product": PRODUCT_REF, "source_ref": nid, "provenance": obj.get("provenance") or {}})
        views.append({"id": "camera:primary", "kind": "camera", "state": scene.get("camera") or {}})
    else:
        contract = copy.deepcopy(scene)
        contract.setdefault("contract", CORE_VISUAL_SCENE_CONTRACT)
        return {"ok": True, "context": context, "scene_bridge": bridge, "core_scene": contract, "automatic_submission": False, "automatic_rendering": False}
    core_scene = {
        "contract": CORE_VISUAL_SCENE_CONTRACT,
        "scene": {"id": bridge["scene_ref"], "project_ref": context["project_ref"], "source_product": PRODUCT_REF, "title": scene.get("title") or scene.get("id") or "Lab scientific scene", "source_fingerprint": bridge["scene_fingerprint"]},
        "layers": layers,
        "nodes": nodes,
        "edges": edges,
        "annotations": [],
        "views": views,
        "bindings": bindings,
        "snapshots": [],
        "boundaries": {"renderer_neutral": True, "layout_computed_by_core": False, "rendered_by_core": False, "gpu_work_by_core": False, "scientific_semantics_inferred_by_core": False, "underlying_scene_authoritative_in_lab": True},
    }
    core_scene["scene_hash"] = _hash(core_scene)
    return {"ok": True, "context": context, "scene_bridge": bridge, "core_scene": core_scene, "automatic_submission": False, "automatic_rendering": False}


def build_core_visual_binding(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    visual_payload = payload.get("visual") if isinstance(payload.get("visual"), dict) else payload
    normalized = normalize_visual({"context": context, "visual": visual_payload})["visual"]
    data = {
        "session_id": _text(context.get("session_id"), "session_id", 240),
        "visual_ref": normalized["visual_ref"],
        "visual_type": normalized["visual_type"],
        "scene_ref": normalized["scene_ref"],
        "view_ref": normalized["view_ref"],
        "source_refs": normalized["source_refs"],
        "visibility": _visibility(context, payload.get("visibility")),
        "metadata": {
            "schema": VISUAL_SCHEMA,
            "lab_release_version": LAB_VERSION,
            "product_ref": PRODUCT_REF,
            "title": normalized["title"],
            "renderer": normalized["renderer"],
            "renderer_version": normalized["renderer_version"],
            "visual_hash": normalized["visual_hash"],
            "lab_metadata": normalized["metadata"],
            "lab_provenance": normalized["provenance"],
            "underlying_visual_remains_authoritative_in_lab": True,
            "core_renders_visual": False,
            "core_infers_truth_from_visual": False,
        },
    }
    return {
        "ok": True,
        "schema": BRIDGE_SCHEMA,
        "target_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "target_endpoint": CORE_VISUAL_BINDING_ENDPOINT,
        "method": "POST",
        "data": data,
        "request_body": {"data": data},
        "automatic_submission": False,
        "automatic_core_mutation": False,
        "automatic_rendering": False,
    }


def bridge_linked_views(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("composition") if isinstance(payload.get("composition"), dict) else payload.get("linked_views") if isinstance(payload.get("linked_views"), dict) else payload
    try:
        composition = normalize_composition(raw)
    except Exception as exc:
        raise PlatformCoreV3VisualSceneError(f"Invalid linked-view composition: {exc}", getattr(exc, "status_code", 422)) from exc
    cid = _text(payload.get("id") or composition.get("title") or f"linked-{composition['fingerprint'][:16]}", "linked view id", 240)
    view_ref = f"lab:linked-views:{_hash({'id': cid, 'fingerprint': composition['fingerprint']})[:24]}"
    source_refs = _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs")
    visual = {
        "id": cid,
        "visual_type": "linked-views",
        "title": composition.get("title") or "Linked scientific views",
        "view_ref": view_ref,
        "source_refs": source_refs,
        "renderer": "mixed",
        "metadata": {"composition_fingerprint": composition.get("fingerprint"), "view_count": len(composition.get("views", [])), "link_count": len(composition.get("links", []))},
        "provenance": composition.get("provenance") or {},
    }
    binding = build_core_visual_binding({"context": context, "visual": visual, "visibility": payload.get("visibility")})
    return {"ok": True, "schema": LINKED_VIEW_SCHEMA, "context": context, "composition": composition, "view_ref": view_ref, "core_visual_binding": binding, "automatic_link_inference": False, "automatic_submission": False}


def bridge_uncertainty_visual(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    raw = payload.get("uncertainty_layer") if isinstance(payload.get("uncertainty_layer"), dict) else payload.get("layer") if isinstance(payload.get("layer"), dict) else payload
    try:
        layer = normalize_uncertainty_layer(raw)
    except Exception as exc:
        raise PlatformCoreV3VisualSceneError(f"Invalid uncertainty visualization layer: {exc}", getattr(exc, "status_code", 422)) from exc
    source_refs = _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs")
    view_ref = f"lab:uncertainty-view:{layer['id']}"
    visual = {
        "id": layer["id"],
        "visual_type": "uncertainty-view",
        "title": layer.get("title") or "Uncertainty visualization",
        "view_ref": view_ref,
        "source_refs": source_refs,
        "metadata": {"layer_fingerprint": layer.get("fingerprint"), "uncertainty_series_count": len(layer.get("uncertaintySeries", [])), "distribution_count": len(layer.get("distributions", [])), "ensemble_count": len(layer.get("ensembles", [])), "automatic_uncertainty_inference": False},
        "provenance": layer.get("provenance") or {},
    }
    binding = build_core_visual_binding({"context": context, "visual": visual, "visibility": payload.get("visibility")})
    return {"ok": True, "schema": UNCERTAINTY_VISUAL_SCHEMA, "context": context, "layer": layer, "view_ref": view_ref, "core_visual_binding": binding, "automatic_uncertainty_inference": False, "automatic_submission": False}


def renderer_catalog() -> dict[str, Any]:
    registry = lab_renderer_registry()
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-renderer-catalog/0.109.0",
        "lab_release_version": LAB_VERSION,
        "registry": registry,
        "advanced_scene": advanced_scene_descriptor(),
        "webgpu": webgpu_renderer_descriptor(),
        "core_visual_contracts": [CORE_VISUAL_SCENE_CONTRACT, CORE_UNIFIED_VISUAL_REASONING_CONTRACT, CORE_CROSS_PRODUCT_VISUAL_CONTRACT],
        "renderer_selection_authority": "sustainable-catalyst-lab/browser-runtime",
        "core_selects_renderer_automatically": False,
        "core_renders_visuals": False,
    }


def negotiate_renderer(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        decision = lab_negotiate_renderer(payload.get("renderer_request") if isinstance(payload.get("renderer_request"), dict) else payload)
    except Exception as exc:
        raise PlatformCoreV3VisualSceneError(f"Renderer negotiation failed: {exc}", getattr(exc, "status_code", 409)) from exc
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-renderer-negotiation/0.109.0",
        "lab_release_version": LAB_VERSION,
        "decision": decision,
        "decision_is_lab_browser_runtime_advisory": True,
        "core_renderer_selection": False,
        "automatic_scientific_semantics_change": False,
    }


def map_legacy_scene(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    scene_result = build_core_scene_contract({"context": context, "scene": payload.get("scene") if isinstance(payload.get("scene"), dict) else payload})
    bridge = scene_result["scene_bridge"]
    raw_scene = bridge["lab_scene"]
    source_refs: list[str] = []
    if bridge["scene_kind"] == "advanced-scene":
        source_refs = [str(n.get("sourceObjectId")) for n in raw_scene.get("nodes", []) if n.get("sourceObjectId")]
    elif bridge["scene_kind"] == "scientific-scene":
        source_refs = [f"lab:scene-object:{o.get('id')}" for o in raw_scene.get("objects", []) if o.get("id")]
    visual = {
        "id": raw_scene.get("id") or bridge["scene_ref"].split(":")[-1],
        "visual_type": "scientific-scene",
        "title": raw_scene.get("title") or "Scientific scene",
        "scene_ref": bridge["scene_ref"],
        "source_refs": source_refs,
        "renderer": raw_scene.get("rendererPreference") or raw_scene.get("renderer"),
        "renderer_version": raw_scene.get("rendererVersion") or raw_scene.get("engineVersion"),
        "metadata": {"scene_kind": bridge["scene_kind"], "scene_fingerprint": bridge["scene_fingerprint"], "core_scene_hash": scene_result["core_scene"].get("scene_hash")},
        "provenance": raw_scene.get("provenance") or {},
    }
    binding = build_core_visual_binding({"context": context, "visual": visual, "visibility": payload.get("visibility")})
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-legacy-scene-map/0.109.0",
        "context": context,
        "scene_bridge": bridge,
        "core_scene": scene_result["core_scene"],
        "core_visual_binding": binding,
        "automatic_submission": False,
        "automatic_rendering": False,
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "visual-reasoning-scientific-scene-bridge-ready",
        "schema": BRIDGE_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "core_unified_runtime_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "core_visual_scene_contract": CORE_VISUAL_SCENE_CONTRACT,
        "core_unified_visual_reasoning_contract": CORE_UNIFIED_VISUAL_REASONING_CONTRACT,
        "core_cross_product_visual_contract": CORE_CROSS_PRODUCT_VISUAL_CONTRACT,
        "core_visual_binding_endpoint": CORE_VISUAL_BINDING_ENDPOINT,
        "capabilities": ["scientific-scene-bridge", "visual-binding", "linked-views", "uncertainty-visualization", "renderer-catalog", "renderer-negotiation", "webgl2", "webgpu", "3d-scene", "4d-time-parameter-views"],
        "boundaries": {
            "lab_is_scientific_rendering_authority": True,
            "underlying_visuals_remain_authoritative_in_lab": True,
            "core_is_renderer_neutral": True,
            "core_renders_visuals": False,
            "core_performs_gpu_work": False,
            "core_infers_scientific_semantics_from_visual_form": False,
            "bridge_auto_submits_to_core": False,
            "bridge_auto_mutates_core": False,
            "bridge_auto_infers_uncertainty": False,
            "bridge_auto_infers_links": False,
        },
    }


def health() -> dict[str, Any]:
    m = manifest()
    return {
        "ok": True,
        "status": m["status"],
        "schema": "sc-lab-platform-core-v3-visual-scene-health/0.109.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "core_visual_scene_contract": CORE_VISUAL_SCENE_CONTRACT,
        "core_visual_binding_endpoint": CORE_VISUAL_BINDING_ENDPOINT,
        "renderer_count": len(lab_renderer_registry().get("renderers", [])),
        "automatic_core_submission": False,
        "automatic_core_mutation": False,
        "automatic_rendering_by_core": False,
        "automatic_visual_truth_inference": False,
        "scientific_rendering_authority": "lab",
        "bridge_hash": _hash(m),
    }
