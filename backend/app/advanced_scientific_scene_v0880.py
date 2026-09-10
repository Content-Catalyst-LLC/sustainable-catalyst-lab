from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

VERSION = "0.88.0"
ENGINE_VERSION = "2.14.0"
SCENE_ENGINE = "advanced-3d-scene"
SCENE_SCHEMA = "sc-lab-advanced-scientific-scene/0.88.0"
CAMERA_SCHEMA = "sc-lab-advanced-scientific-camera/0.88.0"
LIGHT_SCHEMA = "sc-lab-advanced-scientific-light/0.88.0"
MATERIAL_SCHEMA = "sc-lab-advanced-scientific-material/0.88.0"
NODE_SCHEMA = "sc-lab-advanced-scientific-node/0.88.0"
PLAN_SCHEMA = "sc-lab-advanced-scientific-scene-plan/0.88.0"
WORKSPACE_SCHEMA = "sc-lab-advanced-scientific-scene-workspace/0.88.0"

MAX_NODES = 8192
MAX_LIGHTS = 16
MAX_CAMERAS = 16
MAX_INSTANCES_PER_NODE = 1_000_000
MAX_VERTICES_PER_NODE = 25_000_000
MAX_INDICES_PER_NODE = 75_000_000
MAX_CHILDREN_PER_NODE = 4096

NODE_TYPES = {"group", "point-cloud", "line-segments", "polyline", "mesh", "vectors", "raster-plane"}
LIGHT_TYPES = {"ambient", "directional", "point"}
MATERIAL_TYPES = {"scientific-basic", "scientific-lambert", "scientific-phong", "scientific-points", "scientific-lines"}
PROJECTIONS = {"perspective", "orthographic"}
RENDERER_PREFERENCES = {"native-webgpu", "threejs-webgpu", "threejs-webgl", "webgl2"}


