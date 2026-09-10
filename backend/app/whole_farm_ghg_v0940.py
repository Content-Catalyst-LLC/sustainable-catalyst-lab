from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import math
from typing import Any

LAB_RELEASE_VERSION = "0.94.0"
DOMAIN_VERSION = "0.11.0"
ENGINE_VERSION = "1.0.0"
MODEL_VERSION = "0.11.0"
ENTRY_SCHEMA = "sc-carbon-nature-whole-farm-ghg-entry/0.11.0"
BALANCE_SCHEMA = "sc-carbon-nature-whole-farm-ghg-balance/0.11.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_ENTRIES = 1000
MAX_REFS = 100
CO2_PER_C = 44.0 / 12.0

class WholeFarmGHGV01100Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _hash(value: Any) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
    return sha256(payload.encode("utf-8")).hexdigest()

def _number(value: Any,label:str)->float:
    try: out=float(value)
    except (TypeError,ValueError) as exc: raise WholeFarmGHGV01100Error(f"{label} must be numeric") from exc
    if not math.isfinite(out): raise WholeFarmGHGV01100Error(f"{label} must be finite")
    return out

def _nonnegative(value: Any,label:str)->float:
    out=_number(value,label)
    if out<0: raise WholeFarmGHGV01100Error(f"{label} must be >=0")
    return out

def _positive(value: Any,label:str)->float:
    out=_number(value,label)
    if out<=0: raise WholeFarmGHGV01100Error(f"{label} must be >0")
    return out

def _text(value:Any,label:str,required:bool=False,max_len:int=240)->str|None:
    if value is None:
        if required: raise WholeFarmGHGV01100Error(f"{label} is required")
        return None
    text=str(value).strip()
    if not text:
        if required: raise WholeFarmGHGV01100Error(f"{label} is required")
        return None
    if len(text)>max_len: raise WholeFarmGHGV01100Error(f"{label} exceeds {max_len} characters")
    return text

def _refs(value:Any,label:str)->list[str]:
    if value in (None,""): return []
    if not isinstance(value,list): raise WholeFarmGHGV01100Error(f"{label} must be an array")
    if len(value)>MAX_REFS: raise WholeFarmGHGV01100Error(f"{label} may contain at most {MAX_REFS} values")
    out=[]
    for i,item in enumerate(value):
        text=_text(item,f"{label}[{i}]",True,240); assert text is not None
        if text not in out: out.append(text)
    return out

def _parse_date(value:Any,label:str)->date:
    text=_text(value,label,True,20); assert text is not None
    try: return date.fromisoformat(text)
    except ValueError as exc: raise WholeFarmGHGV01100Error(f"{label} must be ISO date YYYY-MM-DD") from exc

def _direction(value:Any)->str:
    out=str(value or "emission").strip().lower()
    if out not in {"emission","removal"}: raise WholeFarmGHGV01100Error("direction must be emission or removal")
    return out

def _normalize_gwp_set(payload:Any)->dict[str,Any]:
    if payload in (None,""): return {"name":None,"source_ref":None,"horizon_years":100,"factors":{}}
    if not isinstance(payload,dict): raise WholeFarmGHGV01100Error("gwp_set must be an object")
    name=_text(payload.get("name"),"gwp_set.name")
    source=_text(payload.get("source_ref"),"gwp_set.source_ref")
    horizon_num=_number(payload.get("horizon_years",100),"gwp_set.horizon_years")
    if not horizon_num.is_integer() or horizon_num<=0: raise WholeFarmGHGV01100Error("gwp_set.horizon_years must be a positive integer")
    raw=payload.get("factors") or {}
    if not isinstance(raw,dict): raise WholeFarmGHGV01100Error("gwp_set.factors must be an object")
    factors={}
    for gas,val in raw.items():
        key=str(gas).strip().upper()
        if not key: raise WholeFarmGHGV01100Error("gwp_set factor gas keys may not be blank")
        f=_positive(val,f"gwp_set.factors.{key}")
        if key=="CO2" and abs(f-1)>1e-12: raise WholeFarmGHGV01100Error("CO2 GWP factor must equal 1")
        factors[key]=f
    if any(g!="CO2" for g in factors) and not source: raise WholeFarmGHGV01100Error("gwp_set.source_ref is required when non-CO2 factors are supplied")
    return {"name":name,"source_ref":source,"horizon_years":int(horizon_num),"factors":factors}

