import hashlib
import pytest
from app.gpu_renderer_architecture_v0840 import *


def fp(text="shader"):
    return hashlib.sha256(text.encode()).hexdigest()


def browser(webgl2=True, webgpu=False):
    return {"detected": {"svg": True, "canvas2d": True, "webgl2": webgl2, "webgpu": webgpu}}


def test_health_and_boundaries():
    h = health()
    assert h["status"] == "gpu-renderer-architecture-ready"
    assert h["version"] == "0.84.0"
    assert h["engineVersion"] == "2.11.0"
    assert h["rendererCapabilityRegistry"] is True
    assert h["webgl2ProductionRendererReady"] is False
    assert h["webgpuProductionRendererReady"] is False
    assert h["gpuRequiredForScientificCorrectness"] is False
    assert h["silentRendererFallback"] is False


def test_registry_separates_architecture_from_renderer_readiness():
    r = renderer_registry()
    by_id = {x["id"]: x for x in r["renderers"]}
    assert by_id["svg2d"]["implementationReady"] is True
    assert by_id["canvas3d"]["implementationReady"] is True
    assert by_id["webgl2"]["implementationReady"] is False
    assert by_id["webgpu"]["implementationReady"] is False


def test_negotiation_records_fallback_instead_of_silently_using_gpu():
    n = negotiate_renderer({
        "browserCapabilities": browser(webgl2=True, webgpu=True),
        "requiredFeatures": ["3d"],
        "preferredRenderers": ["webgpu", "webgl2", "canvas3d"],
        "allowFallback": True,
    })
    assert n["selectedRenderer"] == "canvas3d"
    assert n["requestedRenderer"] == "webgpu"
    assert n["fallbackUsed"] is True
    assert n["fallbackRecorded"] is True
    assert n["scientificContractPreserved"] is True


def test_no_fallback_refuses_unready_requested_renderer():
    with pytest.raises(GPURendererArchitectureError):
        negotiate_renderer({
            "browserCapabilities": browser(webgl2=True, webgpu=True),
            "requiredFeatures": ["3d"],
            "preferredRenderers": ["webgpu", "canvas3d"],
            "allowFallback": False,
        })


def test_buffer_plan_is_typed_and_bounded():
    b = plan_buffer({"id": "vertices", "dataType": "float32", "length": 1000, "components": 3, "usage": "vertex"})
    assert b["byteLength"] == 12000
    assert b["boundaries"]["silentDowncast"] is False
    with pytest.raises(GPURendererArchitectureError):
        plan_buffer({"dataType": "float64", "length": MAX_BUFFER_BYTES, "components": 16, "usage": "vertex"})


def test_shader_descriptor_requires_fingerprint_and_refuses_source():
    s = normalize_shader_descriptor({"id": "approved-vertex", "language": "glsl", "stage": "vertex", "sourceFingerprint": fp(), "approved": True})
    assert s["sourceFingerprint"] == fp()
    assert s["approved"] is True
    assert s["boundaries"]["arbitraryShaderSource"] is False
    with pytest.raises(GPURendererArchitectureError):
        normalize_shader_descriptor({"id": "x", "language": "glsl", "stage": "vertex", "sourceFingerprint": fp(), "source": "void main(){}"})


def test_compute_descriptor_is_wgsl_only_at_architecture_stage():
    with pytest.raises(GPURendererArchitectureError):
        normalize_shader_descriptor({"id": "compute", "language": "glsl", "stage": "compute", "sourceFingerprint": fp()})
    s = normalize_shader_descriptor({"id": "compute", "language": "wgsl", "stage": "compute", "sourceFingerprint": fp()})
    assert s["stage"] == "compute"


def test_picking_does_not_create_observations():
    p = normalize_picking_contract({"mode": "feature", "maxResults": 12})
    assert p["maxResults"] == 12
    assert p["boundaries"]["pickingCreatesObservation"] is False


def test_diagnostics_report_browser_gpu_without_claiming_renderer_ready():
    d = build_diagnostics({"browserCapabilities": browser(webgl2=True, webgpu=True)})["diagnostics"]
    assert d["gpuArchitectureReady"] is True
    assert d["webgl2ProductionRendererReady"] is False
    assert d["webgpuProductionRendererReady"] is False
    by_id = {x["id"]: x for x in d["renderers"]}
    assert by_id["webgpu"]["browserAvailable"] is True
    assert by_id["webgpu"]["usable"] is False


def test_workspace_preserves_0830_and_older_compatibility():
    w = build_workspace({
        "id": "gpu-workspace",
        "buffers": [{"id": "v", "dataType": "float32", "length": 10, "components": 3, "usage": "vertex"}],
        "shaders": [{"id": "approved", "language": "glsl", "stage": "vertex", "sourceFingerprint": fp(), "approved": True}],
        "picking": [{"mode": "object"}],
        "negotiation": {
            "browserCapabilities": browser(),
            "requiredFeatures": ["3d"],
            "preferredRenderers": ["webgl2", "canvas3d"],
            "allowFallback": True,
        },
    })["workspace"]
    assert w["engineVersion"] == "2.11.0"
    assert w["compatibility"]["v0830Provenance"] is True
    assert w["negotiation"]["selectedRenderer"] == "canvas3d"
