from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from itertools import product, combinations
import json
import math
import random
import re
from typing import Any

import numpy as np

VERSION = "0.30.1"
STUDY_SCHEMA = "sc-lab-parameter-study/0.30.1"
MATRIX_SCHEMA = "sc-lab-design-matrix/0.30.1"
ANALYSIS_SCHEMA = "sc-lab-design-analysis/0.30.1"
BATCH_SCHEMA = "sc-lab-design-batch/0.30.1"
BUNDLE_SCHEMA = "sc-lab-design-study-bundle/0.30.1"
MAX_FACTORS = 12
MAX_RUNS = 2000
MAX_LEVELS = 20

class DesignStudyError(ValueError):
    pass

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()

def _text(value: Any, limit: int = 4000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]

def _number(value: Any, default: float | None = None) -> float | None:
    try:
        n=float(value)
        return n if math.isfinite(n) else default
    except (TypeError, ValueError):
        return default

def _list(value: Any, limit: int) -> list[Any]:
    return list(value)[:limit] if isinstance(value, list) else []

def health() -> dict[str, Any]:
    return {
        "ok": True, "status": "ready", "version": VERSION,
        "studySchema": STUDY_SCHEMA, "matrixSchema": MATRIX_SCHEMA,
        "analysisSchema": ANALYSIS_SCHEMA, "batchSchema": BATCH_SCHEMA,
        "designTypes": ["full-factorial", "fractional-factorial", "latin-hypercube", "central-composite", "box-behnken", "one-factor-at-a-time"],
        "capabilities": {"factorialDesigns": True, "responseSurfaces": True, "latinHypercube": True, "sensitivity": True, "batchPlans": True, "optimalDesignRecommendations": True, "arbitraryCode": False, "serverBackedRegistry": False},
        "limits": {"factors": MAX_FACTORS, "runs": MAX_RUNS, "levelsPerFactor": MAX_LEVELS},
    }

def policies() -> dict[str, Any]:
    return {
        "version": VERSION,
        "designTypes": [
            {"id":"full-factorial","purpose":"complete interaction coverage for bounded factor sets"},
            {"id":"fractional-factorial","purpose":"screening with a reduced binary design"},
            {"id":"latin-hypercube","purpose":"space-filling exploration for continuous factors"},
            {"id":"central-composite","purpose":"quadratic response-surface estimation"},
            {"id":"box-behnken","purpose":"quadratic response surfaces without extreme corners"},
            {"id":"one-factor-at-a-time","purpose":"transparent local screening around a baseline"},
        ],
        "factorTypes": ["continuous", "integer", "categorical"],
        "objectives": ["explore", "maximize", "minimize", "target"],
        "registeredMethodsOnly": True,
        "arbitraryCode": False,
        "serverBackedRegistry": False,
    }

def normalize_factors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows=payload.get("factors") if isinstance(payload.get("factors"),list) else []
    if not rows: raise DesignStudyError("At least one factor is required.")
    if len(rows)>MAX_FACTORS: raise DesignStudyError(f"No more than {MAX_FACTORS} factors are allowed.")
    factors=[]
    for i,row in enumerate(rows,1):
        if not isinstance(row,dict): continue
        name=_text(row.get("name"),160)
        if not name: raise DesignStudyError(f"Factor {i} requires a name.")
        kind=_text(row.get("type"),40).lower() or "continuous"
        if kind not in {"continuous","integer","categorical"}: raise DesignStudyError(f"Unsupported factor type: {kind}")
        levels=[]
        if kind=="categorical":
            levels=[_text(x,200) for x in _list(row.get("levels"),MAX_LEVELS) if _text(x,200)]
            if len(levels)<2: raise DesignStudyError(f"Categorical factor {name} requires at least two levels.")
            low=high=None
        else:
            low=_number(row.get("low")); high=_number(row.get("high"))
            if low is None or high is None or high<=low: raise DesignStudyError(f"Factor {name} requires high > low.")
            raw_levels=_list(row.get("levels"),MAX_LEVELS)
            levels=[_number(x) for x in raw_levels]
            levels=[x for x in levels if x is not None]
            if not levels:
                count=max(2,min(MAX_LEVELS,int(row.get("levelCount") or 2)))
                levels=[low+(high-low)*j/(count-1) for j in range(count)]
            levels=sorted(set(int(round(x)) if kind=="integer" else float(x) for x in levels))
        factors.append({"id":_text(row.get("id"),160) or f"factor-{i}","name":name,"type":kind,"unit":_text(row.get("unit"),80),"low":low,"high":high,"levels":levels,"baseline":row.get("baseline")})
    if not factors: raise DesignStudyError("No valid factors were supplied.")
    return factors

