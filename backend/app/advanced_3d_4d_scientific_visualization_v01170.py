from __future__ import annotations

import copy, json, math
from hashlib import sha256
from typing import Any

VERSION="0.117.0"
ENGINE_VERSION="3.3.0"
SCHEMA="sc-lab-advanced-3d-4d-scientific-visualization/0.117.0"
MAX_OBJECTS=96
MAX_VERTICES=250000
MAX_FRAMES=2000
MAX_VOLUME_DIM=512
OBJECT_TYPES={"surface-grid","triangle-mesh","point-cloud","vector-field","scalar-field","volume","trajectory","streamlines","isosurface","slice-plane","uncertainty-envelope","glyph-field"}
RENDERERS={"canvas3d","canvas4d","webgl2","webgpu"}
COORDINATE_FRAMES={"cartesian","geographic","ecef","local-tangent","model"}

class AdvancedScientificVisualizationError(ValueError):
    def __init__(self,detail:str,status_code:int=400): super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _text(v,label,limit=1000,required=False):
    s=str(v or '').strip()
    if required and not s: raise AdvancedScientificVisualizationError(f"{label} is required.")
    if len(s)>limit: raise AdvancedScientificVisualizationError(f"{label} exceeds {limit} characters.")
    return s
def _finite(v,label):
    if isinstance(v,bool): raise AdvancedScientificVisualizationError(f"{label} must be numeric.")
    try: x=float(v)
    except Exception as e: raise AdvancedScientificVisualizationError(f"{label} must be numeric.") from e
    if not math.isfinite(x): raise AdvancedScientificVisualizationError(f"{label} must be finite.")
    return x
def _vec(v,label,n=3):
    if not isinstance(v,(list,tuple)) or len(v)!=n: raise AdvancedScientificVisualizationError(f"{label} must contain {n} numeric values.")
    return [_finite(x,f"{label}[{i}]") for i,x in enumerate(v)]
def _list(v,label,limit):
    if v is None:return []
    if not isinstance(v,list): raise AdvancedScientificVisualizationError(f"{label} must be an array.")
    if len(v)>limit: raise AdvancedScientificVisualizationError(f"{label} exceeds {limit} entries.",413)
    return copy.deepcopy(v)
def _refs(v):
    out=[]
    for x in _list(v,'source_refs',5000):
        s=_text(x,'source_ref',1200,True)
        if s not in out: out.append(s)
    return out

def _points(v,label,limit=MAX_VERTICES):
    rows=_list(v,label,limit)
    return [_vec(p,f"{label}[{i}]") for i,p in enumerate(rows)]

def normalize_camera(payload=None):
    p=payload if isinstance(payload,dict) else {}
    projection=_text(p.get('projection') or 'perspective','projection',32,True).lower()
    if projection not in {'perspective','orthographic'}: raise AdvancedScientificVisualizationError('projection must be perspective or orthographic.')
    position=_vec(p.get('position') or [3,2.5,4], 'camera.position'); target=_vec(p.get('target') or [0,0,0],'camera.target'); up=_vec(p.get('up') or [0,1,0],'camera.up')
    if position==target: raise AdvancedScientificVisualizationError('camera position must differ from target.')
    return {'schema':'sc-lab-scientific-camera-state/0.117.0','projection':projection,'position':position,'target':target,'up':up,'fov_degrees':_finite(p.get('fov_degrees',45),'fov_degrees'),'near':_finite(p.get('near',.01),'near'),'far':_finite(p.get('far',10000),'far'),'interaction':{'orbit':bool(p.get('orbit',True)),'pan':bool(p.get('pan',True)),'zoom':bool(p.get('zoom',True))}}