class AdvancedScientificSceneError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _id(value: Any, fallback: str) -> str:
    text = str(value or fallback).strip()
    if not text:
        raise AdvancedScientificSceneError("identifier must not be empty")
    if len(text) > 160:
        raise AdvancedScientificSceneError("identifier exceeds 160 characters")
    return text


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise AdvancedScientificSceneError(f"{label} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise AdvancedScientificSceneError(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise AdvancedScientificSceneError(f"{label} must be finite")
    return out


def _vec3(value: Any, label: str, default: list[float] | None = None) -> list[float]:
    if value is None:
        value = default
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise AdvancedScientificSceneError(f"{label} must contain exactly three coordinates")
    return [_finite(value[i], f"{label}[{i}]") for i in range(3)]


def _vec4(value: Any, label: str, default: list[float] | None = None) -> list[float]:
    if value is None:
        value = default
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise AdvancedScientificSceneError(f"{label} must contain exactly four values")
    return [_finite(value[i], f"{label}[{i}]") for i in range(4)]


def _positive(value: Any, label: str, *, minimum: float = 0.0, maximum: float | None = None) -> float:
    out = _finite(value, label)
    if out < minimum:
        raise AdvancedScientificSceneError(f"{label} must be >= {minimum}")
    if maximum is not None and out > maximum:
        raise AdvancedScientificSceneError(f"{label} must be <= {maximum}")
    return out


def _normalize_transform(payload: Any) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    out = {
        "position": _vec3(source.get("position"), "transform.position", [0, 0, 0]),
        "rotationEulerRadians": _vec3(source.get("rotationEulerRadians"), "transform.rotationEulerRadians", [0, 0, 0]),
        "scale": _vec3(source.get("scale"), "transform.scale", [1, 1, 1]),
    }
    if any(abs(v) < 1e-15 for v in out["scale"]):
        raise AdvancedScientificSceneError("transform.scale values must be non-zero")
    out["fingerprint"] = _hash(out)
    return out


def normalize_camera(payload: dict[str, Any] | None, index: int = 0) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    projection = str(source.get("projection") or "perspective").strip().lower()
    if projection not in PROJECTIONS:
        raise AdvancedScientificSceneError(f"unsupported camera projection: {projection}")
    position = _vec3(source.get("position"), "camera.position", [3.4, 2.6, 4.8])
    target = _vec3(source.get("target"), "camera.target", [0, 0, 0])
    up = _vec3(source.get("up"), "camera.up", [0, 1, 0])
    if math.dist(position, target) < 1e-10:
        raise AdvancedScientificSceneError("camera.position must differ from camera.target")
    if math.sqrt(sum(v * v for v in up)) < 1e-10:
        raise AdvancedScientificSceneError("camera.up must be non-zero")
    near = _positive(source.get("near", 0.01), "camera.near", minimum=1e-9)
    far = _positive(source.get("far", 10000.0), "camera.far", minimum=near + 1e-9)
    fov = _positive(source.get("fovDegrees", 45.0), "camera.fovDegrees", minimum=5.0, maximum=150.0)
    ortho = _positive(source.get("orthographicScale", 3.0), "camera.orthographicScale", minimum=1e-9)
    out = {
        "schema": CAMERA_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), f"camera-{index + 1}"),
        "projection": projection,
        "position": position,
        "target": target,
        "up": up,
        "fovDegrees": fov,
        "near": near,
        "far": far,
        "orthographicScale": ortho,
        "interaction": {
            "orbit": bool((source.get("interaction") or {}).get("orbit", True)) if isinstance(source.get("interaction"), dict) else True,
            "pan": bool((source.get("interaction") or {}).get("pan", True)) if isinstance(source.get("interaction"), dict) else True,
            "zoom": bool((source.get("interaction") or {}).get("zoom", True)) if isinstance(source.get("interaction"), dict) else True,
            "damping": bool((source.get("interaction") or {}).get("damping", False)) if isinstance(source.get("interaction"), dict) else False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_light(payload: dict[str, Any] | None, index: int = 0) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    kind = str(source.get("type") or "directional").strip().lower()
    if kind not in LIGHT_TYPES:
        raise AdvancedScientificSceneError(f"unsupported light type: {kind}")
    intensity = _positive(source.get("intensity", 1.0), "light.intensity", minimum=0.0, maximum=100.0)
    out: dict[str, Any] = {
        "schema": LIGHT_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), f"light-{index + 1}"),
        "type": kind,
        "intensity": intensity,
        "color": _vec3(source.get("color"), "light.color", [1, 1, 1]),
        "presentationOnly": True,
    }
    if any(v < 0 or v > 1 for v in out["color"]):
        raise AdvancedScientificSceneError("light.color values must be between 0 and 1")
    if kind == "directional":
        out["direction"] = _vec3(source.get("direction"), "light.direction", [0.45, 0.75, 0.8])
        if math.sqrt(sum(v * v for v in out["direction"])) < 1e-10:
            raise AdvancedScientificSceneError("directional light direction must be non-zero")
    elif kind == "point":
        out["position"] = _vec3(source.get("position"), "light.position", [2.5, 3.5, 4.0])
        out["range"] = _positive(source.get("range", 0), "light.range", minimum=0.0)
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_material(payload: dict[str, Any] | None, index: int = 0) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    kind = str(source.get("type") or "scientific-lambert").strip().lower()
    if kind not in MATERIAL_TYPES:
        raise AdvancedScientificSceneError(f"unsupported material type: {kind}")
    color = _vec4(source.get("color"), "material.color", [0.35, 0.72, 0.95, 1.0])
    if any(v < 0 or v > 1 for v in color):
        raise AdvancedScientificSceneError("material.color values must be between 0 and 1")
    out = {
        "schema": MATERIAL_SCHEMA,
        "version": VERSION,
        "id": _id(source.get("id"), f"material-{index + 1}"),
        "type": kind,
        "color": color,
        "opacity": _positive(source.get("opacity", color[3]), "material.opacity", minimum=0.0, maximum=1.0),
        "wireframe": bool(source.get("wireframe", False)),
        "twoSided": bool(source.get("twoSided", False)),
        "depthTest": bool(source.get("depthTest", True)),
        "depthWrite": bool(source.get("depthWrite", True)),
        "scalarColorMapping": deepcopy(source.get("scalarColorMapping")) if isinstance(source.get("scalarColorMapping"), dict) else None,
        "presentationOnly": True,
    }
    if source.get("shaderSource") is not None or source.get("wgsl") is not None:
        raise AdvancedScientificSceneError("arbitrary shader source is not accepted")
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def _normalize_geometry(source: dict[str, Any], kind: str) -> dict[str, Any]:
    geometry = source.get("geometry") if isinstance(source.get("geometry"), dict) else {}
    vertex_count = int(geometry.get("vertexCount") or source.get("vertexCount") or 0)
    index_count = int(geometry.get("indexCount") or source.get("indexCount") or 0)
    instance_count = int(geometry.get("instanceCount") or source.get("instanceCount") or 1)
    if vertex_count < 0 or vertex_count > MAX_VERTICES_PER_NODE:
        raise AdvancedScientificSceneError(f"vertexCount must be between 0 and {MAX_VERTICES_PER_NODE}", 413)
    if index_count < 0 or index_count > MAX_INDICES_PER_NODE:
        raise AdvancedScientificSceneError(f"indexCount must be between 0 and {MAX_INDICES_PER_NODE}", 413)
    if instance_count < 1 or instance_count > MAX_INSTANCES_PER_NODE:
        raise AdvancedScientificSceneError(f"instanceCount must be between 1 and {MAX_INSTANCES_PER_NODE}", 413)
    primitive = {
        "point-cloud": "point-list",
        "line-segments": "line-list",
        "polyline": "line-strip",
        "mesh": "triangle-list",
        "vectors": "line-list",
        "raster-plane": "triangle-list",
        "group": "none",
    }[kind]
    return {
        "primitive": primitive,
        "vertexCount": vertex_count,
        "indexCount": index_count,
        "instanceCount": instance_count,
        "indexed": index_count > 0,
        "attributes": deepcopy(geometry.get("attributes") or {}),
        "sourceFingerprint": str(geometry.get("sourceFingerprint") or source.get("sourceFingerprint") or "")[:128] or None,
    }


