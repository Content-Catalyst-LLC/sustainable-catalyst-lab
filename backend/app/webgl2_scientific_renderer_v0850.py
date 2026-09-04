from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

VERSION = "0.85.0"
ENGINE_VERSION = "2.12.0"
RENDERER = "webgl2"
RENDERER_SCHEMA = "sc-lab-webgl2-renderer/0.85.0"
SCENE_SCHEMA = "sc-lab-webgl2-scene/0.85.0"
PLAN_SCHEMA = "sc-lab-webgl2-render-plan/0.85.0"
PICK_SCHEMA = "sc-lab-webgl2-picking/0.85.0"
WORKSPACE_SCHEMA = "sc-lab-webgl2-workspace/0.85.0"

MAX_VERTICES = 10_000_000
MAX_INDICES = 30_000_000
MAX_DRAW_CALLS = 4096
MAX_INSTANCES = 1_000_000
MAX_CLIPPING_PLANES = 6
MAX_RASTER_PIXELS = 67_108_864
MAX_BUFFER_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BUFFER_BYTES = 1024 * 1024 * 1024

PRIMITIVES = {"points", "lines", "triangles", "raster-quad"}
BLEND_MODES = {"opaque", "alpha"}
DRAW_MODES = {"arrays", "elements", "arrays-instanced", "elements-instanced"}

# Only renderer-owned shader programs are executable in v0.85. User supplied GLSL
# is deliberately excluded; the browser runtime contains the canonical sources.
APPROVED_PROGRAMS = {
    "scientific-points-v0850": {"primitive": "points", "depth": True, "picking": True},
    "scientific-lines-v0850": {"primitive": "lines", "depth": True, "picking": True},
    "scientific-mesh-v0850": {"primitive": "triangles", "depth": True, "picking": True},
    "scientific-instanced-mesh-v0850": {"primitive": "triangles", "depth": True, "picking": True, "instancing": True},
    "scientific-raster-v0850": {"primitive": "raster-quad", "depth": True, "picking": True},
    "scientific-picking-v0850": {"primitive": "picking", "depth": True, "picking": True},
}


class WebGL2ScientificRendererError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _identifier(value: Any, fallback: str) -> str:
    text = str(value or fallback).strip()
    if not text:
        raise WebGL2ScientificRendererError("identifier must not be empty")
    return text[:160]


