from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any

VERSION = "0.83.0"
ENGINE_VERSION = "2.10.0"
RENDERER_OVERLAY = "figure-provenance"
PROVENANCE_SCHEMA = "sc-lab-figure-provenance/0.83.0"
FIGURE_SCHEMA = "sc-lab-provenance-aware-figure/0.83.0"
EXPORT_SCHEMA = "sc-lab-figure-export-manifest/0.83.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.83.0"
MAX_LINEAGE_ITEMS = 512
MAX_FIGURES = 128

class FigureProvenanceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _hash(value: Any) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
    return sha256(payload.encode("utf-8")).hexdigest()

def _identifier(value: Any, fallback: str) -> str:
    text=str(value or fallback).strip()
    if not text: raise FigureProvenanceError("identifier must not be empty")
    return text[:200]

def _fingerprint(value: Any, label: str, required: bool=True) -> str|None:
    if value is None and not required: return None
    text=str(value or "").strip().lower()
    if not text and required: raise FigureProvenanceError(f"{label} fingerprint is required")
    if text and not re_full_hex(text): raise FigureProvenanceError(f"{label} fingerprint must be a 64-character SHA-256 hex digest")
    return text or None

def re_full_hex(text:str)->bool:
    return len(text)==64 and all(c in '0123456789abcdef' for c in text)

def _lineage_items(items:Any, kind:str)->list[dict[str,Any]]:
    if items is None: return []
    if not isinstance(items,list): raise FigureProvenanceError(f"{kind} lineage must be an array")
    if len(items)>MAX_LINEAGE_ITEMS: raise FigureProvenanceError(f"{kind} lineage exceeds {MAX_LINEAGE_ITEMS}",413)
    out=[]
    for i,item in enumerate(items):
        if not isinstance(item,dict): raise FigureProvenanceError(f"{kind}[{i}] must be an object")
        fid=_fingerprint(item.get('fingerprint'),f"{kind}[{i}]")
        entry={"id":_identifier(item.get('id'),f"{kind}-{i+1}"),"fingerprint":fid}
        for key in ('version','uri','method','role','label','units','schema','software','parametersFingerprint'):
            if item.get(key) is not None: entry[key]=deepcopy(item[key])
        if item.get('parameters') is not None:
            entry['parametersFingerprint']=_hash(item['parameters'])
        out.append(entry)
    return out

