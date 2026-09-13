from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np
from fastapi import APIRouter, HTTPException

from .probabilistic_analysis import _transform, _unit_design

LAB_VERSION = "0.103.0"
ENERGY_SYSTEMS_VERSION = "1.6.0"
WORKBENCH_VERSION = "6.3.0"
FRAMEWORK_SCHEMA = "sc-energy-reliability-uncertainty-framework/1.0"
PLAN_SCHEMA = "sc-energy-reliability-uncertainty-plan/1.0"
ANALYSIS_SCHEMA = "sc-energy-reliability-uncertainty-analysis/1.0"
VALIDATION_SCHEMA = "sc-energy-reliability-uncertainty-validation/1.0"
WORKBENCH_HANDOFF_SCHEMA = "sc-energy-runtime-handoff/1.0"
WORKBENCH_CONTRACT = "sc-energy-runtime-workbench-handoff/1.0"
WORKBENCH_RESULT_SCHEMA = "sc-energy-workbench-result-packet/1.0"
DESIGNS={"monte-carlo","latin-hypercube"}
DISTRIBUTIONS={"uniform","normal","lognormal","triangular"}
PARAMETERS={"demand_multiplier","renewable_output_multiplier","storage_availability_multiplier","firm_forced_outage_rate_pct"}
MIN_SAMPLES=8
MAX_SAMPLES=4096
BOUNDARY=(
    "Lab performs seeded uncertainty design around caller-supplied adequacy scenarios. It does not infer "
    "demand, renewable output, storage availability, forced-outage rates, or distributions; it does not call "
    "Workbench automatically, predict outages, declare a real grid reliable/unreliable, rank alternatives, or persist studies automatically."
)
router=APIRouter(prefix="/v1/energy-reliability",tags=["energy-grid-storage-reliability"])

class ReliabilityModelingError(ValueError): pass

def _canonical(x:Any)->str: return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _digest(x:Any,prefix:str)->str: return prefix+sha256(_canonical(x).encode()).hexdigest()[:20]

def _finite(v:Any,label:str)->float:
    try: n=float(v)
    except (TypeError,ValueError) as exc: raise ReliabilityModelingError(f"{label} must be numeric") from exc
    if not math.isfinite(n): raise ReliabilityModelingError(f"{label} must be finite")
    return n

def _series(v:Any,label:str)->list[float]:
    if not isinstance(v,list) or not v: raise ReliabilityModelingError(f"{label} must be a non-empty array")
    if len(v)>100000: raise ReliabilityModelingError(f"{label} may contain at most 100000 values")
    out=[_finite(x,f"{label}[{i}]") for i,x in enumerate(v)]
    if any(x<0 for x in out): raise ReliabilityModelingError(f"{label} values must be zero or greater")
    return out

def _distribution(raw:dict[str,Any])->dict[str,Any]:
    if not isinstance(raw,dict): raise ReliabilityModelingError("uncertainty variables must be objects")
    name=str(raw.get("name") or "").strip()
    if name not in PARAMETERS: raise ReliabilityModelingError(f"unsupported uncertainty parameter: {name}")
    d=str(raw.get("distribution") or "").lower().strip()
    if d not in DISTRIBUTIONS: raise ReliabilityModelingError(f"unsupported distribution for {name}: {d}")
    rec={"symbol":name,"label":str(raw.get("label") or name),"unit":str(raw.get("unit") or ""),"distribution":d}
    if d=="uniform":
        lo=_finite(raw.get("low"),f"{name}.low"); hi=_finite(raw.get("high"),f"{name}.high")
        if hi<=lo: raise ReliabilityModelingError(f"{name}.high must exceed low")
        rec.update(low=lo,high=hi)
    elif d=="normal":
        mean=_finite(raw.get("mean"),f"{name}.mean"); sd=_finite(raw.get("stdDev"),f"{name}.stdDev")
        if sd<=0: raise ReliabilityModelingError(f"{name}.stdDev must be positive")
        rec.update(mean=mean,stdDev=sd)
    elif d=="lognormal":
        ml=_finite(raw.get("meanLog"),f"{name}.meanLog"); sl=_finite(raw.get("stdLog"),f"{name}.stdLog")
        if sl<=0: raise ReliabilityModelingError(f"{name}.stdLog must be positive")
        rec.update(meanLog=ml,stdLog=sl)
    else:
        lo=_finite(raw.get("low"),f"{name}.low"); mode=_finite(raw.get("mode"),f"{name}.mode"); hi=_finite(raw.get("high"),f"{name}.high")
        if hi<=lo or not lo<=mode<=hi: raise ReliabilityModelingError(f"{name} triangular bounds are invalid")
        rec.update(low=lo,mode=mode,high=hi)
    return rec

