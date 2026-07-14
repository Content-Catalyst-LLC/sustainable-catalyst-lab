from fastapi import APIRouter,HTTPException
from .genomic_visualization_comparison import contract,execute
router=APIRouter(tags=["genomic-visualization"])
@router.get("/v1/genomics/visualization/methods")
def methods():return contract()
@router.get("/v1/genomics/visualization/health")
def health():
 c=contract();ok=c.get("version")=="0.24.2" and len(c.get("modes",[]))==8 and len(c.get("analysisMethods",[]))==8 and len(c.get("benchmarks",[]))==8
 return {"ok":ok,"status":"ready" if ok else "contract-incomplete","release":"0.24.2","modeCount":len(c.get("modes",[])),"analysisMethodCount":len(c.get("analysisMethods",[])),"benchmarkCount":len(c.get("benchmarks",[]))}
@router.post("/v1/genomics/visualization/analyze")
def analyze(payload):
 try:return execute(str(payload.get("methodId") or ""),payload.get("inputs") or {})
 except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