def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    source=payload.get("study") if isinstance(payload.get("study"),dict) else payload
    factors=normalize_factors(source)
    record={
        "schema":STUDY_SCHEMA,"version":VERSION,"recordType":"parameter-study",
        "id":_text(source.get("id"),180) or f"parameter-study-{_hash(source)[:16]}",
        "title":_text(source.get("title"),500) or "Untitled parameter study",
        "experimentProtocolId":_text(source.get("experimentProtocolId"),180),
        "designType":_text(source.get("designType"),80).lower() or "full-factorial",
        "objective":_text(source.get("objective"),40).lower() or "explore",
        "responseName":_text(source.get("responseName"),200) or "response",
        "responseUnit":_text(source.get("responseUnit"),80),
        "targetValue":_number(source.get("targetValue")),
        "runBudget":max(2,min(MAX_RUNS,int(source.get("runBudget") or 20))),
        "seed":int(source.get("seed") or 42),
        "centerPoints":max(1,min(20,int(source.get("centerPoints") or 3))),
        "factors":factors,
        "methodId":_text(source.get("methodId"),200),
        "parameterMappings":source.get("parameterMappings") if isinstance(source.get("parameterMappings"),dict) else {},
        "notes":_text(source.get("notes"),8000),
        "createdAt":source.get("createdAt") or _now(),"updatedAt":_now(),
    }
    if record["designType"] not in {x["id"] for x in policies()["designTypes"]}: raise DesignStudyError("Unsupported design type.")
    record["studyHash"]=_hash({k:v for k,v in record.items() if k not in {"studyHash","updatedAt"}})
    return record

def _scale(f: dict[str, Any], coded: float) -> Any:
    if f["type"]=="categorical":
        levels=f["levels"]; idx=max(0,min(len(levels)-1,int(round((coded+1)*(len(levels)-1)/2))))
        return levels[idx]
    val=float(f["low"])+(coded+1.0)*(float(f["high"])-float(f["low"]))/2.0
    if f["type"]=="integer": return int(round(val))
    return val

def _row(factors: list[dict[str, Any]], values: list[Any], coded: list[float], index: int) -> dict[str, Any]:
    return {"run":index+1,"values":{f["name"]:values[i] for i,f in enumerate(factors)},"coded":{f["name"]:float(coded[i]) for i,f in enumerate(factors)},"response":None}