def _normalize(body:dict[str,Any])->dict[str,Any]:
    if not isinstance(body,dict): raise ReliabilityModelingError("request must be an object")
    study_id=str(body.get("study_id") or "").strip()
    if not study_id: raise ReliabilityModelingError("study_id is required")
    b=body.get("baseline")
    if not isinstance(b,dict): raise ReliabilityModelingError("baseline is required")
    demand=_series(b.get("demand_kw_series"),"baseline.demand_kw_series")
    renewable=_series(b.get("renewable_generation_kw_series"),"baseline.renewable_generation_kw_series")
    storage=_series(b.get("storage_discharge_available_kw_series"),"baseline.storage_discharge_available_kw_series")
    if not (len(demand)==len(renewable)==len(storage)): raise ReliabilityModelingError("baseline time series must have the same length")
    firm=_finite(b.get("firm_capacity_kw"),"baseline.firm_capacity_kw")
    dt=_finite(b.get("timestep_hours"),"baseline.timestep_hours")
    if firm<0 or dt<=0: raise ReliabilityModelingError("firm_capacity_kw must be nonnegative and timestep_hours positive")
    u=body.get("uncertainty")
    if not isinstance(u,dict): raise ReliabilityModelingError("uncertainty is required")
    variables=[_distribution(x) for x in (u.get("variables") or [])]
    if not variables: raise ReliabilityModelingError("uncertainty.variables must be non-empty")
    names=[x["symbol"] for x in variables]
    if len(set(names))!=len(names): raise ReliabilityModelingError("uncertainty variable names must be unique")
    design=u.get("design") if isinstance(u.get("design"),dict) else {}
    method=str(design.get("method") or "").lower().strip()
    if method not in DESIGNS: raise ReliabilityModelingError("uncertainty.design.method must be monte-carlo or latin-hypercube")
    try: samples=int(design.get("samples")); seed=int(design.get("seed"))
    except (TypeError,ValueError) as exc: raise ReliabilityModelingError("samples and seed must be integers") from exc
    if samples<MIN_SAMPLES or samples>MAX_SAMPLES: raise ReliabilityModelingError(f"samples must be between {MIN_SAMPLES} and {MAX_SAMPLES}")
    return {"study_id":study_id,"question":str(body.get("question") or ""),"baseline":{"demand_kw_series":demand,"renewable_generation_kw_series":renewable,"storage_discharge_available_kw_series":storage,"firm_capacity_kw":firm,"timestep_hours":dt},"uncertainty":{"variables":variables,"design":{"method":method,"samples":samples,"seed":seed}},"provenance":list(body.get("provenance") or []),"review":body.get("review") if isinstance(body.get("review"),dict) else {"human_review_required":True}}

def framework()->dict[str,Any]:
    return {"ok":True,"schema":FRAMEWORK_SCHEMA,"version":ENERGY_SYSTEMS_VERSION,"lab_version":LAB_VERSION,"workbench_required_version":WORKBENCH_VERSION,"designs":sorted(DESIGNS),"distributions":sorted(DISTRIBUTIONS),"uncertain_parameters":sorted(PARAMETERS),"limits":{"minimum_samples":MIN_SAMPLES,"maximum_samples":MAX_SAMPLES},"capabilities":{"seeded_adequacy_sampling":True,"workbench_adequacy_timeseries_requests":True,"ens_distribution_analysis":True,"loss_of_load_probability_analysis":True,"automatic_workbench_execution":False,"automatic_persistence":False,"outage_prediction":False,"real_grid_reliability_declaration":False,"automatic_ranking":False,"automatic_recommendation":False},"boundary":BOUNDARY}

