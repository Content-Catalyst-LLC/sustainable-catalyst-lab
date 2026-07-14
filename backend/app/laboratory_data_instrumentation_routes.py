from __future__ import annotations
from typing import Any
from fastapi import APIRouter,HTTPException
from .laboratory_data_instrumentation import InstrumentationError,catalog,execute,create_record,create_manifest,create_custody_event,verify_custody,normalize_measurements
router=APIRouter(tags=['laboratory-data-instrumentation'])
@router.get('/v1/instrumentation/methods')
def methods():return catalog()
@router.get('/v1/instrumentation/health')
def health():
 c=catalog();ok=c.get('version')=='0.25.0' and len(c.get('methods',[]))==48 and len(c.get('benchmarks',[]))==48 and len(c.get('categories',[]))==8
 return {'ok':ok,'status':'ready' if ok else 'contract-incomplete','release':'0.25.0','methodCount':len(c.get('methods',[])),'benchmarkCount':len(c.get('benchmarks',[])),'categoryCount':len(c.get('categories',[]))}
@router.post('/v1/instrumentation/run')
def run(p:dict[str,Any]):
 try:return execute(str(p.get('methodId') or ''),p.get('inputs') or {})
 except InstrumentationError as e:raise HTTPException(status_code=422,detail=str(e)) from e
@router.post('/v1/instrumentation/records')
def record(p:dict[str,Any]):return create_record(str(p.get('recordType') or ''),p.get('data') or {},p.get('metadata') or {})
@router.post('/v1/instrumentation/manifest')
def manifest(p:dict[str,Any]):return create_manifest(p.get('records') or [])
@router.post('/v1/instrumentation/custody')
def custody(p:dict[str,Any]):return create_custody_event(str(p.get('sampleId') or ''),str(p.get('action') or ''),str(p.get('actor') or ''),str(p.get('location') or ''),p.get('previousHash'),p.get('notes'))
@router.post('/v1/instrumentation/custody/verify')
def verify(p:dict[str,Any]):return verify_custody(p.get('events') or [])
@router.post('/v1/instrumentation/measurements/ingest')
def ingest(p:dict[str,Any]):return normalize_measurements(p.get('rows') or [],p.get('unitMap') or {})
