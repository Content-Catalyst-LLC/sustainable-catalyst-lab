from __future__ import annotations
from typing import Any
from fastapi import APIRouter,HTTPException
from .genetics_genomics_sequence_analysis import GenomicError,batch_execute,catalog,execute
router=APIRouter(tags=["genetics-genomics-sequence-analysis"])
@router.get("/v1/genomics/methods")
def methods()->dict[str,Any]:return catalog()
@router.get("/v1/genomics/health")
def health()->dict[str,Any]:
 c=catalog();ok=c.get("version")=="0.24.0" and len(c.get("methods",[]))==48 and len(c.get("benchmarks",[]))==48 and len(c.get("categories",[]))==8
 return {"ok":ok,"status":"ready" if ok else "contract-incomplete","release":"0.24.0","methodCount":len(c.get("methods",[])),"benchmarkCount":len(c.get("benchmarks",[])),"categoryCount":len(c.get("categories",[]))}
@router.post("/v1/genomics/run")
def run(payload:dict[str,Any])->dict[str,Any]:
 try:return execute(str(payload.get("methodId") or ""),payload.get("inputs") or {})
 except GenomicError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
@router.post("/v1/genomics/batch")
def batch(payload:dict[str,Any])->dict[str,Any]:return batch_execute(payload.get("rows") or [])