def normalize_provenance(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise FigureProvenanceError("provenance must be an object")
    datasets=_lineage_items(payload.get('datasets'), 'datasets')
    transformations=_lineage_items(payload.get('transformations'), 'transformations')
    models=_lineage_items(payload.get('models'), 'models')
    annotations=_lineage_items(payload.get('annotations'), 'annotations')
    uncertainty=_lineage_items(payload.get('uncertainty'), 'uncertainty')
    selections=_lineage_items(payload.get('selections'), 'selections')
    renderer=deepcopy(payload.get('renderer') or {})
    if not isinstance(renderer,dict): raise FigureProvenanceError("renderer must be an object")
    if not renderer.get('id'): raise FigureProvenanceError("renderer.id is required")
    renderer={"id":_identifier(renderer.get('id'),'renderer'),"version":str(renderer.get('version') or 'unknown')[:80],"backend":str(renderer.get('backend') or renderer.get('id'))[:80]}
    state=deepcopy(payload.get('state') or {})
    if not isinstance(state,dict): raise FigureProvenanceError("state must be an object")
    state_fp=_hash(state)
    source_chain=[x['fingerprint'] for group in (datasets,transformations,models,annotations,uncertainty,selections) for x in group]
    out={
        "schema":PROVENANCE_SCHEMA,"version":VERSION,
        "datasets":datasets,"transformations":transformations,"models":models,
        "annotations":annotations,"uncertainty":uncertainty,"selections":selections,
        "renderer":renderer,"state":state,"stateFingerprint":state_fp,
        "sourceFingerprintChain":source_chain,
        "createdAt":str(payload.get('createdAt') or datetime.now(timezone.utc).isoformat()),
        "createdBy":deepcopy(payload.get('createdBy') or {"type":"human-or-governed-runtime"}),
        "notes":str(payload.get('notes') or '')[:2000],
        "boundaries":{"automaticSourceInference":False,"automaticProvenanceRepair":False,"silentFingerprintOverride":False,"hiddenTransformations":False,"unverifiableClaimAsVerified":False,"arbitraryCode":False}
    }
    out['fingerprint']=_hash({k:v for k,v in out.items() if k!='fingerprint'})
    return out

def attach_provenance(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict) or not isinstance(payload.get('baseFigure'),dict): raise FigureProvenanceError("baseFigure is required")
    base=deepcopy(payload['baseFigure'])
    upstream_fp=str(base.get('fingerprint') or '').lower()
    actual_base_fp=upstream_fp if re_full_hex(upstream_fp) else _hash(base)
    expected=payload.get('baseFigureFingerprint')
    if expected is not None and _fingerprint(expected,'baseFigure') != actual_base_fp:
        raise FigureProvenanceError("baseFigureFingerprint does not match the supplied base figure")
    provenance=normalize_provenance(payload.get('provenance') or {})
    out={"schema":FIGURE_SCHEMA,"version":VERSION,"engineVersion":ENGINE_VERSION,"rendererOverlay":RENDERER_OVERLAY,
         "id":_identifier(payload.get('id'),'provenance-aware-figure'),"title":str(payload.get('title') or base.get('title') or 'Provenance-aware scientific figure')[:240],
         "baseFigure":base,"baseFigureFingerprint":actual_base_fp,"baseRenderer":base.get('renderer'),"figureProvenance":provenance,
         "lineageFingerprint":_hash({"baseFigureFingerprint":actual_base_fp,"provenanceFingerprint":provenance['fingerprint']}),
         "boundaries":{"baseFigureMutation":False,"automaticSourceInference":False,"automaticProvenanceRepair":False,"silentFingerprintOverride":False,"hiddenTransformations":False,"unverifiableClaimAsVerified":False}}
    out['fingerprint']=_hash({k:v for k,v in out.items() if k!='fingerprint'})
    return out

def verify_provenance(payload:dict[str,Any])->dict[str,Any]:
    figure=payload.get('figure') if isinstance(payload,dict) and isinstance(payload.get('figure'),dict) else payload
    if not isinstance(figure,dict): raise FigureProvenanceError("figure must be an object")
    checks=[]
    base=figure.get('baseFigure'); declared=figure.get('baseFigureFingerprint')
    upstream_fp=str(base.get('fingerprint') or '').lower() if isinstance(base,dict) else ''
    base_actual=(upstream_fp if re_full_hex(upstream_fp) else _hash(base)) if isinstance(base,dict) else None
    checks.append({"check":"baseFigureFingerprint","ok":bool(base_actual and declared==base_actual),"declared":declared,"actual":base_actual})
    prov=figure.get('figureProvenance'); prov_actual=_hash({k:v for k,v in prov.items() if k!='fingerprint'}) if isinstance(prov,dict) else None
    prov_declared=prov.get('fingerprint') if isinstance(prov,dict) else None
    checks.append({"check":"provenanceFingerprint","ok":bool(prov_actual and prov_declared==prov_actual),"declared":prov_declared,"actual":prov_actual})
    lineage_actual=_hash({"baseFigureFingerprint":base_actual,"provenanceFingerprint":prov_actual}) if base_actual and prov_actual else None
    checks.append({"check":"lineageFingerprint","ok":bool(lineage_actual and figure.get('lineageFingerprint')==lineage_actual),"declared":figure.get('lineageFingerprint'),"actual":lineage_actual})
    complete=all(c['ok'] for c in checks)
    return {"ok":True,"verified":complete,"status":"verified" if complete else "lineage-mismatch","checks":checks,"boundaries":{"automaticProvenanceRepair":False,"unverifiableClaimAsVerified":False}}

def build_export_manifest(payload:dict[str,Any])->dict[str,Any]:
    figure=payload.get('figure') if isinstance(payload,dict) else None
    if not isinstance(figure,dict): raise FigureProvenanceError("figure is required")
    verification=verify_provenance(figure)
    fmt=str(payload.get('format') or 'json').lower()
    if fmt not in {'json','svg','png','pdf','tiff'}: raise FigureProvenanceError("unsupported export format")
    export={"schema":EXPORT_SCHEMA,"version":VERSION,"format":fmt,"figureFingerprint":str(figure.get('fingerprint') or _hash(figure)),"baseFigureFingerprint":figure.get('baseFigureFingerprint'),"lineageFingerprint":figure.get('lineageFingerprint'),"provenanceVerified":verification['verified'],"verification":verification,"renderer":deepcopy((figure.get('figureProvenance') or {}).get('renderer') or {}),"dimensions":deepcopy(payload.get('dimensions') or {}),"exportedAt":str(payload.get('exportedAt') or datetime.now(timezone.utc).isoformat()),"boundaries":{"exportDoesNotAlterScientificLineage":True,"automaticProvenanceRepair":False}}
    export['fingerprint']=_hash({k:v for k,v in export.items() if k!='fingerprint'})
    return {"ok":True,"exportManifest":export}

def build_workspace(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise FigureProvenanceError("workspace must be an object")
    raw=payload.get('figures') or []
    if not isinstance(raw,list) or len(raw)>MAX_FIGURES: raise FigureProvenanceError(f"figures must contain at most {MAX_FIGURES} entries")
    figures=[]
    for i,item in enumerate(raw):
        if not isinstance(item,dict): raise FigureProvenanceError(f"figures[{i}] must be an object")
        figures.append(attach_provenance(item) if item.get('baseFigure') and item.get('provenance') is not None else deepcopy(item))
    workspace={"schema":WORKSPACE_SCHEMA,"version":VERSION,"engineVersion":ENGINE_VERSION,"id":_identifier(payload.get('id'),'provenance-figure-workspace'),"title":str(payload.get('title') or 'Provenance-aware figure workspace')[:240],"figures":figures,"figureCount":len(figures),"compatibility":{"v0820Uncertainty":True,"v0810Markup":True,"v0800Spatial":True,"v0790LinkedViews":True,"v0780TimeParameter":True,"v0770Scene":True,"v0760Adaptive":True,"v0750DataBinding":True},"boundaries":{"automaticSourceInference":False,"automaticProvenanceRepair":False,"hiddenTransformations":False}}
    workspace['fingerprint']=_hash({k:v for k,v in workspace.items() if k!='fingerprint'})
    return {"ok":True,"workspace":workspace}

def health()->dict[str,Any]:
    return {"ok":True,"status":"provenance-aware-scientific-figures-ready","version":VERSION,"engineVersion":ENGINE_VERSION,"rendererOverlay":RENDERER_OVERLAY,
        "datasetFingerprinting":True,"transformationFingerprinting":True,"modelFingerprinting":True,"rendererProvenance":True,"interactionStateFingerprinting":True,"annotationLineage":True,"uncertaintyLineage":True,"exportManifest":True,"lineageVerification":True,"baseFigurePreservation":True,
        "v0820UncertaintyCompatibility":True,"v0810MarkupCompatibility":True,"v0800SpatialCompatibility":True,"v0790LinkedViewsCompatibility":True,"v0780TimeParameterCompatibility":True,"v0770SceneCompatibility":True,"v0760AdaptiveCompatibility":True,"v0750DataBindingCompatibility":True,
        "automaticSourceInference":False,"automaticProvenanceRepair":False,"silentFingerprintOverride":False,"hiddenTransformations":False,"unverifiableClaimAsVerified":False,"arbitraryCode":False,"limits":{"lineageItems":MAX_LINEAGE_ITEMS,"figures":MAX_FIGURES}}

def policies()->dict[str,Any]: return health()
