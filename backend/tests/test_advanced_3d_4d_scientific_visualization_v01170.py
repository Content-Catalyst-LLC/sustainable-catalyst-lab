import pytest
from app.advanced_3d_4d_scientific_visualization_v01170 import *

def surface(): return {'id':'s','x':[0,1],'y':[0,1],'z':[[0,1],[1,0]],'source_refs':['lab:dataset:d1'],'units':{'x':'m','y':'m','z':'K'}}
def scene(): return {'id':'scene-1','title':'Field evolution','source_refs':['lab:dataset:d1'],'objects':[{'id':'mesh','type':'triangle-mesh','vertices':[[0,0,0],[1,0,0],[0,1,0]],'triangles':[[0,1,2]],'semantic_role':'observed','source_refs':['lab:dataset:d1']}],'time_axis':{'values':[0,1,2],'unit':'s'}}
def test_catalog_manifest():
 assert len(catalog()['object_types'])==12 and manifest()['features']['temporal_4d_scenes'] is True
 assert manifest()['boundaries']['automatic_geometry_inference'] is False

def test_surface():
 x=build_surface(surface()); assert x['object']['type']=='surface-grid' and x['scientific_validity_certified'] is False

def test_mesh_requires_topology():
 with pytest.raises(AdvancedScientificVisualizationError): build_mesh({'vertices':[[0,0,0],[1,0,0],[0,1,0]]})
 m=build_mesh({'vertices':[[0,0,0],[1,0,0],[0,1,0]],'triangles':[[0,1,2]]}); assert m['automatic_triangulation'] is False

def test_fields():
 v=build_vector_field({'positions':[[0,0,0]],'vectors':[[1,0,0]]}); assert v['object']['vectors'][0]==[1.0,0.0,0.0]
 s=build_scalar_field({'positions':[[0,0,0]],'values':[3]}); assert s['automatic_interpolation'] is False

def test_volume_requires_transfer_function():
 with pytest.raises(AdvancedScientificVisualizationError): build_volume({'dimensions':[2,2,2],'data_ref':'lab:volume:v'})
 v=build_volume({'dimensions':[2,2,2],'data_ref':'lab:volume:v','transfer_function':{'opacity_stops':[[0,0],[1,1]]}}); assert v['automatic_transfer_function'] is False

def test_temporal_scene():
 s=normalize_scene(scene())['scene']; assert s['time_axis']['frame_count']==3
 f=build_temporal_frames({'time_axis':{'values':[0,1],'unit':'s'},'states':[{'a':1},{'a':2}]}); assert f['automatic_time_inference'] is False

def test_slice_iso_explicit():
 sl=build_slice_plan({'source_field_ref':'lab:field:f','planes':[{'origin':[0,0,0],'normal':[0,0,1]}]}); assert sl['automatic_slice_selection'] is False
 iso=build_isosurface_plan({'source_field_ref':'lab:field:f','iso_values':[0.2,0.5]}); assert iso['automatic_threshold_selection'] is False

def test_uncertainty_and_renderer():
 u=build_uncertainty_geometry({'kind':'uncertainty-envelope','level':.95,'geometry_ref':'lab:geom:g'}); assert u['semantic_role']=='uncertainty'
 r=build_renderer_plan({'scene':scene(),'renderer':'webgpu'}); assert r['gpu_required'] is True and r['automatic_renderer_execution'] is False

def test_export_dashboard_core():
 e=build_publication_export({'scene':scene(),'formats':['png','pdf','gltf','json']}); assert e['automatic_file_write'] is False
 p=build_dashboard_panel({'scene':scene(),'panel_id':'p1'}); assert p['panel']['figure_kind']=='scientific-3d-4d-scene'
 c=build_core_visual_plan({'scene':scene(),'session_id':'s1'}); assert c['automatic_core_submission'] is False and c['core_renders_scene'] is False

def test_accessibility():
 a=accessibility_audit({'scene':scene(),'alt_text':'A three-dimensional triangular mesh over time.'}); assert a['accessible'] is True and a['automatic_alt_text_inference'] is False
