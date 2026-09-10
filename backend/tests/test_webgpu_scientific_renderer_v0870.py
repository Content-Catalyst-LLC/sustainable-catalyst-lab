import pytest
from app.webgpu_scientific_renderer_v0870 import (
    WebGPUScientificRendererError, renderer_descriptor, normalize_render_pass,
    normalize_compute_dispatch, build_render_plan, build_compute_plan, build_workspace,
    health, policies,
)
FP='a'*64

def test_health_identity_and_webgpu_compute_ready():
    h=health(); assert h['ok'] is True
    assert h['status']=='webgpu-scientific-renderer-compute-ready'
    assert h['version']=='0.87.0' and h['engineVersion']=='2.13.0'
    assert h['renderer']=='webgpu' and h['productionRendererReady'] is True
    assert h['webgpuComputeReady'] and h['gpuFiltering'] and h['gpuHistogram'] and h['gpuReduction'] and h['gpuSpatialBinning']
    assert h['explicitWebGL2Fallback'] is True

def test_descriptor_preserves_scientific_boundaries():
    d=renderer_descriptor(); b=d['boundaries']
    assert d['productionRendererReady'] is True and d['fallbackRenderer']=='webgl2'
    assert b['gpuRequiredForScientificCorrectness'] is False
    assert b['silentRendererFallback'] is False
    assert b['arbitraryWGSLSource'] is False
    assert b['computeResultCreatesObservation'] is False

def test_render_pass_rejects_arbitrary_wgsl_and_unapproved_pipeline():
    p=normalize_render_pass({'id':'pts','pipeline':'scientific-points-v0870','vertexCount':1000,'sourceFingerprint':FP})
    assert p['vertexCount']==1000 and p['sourceObjectId']=='pts'
    with pytest.raises(WebGPUScientificRendererError): normalize_render_pass({'wgsl':'@vertex fn x(){}'})
    with pytest.raises(WebGPUScientificRendererError): normalize_render_pass({'pipeline':'user-pipeline'})

def test_compute_dispatch_is_bounded_and_explicit():
    d=normalize_compute_dispatch({'kernel':'histogram-v0870','itemCount':10000,'parameters':{'bins':128},'sourceFingerprint':FP})
    assert d['operation']=='histogram' and d['workgroups']==40 and d['createsObservation'] is False
    with pytest.raises(WebGPUScientificRendererError): normalize_compute_dispatch({'kernel':'histogram-v0870','itemCount':10,'parameters':{'bins':5000}})
    with pytest.raises(WebGPUScientificRendererError): normalize_compute_dispatch({'kernel':'user-kernel','itemCount':10})

def test_render_plan_records_webgl2_fallback_and_buffer_budget():
    p=build_render_plan({'id':'scene','buffers':[{'id':'xyz','byteLength':12000,'sourceFingerprint':FP}], 'renderPasses':[{'id':'pts','pipeline':'scientific-points-v0870','vertexCount':1000,'sourceFingerprint':FP}]})
    assert p['renderer']=='webgpu' and p['productionRendererReady'] is True
    assert p['fallback']['renderer']=='webgl2' and p['fallback']['mustBeRecorded'] is True
    with pytest.raises(WebGPUScientificRendererError): build_render_plan({'buffers':[{'byteLength':1073741825}]})

def test_compute_plan_has_governed_cpu_fallback():
    p=build_compute_plan({'dispatches':[{'kernel':'sum-v0870','itemCount':1024}]})
    assert p['execution']=='browser-webgpu'
    assert p['fallback']['computeFallback']=='cpu-governed-transform'
    assert p['boundaries']['arbitraryWGSLSource'] is False

def test_workspace_preserves_visualization_and_systems_compatibility():
    w=build_workspace({'id':'w','renderPlan':{'renderPasses':[],'buffers':[]},'computePlan':{'dispatches':[]}})['workspace']
    assert w['compatibility']['v0860SystemDynamics'] is True
    assert w['compatibility']['v0850WebGL2'] is True
    assert w['compatibility']['v0830Provenance'] is True

def test_policies_use_approved_wgsl_only():
    p=policies(); assert p['rendererDescriptor']['productionRendererReady'] is True
    assert p['boundaries']['arbitraryWGSLSource'] is False