def normalize_object(payload,index=0):
    if not isinstance(payload,dict): raise AdvancedScientificVisualizationError('scene object must be an object.')
    kind=_text(payload.get('type'),'object.type',80,True).lower()
    if kind not in OBJECT_TYPES: raise AdvancedScientificVisualizationError(f'unsupported 3D/4D object type: {kind}.')
    obj={'id':_text(payload.get('id') or f'object-{index+1}','object.id',180,True),'type':kind,'title':_text(payload.get('title') or payload.get('id') or kind,'object.title',300,True),'coordinate_frame':_text(payload.get('coordinate_frame') or 'cartesian','coordinate_frame',80,True).lower(),'units':copy.deepcopy(payload.get('units') or {}),'source_refs':_refs(payload.get('source_refs')),'style':copy.deepcopy(payload.get('style') or {}),'semantic_role':_text(payload.get('semantic_role') or 'model','semantic_role',80,True).lower(),'visible':payload.get('visible') is not False}
    if obj['coordinate_frame'] not in COORDINATE_FRAMES: raise AdvancedScientificVisualizationError('unsupported coordinate_frame.')
    if kind in {'triangle-mesh','point-cloud','trajectory','streamlines','uncertainty-envelope','glyph-field'}:
        obj['vertices']=_points(payload.get('vertices'),f'{kind}.vertices')
    if kind=='triangle-mesh':
        faces=_list(payload.get('triangles'),'triangles',500000)
        if not faces: raise AdvancedScientificVisualizationError('triangle-mesh requires explicit triangle topology.')
        n=len(obj['vertices']); out=[]
        for i,f in enumerate(faces):
            if not isinstance(f,list) or len(f)!=3: raise AdvancedScientificVisualizationError(f'triangle {i} must contain three indexes.')
            idx=[int(x) for x in f]
            if min(idx)<0 or max(idx)>=n or len(set(idx))<3: raise AdvancedScientificVisualizationError(f'triangle {i} has invalid topology.')
            out.append(idx)
        obj['triangles']=out
    elif kind=='surface-grid':
        x=[_finite(v,'x') for v in _list(payload.get('x'),'x',4096)]; y=[_finite(v,'y') for v in _list(payload.get('y'),'y',4096)]; z=_list(payload.get('z'),'z',4096)
        if not x or not y or len(z)!=len(y) or any(not isinstance(row,list) or len(row)!=len(x) for row in z): raise AdvancedScientificVisualizationError('surface-grid requires x, y and rectangular z[y][x].')
        obj.update({'x':x,'y':y,'z':[[_finite(v,'z') for v in row] for row in z]})
    elif kind in {'vector-field','scalar-field'}:
        positions=_points(payload.get('positions'),f'{kind}.positions'); obj['positions']=positions
        if kind=='vector-field':
            vectors=_points(payload.get('vectors'),'vector-field.vectors')
            if len(vectors)!=len(positions): raise AdvancedScientificVisualizationError('vector-field vectors must align with positions.')
            obj['vectors']=vectors
        else:
            values=[_finite(v,'scalar-field.value') for v in _list(payload.get('values'),'values',MAX_VERTICES)]
            if len(values)!=len(positions): raise AdvancedScientificVisualizationError('scalar-field values must align with positions.')
            obj['values']=values
    elif kind=='volume':
        dims=[int(v) for v in _vec(payload.get('dimensions'),'volume.dimensions')]
        if any(d<=0 or d>MAX_VOLUME_DIM for d in dims): raise AdvancedScientificVisualizationError('volume dimensions must be 1..512.')
        obj['dimensions']=dims; obj['data_ref']=_text(payload.get('data_ref'),'volume.data_ref',1200,True)
        transfer=payload.get('transfer_function')
        if not isinstance(transfer,dict) or not transfer.get('opacity_stops'): raise AdvancedScientificVisualizationError('volume requires an explicit transfer_function with opacity_stops.')
        obj['transfer_function']=copy.deepcopy(transfer)
    elif kind in {'isosurface','slice-plane'}:
        obj['source_field_ref']=_text(payload.get('source_field_ref'),'source_field_ref',1200,True)
        if kind=='isosurface': obj['iso_value']=_finite(payload.get('iso_value'),'iso_value')
        else: obj['plane']={'origin':_vec((payload.get('plane') or {}).get('origin'),'plane.origin'),'normal':_vec((payload.get('plane') or {}).get('normal'),'plane.normal')}
    obj['fingerprint']=_hash(obj)
    return obj

def normalize_time_axis(payload):
    p=payload if isinstance(payload,dict) else {}
    values=_list(p.get('values'),'time_axis.values',MAX_FRAMES)
    if not values: raise AdvancedScientificVisualizationError('4D visualization requires an explicit time_axis.values array.')
    unit=_text(p.get('unit'),'time_axis.unit',80,True)
    return {'schema':'sc-lab-scientific-time-axis/0.117.0','values':copy.deepcopy(values),'unit':unit,'label':_text(p.get('label') or 'Time','time_axis.label',120,True),'interpolation':_text(p.get('interpolation') or 'none','time_axis.interpolation',40,True),'frame_count':len(values)}

def normalize_scene(payload):
    if not isinstance(payload,dict): raise AdvancedScientificVisualizationError('scene must be an object.')
    objects=[normalize_object(o,i) for i,o in enumerate(_list(payload.get('objects'),'objects',MAX_OBJECTS))]
    if not objects: raise AdvancedScientificVisualizationError('scene requires at least one object.')
    scene={'schema':SCHEMA,'version':VERSION,'id':_text(payload.get('id') or 'scene','scene.id',180,True),'title':_text(payload.get('title') or 'Scientific 3D/4D scene','scene.title',300,True),'camera':normalize_camera(payload.get('camera')),'objects':objects,'source_refs':_refs(payload.get('source_refs')),'background':copy.deepcopy(payload.get('background') or {'mode':'solid','value':'paper'}),'lighting':copy.deepcopy(payload.get('lighting') or {'mode':'scientific-default'}),'axes':copy.deepcopy(payload.get('axes') or {'visible':True})}
    if payload.get('time_axis') is not None: scene['time_axis']=normalize_time_axis(payload.get('time_axis'))
    scene['scene_hash']=_hash(scene); return {'ok':True,'scene':scene,'automatic_geometry_inference':False,'automatic_time_inference':False}