def normalize_entry(payload:dict[str,Any],gwp_set:dict[str,Any]|None=None)->dict[str,Any]:
    if not isinstance(payload,dict): raise WholeFarmGHGV01100Error("GHG entry must be an object")
    entry_id=_text(payload.get("entry_id"),"entry_id",True); category=_text(payload.get("category") or "other","category",True); direction=_direction(payload.get("direction")); source_refs=_refs(payload.get("source_refs"),"source_refs"); notes=_text(payload.get("notes"),"notes",False,2000)
    has_direct=payload.get("co2e_kg") not in (None,"")
    has_gas=payload.get("mass_kg") not in (None,"") or payload.get("gas") not in (None,"")
    has_activity=payload.get("activity_value") not in (None,"") or payload.get("emission_factor_kg_co2e_per_unit") not in (None,"")
    if sum(bool(x) for x in (has_direct,has_gas,has_activity))!=1: raise WholeFarmGHGV01100Error("entry must use exactly one calculation basis: co2e_kg, gas mass, or activity factor")
    gas=gas_mass_kg=gwp=gwp_source_ref=activity=factor=factor_unit=factor_source_ref=None
    if has_direct:
        mode="direct-co2e"; magnitude=_nonnegative(payload.get("co2e_kg"),"co2e_kg")
    elif has_gas:
        mode="gas-mass"; gas=_text(payload.get("gas"),"gas",True,40); assert gas is not None; gas=gas.upper(); gas_mass_kg=_nonnegative(payload.get("mass_kg"),"mass_kg")
        if gas=="CO2": gwp=1.0; gwp_source_ref="identity:CO2-to-CO2e"
        elif payload.get("gwp100") not in (None,""):
            gwp=_positive(payload.get("gwp100"),"gwp100"); gwp_source_ref=_text(payload.get("gwp_source_ref"),"gwp_source_ref",True)
        else:
            gs=gwp_set or {"factors":{}}
            if gas not in gs.get("factors",{}): raise WholeFarmGHGV01100Error(f"no GWP factor supplied for {gas}; Sustainable Catalyst supplies no default non-CO2 GWP")
            gwp=float(gs["factors"][gas]); gwp_source_ref=gs.get("source_ref")
            if not gwp_source_ref: raise WholeFarmGHGV01100Error(f"GWP source reference is required for {gas}")
        magnitude=gas_mass_kg*gwp
    else:
        mode="activity-factor"; activity=_nonnegative(payload.get("activity_value"),"activity_value"); factor=_nonnegative(payload.get("emission_factor_kg_co2e_per_unit"),"emission_factor_kg_co2e_per_unit"); factor_unit=_text(payload.get("activity_unit"),"activity_unit",True,80); factor_source_ref=_text(payload.get("factor_source_ref"),"factor_source_ref",True); magnitude=activity*factor
    signed=magnitude if direction=="emission" else -magnitude
    result={"schema":ENTRY_SCHEMA,"entry_id":entry_id,"category":category,"direction":direction,"calculation_basis":mode,"co2e_magnitude_kg":magnitude,"signed_co2e_kg":signed,"gas":gas,"gas_mass_kg":gas_mass_kg,"gwp_factor":gwp,"gwp_source_ref":gwp_source_ref,"activity_value":activity,"activity_unit":factor_unit,"emission_factor_kg_co2e_per_unit":factor,"factor_source_ref":factor_source_ref,"source_refs":source_refs,"notes":notes}
    result["input_fingerprint"]=_hash(payload); result["result_fingerprint"]=_hash({k:v for k,v in result.items() if k!="result_fingerprint"}); return result