def normalize_node(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedScientificSceneError("scene node must be an object")
    kind = str(payload.get("type") or "group").strip().lower()
    if kind not in NODE_TYPES:
        raise AdvancedScientificSceneError(f"unsupported node type: {kind}")
    children = payload.get("children") or []
    if not isinstance(children, list) or len(children) > MAX_CHILDREN_PER_NODE:
        raise AdvancedScientificSceneError(f"node children must contain at most {MAX_CHILDREN_PER_NODE} ids", 413)
    node = {
        "schema": NODE_SCHEMA,
        "version": VERSION,
        "id": _id(payload.get("id"), f"node-{index + 1}"),
        "type": kind,
        "name": str(payload.get("name") or payload.get("id") or f"Node {index + 1}")[:240],
        "visible": payload.get("visible") is not False,
        "transform": _normalize_transform(payload.get("transform")),
        "geometry": _normalize_geometry(payload, kind),
        "materialId": str(payload.get("materialId") or "")[:160] or None,
        "children": [_id(v, "child") for v in children],
        "sourceObjectId": str(payload.get("sourceObjectId") or payload.get("id") or f"node-{index + 1}")[:160],
        "provenance": deepcopy(payload.get("provenance") or {}),
    }
    if kind == "group" and (node["geometry"]["vertexCount"] or node["geometry"]["indexCount"]):
        raise AdvancedScientificSceneError("group nodes may not declare render geometry")
    node["fingerprint"] = _hash({k: v for k, v in node.items() if k != "fingerprint"})
    return node


def _validate_scene_graph(nodes: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        raise AdvancedScientificSceneError("scene node ids must be unique")
    by_id = {n["id"]: n for n in nodes}
    parents: dict[str, str] = {}
    for node in nodes:
        for child in node["children"]:
            if child not in by_id:
                raise AdvancedScientificSceneError(f"node {node['id']} references missing child {child}")
            if child in parents:
                raise AdvancedScientificSceneError(f"node {child} has more than one parent")
            parents[child] = node["id"]
    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(node_id: str) -> None:
        if node_id in visiting:
            raise AdvancedScientificSceneError("scene graph contains a cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for child in by_id[node_id]["children"]:
            walk(child)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in ids:
        walk(node_id)
    roots = [node_id for node_id in ids if node_id not in parents]
    return roots, sorted(parents)


def normalize_scene(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedScientificSceneError("scene must be an object")
    raw_nodes = payload.get("nodes") or []
    raw_lights = payload.get("lights") or []
    raw_cameras = payload.get("cameras") or ([payload.get("camera")] if payload.get("camera") else [{}])
    raw_materials = payload.get("materials") or [{}]
    if not isinstance(raw_nodes, list) or len(raw_nodes) > MAX_NODES:
        raise AdvancedScientificSceneError(f"nodes must contain at most {MAX_NODES} entries", 413)
    if not isinstance(raw_lights, list) or len(raw_lights) > MAX_LIGHTS:
        raise AdvancedScientificSceneError(f"lights must contain at most {MAX_LIGHTS} entries", 413)
    if not isinstance(raw_cameras, list) or len(raw_cameras) > MAX_CAMERAS:
        raise AdvancedScientificSceneError(f"cameras must contain at most {MAX_CAMERAS} entries", 413)
    if not isinstance(raw_materials, list) or len(raw_materials) > 512:
        raise AdvancedScientificSceneError("materials must contain at most 512 entries", 413)
    nodes = [normalize_node(v, i) for i, v in enumerate(raw_nodes)]
    roots, children = _validate_scene_graph(nodes)
    lights = [normalize_light(v, i) for i, v in enumerate(raw_lights)] or [normalize_light({"type": "ambient", "intensity": 0.28}, 0), normalize_light({"type": "directional", "intensity": 0.9}, 1)]
    cameras = [normalize_camera(v, i) for i, v in enumerate(raw_cameras)]
    materials = [normalize_material(v, i) for i, v in enumerate(raw_materials)]
    material_ids = {m["id"] for m in materials}
    for node in nodes:
        if node["materialId"] and node["materialId"] not in material_ids:
            raise AdvancedScientificSceneError(f"node {node['id']} references missing material {node['materialId']}")
    active_camera = str(payload.get("activeCameraId") or cameras[0]["id"])
    if active_camera not in {c["id"] for c in cameras}:
        raise AdvancedScientificSceneError("activeCameraId must reference a declared camera")
    renderer_preference = str(payload.get("rendererPreference") or "native-webgpu").strip().lower()
    if renderer_preference not in RENDERER_PREFERENCES:
        raise AdvancedScientificSceneError("rendererPreference is unsupported")
    scene = {
        "schema": SCENE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": _id(payload.get("id"), "advanced-scientific-scene"),
        "rendererPreference": renderer_preference,
        "activeCameraId": active_camera,
        "cameras": cameras,
        "lights": lights,
        "materials": materials,
        "nodes": nodes,
        "rootNodeIds": roots,
        "childNodeIds": children,
        "nodeCount": len(nodes),
        "renderableNodeCount": sum(1 for n in nodes if n["type"] != "group" and n["visible"]),
        "interaction": {
            "orbit": bool((payload.get("interaction") or {}).get("orbit", True)) if isinstance(payload.get("interaction"), dict) else True,
            "pan": bool((payload.get("interaction") or {}).get("pan", True)) if isinstance(payload.get("interaction"), dict) else True,
            "zoom": bool((payload.get("interaction") or {}).get("zoom", True)) if isinstance(payload.get("interaction"), dict) else True,
            "objectPicking": bool((payload.get("interaction") or {}).get("objectPicking", True)) if isinstance(payload.get("interaction"), dict) else True,
        },
        "background": _vec4(payload.get("background"), "scene.background", [0.02, 0.025, 0.035, 1.0]),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "boundaries": scene_descriptor()["boundaries"],
    }
    if any(v < 0 or v > 1 for v in scene["background"]):
        raise AdvancedScientificSceneError("scene.background values must be between 0 and 1")
    scene["fingerprint"] = _hash({k: v for k, v in scene.items() if k != "fingerprint"})
    return scene


def scene_descriptor() -> dict[str, Any]:
    out = {
        "schema": "sc-lab-advanced-scientific-scene-engine/0.88.0",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "engine": SCENE_ENGINE,
        "nativeWebGPUSceneRendererReady": True,
        "threeJSAdapterReady": True,
        "threeJSRuntimeBundled": False,
        "externalCDNRequired": False,
        "webgpuRequiredForScientificCorrectness": False,
        "fallbackRenderers": ["threejs-webgl", "webgl2", "canvas3d"],
        "nodeTypes": sorted(NODE_TYPES),
        "lightTypes": sorted(LIGHT_TYPES),
        "materialTypes": sorted(MATERIAL_TYPES),
        "capabilities": {
            "sceneGraphs": True,
            "perspectiveCamera": True,
            "orthographicCamera": True,
            "orbitInteraction": True,
            "panInteraction": True,
            "zoomInteraction": True,
            "objectPickingContract": True,
            "ambientLighting": True,
            "directionalLighting": True,
            "pointLighting": True,
            "instancedGeometry": True,
            "pointClouds": True,
            "lineGeometry": True,
            "triangleMeshes": True,
            "explicitMaterials": True,
            "threeJSCompatibilityAdapter": True,
            "nativeWebGPUExecution": True,
            "v0870WebGPUCompatibility": True,
            "v0850WebGL2Compatibility": True,
            "v0830ProvenanceCompatibility": True,
            "v0770SceneSemanticsCompatibility": True,
        },
        "limits": {
            "maxNodes": MAX_NODES,
            "maxLights": MAX_LIGHTS,
            "maxCameras": MAX_CAMERAS,
            "maxInstancesPerNode": MAX_INSTANCES_PER_NODE,
            "maxVerticesPerNode": MAX_VERTICES_PER_NODE,
            "maxIndicesPerNode": MAX_INDICES_PER_NODE,
        },
        "boundaries": {
            "automaticGeometryGeneration": False,
            "automaticTriangulation": False,
            "automaticSurfaceInterpolation": False,
            "automaticScientificInterpretation": False,
            "automaticUnitConversion": False,
            "automaticLightingFromData": False,
            "lightingChangesScientificValues": False,
            "materialChangesScientificValues": False,
            "interactionCreatesObservation": False,
            "arbitraryShaderSource": False,
            "silentRendererFallback": False,
            "threeJSRequiredForScientificCorrectness": False,
            "webgpuRequiredForScientificCorrectness": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def build_render_plan(payload: dict[str, Any]) -> dict[str, Any]:
    scene = normalize_scene(payload.get("scene") or payload)
    passes = []
    material_map = {m["id"]: m for m in scene["materials"]}
    for node in scene["nodes"]:
        if node["type"] == "group" or not node["visible"]:
            continue
        material = material_map.get(node["materialId"]) if node["materialId"] else scene["materials"][0]
        passes.append({
            "id": f"pass:{node['id']}",
            "nodeId": node["id"],
            "primitive": node["geometry"]["primitive"],
            "vertexCount": node["geometry"]["vertexCount"],
            "indexCount": node["geometry"]["indexCount"],
            "instanceCount": node["geometry"]["instanceCount"],
            "materialId": material["id"],
            "materialType": material["type"],
            "depthTest": material["depthTest"],
            "depthWrite": material["depthWrite"],
            "sourceObjectId": node["sourceObjectId"],
            "sourceFingerprint": node["geometry"]["sourceFingerprint"],
        })
    plan = {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": _id(payload.get("id"), "advanced-scene-render-plan"),
        "sceneFingerprint": scene["fingerprint"],
        "rendererPreference": scene["rendererPreference"],
        "activeCameraId": scene["activeCameraId"],
        "passes": passes,
        "drawCallCount": len(passes),
        "fallbackPolicy": {
            "silent": False,
            "ordered": ["native-webgpu", "threejs-webgpu", "threejs-webgl", "webgl2", "canvas3d"],
            "recordSelection": True,
        },
        "boundaries": scene_descriptor()["boundaries"],
    }
    plan["fingerprint"] = _hash({k: v for k, v in plan.items() if k != "fingerprint"})
    return {"ok": True, "scene": scene, "renderPlan": plan}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    built = build_render_plan(payload)
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": _id(payload.get("workspaceId") or payload.get("id"), "advanced-3d-workspace"),
        "scene": built["scene"],
        "renderPlan": built["renderPlan"],
        "compatibility": {
            "v0870WebGPU": True,
            "v0850WebGL2": True,
            "v0840GPUArchitecture": True,
            "v0830Provenance": True,
            "v0770ScientificScene": True,
        },
        "boundaries": scene_descriptor()["boundaries"],
    }
    workspace["fingerprint"] = _hash({k: v for k, v in workspace.items() if k != "fingerprint"})
    return {"ok": True, "workspace": workspace}


def health() -> dict[str, Any]:
    descriptor = scene_descriptor()
    return {
        "ok": True,
        "status": "advanced-3d-scientific-scene-ready",
        "version": VERSION,
        "release": VERSION,
        "engineVersion": ENGINE_VERSION,
        "engine": SCENE_ENGINE,
        "nativeWebGPUSceneRendererReady": True,
        "threeJSAdapterReady": True,
        "threeJSRuntimeBundled": False,
        "externalCDNRequired": False,
        "sceneGraphs": True,
        "lighting": True,
        "instancing": True,
        "scientific3DInteraction": True,
        "v0870WebGPUCompatibility": True,
        "v0850WebGL2Compatibility": True,
        "v0830ProvenanceCompatibility": True,
        "v0770SceneSemanticsCompatibility": True,
        **descriptor["boundaries"],
    }


def policies() -> dict[str, Any]:
    descriptor = scene_descriptor()
    return {"ok": True, "version": VERSION, "engineVersion": ENGINE_VERSION, "descriptor": descriptor, "boundaries": descriptor["boundaries"]}