def build_surface(payload):
    obj=normalize_object({**payload,'type':'surface-grid'},0); return {'ok':True,'figure_type':'surface-grid','object':obj,'scientific_validity_certified':False}
def build_mesh(payload):
    obj=normalize_object({**payload,'type':'triangle-mesh'},0); return {'ok':True,'figure_type':'triangle-mesh','object':obj,'automatic_triangulation':False}
def build_vector_field(payload):
    obj=normalize_object({**payload,'type':'vector-field'},0); return {'ok':True,'figure_type':'vector-field','object':obj,'automatic_vector_inference':False}
def build_scalar_field(payload):
    obj=normalize_object({**payload,'type':'scalar-field'},0); return {'ok':True,'figure_type':'scalar-field','object':obj,'automatic_interpolation':False}
def build_volume(payload):
    obj=normalize_object({**payload,'type':'volume'},0); return {'ok':True,'figure_type':'volume','object':obj,'automatic_transfer_function':False}
def build_trajectory(payload):
    obj=normalize_object({**payload,'type':'trajectory'},0); times=_list(payload.get('time_values'),'time_values',MAX_FRAMES)
    if times and len(times)!=len(obj['vertices']): raise AdvancedScientificVisualizationError('trajectory time_values must align with vertices.')
    obj['time_values']=times; return {'ok':True,'figure_type':'trajectory','object':obj,'automatic_time_inference':False}

def build_slice_plan(payload):
    field=_text(payload.get('source_field_ref'),'source_field_ref',1200,True); planes=_list(payload.get('planes'),'planes',64)
    if not planes: raise AdvancedScientificVisualizationError('slice plan requires explicit planes.')
    out=[]
    for i,p in enumerate(planes): out.append({'id':_text(p.get('id') or f'slice-{i+1}','slice.id',120,True),'origin':_vec(p.get('origin'),'slice.origin'),'normal':_vec(p.get('normal'),'slice.normal')})
    return {'ok':True,'source_field_ref':field,'planes':out,'automatic_slice_selection':False}
def build_isosurface_plan(payload):
    field=_text(payload.get('source_field_ref'),'source_field_ref',1200,True); vals=[_finite(v,'iso_value') for v in _list(payload.get('iso_values'),'iso_values',32)]
    if not vals: raise AdvancedScientificVisualizationError('isosurface plan requires explicit iso_values.')
    return {'ok':True,'source_field_ref':field,'iso_values':vals,'automatic_threshold_selection':False}
def build_temporal_frames(payload):
    axis=normalize_time_axis(payload.get('time_axis')); states=_list(payload.get('states'),'states',MAX_FRAMES)
    if states and len(states)!=axis['frame_count']: raise AdvancedScientificVisualizationError('states must align one-to-one with time_axis values.')
    return {'ok':True,'schema':'sc-lab-4d-frame-plan/0.117.0','time_axis':axis,'states':copy.deepcopy(states),'automatic_interpolation':False,'automatic_time_inference':False,'frame_hash':_hash({'axis':axis,'states':states})}
def build_uncertainty_geometry(payload):
    kind=_text(payload.get('kind') or 'uncertainty-envelope','kind',80,True)
    if kind not in {'uncertainty-envelope','ensemble-trajectories','probability-volume'}: raise AdvancedScientificVisualizationError('unsupported uncertainty geometry kind.')
    level=_finite(payload.get('level'),'level')
    if not (0<level<1): raise AdvancedScientificVisualizationError('uncertainty level must be between 0 and 1.')
    return {'ok':True,'kind':kind,'level':level,'semantic_role':'uncertainty','source_refs':_refs(payload.get('source_refs')),'geometry_ref':_text(payload.get('geometry_ref'),'geometry_ref',1200,True),'automatic_uncertainty_inference':False,'scientific_validity_certified':False}
def build_renderer_plan(payload):
    scene=normalize_scene(payload.get('scene') or payload)['scene']; requested=_text(payload.get('renderer') or 'webgpu','renderer',40,True).lower()
    if requested not in RENDERERS: raise AdvancedScientificVisualizationError('unsupported renderer.')
    complexity=sum(len(o.get('vertices',[]))+len(o.get('positions',[])) for o in scene['objects'])
    fallback='webgl2' if requested=='webgpu' else 'canvas3d'
    return {'ok':True,'renderer':requested,'fallback_renderer':fallback,'scene_hash':scene['scene_hash'],'estimated_geometry_points':complexity,'gpu_required':requested in {'webgl2','webgpu'},'automatic_renderer_execution':False,'hardware_capability_required':requested in {'webgl2','webgpu'}}