def _sha256(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        raise WebGL2ScientificRendererError(f"{label} must be a 64-character SHA-256 hex digest")
    return text


def _number(value: Any, label: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise WebGL2ScientificRendererError(f"{label} must be numeric")
    if minimum is not None and out < minimum:
        raise WebGL2ScientificRendererError(f"{label} must be >= {minimum}")
    if maximum is not None and out > maximum:
        raise WebGL2ScientificRendererError(f"{label} must be <= {maximum}")
    return out


def renderer_descriptor() -> dict[str, Any]:
    out = {
        "schema": RENDERER_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": RENDERER,
        "family": "gpu-webgl2",
        "productionRendererReady": True,
        "browserRequirement": "WebGL2RenderingContext",
        "features": [
            "2d", "3d", "gpu", "depth-buffer", "point-cloud", "line-segments",
            "triangle-mesh", "instancing", "raster-texture", "clipping-planes",
            "alpha-blending", "framebuffer-picking", "explicit-fallback",
        ],
        "programs": [{"id": k, **deepcopy(v)} for k, v in APPROVED_PROGRAMS.items()],
        "limits": {
            "maxVertices": MAX_VERTICES,
            "maxIndices": MAX_INDICES,
            "maxDrawCalls": MAX_DRAW_CALLS,
            "maxInstances": MAX_INSTANCES,
            "maxClippingPlanes": MAX_CLIPPING_PLANES,
            "maxRasterPixels": MAX_RASTER_PIXELS,
            "maxBufferBytes": MAX_BUFFER_BYTES,
            "maxTotalBufferBytes": MAX_TOTAL_BUFFER_BYTES,
        },
        "boundaries": {
            "gpuRequiredForScientificCorrectness": False,
            "silentRendererFallback": False,
            "arbitraryShaderSource": False,
            "automaticSurfaceGeneration": False,
            "automaticSpatialInterpolation": False,
            "automaticTemporalInterpolation": False,
            "automaticScientificSemanticsChange": False,
            "webgpuProductionRendererReady": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_camera(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGL2ScientificRendererError("camera must be an object")
    projection = str(payload.get("projection") or "perspective").lower()
    if projection not in {"perspective", "orthographic"}:
        raise WebGL2ScientificRendererError("projection must be perspective or orthographic")
    def vec3(name: str, default: list[float]) -> list[float]:
        raw = payload.get(name, default)
        if not isinstance(raw, list) or len(raw) != 3:
            raise WebGL2ScientificRendererError(f"{name} must contain exactly 3 numeric values")
        return [_number(x, f"{name}[{i}]") for i, x in enumerate(raw)]
    near = _number(payload.get("near", 0.01), "near", minimum=1e-9)
    far = _number(payload.get("far", 10000.0), "far", minimum=near + 1e-9)
    out = {
        "projection": projection,
        "eye": vec3("eye", [3.0, 3.0, 3.0]),
        "target": vec3("target", [0.0, 0.0, 0.0]),
        "up": vec3("up", [0.0, 0.0, 1.0]),
        "near": near,
        "far": far,
    }
    if projection == "perspective":
        out["fovDegrees"] = _number(payload.get("fovDegrees", 45.0), "fovDegrees", minimum=1.0, maximum=179.0)
    else:
        out["orthoHeight"] = _number(payload.get("orthoHeight", 2.0), "orthoHeight", minimum=1e-9)
    out["fingerprint"] = _hash(out)
    return out


def normalize_draw_call(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGL2ScientificRendererError("draw call must be an object")
    primitive = str(payload.get("primitive") or "points").lower()
    if primitive not in PRIMITIVES:
        raise WebGL2ScientificRendererError("unsupported primitive")
    mode = str(payload.get("mode") or ("elements" if payload.get("indexed") else "arrays")).lower()
    if mode not in DRAW_MODES:
        raise WebGL2ScientificRendererError("unsupported draw mode")
    count = int(payload.get("count") or 0)
    if count < 0:
        raise WebGL2ScientificRendererError("draw count must be non-negative")
    max_count = MAX_INDICES if "elements" in mode else MAX_VERTICES
    if count > max_count:
        raise WebGL2ScientificRendererError(f"draw count exceeds {max_count}", 413)
    instances = int(payload.get("instanceCount") or 1)
    if instances < 1 or instances > MAX_INSTANCES:
        raise WebGL2ScientificRendererError(f"instanceCount must be between 1 and {MAX_INSTANCES}")
    if "instanced" not in mode and instances != 1:
        raise WebGL2ScientificRendererError("instanceCount > 1 requires an instanced draw mode")
    blend = str(payload.get("blendMode") or "opaque").lower()
    if blend not in BLEND_MODES:
        raise WebGL2ScientificRendererError("unsupported blendMode")
    program = str(payload.get("program") or {
        "points": "scientific-points-v0850",
        "lines": "scientific-lines-v0850",
        "triangles": "scientific-mesh-v0850",
        "raster-quad": "scientific-raster-v0850",
    }[primitive])
    if program not in APPROVED_PROGRAMS:
        raise WebGL2ScientificRendererError("draw call references an unapproved renderer-owned program")
    if payload.get("shaderSource") is not None:
        raise WebGL2ScientificRendererError("arbitrary shader source is not accepted")
    source_fp = payload.get("sourceFingerprint")
    if source_fp is not None:
        source_fp = _sha256(source_fp, "sourceFingerprint")
    clip = payload.get("clippingPlanes") or []
    if not isinstance(clip, list) or len(clip) > MAX_CLIPPING_PLANES:
        raise WebGL2ScientificRendererError(f"clippingPlanes must be an array with at most {MAX_CLIPPING_PLANES} entries")
    normalized_clip = []
    for i, plane in enumerate(clip):
        if not isinstance(plane, list) or len(plane) != 4:
            raise WebGL2ScientificRendererError(f"clippingPlanes[{i}] must contain 4 coefficients")
        normalized_clip.append([_number(x, f"clippingPlanes[{i}]") for x in plane])
    out = {
        "id": _identifier(payload.get("id"), f"draw-{index+1}"),
        "primitive": primitive,
        "mode": mode,
        "count": count,
        "instanceCount": instances,
        "program": program,
        "depthTest": bool(payload.get("depthTest", True)),
        "depthWrite": bool(payload.get("depthWrite", blend == "opaque")),
        "blendMode": blend,
        "cullFace": str(payload.get("cullFace") or "none").lower(),
        "clippingPlanes": normalized_clip,
        "pickingEnabled": bool(payload.get("pickingEnabled", True)),
        "sourceFingerprint": source_fp,
        "sourceObjectId": str(payload.get("sourceObjectId") or payload.get("id") or f"draw-{index+1}")[:160],
    }
    if out["cullFace"] not in {"none", "back", "front"}:
        raise WebGL2ScientificRendererError("cullFace must be none, back, or front")
    out["fingerprint"] = _hash(out)
    return out


def build_render_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGL2ScientificRendererError("render plan must be an object")
    calls_raw = payload.get("drawCalls") or []
    if not isinstance(calls_raw, list):
        raise WebGL2ScientificRendererError("drawCalls must be an array")
    if len(calls_raw) > MAX_DRAW_CALLS:
        raise WebGL2ScientificRendererError(f"drawCalls exceeds {MAX_DRAW_CALLS}", 413)
    calls = [normalize_draw_call(x, i) for i, x in enumerate(calls_raw)]
    buffers = payload.get("buffers") or []
    if not isinstance(buffers, list):
        raise WebGL2ScientificRendererError("buffers must be an array")
    total_bytes = 0
    normalized_buffers = []
    for i, buf in enumerate(buffers):
        if not isinstance(buf, dict):
            raise WebGL2ScientificRendererError("buffer descriptors must be objects")
        byte_length = int(buf.get("byteLength") or 0)
        if byte_length < 0 or byte_length > MAX_BUFFER_BYTES:
            raise WebGL2ScientificRendererError(f"buffer {i} exceeds bounded memory policy", 413)
        total_bytes += byte_length
        if total_bytes > MAX_TOTAL_BUFFER_BYTES:
            raise WebGL2ScientificRendererError("render plan exceeds total GPU buffer budget", 413)
        source_fp = buf.get("sourceFingerprint")
        normalized_buffers.append({
            "id": _identifier(buf.get("id"), f"buffer-{i+1}"),
            "usage": str(buf.get("usage") or "vertex")[:40],
            "byteLength": byte_length,
            "sourceFingerprint": _sha256(source_fp, "sourceFingerprint") if source_fp is not None else None,
            "immutableSource": bool(buf.get("immutableSource", True)),
        })
    viewport = payload.get("viewport") or {}
    width = int(viewport.get("width") or 960)
    height = int(viewport.get("height") or 540)
    if width < 1 or height < 1 or width > 16384 or height > 16384:
        raise WebGL2ScientificRendererError("viewport dimensions must be between 1 and 16384")
    out = {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "productionRendererReady": True,
        "id": _identifier(payload.get("id"), "webgl2-render-plan"),
        "camera": normalize_camera(payload.get("camera") or {}),
        "viewport": {"width": width, "height": height, "devicePixelRatioCap": 2.0},
        "clear": {"depth": True, "color": True},
        "buffers": normalized_buffers,
        "totalBufferBytes": total_bytes,
        "drawCalls": calls,
        "picking": {
            "strategy": "rgba8-framebuffer-object-id",
            "preserveSourceIdentity": True,
            "createsObservation": False,
        },
        "fallback": {
            "allowed": bool(payload.get("allowFallback", True)),
            "preferredFallback": str(payload.get("fallbackRenderer") or "canvas3d"),
            "mustBeRecorded": True,
            "scientificContractPreserved": True,
        },
        "boundaries": {
            "arbitraryShaderSource": False,
            "automaticSurfaceGeneration": False,
            "automaticSpatialInterpolation": False,
            "automaticTemporalInterpolation": False,
            "automaticScientificSemanticsChange": False,
            "silentRendererFallback": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_picking(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGL2ScientificRendererError("picking payload must be an object")
    mode = str(payload.get("mode") or "object").lower()
    if mode not in {"object", "feature"}:
        raise WebGL2ScientificRendererError("v0.85 framebuffer picking supports object or feature identity")
    out = {
        "schema": PICK_SCHEMA,
        "version": VERSION,
        "renderer": RENDERER,
        "mode": mode,
        "strategy": "rgba8-framebuffer-object-id",
        "preserveSourceIdentity": True,
        "returnCanvasCoordinates": bool(payload.get("returnCanvasCoordinates", True)),
        "returnSourceObjectId": True,
        "boundaries": {
            "pickingCreatesObservation": False,
            "automaticScientificInterpretation": False,
            "nearestObservationInference": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGL2ScientificRendererError("workspace must be an object")
    plan = build_render_plan(payload.get("renderPlan") or payload)
    provenance = deepcopy(payload.get("provenance") or {})
    out = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "id": _identifier(payload.get("id"), "webgl2-scientific-workspace"),
        "title": str(payload.get("title") or "WebGL2 scientific rendering workspace")[:240],
        "renderPlan": plan,
        "rendererDescriptorFingerprint": renderer_descriptor()["fingerprint"],
        "provenance": provenance,
        "compatibility": {
            "v0840GPUArchitecture": True,
            "v0830Provenance": True,
            "v0820Uncertainty": True,
            "v0810Markup": True,
            "v0800Spatial": True,
            "v0790LinkedViews": True,
            "v0780TimeParameter": True,
            "v0770Scene": True,
            "v0760Adaptive": True,
            "v0750DataBinding": True,
        },
        "boundaries": {
            "gpuRequiredForScientificCorrectness": False,
            "silentRendererFallback": False,
            "arbitraryShaderSource": False,
            "webgpuProductionRendererReady": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return {"ok": True, "workspace": out}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "rendererDescriptor": renderer_descriptor(),
        "picking": normalize_picking({}),
        "boundaries": renderer_descriptor()["boundaries"],
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "webgl2-scientific-renderer-ready",
        "version": VERSION,
        "release": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "productionRendererReady": True,
        "depthBuffered3D": True,
        "gpuPointClouds": True,
        "gpuLineSegments": True,
        "gpuTriangleMeshes": True,
        "instancedGeometry": True,
        "rasterTextures": True,
        "clippingPlanes": True,
        "alphaBlending": True,
        "framebufferObjectPicking": True,
        "explicitRendererFallback": True,
        "approvedInternalShadersOnly": True,
        "v0840GPUArchitectureCompatibility": True,
        "v0830ProvenanceCompatibility": True,
        "v0820UncertaintyCompatibility": True,
        "v0810MarkupCompatibility": True,
        "v0800SpatialCompatibility": True,
        "v0790LinkedViewsCompatibility": True,
        "v0780TimeParameterCompatibility": True,
        "v0770SceneCompatibility": True,
        "v0760AdaptiveCompatibility": True,
        "v0750DataBindingCompatibility": True,
        "gpuRequiredForScientificCorrectness": False,
        "silentRendererFallback": False,
        "arbitraryShaderSource": False,
        "automaticSurfaceGeneration": False,
        "automaticSpatialInterpolation": False,
        "automaticTemporalInterpolation": False,
        "automaticScientificSemanticsChange": False,
        "webgpuProductionRendererReady": False,
    }
