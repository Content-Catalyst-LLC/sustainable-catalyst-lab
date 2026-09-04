from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

VERSION = "0.84.0"
ENGINE_VERSION = "2.11.0"
ARCHITECTURE = "gpu-renderer-architecture"
REGISTRY_SCHEMA = "sc-lab-renderer-registry/0.84.0"
NEGOTIATION_SCHEMA = "sc-lab-renderer-negotiation/0.84.0"
BUFFER_SCHEMA = "sc-lab-gpu-buffer-plan/0.84.0"
SHADER_SCHEMA = "sc-lab-shader-descriptor/0.84.0"
PICKING_SCHEMA = "sc-lab-picking-contract/0.84.0"
DIAGNOSTIC_SCHEMA = "sc-lab-renderer-diagnostics/0.84.0"
WORKSPACE_SCHEMA = "sc-lab-gpu-renderer-workspace/0.84.0"

MAX_BUFFER_BYTES = 256 * 1024 * 1024
MAX_TOTAL_BUFFER_BYTES = 512 * 1024 * 1024
MAX_PICK_RESULTS = 4096

# These are architectural capabilities. WebGL2/WebGPU are intentionally marked
# implementation-ready=False in v0.84; v0.85/v0.86 add the production renderers.
RENDERERS: dict[str, dict[str, Any]] = {
    "svg2d": {
        "family": "cpu-vector",
        "implementationReady": True,
        "browserDetection": "svg",
        "features": ["2d", "vector", "publication", "text", "annotations"],
    },
    "canvas2d": {
        "family": "cpu-raster",
        "implementationReady": True,
        "browserDetection": "canvas2d",
        "features": ["2d", "raster", "interactive", "annotations"],
    },
    "canvas3d": {
        "family": "cpu-projected-3d",
        "implementationReady": True,
        "browserDetection": "canvas2d",
        "features": ["3d", "camera", "picking-basic", "annotations"],
    },
    "canvas4d": {
        "family": "cpu-projected-4d",
        "implementationReady": True,
        "browserDetection": "canvas2d",
        "features": ["3d", "4d", "state-axis", "camera", "picking-basic"],
    },
    "canvas-spatial": {
        "family": "cpu-spatial",
        "implementationReady": True,
        "browserDetection": "canvas2d",
        "features": ["2d", "spatial", "raster", "vector", "bbox-selection"],
    },
    "webgl2": {
        "family": "gpu-webgl2",
        "implementationReady": False,
        "browserDetection": "webgl2",
        "features": ["2d", "3d", "gpu", "depth-buffer", "instancing", "shader-graphics", "gpu-picking"],
    },
    "webgpu": {
        "family": "gpu-webgpu",
        "implementationReady": False,
        "browserDetection": "webgpu",
        "features": ["2d", "3d", "gpu", "depth-buffer", "instancing", "shader-graphics", "compute", "gpu-picking"],
    },
}

DATA_TYPES = {
    "float32": 4,
    "float64": 8,
    "int8": 1,
    "uint8": 1,
    "int16": 2,
    "uint16": 2,
    "int32": 4,
    "uint32": 4,
}
BUFFER_USAGES = {"vertex", "index", "uniform", "storage", "readback", "texture-staging"}
SHADER_LANGUAGES = {"glsl", "wgsl"}
SHADER_STAGES = {"vertex", "fragment", "compute"}
PICKING_MODES = {"point", "object", "cell", "triangle", "feature"}


class GPURendererArchitectureError(ValueError):
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
        raise GPURendererArchitectureError("identifier must not be empty")
    return text[:160]


