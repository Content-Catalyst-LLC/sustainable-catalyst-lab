import pytest
from app.webgl2_scientific_renderer_v0850 import (
    VERSION, ENGINE_VERSION, WebGL2ScientificRendererError,
    renderer_descriptor, normalize_camera, normalize_draw_call,
    build_render_plan, normalize_picking, build_workspace, health, policies,
)

FP='a'*64

def test_health_identity_and_production_renderer():
    h=health()
    assert h['ok'] is True
    assert h['status']=='webgl2-scientific-renderer-ready'
    assert h['version']=='0.85.0' and h['engineVersion']=='2.12.0'
    assert h['renderer']=='webgl2' and h['productionRendererReady'] is True
    assert h['depthBuffered3D'] and h['gpuPointClouds'] and h['gpuTriangleMeshes']
    assert h['instancedGeometry'] and h['rasterTextures'] and h['framebufferObjectPicking']
    assert h['webgpuProductionRendererReady'] is False

def test_descriptor_preserves_scientific_boundaries():
    d=renderer_descriptor()
    assert d['productionRendererReady'] is True
    assert d['boundaries']['gpuRequiredForScientificCorrectness'] is False
    assert d['boundaries']['silentRendererFallback'] is False
    assert d['boundaries']['arbitraryShaderSource'] is False
    assert d['boundaries']['automaticSurfaceGeneration'] is False

def test_camera_is_explicit_and_bounded():
    c=normalize_camera({'projection':'perspective','eye':[4,4,3],'target':[0,0,0],'up':[0,0,1],'near':.1,'far':100,'fovDegrees':55})
    assert c['projection']=='perspective' and c['fovDegrees']==55
    with pytest.raises(WebGL2ScientificRendererError): normalize_camera({'near':1,'far':.5})

def test_draw_calls_accept_points_meshes_and_instancing():
    p=normalize_draw_call({'id':'pts','primitive':'points','count':1000,'sourceFingerprint':FP})
    assert p['program']=='scientific-points-v0850' and p['count']==1000
    m=normalize_draw_call({'id':'mesh','primitive':'triangles','mode':'elements-instanced','count':3000,'instanceCount':25,'program':'scientific-instanced-mesh-v0850','sourceFingerprint':FP})
    assert m['instanceCount']==25 and m['mode']=='elements-instanced'

def test_arbitrary_shader_source_and_unapproved_program_rejected():
    with pytest.raises(WebGL2ScientificRendererError): normalize_draw_call({'primitive':'points','count':3,'shaderSource':'void main(){}'})
    with pytest.raises(WebGL2ScientificRendererError): normalize_draw_call({'primitive':'points','count':3,'program':'user-program'})

def test_render_plan_records_fallback_and_source_identity():
    p=build_render_plan({'id':'scene','camera':{},'viewport':{'width':960,'height':540},'buffers':[{'id':'xyz','byteLength':12000,'sourceFingerprint':FP}], 'drawCalls':[{'id':'points','primitive':'points','count':1000,'sourceFingerprint':FP,'sourceObjectId':'observations-1'}], 'allowFallback':True,'fallbackRenderer':'canvas3d'})
    assert p['renderer']=='webgl2' and p['productionRendererReady'] is True
    assert p['fallback']['mustBeRecorded'] is True and p['fallback']['scientificContractPreserved'] is True
    assert p['drawCalls'][0]['sourceObjectId']=='observations-1'

def test_picking_is_interaction_not_observation():
    p=normalize_picking({'mode':'object'})
    assert p['strategy']=='rgba8-framebuffer-object-id'
    assert p['preserveSourceIdentity'] is True
    assert p['boundaries']['pickingCreatesObservation'] is False

def test_workspace_carries_v0840_and_provenance_compatibility():
    w=build_workspace({'id':'w','renderPlan':{'drawCalls':[{'primitive':'points','count':3}],'buffers':[]}})['workspace']
    assert w['compatibility']['v0840GPUArchitecture'] is True
    assert w['compatibility']['v0830Provenance'] is True
    assert w['boundaries']['webgpuProductionRendererReady'] is False

def test_limits_refuse_unbounded_geometry():
    with pytest.raises(WebGL2ScientificRendererError): normalize_draw_call({'primitive':'points','count':10000001})
    with pytest.raises(WebGL2ScientificRendererError): build_render_plan({'drawCalls':[],'buffers':[{'byteLength':536870913}]})

def test_policies_report_webgl2_production_and_webgpu_not_ready():
    p=policies()
    assert p['rendererDescriptor']['productionRendererReady'] is True
    assert p['boundaries']['webgpuProductionRendererReady'] is False
