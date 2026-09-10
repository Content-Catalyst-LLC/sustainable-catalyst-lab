from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

VERSION = "0.87.0"
ENGINE_VERSION = "2.13.0"
RENDERER = "webgpu"
RENDERER_SCHEMA = "sc-lab-webgpu-renderer/0.87.0"
PLAN_SCHEMA = "sc-lab-webgpu-render-plan/0.87.0"
COMPUTE_SCHEMA = "sc-lab-webgpu-compute-plan/0.87.0"
WORKSPACE_SCHEMA = "sc-lab-webgpu-workspace/0.87.0"

MAX_VERTICES = 25_000_000
MAX_INDICES = 75_000_000
MAX_DRAW_CALLS = 8192
MAX_BUFFER_BYTES = 1024 * 1024 * 1024
MAX_TOTAL_BUFFER_BYTES = 2 * 1024 * 1024 * 1024
MAX_WORKGROUPS = 65535
MAX_HISTOGRAM_BINS = 4096
MAX_COMPUTE_ITEMS = 100_000_000

APPROVED_RENDER_PIPELINES = {
    "scientific-points-v0870": {"primitive": "point-list", "depth": True, "picking": True},
    "scientific-lines-v0870": {"primitive": "line-list", "depth": True, "picking": True},
    "scientific-mesh-v0870": {"primitive": "triangle-list", "depth": True, "picking": True},
    "scientific-raster-v0870": {"primitive": "triangle-list", "depth": True, "picking": True},
    "scientific-picking-v0870": {"primitive": "triangle-list", "depth": True, "picking": True},
}

APPROVED_COMPUTE_KERNELS = {
    "filter-threshold-v0870": {"operation": "filter", "workgroupSize": 256},
    "histogram-v0870": {"operation": "histogram", "workgroupSize": 256},
    "minmax-v0870": {"operation": "reduction", "workgroupSize": 256},
    "sum-v0870": {"operation": "reduction", "workgroupSize": 256},
    "spatial-bin-v0870": {"operation": "binning", "workgroupSize": 256},
}


class WebGPUScientificRendererError(ValueError):
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
        raise WebGPUScientificRendererError("identifier must not be empty")
    return text[:160]