def plan(body:dict[str,Any])->dict[str,Any]:
    study=_normalize(body); vars=study["uncertainty"]["variables"]; d=study["uncertainty"]["design"]
    unit=_unit_design(d["method"],d["samples"],len(vars),d["seed"])
    matrix=np.column_stack([_transform(unit[:,i],spec) for i,spec in enumerate(vars)])
    base=study["baseline"]; requests=[]; eval_map=[]
    for i,row in enumerate(matrix):
        sample={spec["symbol"]:float(row[j]) for j,spec in enumerate(vars)}
        dm=sample.get("demand_multiplier",1.0); rm=sample.get("renewable_output_multiplier",1.0); sm=sample.get("storage_availability_multiplier",1.0); fo=sample.get("firm_forced_outage_rate_pct",0.0)
        if dm<0 or rm<0 or sm<0: raise ReliabilityModelingError("sampled multipliers must be zero or greater")
        if fo<0 or fo>100: raise ReliabilityModelingError("sampled firm_forced_outage_rate_pct must remain between 0 and 100")
        demand=[v*dm for v in base["demand_kw_series"]]
        firm_available=base["firm_capacity_kw"]*(1-fo/100.0)
        available=[firm_available+r*rm+s*sm for r,s in zip(base["renewable_generation_kw_series"],base["storage_discharge_available_kw_series"])]
        req_id=_digest({"study":study["study_id"],"index":i,"sample":sample},"era-eval-")
        requests.append({"request_id":req_id,"operation":"adequacy-timeseries","inputs":{"demand_kw_series":demand,"available_capacity_kw_series":available,"timestep_hours":base["timestep_hours"]},"source_refs":[],"assumptions":["Availability transformation uses only caller-supplied baseline series and sampled explicit parameters."]})
        eval_map.append({"evaluation_index":i,"request_id":req_id,"sampled_parameters":sample})
    payload={"identity":{"study_id":study["study_id"],"question":study["question"]},"numeric_registry":{"calculation_requests":[]},"energy_balance":{"calculation_requests":[]},"economics":{"calculation_requests":[]},"bioenergy_and_carbon":{"calculation_requests":[]},"grid_storage_reliability":{"calculation_requests":requests},"provenance":study["provenance"],"review":study["review"]}
    plan_id=_digest({"study":study,"evaluation_map":eval_map},"era-plan-")
    handoff={"schema":WORKBENCH_HANDOFF_SCHEMA,"version":ENERGY_SYSTEMS_VERSION,"packet":{"handoff_id":plan_id+"-workbench","source":{"product":"Lab","subsystem":"Grid, Storage & Reliability Uncertainty","version":ENERGY_SYSTEMS_VERSION},"target":{"key":"workbench","product":"Workbench","consumer_contract":WORKBENCH_CONTRACT},"contract_refs":["energy-grid-storage-reliability/1.0","energy-reliability-uncertainty/1.0"],"payload":payload}}
    return {"ok":True,"schema":PLAN_SCHEMA,"version":ENERGY_SYSTEMS_VERSION,"lab_version":LAB_VERSION,"plan_id":plan_id,"study":study,"evaluation_count":len(eval_map),"evaluation_map":eval_map,"workbench":{"required_version":WORKBENCH_VERSION,"execute_route":"/v1/energy-runtime/execute","handoff":handoff,"execution_performed":False},"persistence":{"performed":False},"boundary":BOUNDARY}

def _value(result:dict[str,Any],key:str)->float:
    try: return float((result.get("output") or {})[key])
    except (KeyError,TypeError,ValueError) as exc: raise ReliabilityModelingError(f"Workbench adequacy result missing numeric {key}") from exc