def build_publication_export(payload):
    scene=normalize_scene(payload.get('scene') or payload)['scene']; formats=_list(payload.get('formats') or ['png','svg','pdf'],'formats',10)
    allowed={'png','svg','pdf','tiff','gltf','glb','json'}
    if any(f not in allowed for f in formats): raise AdvancedScientificVisualizationError('unsupported export format.')
    return {'ok':True,'scene_hash':scene['scene_hash'],'formats':formats,'camera_state':scene['camera'],'time_axis':scene.get('time_axis'),'vector_overlay_export':any(f in {'svg','pdf'} for f in formats),'scientific_scene_export':any(f in {'gltf','glb','json'} for f in formats),'automatic_file_write':False,'scientific_validity_certified':False}
def build_dashboard_panel(payload):
    scene=normalize_scene(payload.get('scene') or payload)['scene']; return {'ok':True,'panel':{'id':_text(payload.get('panel_id') or scene['id'],'panel_id',180,True),'title':scene['title'],'renderer':_text(payload.get('renderer') or 'webgpu','renderer',40,True),'figure_kind':'scientific-3d-4d-scene','figure_ref':f"lab:scene:{scene['id']}",'source_refs':scene['source_refs'],'spec':{'scene_hash':scene['scene_hash'],'camera':scene['camera'],'time_axis':scene.get('time_axis')}},'automatic_dashboard_mutation':False}
def build_core_visual_plan(payload):
    scene=normalize_scene(payload.get('scene') or payload)['scene']; session=_text(payload.get('session_id'),'session_id',240,True)
    return {'ok':True,'endpoint':'/v1/research/unified-runtime/visual-bindings','request_body':{'data':{'session_id':session,'visual_ref':f"lab:scene:{scene['id']}",'visual_type':'scientific-scene','scene_ref':f"lab:scene:{scene['id']}",'source_refs':scene['source_refs'],'metadata':{'lab_release_version':VERSION,'scene_hash':scene['scene_hash'],'dimension':'4d' if scene.get('time_axis') else '3d','underlying_scene_remains_authoritative_in_lab':True}}},'automatic_core_submission':False,'core_renders_scene':False}
def accessibility_audit(payload):
    scene=normalize_scene(payload.get('scene') or payload)['scene']; desc=_text(payload.get('alt_text'),'alt_text',4000,False)
    issues=[]
    if not desc: issues.append('missing-alt-text')
    if not scene.get('axes'): issues.append('missing-axes-metadata')
    return {'ok':True,'accessible':not issues,'issues':issues,'automatic_alt_text_inference':False,'requires_nonvisual_data_table':True}

def catalog():
    return {'ok':True,'version':VERSION,'engine_version':ENGINE_VERSION,'object_types':sorted(OBJECT_TYPES),'renderers':sorted(RENDERERS),'coordinate_frames':sorted(COORDINATE_FRAMES),'capabilities':['scientific-surfaces','explicit-mesh-topology','vector-fields','scalar-fields','volume-rendering-plans','isosurfaces','slice-planes','trajectories','streamlines','temporal-4d-scenes','uncertainty-geometry','camera-state-provenance','dashboard-panels','publication-exports','core-visual-bindings']}
def schema_info(): return {'ok':True,'schema':SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,'object_limit':MAX_OBJECTS,'vertex_limit':MAX_VERTICES,'frame_limit':MAX_FRAMES,'volume_dimension_limit':MAX_VOLUME_DIM,'api_route_count':21}
def manifest():
    return {'ok':True,'status':'advanced-3d-4d-scientific-visualization-ready','version':VERSION,'engine_version':ENGINE_VERSION,'features':{'scientific_surfaces':True,'explicit_mesh_topology':True,'vector_scalar_fields':True,'volume_rendering_plans':True,'trajectories_streamlines':True,'temporal_4d_scenes':True,'uncertainty_geometry':True,'camera_state_provenance':True,'publication_export_plans':True,'dashboard_integration':True,'core_visual_bridge':True},'boundaries':{'automatic_geometry_inference':False,'automatic_triangulation':False,'automatic_transfer_function':False,'automatic_threshold_selection':False,'automatic_time_inference':False,'automatic_uncertainty_inference':False,'automatic_core_submission':False,'core_renders_scene':False,'scientific_validity_certified':False,'truth_determined':False}}
def health():
    return {'ok':True,'status':'advanced-3d-4d-scientific-visualization-ready','version':VERSION,'engine_version':ENGINE_VERSION,'object_type_count':len(OBJECT_TYPES),'renderer_count':len(RENDERERS),'automatic_core_submission':False,'scientific_validity_certified':False}