def _number(value: Any, label: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise WebGPUScientificRendererError(f"{label} must be numeric")
    if minimum is not None and out < minimum:
        raise WebGPUScientificRendererError(f"{label} must be >= {minimum}")
    if maximum is not None and out > maximum:
        raise WebGPUScientificRendererError(f"{label} must be <= {maximum}")
    return out


def _sha256(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        raise WebGPUScientificRendererError(f"{label} must be a 64-character SHA-256 hex digest")
    return text


def renderer_descriptor() -> dict[str, Any]:
    out = {
        "schema": RENDERER_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": RENDERER,
        "family": "gpu-webgpu",
        "productionRendererReady": True,
        "browserRequirement": "navigator.gpu + GPUCanvasContext",
        "fallbackRenderer": "webgl2",
        "features": [
            "2d", "3d", "gpu", "depth-buffer", "point-cloud", "line-segments", "triangle-mesh",
            "raster-texture", "object-picking", "compute-shaders", "gpu-filtering", "gpu-histogram",
            "gpu-reduction", "gpu-binning", "typed-storage-buffers", "explicit-fallback",
        ],
        "renderPipelines": [{"id": k, **deepcopy(v)} for k, v in APPROVED_RENDER_PIPELINES.items()],
        "computeKernels": [{"id": k, **deepcopy(v)} for k, v in APPROVED_COMPUTE_KERNELS.items()],
        "limits": {
            "maxVertices": MAX_VERTICES,
            "maxIndices": MAX_INDICES,
            "maxDrawCalls": MAX_DRAW_CALLS,
            "maxBufferBytes": MAX_BUFFER_BYTES,
            "maxTotalBufferBytes": MAX_TOTAL_BUFFER_BYTES,
            "maxWorkgroups": MAX_WORKGROUPS,
            "maxHistogramBins": MAX_HISTOGRAM_BINS,
            "maxComputeItems": MAX_COMPUTE_ITEMS,
        },
        "boundaries": {
            "gpuRequiredForScientificCorrectness": False,
            "silentRendererFallback": False,
            "arbitraryWGSLSource": False,
            "automaticScientificSemanticsChange": False,
            "automaticInterpolation": False,
            "automaticImputation": False,
            "automaticForecasting": False,
            "computeResultCreatesObservation": False,
            "webgl2FallbackPreservesScientificContract": True,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_render_pass(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGPUScientificRendererError("render pass must be an object")
    pipeline = str(payload.get("pipeline") or "scientific-points-v0870")
    if pipeline not in APPROVED_RENDER_PIPELINES:
        raise WebGPUScientificRendererError("render pass references an unapproved renderer-owned pipeline")
    if payload.get("wgsl") is not None or payload.get("shaderSource") is not None:
        raise WebGPUScientificRendererError("arbitrary WGSL source is not accepted")
    vertex_count = int(payload.get("vertexCount") or 0)
    index_count = int(payload.get("indexCount") or 0)
    instance_count = int(payload.get("instanceCount") or 1)
    if vertex_count < 0 or vertex_count > MAX_VERTICES:
        raise WebGPUScientificRendererError(f"vertexCount must be between 0 and {MAX_VERTICES}", 413)
    if index_count < 0 or index_count > MAX_INDICES:
        raise WebGPUScientificRendererError(f"indexCount must be between 0 and {MAX_INDICES}", 413)
    if instance_count < 1 or instance_count > 1_000_000:
        raise WebGPUScientificRendererError("instanceCount must be between 1 and 1000000", 413)
    source_fp = payload.get("sourceFingerprint")
    if source_fp is not None:
        source_fp = _sha256(source_fp, "sourceFingerprint")
    out = {
        "id": _identifier(payload.get("id"), f"render-pass-{index+1}"),
        "pipeline": pipeline,
        "vertexCount": vertex_count,
        "indexCount": index_count,
        "instanceCount": instance_count,
        "depthTest": bool(payload.get("depthTest", True)),
        "alphaBlending": bool(payload.get("alphaBlending", False)),
        "pickingEnabled": bool(payload.get("pickingEnabled", True)),
        "sourceFingerprint": source_fp,
        "sourceObjectId": str(payload.get("sourceObjectId") or payload.get("id") or f"render-pass-{index+1}")[:160],
    }
    out["fingerprint"] = _hash(out)
    return out


def normalize_compute_dispatch(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGPUScientificRendererError("compute dispatch must be an object")
    kernel = str(payload.get("kernel") or "sum-v0870")
    if kernel not in APPROVED_COMPUTE_KERNELS:
        raise WebGPUScientificRendererError("compute dispatch references an unapproved kernel")
    if payload.get("wgsl") is not None or payload.get("shaderSource") is not None:
        raise WebGPUScientificRendererError("arbitrary WGSL source is not accepted")
    item_count = int(payload.get("itemCount") or 0)
    if item_count < 0 or item_count > MAX_COMPUTE_ITEMS:
        raise WebGPUScientificRendererError(f"itemCount must be between 0 and {MAX_COMPUTE_ITEMS}", 413)
    workgroup_size = int(APPROVED_COMPUTE_KERNELS[kernel]["workgroupSize"])
    workgroups = (item_count + workgroup_size - 1) // workgroup_size if item_count else 0
    if workgroups > MAX_WORKGROUPS:
        raise WebGPUScientificRendererError(f"dispatch would exceed {MAX_WORKGROUPS} workgroups; chunking must be explicit", 413)
    params = payload.get("parameters") or {}
    if not isinstance(params, dict):
        raise WebGPUScientificRendererError("parameters must be an object")
    if kernel == "histogram-v0870":
        bins = int(params.get("bins") or 64)
        if bins < 1 or bins > MAX_HISTOGRAM_BINS:
            raise WebGPUScientificRendererError(f"histogram bins must be between 1 and {MAX_HISTOGRAM_BINS}")
    source_fp = payload.get("sourceFingerprint")
    if source_fp is not None:
        source_fp = _sha256(source_fp, "sourceFingerprint")
    out = {
        "id": _identifier(payload.get("id"), f"compute-{index+1}"),
        "kernel": kernel,
        "operation": APPROVED_COMPUTE_KERNELS[kernel]["operation"],
        "itemCount": item_count,
        "workgroupSize": workgroup_size,
        "workgroups": workgroups,
        "parameters": deepcopy(params),
        "sourceFingerprint": source_fp,
        "createsObservation": False,
    }
    out["fingerprint"] = _hash(out)
    return out


def build_render_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGPUScientificRendererError("render plan must be an object")
    passes = payload.get("renderPasses") or []
    if not isinstance(passes, list) or len(passes) > MAX_DRAW_CALLS:
        raise WebGPUScientificRendererError(f"renderPasses must contain at most {MAX_DRAW_CALLS} entries")
    buffers = payload.get("buffers") or []
    if not isinstance(buffers, list):
        raise WebGPUScientificRendererError("buffers must be an array")
    normalized_buffers = []
    total = 0
    for i, b in enumerate(buffers):
        if not isinstance(b, dict):
            raise WebGPUScientificRendererError(f"buffers[{i}] must be an object")
        size = int(b.get("byteLength") or 0)
        if size < 0 or size > MAX_BUFFER_BYTES:
            raise WebGPUScientificRendererError(f"buffers[{i}].byteLength exceeds per-buffer limit", 413)
        total += size
        if total > MAX_TOTAL_BUFFER_BYTES:
            raise WebGPUScientificRendererError("total buffer budget exceeded", 413)
        fp = b.get("sourceFingerprint")
        if fp is not None:
            fp = _sha256(fp, f"buffers[{i}].sourceFingerprint")
        normalized_buffers.append({"id": _identifier(b.get("id"), f"buffer-{i+1}"), "byteLength": size, "usage": list(b.get("usage") or []), "sourceFingerprint": fp})
    out = {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "productionRendererReady": True,
        "id": _identifier(payload.get("id"), "webgpu-plan"),
        "renderPasses": [normalize_render_pass(v, i) for i, v in enumerate(passes)],
        "buffers": normalized_buffers,
        "totalBufferBytes": total,
        "fallback": {
            "renderer": str(payload.get("fallbackRenderer") or "webgl2"),
            "mustBeRecorded": True,
            "scientificContractPreserved": True,
        },
    }
    out["fingerprint"] = _hash(out)
    return out


def build_compute_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGPUScientificRendererError("compute plan must be an object")
    dispatches = payload.get("dispatches") or []
    if not isinstance(dispatches, list):
        raise WebGPUScientificRendererError("dispatches must be an array")
    if len(dispatches) > 4096:
        raise WebGPUScientificRendererError("compute plan exceeds 4096 dispatches", 413)
    out = {
        "schema": COMPUTE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": _identifier(payload.get("id"), "webgpu-compute-plan"),
        "dispatches": [normalize_compute_dispatch(v, i) for i, v in enumerate(dispatches)],
        "execution": "browser-webgpu",
        "fallback": {
            "renderer": "webgl2",
            "computeFallback": "cpu-governed-transform",
            "mustBeRecorded": True,
        },
        "boundaries": {"computeResultCreatesObservation": False, "arbitraryWGSLSource": False},
    }
    out["fingerprint"] = _hash(out)
    return out


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WebGPUScientificRendererError("workspace must be an object")
    render_plan = build_render_plan(payload.get("renderPlan") or {})
    compute_plan = build_compute_plan(payload.get("computePlan") or {"dispatches": []})
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": _identifier(payload.get("id"), "webgpu-workspace"),
        "renderPlan": render_plan,
        "computePlan": compute_plan,
        "compatibility": {
            "v0860SystemDynamics": True,
            "v0850WebGL2": True,
            "v0840GPUArchitecture": True,
            "v0830Provenance": True,
            "v0820Uncertainty": True,
        },
        "boundaries": renderer_descriptor()["boundaries"],
    }
    workspace["fingerprint"] = _hash({k: v for k, v in workspace.items() if k != "fingerprint"})
    return {"ok": True, "workspace": workspace}


def health() -> dict[str, Any]:
    d = renderer_descriptor()
    return {
        "ok": True,
        "status": "webgpu-scientific-renderer-compute-ready",
        "version": VERSION,
        "release": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "productionRendererReady": True,
        "webgpuComputeReady": True,
        "gpuFiltering": True,
        "gpuHistogram": True,
        "gpuReduction": True,
        "gpuSpatialBinning": True,
        "typedStorageBuffers": True,
        "approvedWGSLOnly": True,
        "explicitWebGL2Fallback": True,
        "v0860SystemDynamicsCompatibility": True,
        "v0850WebGL2Compatibility": True,
        "v0840GPUArchitectureCompatibility": True,
        "v0830ProvenanceCompatibility": True,
        "v0820UncertaintyCompatibility": True,
        **d["boundaries"],
    }


def policies() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "rendererDescriptor": renderer_descriptor(), "boundaries": renderer_descriptor()["boundaries"]}