def _soc_contribution(payload:Any,fallback_area_ha:float|None)->dict[str,Any]|None:
    if payload in (None,""): return None
    if not isinstance(payload,dict): raise WholeFarmGHGV01100Error("soc_stock_change must be an object")
    change=_number(payload.get("stock_change_Mg_C_ha"),"soc_stock_change.stock_change_Mg_C_ha")
    area=payload.get("area_ha"); area_ha=_positive(area,"soc_stock_change.area_ha") if area not in (None,"") else fallback_area_ha
    if area_ha is None: raise WholeFarmGHGV01100Error("area_ha is required to convert SOC stock change to farm-scale CO2e")
    basis=str(payload.get("basis") or "").strip().lower(); allowed={"measured-change","scenario","user-supplied-estimate"}
    if basis not in allowed: raise WholeFarmGHGV01100Error("soc_stock_change.basis must be measured-change, scenario, or user-supplied-estimate")
    include=payload.get("include_in_net") is True; total_c=change*area_ha; co2e_mg=-total_c*CO2_PER_C
    return {"stock_change_Mg_C_ha":change,"area_ha":area_ha,"total_stock_change_Mg_C":total_c,"co2_per_c_mass_ratio":CO2_PER_C,"signed_co2e_Mg":co2e_mg,"signed_co2e_kg":co2e_mg*1000,"direction":"removal" if co2e_mg<0 else ("emission" if co2e_mg>0 else "neutral"),"basis":basis,"include_in_net":include,"source_refs":_refs(payload.get("source_refs"),"soc_stock_change.source_refs"),"interpretation":"SOC stock-change carbon is converted by the exact molecular mass ratio 44/12. Inclusion in a farm GHG balance does not establish causal attribution, additionality, permanence, verification, or credit eligibility."}