def analyze(body:dict[str,Any])->dict[str,Any]:
    if not isinstance(body,dict): raise ReliabilityModelingError("analysis request must be an object")
    plan_obj=body.get("plan"); wb=body.get("workbench_result")
    if not isinstance(plan_obj,dict) or plan_obj.get("schema")!=PLAN_SCHEMA: raise ReliabilityModelingError(f"plan must be {PLAN_SCHEMA}")
    if not isinstance(wb,dict) or wb.get("schema")!=WORKBENCH_RESULT_SCHEMA: raise ReliabilityModelingError(f"workbench_result must be {WORKBENCH_RESULT_SCHEMA}")
    if str(wb.get("workbench_version"))!=WORKBENCH_VERSION: raise ReliabilityModelingError(f"workbench_result.workbench_version must be {WORKBENCH_VERSION}")
    by_id={str(r.get("request_id")):r for r in wb.get("results",[]) if isinstance(r,dict)}
    ens=[]; lolh=[]; events=[]; served=[]
    for row in plan_obj.get("evaluation_map") or []:
        r=by_id.get(row["request_id"])
        if not r or r.get("operation")!="adequacy-timeseries": raise ReliabilityModelingError(f"missing adequacy-timeseries result for {row['request_id']}")
        ens.append(_value(r,"energy_not_served_kwh")); lolh.append(_value(r,"loss_of_load_hours")); events.append(_value(r,"loss_of_load_events")); served.append(_value(r,"served_energy_pct"))
    if not ens: raise ReliabilityModelingError("no evaluation results")
    def summary(vals:list[float])->dict[str,float]:
        a=np.asarray(vals,dtype=float); return {"mean":float(np.mean(a)),"median":float(np.median(a)),"p05":float(np.quantile(a,.05)),"p95":float(np.quantile(a,.95)),"minimum":float(np.min(a)),"maximum":float(np.max(a))}
    output={"energy_not_served_kwh":summary(ens),"loss_of_load_hours":summary(lolh),"loss_of_load_events":summary(events),"served_energy_pct":summary(served),"probability_any_energy_not_served":float(np.mean(np.asarray(ens)>0)),"probability_any_loss_of_load":float(np.mean(np.asarray(lolh)>0))}
    return {"ok":True,"schema":ANALYSIS_SCHEMA,"version":ENERGY_SYSTEMS_VERSION,"lab_version":LAB_VERSION,"plan_id":plan_obj.get("plan_id"),"sample_count":len(ens),"output":output,"reliability_declaration":{"performed":False},"outage_prediction":{"performed":False},"ranking":{"performed":False},"recommendation":{"performed":False},"persistence":{"performed":False},"boundary":BOUNDARY}

def validate_result(body:dict[str,Any])->dict[str,Any]:
    errors=[]
    if not isinstance(body,dict) or body.get("schema")!=ANALYSIS_SCHEMA: errors.append(f"schema must be {ANALYSIS_SCHEMA}")
    if isinstance(body,dict) and str(body.get("lab_version"))!=LAB_VERSION: errors.append(f"lab_version must be {LAB_VERSION}")
    if isinstance(body,dict) and (body.get("reliability_declaration") or {}).get("performed") is not False: errors.append("reliability_declaration.performed must be false")
    return {"ok":not errors,"schema":VALIDATION_SCHEMA,"valid":not errors,"errors":errors,"boundary":"Structural validation only; not a real-world reliability certification."}

@router.get("/framework")
def route_framework(): return framework()
@router.post("/plan")
def route_plan(body:dict[str,Any]):
    try: return plan(body)
    except ReliabilityModelingError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
@router.post("/analyze")
def route_analyze(body:dict[str,Any]):
    try: return analyze(body)
    except ReliabilityModelingError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
@router.post("/validate-result")
def route_validate(body:dict[str,Any]): return validate_result(body)