def _full_factorial(factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    level_lists=[]
    for f in factors:
        vals=f["levels"]
        if len(vals)>MAX_LEVELS: vals=vals[:MAX_LEVELS]
        level_lists.append(vals)
    count=math.prod(len(x) for x in level_lists)
    if count>MAX_RUNS: raise DesignStudyError(f"Full factorial design requires {count} runs; limit is {MAX_RUNS}.")
    rows=[]
    for i,vals in enumerate(product(*level_lists)):
        coded=[]
        for f,v in zip(factors,vals):
            if f["type"]=="categorical":
                idx=f["levels"].index(v); coded.append(-1+2*idx/max(1,len(f["levels"])-1))
            else: coded.append(-1+2*(float(v)-float(f["low"]))/(float(f["high"])-float(f["low"])))
        rows.append(_row(factors,list(vals),coded,i))
    return rows

def _fractional(factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(factors)<3: return _full_factorial(factors)
    for f in factors:
        if f["type"]=="categorical" and len(f["levels"])!=2: raise DesignStudyError("Fractional factorial requires two-level categorical factors.")
    coded_rows=[]
    for bits in product([-1.0,1.0],repeat=len(factors)-1):
        last=float(np.prod(bits))
        coded_rows.append(list(bits)+[last])
    if len(coded_rows)>MAX_RUNS: raise DesignStudyError("Fractional factorial exceeds the run limit.")
    return [_row(factors,[_scale(f,c[i]) for i,f in enumerate(factors)],c,j) for j,c in enumerate(coded_rows)]

def _lhs(factors: list[dict[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    rng=random.Random(seed); cols=[]
    for f in factors:
        if f["type"]=="categorical":
            vals=[f["levels"][i%len(f["levels"])] for i in range(n)]; rng.shuffle(vals)
            coded=[-1+2*f["levels"].index(v)/max(1,len(f["levels"])-1) for v in vals]
        else:
            bins=list(range(n)); rng.shuffle(bins); coded=[]; vals=[]
            for b in bins:
                u=(b+rng.random())/n; c=-1+2*u; coded.append(c); vals.append(_scale(f,c))
        cols.append((vals,coded))
    rows=[]
    for i in range(n): rows.append(_row(factors,[cols[j][0][i] for j in range(len(factors))],[cols[j][1][i] for j in range(len(factors))],i))
    return rows

def _central_composite(factors: list[dict[str, Any]], centers: int) -> list[dict[str, Any]]:
    k=len(factors); alpha=math.sqrt(k); coded=[list(x) for x in product([-1.0,1.0],repeat=k)]
    for i in range(k):
        a=[0.0]*k; a[i]=alpha; coded.append(a); b=[0.0]*k; b[i]=-alpha; coded.append(b)
    coded += [[0.0]*k for _ in range(centers)]
    if len(coded)>MAX_RUNS: raise DesignStudyError("Central composite design exceeds the run limit.")
    # Clamp axial points to declared bounds while retaining original coded values.
    return [_row(factors,[_scale(f,max(-1,min(1,c[i]))) for i,f in enumerate(factors)],c,j) for j,c in enumerate(coded)]

def _box_behnken(factors: list[dict[str, Any]], centers: int) -> list[dict[str, Any]]:
    k=len(factors)
    if k<3: raise DesignStudyError("Box-Behnken design requires at least three factors.")
    coded=[]
    for i,j in combinations(range(k),2):
        for a,b in product([-1.0,1.0],repeat=2):
            row=[0.0]*k; row[i]=a; row[j]=b; coded.append(row)
    coded += [[0.0]*k for _ in range(centers)]
    if len(coded)>MAX_RUNS: raise DesignStudyError("Box-Behnken design exceeds the run limit.")
    return [_row(factors,[_scale(f,c[i]) for i,f in enumerate(factors)],c,j) for j,c in enumerate(coded)]

def _ofat(factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    center=[0.0]*len(factors); coded=[center]
    for i in range(len(factors)):
        for val in (-1.0,1.0):
            row=[0.0]*len(factors); row[i]=val; coded.append(row)
    return [_row(factors,[_scale(f,c[i]) for i,f in enumerate(factors)],c,j) for j,c in enumerate(coded)]

def generate_design(payload: dict[str, Any]) -> dict[str, Any]:
    study=normalize_study(payload)
    kind=study["designType"]; factors=study["factors"]
    if kind=="full-factorial": rows=_full_factorial(factors)
    elif kind=="fractional-factorial": rows=_fractional(factors)
    elif kind=="latin-hypercube": rows=_lhs(factors,study["runBudget"],study["seed"])
    elif kind=="central-composite": rows=_central_composite(factors,study["centerPoints"])
    elif kind=="box-behnken": rows=_box_behnken(factors,study["centerPoints"])
    else: rows=_ofat(factors)
    matrix={"schema":MATRIX_SCHEMA,"version":VERSION,"recordType":"design-matrix","id":f"design-matrix-{_hash([study['studyHash'],kind,rows])[:16]}","title":f"{study['title']} — {kind}","studyId":study["id"],"studyHash":study["studyHash"],"designType":kind,"factorNames":[f["name"] for f in factors],"runCount":len(rows),"randomized":kind in {"latin-hypercube"},"seed":study["seed"],"rows":rows,"createdAt":_now()}
    matrix["matrixHash"]=_hash({k:v for k,v in matrix.items() if k!="matrixHash"})
    return {"ok":True,"study":study,"matrix":matrix}

def _design_terms(names: list[str], quadratic: bool) -> list[tuple[str, tuple[int,...]]]:
    terms=[("intercept",())]+[(n,(i,)) for i,n in enumerate(names)]
    if quadratic:
        terms += [(f"{n}^2",(i,i)) for i,n in enumerate(names)]
        terms += [(f"{names[i]}:{names[j]}",(i,j)) for i,j in combinations(range(len(names)),2)]
    return terms

def analyze_results(payload: dict[str, Any]) -> dict[str, Any]:
    matrix=payload.get("matrix") if isinstance(payload.get("matrix"),dict) else payload
    rows=_list(matrix.get("rows"),MAX_RUNS)
    names=_list(matrix.get("factorNames"),MAX_FACTORS)
    if not rows or not names: raise DesignStudyError("A design matrix with rows and factor names is required.")
    xs=[]; ys=[]; used=[]
    supplied=payload.get("responses")
    responses=supplied if isinstance(supplied,list) else [r.get("response") for r in rows]
    for i,row in enumerate(rows):
        y=_number(responses[i] if i<len(responses) else row.get("response"))
        if y is None: continue
        coded=row.get("coded") if isinstance(row.get("coded"),dict) else {}
        xs.append([float(coded.get(n,0.0)) for n in names]); ys.append(y); used.append(i+1)
    if len(ys)<max(3,len(names)+1): raise DesignStudyError("More completed responses are required for analysis.")
    quadratic=len(ys)>=1+2*len(names)+(len(names)*(len(names)-1))//2
    terms=_design_terms(names,quadratic)
    X=[]
    for row in xs:
        values=[]
        for _,idx in terms:
            if not idx: values.append(1.0)
            elif len(idx)==1: values.append(row[idx[0]])
            else: values.append(row[idx[0]]*row[idx[1]])
        X.append(values)
    Xn=np.asarray(X,dtype=float); yn=np.asarray(ys,dtype=float)
    coef,_,rank,_=np.linalg.lstsq(Xn,yn,rcond=None); pred=Xn@coef; resid=yn-pred
    ss_res=float(np.sum(resid**2)); ss_tot=float(np.sum((yn-np.mean(yn))**2)); r2=1.0-ss_res/ss_tot if ss_tot>0 else 1.0
    coeffs=[{"term":terms[i][0],"coefficient":float(coef[i]),"absoluteEffect":abs(float(coef[i]))} for i in range(len(terms))]
    main=[c for c in coeffs if c["term"] in names]; main.sort(key=lambda x:x["absoluteEffect"],reverse=True)
    objective=_text(payload.get("objective"),40).lower() or "maximize"
    target=_number(payload.get("targetValue"))
    if objective=="minimize": best_idx=int(np.argmin(yn))
    elif objective=="target" and target is not None: best_idx=int(np.argmin(np.abs(yn-target)))
    else: best_idx=int(np.argmax(yn))
    best_row=rows[used[best_idx]-1]
    analysis={"schema":ANALYSIS_SCHEMA,"version":VERSION,"recordType":"design-analysis","id":f"design-analysis-{_hash([matrix.get('matrixHash'),ys])[:16]}","title":f"Analysis of {matrix.get('title') or 'design study'}","matrixId":matrix.get("id"),"matrixHash":matrix.get("matrixHash"),"responseName":_text(payload.get("responseName"),200) or "response","objective":objective,"completedRunCount":len(ys),"model":"quadratic-response-surface" if quadratic else "linear-main-effects","rank":int(rank),"rSquared":r2,"rmse":math.sqrt(ss_res/max(1,len(ys))),"coefficients":coeffs,"sensitivity":main,"predicted":[float(x) for x in pred],"residuals":[float(x) for x in resid],"bestObserved":{"run":used[best_idx],"response":float(yn[best_idx]),"values":best_row.get("values",{}),"coded":best_row.get("coded",{})},"warnings":[] if rank==len(terms) else ["The fitted design matrix is rank deficient; interpret coefficients cautiously."],"createdAt":_now()}
    analysis["analysisHash"]=_hash({k:v for k,v in analysis.items() if k!="analysisHash"})
    return analysis

def recommend_design(payload: dict[str, Any]) -> dict[str, Any]:
    factors=normalize_factors(payload)
    purpose=_text(payload.get("purpose"),80).lower() or "screening"
    budget=max(2,min(MAX_RUNS,int(payload.get("runBudget") or 20)))
    continuous=sum(1 for f in factors if f["type"]!="categorical")
    k=len(factors)
    if purpose in {"optimization","response-surface","quadratic"}:
        if k>=3 and 4*math.comb(k,2)+3<=budget: choice="box-behnken"
        else: choice="central-composite"
    elif purpose in {"space-filling","exploration","uncertainty"}: choice="latin-hypercube"
    elif k<=4 and math.prod(len(f["levels"]) for f in factors)<=budget: choice="full-factorial"
    elif k>=3: choice="fractional-factorial"
    else: choice="one-factor-at-a-time"
    reasons={"full-factorial":"The complete design fits within the stated run budget.","fractional-factorial":"A reduced binary design provides efficient screening for several factors.","latin-hypercube":"A space-filling design covers continuous ranges without an exponential run count.","central-composite":"Axial and center points support a quadratic response surface.","box-behnken":"Pairwise edge-midpoint runs support quadratic optimization without extreme corners.","one-factor-at-a-time":"A compact baseline-centered design is appropriate for a small local study."}
    return {"ok":True,"version":VERSION,"recommendedDesign":choice,"reason":reasons[choice],"factorCount":k,"continuousFactorCount":continuous,"runBudget":budget,"alternatives":[x["id"] for x in policies()["designTypes"] if x["id"]!=choice]}

def build_batch(payload: dict[str, Any]) -> dict[str, Any]:
    matrix=payload.get("matrix") if isinstance(payload.get("matrix"),dict) else {}
    rows=_list(matrix.get("rows"),MAX_RUNS); method=_text(payload.get("methodId"),200)
    if not method: raise DesignStudyError("A registered method ID is required for a batch plan.")
    mappings=payload.get("parameterMappings") if isinstance(payload.get("parameterMappings"),dict) else {}
    jobs=[]
    for row in rows:
        parameters={}
        for factor,value in (row.get("values") or {}).items(): parameters[mappings.get(factor,factor)]=value
        jobs.append({"methodId":method,"projectId":_text(payload.get("projectId"),180),"parameters":parameters,"requestedOutputs":["summary","values"],"designRun":row.get("run"),"designMatrixId":matrix.get("id")})
    batch={"schema":BATCH_SCHEMA,"version":VERSION,"recordType":"design-batch","id":f"design-batch-{_hash([method,matrix.get('matrixHash')])[:16]}","title":_text(payload.get("title"),500) or f"Batch for {matrix.get('title') or method}","matrixId":matrix.get("id"),"matrixHash":matrix.get("matrixHash"),"methodId":method,"jobCount":len(jobs),"jobs":jobs,"execution":"queue-handoff-only","createdAt":_now()}
    batch["batchHash"]=_hash({k:v for k,v in batch.items() if k!="batchHash"})
    return batch

def verify(payload: dict[str, Any]) -> dict[str, Any]:
    record=payload.get("record") if isinstance(payload.get("record"),dict) else payload
    key=next((k for k in ("batchHash","analysisHash","matrixHash","studyHash") if record.get(k)),None)
    if not key: raise DesignStudyError("A supported design-study record hash is required.")
    excluded={key}
    if key=="studyHash": excluded.add("updatedAt")
    actual=_hash({k:v for k,v in record.items() if k not in excluded})
    return {"ok":actual==record[key],"expectedHash":record[key],"actualHash":actual,"verifiedAt":_now()}