def _sha256(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        raise GPURendererArchitectureError(f"{label} must be a 64-character SHA-256 hex digest")
    return text


def renderer_registry() -> dict[str, Any]:
    renderers = []
    for renderer_id, spec in RENDERERS.items():
        entry = {"id": renderer_id, **deepcopy(spec)}
        entry["scientificContractAuthority"] = "sc-lab-figure-contract"
        renderers.append(entry)
    out = {
        "schema": REGISTRY_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "architecture": ARCHITECTURE,
        "renderers": renderers,
        "fallbackOrder": ["webgpu", "webgl2", "canvas3d", "canvas-spatial", "canvas2d", "svg2d"],
        "boundaries": {
            "gpuRequiredForScientificCorrectness": False,
            "serverAssumesBrowserGPU": False,
            "silentRendererFallback": False,
            "automaticScientificSemanticsChange": False,
            "arbitraryShaderSource": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_browser_capabilities(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("browser capabilities must be an object")
    allowed = {"svg", "canvas2d", "webgl2", "webgpu"}
    detected = payload.get("detected") or {}
    if not isinstance(detected, dict):
        raise GPURendererArchitectureError("detected must be an object")
    normalized = {key: bool(detected.get(key, False)) for key in sorted(allowed)}
    # SVG/canvas are browser feature declarations, not server assumptions.
    out = {
        "schema": "sc-lab-browser-renderer-capabilities/0.84.0",
        "version": VERSION,
        "detected": normalized,
        "adapter": str(payload.get("adapter") or "browser-runtime")[:120],
        "userAgentFingerprint": str(payload.get("userAgentFingerprint") or "")[:128] or None,
        "boundaries": {
            "serverAssumesBrowserGPU": False,
            "detectionDoesNotEnableRendererImplementation": True,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def negotiate_renderer(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("renderer negotiation must be an object")
    capabilities = normalize_browser_capabilities(payload.get("browserCapabilities") or {"detected": {}})
    required = payload.get("requiredFeatures") or []
    preferred = payload.get("preferredRenderers") or ["webgpu", "webgl2", "canvas3d", "canvas-spatial", "canvas2d", "svg2d"]
    allow_fallback = bool(payload.get("allowFallback", True))
    if not isinstance(required, list) or not all(isinstance(x, str) and x for x in required):
        raise GPURendererArchitectureError("requiredFeatures must be an array of strings")
    if not isinstance(preferred, list) or not preferred:
        raise GPURendererArchitectureError("preferredRenderers must be a non-empty array")
    unknown = [x for x in preferred if x not in RENDERERS]
    if unknown:
        raise GPURendererArchitectureError("unknown renderers: " + ", ".join(unknown))

    considered = []
    selected = None
    for renderer_id in preferred:
        spec = RENDERERS[renderer_id]
        detected_key = spec["browserDetection"]
        browser_available = bool(capabilities["detected"].get(detected_key, False))
        implementation_ready = bool(spec["implementationReady"])
        supports = all(feature in spec["features"] for feature in required)
        eligible = browser_available and implementation_ready and supports
        considered.append({
            "id": renderer_id,
            "browserAvailable": browser_available,
            "implementationReady": implementation_ready,
            "supportsRequiredFeatures": supports,
            "eligible": eligible,
        })
        if selected is None and eligible:
            selected = renderer_id
            if not allow_fallback and renderer_id != preferred[0]:
                selected = None
                break
            if allow_fallback or renderer_id == preferred[0]:
                break

    if selected is None:
        raise GPURendererArchitectureError("no eligible renderer satisfies the declared browser capabilities and required features", 409)

    requested = preferred[0]
    fallback_used = selected != requested
    out = {
        "schema": NEGOTIATION_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "selectedRenderer": selected,
        "requestedRenderer": requested,
        "fallbackUsed": fallback_used,
        "fallbackRecorded": True,
        "scientificContractPreserved": True,
        "requiredFeatures": deepcopy(required),
        "browserCapabilities": capabilities,
        "considered": considered,
        "boundaries": {
            "silentRendererFallback": False,
            "automaticScientificSemanticsChange": False,
            "gpuRequiredForScientificCorrectness": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def plan_buffer(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("buffer plan must be an object")
    data_type = str(payload.get("dataType") or "float32").lower()
    if data_type not in DATA_TYPES:
        raise GPURendererArchitectureError("unsupported dataType")
    try:
        length = int(payload.get("length"))
    except (TypeError, ValueError):
        raise GPURendererArchitectureError("length must be an integer")
    if length < 0:
        raise GPURendererArchitectureError("length must be non-negative")
    usage = str(payload.get("usage") or "vertex").lower()
    if usage not in BUFFER_USAGES:
        raise GPURendererArchitectureError("unsupported buffer usage")
    components = int(payload.get("components") or 1)
    if components < 1 or components > 16:
        raise GPURendererArchitectureError("components must be between 1 and 16")
    byte_length = length * components * DATA_TYPES[data_type]
    if byte_length > MAX_BUFFER_BYTES:
        raise GPURendererArchitectureError(f"single buffer exceeds {MAX_BUFFER_BYTES} bytes", 413)
    out = {
        "schema": BUFFER_SCHEMA,
        "version": VERSION,
        "id": _identifier(payload.get("id"), "gpu-buffer"),
        "dataType": data_type,
        "length": length,
        "components": components,
        "bytesPerElement": DATA_TYPES[data_type],
        "byteLength": byte_length,
        "usage": usage,
        "immutableSource": bool(payload.get("immutableSource", True)),
        "memoryBudget": {"singleBufferBytes": MAX_BUFFER_BYTES, "workspaceBytes": MAX_TOTAL_BUFFER_BYTES},
        "boundaries": {"silentDowncast": False, "silentTruncation": False, "unboundedAllocation": False},
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_shader_descriptor(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("shader descriptor must be an object")
    shader_id = _identifier(payload.get("id"), "approved-shader")
    language = str(payload.get("language") or "glsl").lower()
    stage = str(payload.get("stage") or "vertex").lower()
    if language not in SHADER_LANGUAGES:
        raise GPURendererArchitectureError("unsupported shader language")
    if stage not in SHADER_STAGES:
        raise GPURendererArchitectureError("unsupported shader stage")
    source_fp = _sha256(payload.get("sourceFingerprint"), "sourceFingerprint")
    if payload.get("source") is not None:
        raise GPURendererArchitectureError("arbitrary shader source is not accepted by the v0.84 architecture contract")
    if stage == "compute" and language != "wgsl":
        raise GPURendererArchitectureError("compute shader descriptors require WGSL in the v0.84 architecture contract")
    out = {
        "schema": SHADER_SCHEMA,
        "version": VERSION,
        "id": shader_id,
        "language": language,
        "stage": stage,
        "sourceFingerprint": source_fp,
        "entryPoint": str(payload.get("entryPoint") or "main")[:120],
        "approved": bool(payload.get("approved", False)),
        "boundaries": {"arbitraryShaderSource": False, "runtimeSourceMutation": False, "approvalRequiredForExecution": True},
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_picking_contract(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("picking contract must be an object")
    mode = str(payload.get("mode") or "object").lower()
    if mode not in PICKING_MODES:
        raise GPURendererArchitectureError("unsupported picking mode")
    max_results = int(payload.get("maxResults") or 1)
    if max_results < 1 or max_results > MAX_PICK_RESULTS:
        raise GPURendererArchitectureError(f"maxResults must be between 1 and {MAX_PICK_RESULTS}")
    out = {
        "schema": PICKING_SCHEMA,
        "version": VERSION,
        "mode": mode,
        "maxResults": max_results,
        "preserveSourceIdentity": bool(payload.get("preserveSourceIdentity", True)),
        "returnCoordinates": bool(payload.get("returnCoordinates", True)),
        "boundaries": {"pickingCreatesObservation": False, "automaticScientificInterpretation": False},
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def build_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("diagnostics payload must be an object")
    browser = normalize_browser_capabilities(payload.get("browserCapabilities") or {"detected": {}})
    registry = renderer_registry()
    renderers = []
    for entry in registry["renderers"]:
        detected = bool(browser["detected"].get(entry["browserDetection"], False))
        renderers.append({
            "id": entry["id"],
            "family": entry["family"],
            "browserAvailable": detected,
            "implementationReady": entry["implementationReady"],
            "usable": detected and entry["implementationReady"],
        })
    out = {
        "schema": DIAGNOSTIC_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "browserCapabilities": browser,
        "renderers": renderers,
        "gpuArchitectureReady": True,
        "webgl2ProductionRendererReady": False,
        "webgpuProductionRendererReady": False,
        "nextProductionRenderer": "webgl2-v0850",
        "boundaries": {"diagnosticsEnableUnsupportedRenderer": False, "serverAssumesBrowserGPU": False},
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return {"ok": True, "diagnostics": out}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GPURendererArchitectureError("workspace must be an object")
    buffers_raw = payload.get("buffers") or []
    shaders_raw = payload.get("shaders") or []
    picks_raw = payload.get("picking") or []
    if not isinstance(buffers_raw, list) or not isinstance(shaders_raw, list) or not isinstance(picks_raw, list):
        raise GPURendererArchitectureError("buffers, shaders and picking must be arrays")
    buffers = [plan_buffer(x) for x in buffers_raw]
    total = sum(x["byteLength"] for x in buffers)
    if total > MAX_TOTAL_BUFFER_BYTES:
        raise GPURendererArchitectureError(f"workspace buffer budget exceeds {MAX_TOTAL_BUFFER_BYTES} bytes", 413)
    shaders = [normalize_shader_descriptor(x) for x in shaders_raw]
    picks = [normalize_picking_contract(x) for x in picks_raw]
    negotiation = None
    if payload.get("negotiation") is not None:
        negotiation = negotiate_renderer(payload["negotiation"])
    out = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "id": _identifier(payload.get("id"), "gpu-renderer-workspace"),
        "title": str(payload.get("title") or "GPU renderer architecture workspace")[:240],
        "registryFingerprint": renderer_registry()["fingerprint"],
        "negotiation": negotiation,
        "buffers": buffers,
        "totalBufferBytes": total,
        "shaders": shaders,
        "picking": picks,
        "compatibility": {
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
            "automaticScientificSemanticsChange": False,
            "arbitraryShaderSource": False,
            "webgl2ProductionRendererReady": False,
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
        "architecture": ARCHITECTURE,
        "registry": renderer_registry(),
        "limits": {
            "maxBufferBytes": MAX_BUFFER_BYTES,
            "maxWorkspaceBufferBytes": MAX_TOTAL_BUFFER_BYTES,
            "maxPickResults": MAX_PICK_RESULTS,
        },
        "boundaries": {
            "gpuRequiredForScientificCorrectness": False,
            "serverAssumesBrowserGPU": False,
            "silentRendererFallback": False,
            "automaticScientificSemanticsChange": False,
            "arbitraryShaderSource": False,
            "webgl2ProductionRendererReady": False,
            "webgpuProductionRendererReady": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "gpu-renderer-architecture-ready",
        "version": VERSION,
        "release": VERSION,
        "engineVersion": ENGINE_VERSION,
        "architecture": ARCHITECTURE,
        "rendererCapabilityRegistry": True,
        "browserFeatureDetection": True,
        "safeRendererNegotiation": True,
        "explicitFallbackRecording": True,
        "gpuBufferContracts": True,
        "shaderRegistryContracts": True,
        "pickingContracts": True,
        "memoryBudgets": True,
        "rendererDiagnostics": True,
        "webgl2CapabilityDetection": True,
        "webgpuCapabilityDetection": True,
        "webgl2ProductionRendererReady": False,
        "webgpuProductionRendererReady": False,
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
        "serverAssumesBrowserGPU": False,
        "silentRendererFallback": False,
        "automaticScientificSemanticsChange": False,
        "arbitraryShaderSource": False,
    }