def calculate_balance(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise WholeFarmGHGV01100Error("balance request must be an object")
    balance_id=_text(payload.get("balance_id") or "ghg-balance:whole-farm","balance_id",True); farm_id=_text(payload.get("farm_id"),"farm_id")
    area_ha=_positive(payload.get("area_ha"),"area_ha") if payload.get("area_ha") not in (None,"") else None
    gwp_set=_normalize_gwp_set(payload.get("gwp_set")); entries=payload.get("entries")
    if not isinstance(entries,list) or not (1<=len(entries)<=MAX_ENTRIES): raise WholeFarmGHGV01100Error(f"entries must contain 1..{MAX_ENTRIES} records")
    normalized=[]; seen=set()
    for i,entry in enumerate(entries):
        try: rec=normalize_entry(entry,gwp_set)
        except WholeFarmGHGV01100Error as exc: raise WholeFarmGHGV01100Error(f"entries[{i}]: {exc.detail}") from exc
        if rec["entry_id"] in seen: raise WholeFarmGHGV01100Error("entry_id values must be unique")
        seen.add(rec["entry_id"]); normalized.append(rec)
    soc=_soc_contribution(payload.get("soc_stock_change"),area_ha); signed=[x["signed_co2e_kg"] for x in normalized]
    if soc and soc["include_in_net"]: signed.append(soc["signed_co2e_kg"])
    gross_emissions=sum(x for x in signed if x>0); gross_removals=-sum(x for x in signed if x<0); net=gross_emissions-gross_removals
    by_category={}; by_gas={}
    for rec in normalized:
        b=by_category.setdefault(rec["category"],{"emissions_kg_CO2e":0.0,"removals_kg_CO2e":0.0,"net_kg_CO2e":0.0})
        if rec["signed_co2e_kg"]>=0:b["emissions_kg_CO2e"]+=rec["signed_co2e_kg"]
        else:b["removals_kg_CO2e"]+=-rec["signed_co2e_kg"]
        b["net_kg_CO2e"]+=rec["signed_co2e_kg"]
        if rec["gas"]:
            gb=by_gas.setdefault(rec["gas"],{"gas_mass_kg":0.0,"net_kg_CO2e":0.0}); gb["gas_mass_kg"]+=rec["gas_mass_kg"] or 0; gb["net_kg_CO2e"]+=rec["signed_co2e_kg"]
    if soc and soc["include_in_net"]:
        b=by_category.setdefault("soil-organic-carbon-stock-change",{"emissions_kg_CO2e":0.0,"removals_kg_CO2e":0.0,"net_kg_CO2e":0.0})
        if soc["signed_co2e_kg"]>=0:b["emissions_kg_CO2e"]+=soc["signed_co2e_kg"]
        else:b["removals_kg_CO2e"]+=-soc["signed_co2e_kg"]
        b["net_kg_CO2e"]+=soc["signed_co2e_kg"]
    period=annualized=None; raw_period=payload.get("period")
    if raw_period not in (None,""):
        if not isinstance(raw_period,dict): raise WholeFarmGHGV01100Error("period must be an object")
        start=_parse_date(raw_period.get("start_date"),"period.start_date"); end=_parse_date(raw_period.get("end_date"),"period.end_date")
        if end<=start: raise WholeFarmGHGV01100Error("period.end_date must be after period.start_date")
        days=(end-start).days; years=days/365.2425; period={"start_date":start.isoformat(),"end_date":end.isoformat(),"elapsed_days":days,"elapsed_years":years}
        if payload.get("annualize") is True: annualized={"net_kg_CO2e_per_year":net/years,"gross_emissions_kg_CO2e_per_year":gross_emissions/years,"gross_removals_kg_CO2e_per_year":gross_removals/years}
    elif payload.get("annualize") is True: raise WholeFarmGHGV01100Error("period is required when annualize is true")
    missing_sources=[x["entry_id"] for x in normalized if not x["source_refs"] and x["calculation_basis"]=="direct-co2e"]
    result={"ok":True,"schema":BALANCE_SCHEMA,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,"balance_id":balance_id,"farm_id":farm_id,"area_ha":area_ha,"period":period,"gwp_set":gwp_set,"entry_count":len(normalized),"entries":normalized,"soc_stock_change":soc,"gross_emissions_kg_CO2e":gross_emissions,"gross_removals_kg_CO2e":gross_removals,"net_balance_kg_CO2e":net,"net_balance_Mg_CO2e":net/1000,"net_direction":"net-emissions" if net>0 else ("net-removals" if net<0 else "neutral"),"by_category":by_category,"by_gas":by_gas,"annualized":annualized,"intensity_kg_CO2e_per_ha":net/area_ha if area_ha is not None else None,"evidence_diagnostics":{"direct_co2e_entries_without_source_refs":missing_sources,"all_non_co2_gwp_factors_explicit_and_sourced":True,"activity_factor_sources_required":True},"interpretation":{"sign_convention":"positive net balance = net emissions; negative net balance = net removals","whole_farm_balance_is_verification":False,"soc_contribution_is_attributed_sequestration":False,"statement":"This balance aggregates explicit user-supplied GHG records, factors, and optional SOC stock change. It is an accounting model, not verification, causal attribution, additionality, permanence, or carbon-credit eligibility determination."},"guardrails":_guardrails()}
    result["input_fingerprint"]=_hash(payload); result["result_fingerprint"]=_hash({k:v for k,v in result.items() if k!="result_fingerprint"}); return result

def build_project_packet(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise WholeFarmGHGV01100Error("project packet request must be an object")
    project_id=_text(payload.get("project_id"),"project_id",True); actor=_text(payload.get("actor_ref") or "system:sustainable-catalyst-lab","actor_ref",True); balance_payload=payload.get("balance")
    if not isinstance(balance_payload,dict): raise WholeFarmGHGV01100Error("balance object is required")
    balance=calculate_balance(balance_payload); object_id=_text(payload.get("object_id") or f"model-run:whole-farm-ghg-{balance['result_fingerprint'][:16]}","object_id",True); source_refs=[]
    for entry in balance["entries"]:
        for ref in entry["source_refs"]:
            if ref not in source_refs: source_refs.append(ref)
        for ref in (entry.get("factor_source_ref"),entry.get("gwp_source_ref")):
            if ref and ref not in source_refs: source_refs.append(ref)
    if balance.get("soc_stock_change"):
        for ref in balance["soc_stock_change"].get("source_refs",[]):
            if ref not in source_refs: source_refs.append(ref)
    obj={"object_id":object_id,"object_type":"model-run","project_id":project_id,"version":"1.0.0","status":"draft","payload":{"model_key":"whole-farm-ghg-balance-v1100","model_version":MODEL_VERSION,"lab_release_version":LAB_RELEASE_VERSION,"domain_version":DOMAIN_VERSION,"balance_id":balance["balance_id"],"output_summary":{"gross_emissions_kg_CO2e":balance["gross_emissions_kg_CO2e"],"gross_removals_kg_CO2e":balance["gross_removals_kg_CO2e"],"net_balance_kg_CO2e":balance["net_balance_kg_CO2e"],"net_direction":balance["net_direction"]},"result_fingerprint":balance["result_fingerprint"],"interpretation":balance["interpretation"],"guardrails":balance["guardrails"]},"source_refs":source_refs,"evidence_refs":source_refs,"provenance_refs":["provenance:whole-farm-ghg-balance-model-run"]}
    event={"provenance_id":"provenance:whole-farm-ghg-balance-model-run","event_type":"modeled","object_id":object_id,"actor_ref":actor,"details":{"model_version":MODEL_VERSION,"result_fingerprint":balance["result_fingerprint"],"whole_farm_balance_is_verification":False}}
    packet={"schema":PROJECT_PACKET_SCHEMA,"objects":[obj],"provenance":[event],"links":[]}; return {"ok":True,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,"packet":packet,"balance":balance,"packet_fingerprint":_hash(packet)}

def _guardrails()->dict[str,bool]:
    return {"no_default_non_co2_gwp_factors":True,"no_default_activity_emission_factors":True,"activity_factor_source_required":True,"soc_stock_change_inclusion_is_explicit":True,"soc_stock_change_is_not_automatically_attributed_sequestration":True,"whole_farm_balance_is_not_verification":True,"inventory_completeness_not_inferred":True,"causal_attribution_not_established":True,"additionality_not_determined":True,"leakage_not_determined":True,"permanence_not_determined":True,"credit_eligibility_not_determined":True,"automatic_recommendation_generated":False}

def policies()->dict[str,Any]:
    return {"ok":True,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,"capabilities":{"direct_co2e_entries":True,"gas_mass_with_explicit_gwp":True,"activity_factor_entries":True,"emissions_and_removals":True,"category_aggregation":True,"gas_aggregation":True,"optional_soc_stock_change_integration":True,"optional_period_annualization":True,"farm_area_intensity":True,"carbon_project_packet_handoff":True,"deterministic_fingerprints":True},"limits":{"max_entries":MAX_ENTRIES,"max_refs_per_field":MAX_REFS},"guardrails":_guardrails()}

def schema()->dict[str,Any]:
    return {"ok":True,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,"entry_schema":ENTRY_SCHEMA,"balance_schema":BALANCE_SCHEMA,"entry_calculation_bases":["direct-co2e","gas-mass","activity-factor"],"directions":["emission","removal"],"soc_stock_change_bases":["measured-change","scenario","user-supplied-estimate"],"sign_convention":"positive net balance = net emissions; negative = net removals","co2_per_c_mass_ratio":CO2_PER_C}

def health()->dict[str,Any]:
    return {"ok":True,"status":"whole-farm-ghg-balance-ready","service":"Sustainable Catalyst Lab Whole-Farm GHG Balance","lab_release_version":LAB_RELEASE_VERSION,"domain_version":DOMAIN_VERSION,"engine_version":ENGINE_VERSION,"model_version":MODEL_VERSION,"guardrails":_guardrails()}
