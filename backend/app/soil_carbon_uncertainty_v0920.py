from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from statistics import mean, median, stdev
from typing import Any

from .soil_organic_carbon_v0890 import calculate_layer_stock, calculate_profile_stock

LAB_RELEASE_VERSION = "0.92.0"
DOMAIN_VERSION = "0.9.0"
ENGINE_VERSION = "1.0.0"
MODEL_VERSION = "0.9.0"
REPLICATE_SCHEMA = "sc-carbon-nature-soc-spatial-uncertainty/0.9.0"
STRATIFIED_SCHEMA = "sc-carbon-nature-soc-stratified-estimate/0.9.0"
CHANGE_UNCERTAINTY_SCHEMA = "sc-carbon-nature-soc-change-uncertainty/0.9.0"
PROPAGATION_SCHEMA = "sc-carbon-nature-soc-layer-input-uncertainty/0.9.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_OBSERVATIONS = 2000
MAX_STRATA = 100
EARTH_RADIUS_KM = 6371.0088
SUPPORTED_CONFIDENCE = (0.90, 0.95, 0.99)

_T = {
0.90: [6.313751515,2.919985580,2.353363435,2.131846786,2.015048373,1.943180281,1.894578605,1.859548038,1.833112933,1.812461123,1.795884819,1.782287556,1.770933396,1.761310136,1.753050356,1.745883676,1.739606726,1.734063607,1.729132812,1.724718243,1.720742903,1.717144374,1.713871528,1.710882080,1.708140761,1.705617920,1.703288446,1.701130934,1.699127027,1.697260887],
0.95: [12.706204736,4.302652730,3.182446305,2.776445105,2.570581836,2.446911851,2.364624252,2.306004135,2.262157163,2.228138852,2.200985160,2.178812830,2.160368656,2.144786688,2.131449546,2.119905299,2.109815578,2.100922040,2.093024054,2.085963447,2.079613845,2.073873068,2.068657610,2.063898562,2.059538553,2.055529439,2.051830516,2.048407142,2.045229642,2.042272456],
0.99: [63.656741163,9.924843201,5.840909310,4.604094871,4.032142984,3.707428021,3.499483297,3.355387331,3.249835542,3.169272673,3.105806516,3.054539589,3.012275839,2.976842734,2.946712883,2.920781622,2.898230520,2.878440473,2.860934606,2.845339710,2.831359558,2.818756061,2.807335684,2.796939505,2.787435814,2.778714533,2.770682957,2.763262455,2.756385904,2.749995654],
}
_Z = {0.90: 1.644853627, 0.95: 1.959963985, 0.99: 2.575829304}


class SoilCarbonUncertaintyV0900Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _number(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise SoilCarbonUncertaintyV0900Error(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise SoilCarbonUncertaintyV0900Error(f"{label} must be finite")
    return out


def _confidence(value: Any) -> float:
    if value in (None, ""):
        return 0.95
    out = _number(value, "confidence_level")
    for level in SUPPORTED_CONFIDENCE:
        if abs(out - level) < 1e-12:
            return level
    raise SoilCarbonUncertaintyV0900Error("confidence_level must be 0.90, 0.95, or 0.99")


def _t_critical(confidence: float, df: float) -> float:
    if df <= 0:
        raise SoilCarbonUncertaintyV0900Error("degrees of freedom must be >0")
    if df <= 30:
        lo = max(1, int(math.floor(df)))
        hi = max(1, int(math.ceil(df)))
        if lo == hi:
            return _T[confidence][lo - 1]
        a = _T[confidence][lo - 1]
        b = _T[confidence][hi - 1]
        return a + (b - a) * (df - lo) / (hi - lo)
    z = _Z[confidence]
    v = df
    # Cornish-Fisher expansion of the Student-t quantile; accurate in the large-df regime.
    return z + (z**3 + z)/(4*v) + (5*z**5 + 16*z**3 + 3*z)/(96*v*v) + (3*z**7 + 19*z**5 + 17*z**3 - 15*z)/(384*v**3)


def _safe_text(value: Any, label: str, required: bool = False, max_len: int = 180) -> str | None:
    if value is None:
        if required:
            raise SoilCarbonUncertaintyV0900Error(f"{label} is required")
        return None
    text = str(value).strip()
    if not text:
        if required:
            raise SoilCarbonUncertaintyV0900Error(f"{label} is required")
        return None
    if len(text) > max_len:
        raise SoilCarbonUncertaintyV0900Error(f"{label} exceeds {max_len} characters")
    return text


def _stock_from_observation(row: Any, index: int = 0) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise SoilCarbonUncertaintyV0900Error(f"observations[{index}] must be an object")
    obs_id = _safe_text(row.get("observation_id") or f"observation-{index+1}", f"observations[{index}].observation_id", True)
    if row.get("stock_Mg_C_ha") not in (None, ""):
        stock = _number(row.get("stock_Mg_C_ha"), f"observations[{index}].stock_Mg_C_ha")
        source = "supplied-stock"
        profile_fingerprint = None
    elif isinstance(row.get("profile"), dict):
        try:
            result = calculate_profile_stock(row["profile"])
        except Exception as exc:
            raise SoilCarbonUncertaintyV0900Error(f"observations[{index}].profile invalid: {getattr(exc, 'detail', str(exc))}") from exc
        stock = float(result["soc_stock_Mg_C_ha"])
        source = "soc-v0600-profile-calculation"
        profile_fingerprint = result.get("result_fingerprint")
    else:
        raise SoilCarbonUncertaintyV0900Error(f"observations[{index}] requires stock_Mg_C_ha or profile")
    if stock < 0:
        raise SoilCarbonUncertaintyV0900Error(f"observations[{index}].stock_Mg_C_ha must be >=0")
    lat = lon = None
    if row.get("latitude") not in (None, "") or row.get("longitude") not in (None, ""):
        if row.get("latitude") in (None, "") or row.get("longitude") in (None, ""):
            raise SoilCarbonUncertaintyV0900Error(f"observations[{index}] coordinates require both latitude and longitude")
        lat = _number(row.get("latitude"), f"observations[{index}].latitude")
        lon = _number(row.get("longitude"), f"observations[{index}].longitude")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise SoilCarbonUncertaintyV0900Error(f"observations[{index}] coordinates are outside WGS84 bounds")
    return {
        "observation_id": obs_id,
        "stock_Mg_C_ha": stock,
        "stratum_id": _safe_text(row.get("stratum_id"), f"observations[{index}].stratum_id"),
        "latitude": lat,
        "longitude": lon,
        "source_basis": source,
        "profile_result_fingerprint": profile_fingerprint,
    }


def _summary(values: list[float], confidence: float) -> dict[str, Any]:
    n = len(values)
    if n < 2:
        raise SoilCarbonUncertaintyV0900Error("at least two replicate values are required for sample uncertainty")
    m = mean(values)
    sd = stdev(values)
    se = sd / math.sqrt(n)
    df = n - 1
    critical = _t_critical(confidence, df)
    half = critical * se
    return {
        "n": n,
        "mean_Mg_C_ha": m,
        "sample_sd_Mg_C_ha": sd,
        "standard_error_Mg_C_ha": se,
        "coefficient_of_variation_percent": (sd / abs(m) * 100.0) if abs(m) > 1e-15 else None,
        "degrees_of_freedom": float(df),
        "confidence_level": confidence,
        "student_t_critical": critical,
        "confidence_interval_Mg_C_ha": {"lower": m - half, "upper": m + half, "half_width": half},
    }


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat = lat2-lat1; dlon = lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*EARTH_RADIUS_KM*math.asin(min(1.0, math.sqrt(h)))


def _spatial_coverage(observations: list[dict[str, Any]]) -> dict[str, Any]:
    coords = [(x["latitude"], x["longitude"]) for x in observations if x["latitude"] is not None]
    if not coords:
        return {"coordinate_count": 0, "available": False, "representativeness_determined": False}
    duplicates = len(coords) - len(set(coords))
    result: dict[str, Any] = {
        "coordinate_count": len(coords), "available": True, "duplicate_coordinate_count": duplicates,
        "centroid_wgs84": {"latitude": mean([x[0] for x in coords]), "longitude": mean([x[1] for x in coords])},
        "bbox_wgs84": {"min_latitude": min(x[0] for x in coords), "max_latitude": max(x[0] for x in coords), "min_longitude": min(x[1] for x in coords), "max_longitude": max(x[1] for x in coords)},
        "representativeness_determined": False,
    }
    if len(coords) >= 2:
        nearest=[]; pairwise=[]
        for i,a in enumerate(coords):
            distances=[]
            for j,b in enumerate(coords):
                if i==j: continue
                d=_haversine_km(a,b); distances.append(d)
                if j>i: pairwise.append(d)
            nearest.append(min(distances))
        result["nearest_neighbor_km"]={"min":min(nearest),"median":median(nearest),"max":max(nearest)}
        result["max_pairwise_distance_km"] = max(pairwise) if pairwise else 0.0
    return result


def summarize_replicates(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonUncertaintyV0900Error("replicate summary request must be an object")
    confidence = _confidence(payload.get("confidence_level"))
    rows = payload.get("observations")
    if not isinstance(rows, list) or not (2 <= len(rows) <= MAX_OBSERVATIONS):
        raise SoilCarbonUncertaintyV0900Error(f"observations must contain 2..{MAX_OBSERVATIONS} records")
    observations=[_stock_from_observation(row,i) for i,row in enumerate(rows)]
    ids=[x["observation_id"] for x in observations]
    if len(ids)!=len(set(ids)):
        raise SoilCarbonUncertaintyV0900Error("observation_id values must be unique")
    stats=_summary([x["stock_Mg_C_ha"] for x in observations],confidence)
    result={
        "ok":True,"schema":REPLICATE_SCHEMA,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,
        "estimate_id":_safe_text(payload.get("estimate_id") or "estimate:soc-replicates","estimate_id",True),
        "spatial_unit_id":_safe_text(payload.get("spatial_unit_id"),"spatial_unit_id"),
        "uncertainty_basis":"sample-replicate-variability","statistics":stats,"observations":observations,
        "spatial_coverage":_spatial_coverage(observations),"guardrails":_guardrails(),
    }
    result["input_fingerprint"]=_hash({"confidence_level":confidence,"observations":observations,"spatial_unit_id":result["spatial_unit_id"]})
    result["result_fingerprint"]=_hash(result)
    return result


def stratified_estimate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonUncertaintyV0900Error("stratified estimate request must be an object")
    confidence=_confidence(payload.get("confidence_level"))
    strata=payload.get("strata")
    if not isinstance(strata,list) or not (1 <= len(strata) <= MAX_STRATA):
        raise SoilCarbonUncertaintyV0900Error(f"strata must contain 1..{MAX_STRATA} records")
    seen=set(); normalized=[]
    for i,row in enumerate(strata):
        if not isinstance(row,dict): raise SoilCarbonUncertaintyV0900Error(f"strata[{i}] must be an object")
        sid=_safe_text(row.get("stratum_id"),f"strata[{i}].stratum_id",True)
        if sid in seen: raise SoilCarbonUncertaintyV0900Error("stratum_id values must be unique")
        seen.add(sid)
        area=_number(row.get("area_ha"),f"strata[{i}].area_ha")
        if area<=0: raise SoilCarbonUncertaintyV0900Error(f"strata[{i}].area_ha must be >0")
        obs=row.get("observations")
        if not isinstance(obs,list) or len(obs)<2: raise SoilCarbonUncertaintyV0900Error(f"strata[{i}].observations requires at least two records")
        observations=[_stock_from_observation(x,j) for j,x in enumerate(obs)]
        ids=[x["observation_id"] for x in observations]
        if len(ids)!=len(set(ids)): raise SoilCarbonUncertaintyV0900Error(f"strata[{i}] observation_id values must be unique")
        s=_summary([x["stock_Mg_C_ha"] for x in observations],confidence)
        normalized.append({"stratum_id":sid,"area_ha":area,"statistics":s,"observations":observations,"spatial_coverage":_spatial_coverage(observations)})
    total_area=sum(x["area_ha"] for x in normalized)
    for x in normalized: x["area_weight"]=x["area_ha"]/total_area
    weighted_mean=sum(x["area_weight"]*x["statistics"]["mean_Mg_C_ha"] for x in normalized)
    components=[]
    variance_mean=0.0
    for x in normalized:
        n=x["statistics"]["n"]; sd=x["statistics"]["sample_sd_Mg_C_ha"]; w=x["area_weight"]
        comp=w*w*sd*sd/n; components.append((comp,n-1)); variance_mean += comp
    se=math.sqrt(variance_mean)
    numerator=variance_mean*variance_mean
    denominator=sum((v*v)/df for v,df in components if df>0)
    df_eff=(numerator/denominator) if denominator>0 else sum(df for _,df in components)
    critical=_t_critical(confidence,max(df_eff,1.0))
    half=critical*se
    result={
        "ok":True,"schema":STRATIFIED_SCHEMA,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,
        "estimate_id":_safe_text(payload.get("estimate_id") or "estimate:soc-stratified","estimate_id",True),
        "confidence_level":confidence,"total_area_ha":total_area,"strata":normalized,
        "weighted_mean_stock_Mg_C_ha":weighted_mean,"total_stock_Mg_C":weighted_mean*total_area,
        "standard_error_Mg_C_ha":se,"effective_degrees_of_freedom":df_eff,"student_t_critical":critical,
        "confidence_interval_Mg_C_ha":{"lower":weighted_mean-half,"upper":weighted_mean+half,"half_width":half},
        "variance_model":"independent-strata-area-weighted-without-finite-population-correction",
        "guardrails":_guardrails(),
    }
    result["input_fingerprint"]=_hash({"confidence_level":confidence,"strata":normalized})
    result["result_fingerprint"]=_hash(result)
    return result


def _elapsed_years(payload: dict[str, Any]) -> float | None:
    if payload.get("elapsed_years") not in (None, ""):
        years=_number(payload.get("elapsed_years"),"elapsed_years")
        if years<=0: raise SoilCarbonUncertaintyV0900Error("elapsed_years must be >0")
        return years
    if payload.get("baseline_at") and payload.get("followup_at"):
        def parse(v,label):
            try: d=datetime.fromisoformat(str(v).replace('Z','+00:00'))
            except ValueError as exc: raise SoilCarbonUncertaintyV0900Error(f"{label} must be ISO-8601") from exc
            if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc)
        a=parse(payload['baseline_at'],'baseline_at'); b=parse(payload['followup_at'],'followup_at')
        days=(b-a).total_seconds()/86400.0
        if days<=0: raise SoilCarbonUncertaintyV0900Error("followup_at must be later than baseline_at")
        return days/365.2425
    return None


def change_uncertainty(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise SoilCarbonUncertaintyV0900Error("change uncertainty request must be an object")
    confidence=_confidence(payload.get("confidence_level")); mode=str(payload.get("mode") or "paired").strip().lower()
    if mode not in {"paired","independent"}: raise SoilCarbonUncertaintyV0900Error("mode must be paired or independent")
    baseline_summary=followup_summary=None
    if mode=="paired":
        pairs=payload.get("pairs")
        if not isinstance(pairs,list) or not (2 <= len(pairs) <= MAX_OBSERVATIONS): raise SoilCarbonUncertaintyV0900Error(f"pairs must contain 2..{MAX_OBSERVATIONS} records")
        diffs=[]; normalized=[]; ids=set()
        for i,p in enumerate(pairs):
            if not isinstance(p,dict): raise SoilCarbonUncertaintyV0900Error(f"pairs[{i}] must be an object")
            pid=_safe_text(p.get("pair_id") or f"pair-{i+1}",f"pairs[{i}].pair_id",True)
            if pid in ids: raise SoilCarbonUncertaintyV0900Error("pair_id values must be unique")
            ids.add(pid)
            b=_stock_from_observation(p.get("baseline") or {},i); f=_stock_from_observation(p.get("followup") or {},i)
            d=f["stock_Mg_C_ha"]-b["stock_Mg_C_ha"]; diffs.append(d)
            normalized.append({"pair_id":pid,"baseline":b,"followup":f,"difference_Mg_C_ha":d})
        s=_summary(diffs,confidence); delta=s["mean_Mg_C_ha"]; se=s["standard_error_Mg_C_ha"]; df=s["degrees_of_freedom"]; critical=s["student_t_critical"]; ci=s["confidence_interval_Mg_C_ha"]
        detail={"pairs":normalized,"difference_statistics":s}
    else:
        bro=payload.get("baseline_observations"); fro=payload.get("followup_observations")
        if not isinstance(bro,list) or len(bro)<2 or not isinstance(fro,list) or len(fro)<2: raise SoilCarbonUncertaintyV0900Error("independent mode requires at least two baseline_observations and two followup_observations")
        bobs=[_stock_from_observation(x,i) for i,x in enumerate(bro)]; fobs=[_stock_from_observation(x,i) for i,x in enumerate(fro)]
        baseline_summary=_summary([x["stock_Mg_C_ha"] for x in bobs],confidence); followup_summary=_summary([x["stock_Mg_C_ha"] for x in fobs],confidence)
        delta=followup_summary["mean_Mg_C_ha"]-baseline_summary["mean_Mg_C_ha"]
        vb=baseline_summary["sample_sd_Mg_C_ha"]**2/baseline_summary["n"]; vf=followup_summary["sample_sd_Mg_C_ha"]**2/followup_summary["n"]
        se=math.sqrt(vb+vf); den=(vb*vb)/(baseline_summary["n"]-1)+(vf*vf)/(followup_summary["n"]-1)
        df=((vb+vf)**2/den) if den>0 else baseline_summary["n"]+followup_summary["n"]-2
        critical=_t_critical(confidence,max(df,1.0)); half=critical*se; ci={"lower":delta-half,"upper":delta+half,"half_width":half}
        detail={"baseline_observations":bobs,"followup_observations":fobs,"baseline_statistics":baseline_summary,"followup_statistics":followup_summary}
    years=_elapsed_years(payload)
    excludes=ci["lower"]>0 or ci["upper"]<0
    result={
        "ok":True,"schema":CHANGE_UNCERTAINTY_SCHEMA,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,
        "analysis_id":_safe_text(payload.get("analysis_id") or "uncertainty:soc-change","analysis_id",True),"mode":mode,
        "confidence_level":confidence,"mean_stock_change_Mg_C_ha":delta,"standard_error_Mg_C_ha":se,"degrees_of_freedom":df,
        "student_t_critical":critical,"confidence_interval_Mg_C_ha":ci,
        "confidence_threshold_Mg_C_ha":critical*se,"confidence_interval_excludes_zero":excludes,
        "elapsed_years":years,
        "annualized_mean_stock_change_Mg_C_ha_yr":delta/years if years else None,
        "annualized_confidence_interval_Mg_C_ha_yr":{"lower":ci["lower"]/years,"upper":ci["upper"]/years} if years else None,
        "uncertainty_basis":"replicate-sampling-variability","detail":detail,
        "interpretation":{"directional_separation_at_stated_confidence":excludes,"causal_attribution_established":False,"verified_sequestration_established":False,
          "statement":"The interval quantifies variability in the supplied replicate stock estimates under the stated paired/independent model. Excluding zero does not establish intervention attribution, additionality, permanence, verification, or credit eligibility."},
        "guardrails":_guardrails(),
    }
    result["input_fingerprint"]=_hash({"mode":mode,"confidence":confidence,"detail":detail,"elapsed_years":years})
    result["result_fingerprint"]=_hash(result)
    return result


def _uncertainty_factor(value: Any, unit: Any, kind: str, label: str) -> float:
    x=_number(value,label)
    if x<0: raise SoilCarbonUncertaintyV0900Error(f"{label} must be >=0")
    u=str(unit or '').strip().lower().replace(' ','').replace('³','3')
    if kind=='soc':
        if u in {'g/kg','gkg','gkg-1','gkg^-1','mg/g','mgg-1','mg/gsoil'}: return x
        if u in {'%','percent','percentage'}: return x*10.0
        if u in {'fraction','kg/kg','kgkg-1','kgkg^-1'}: return x*1000.0
    if kind=='bd':
        if u in {'g/cm3','gcm-3','gcm^-3','mg/m3','mgm-3','mgm^-3','t/m3','tm-3','tm^-3'}: return x
        if u in {'kg/m3','kgm-3','kgm^-3'}: return x/1000.0
    if kind=='depth':
        if u=='cm': return x
        if u=='mm': return x*0.1
        if u=='m': return x*100.0
    raise SoilCarbonUncertaintyV0900Error(f"unsupported {kind} uncertainty unit")


def propagate_layer_uncertainty(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise SoilCarbonUncertaintyV0900Error("layer uncertainty request must be an object")
    layer=payload.get("layer") or payload
    if not isinstance(layer,dict): raise SoilCarbonUncertaintyV0900Error("layer must be an object")
    try: calc=calculate_layer_stock(layer)
    except Exception as exc: raise SoilCarbonUncertaintyV0900Error(f"layer is invalid: {getattr(exc,'detail',str(exc))}") from exc
    n=calc['layer']; C=n['soc_g_per_kg']; B=n['bulk_density_g_cm3']; D=n['thickness_cm']; f=n['coarse_fragments_percent']/100.0
    uC=_uncertainty_factor(payload.get('soc_standard_uncertainty',0), layer.get('soc_unit') or 'g/kg','soc','soc_standard_uncertainty')
    uB=_uncertainty_factor(payload.get('bulk_density_standard_uncertainty',0), layer.get('bulk_density_unit') or 'g/cm3','bd','bulk_density_standard_uncertainty')
    uD=_uncertainty_factor(payload.get('thickness_standard_uncertainty',0), layer.get('depth_unit') or 'cm','depth','thickness_standard_uncertainty')
    uf=_number(payload.get('coarse_fragments_standard_uncertainty_percent',0),'coarse_fragments_standard_uncertainty_percent')/100.0
    if uf<0: raise SoilCarbonUncertaintyV0900Error('coarse_fragments_standard_uncertainty_percent must be >=0')
    k=0.1
    components={
      'soc_concentration': (B*D*k*(1-f)*uC)**2,
      'bulk_density': (C*D*k*(1-f)*uB)**2,
      'thickness': (C*B*k*(1-f)*uD)**2,
      'coarse_fragments': (C*B*D*k*uf)**2,
    }
    variance=sum(components.values()); u=math.sqrt(variance); confidence=_confidence(payload.get('confidence_level')); z=_Z[confidence]
    stock=float(calc['soc_stock_Mg_C_ha']); half=z*u
    result={
      'ok':True,'schema':PROPAGATION_SCHEMA,'domain_version':DOMAIN_VERSION,'lab_release_version':LAB_RELEASE_VERSION,
      'stock_Mg_C_ha':stock,'combined_standard_uncertainty_Mg_C_ha':u,'confidence_level':confidence,'normal_coverage_factor':z,
      'expanded_uncertainty_Mg_C_ha':half,'coverage_interval_Mg_C_ha':{'lower':stock-half,'upper':stock+half},
      'variance_components_Mg2_C2_ha2':components,'method':'first-order-independent-input-uncertainty-propagation',
      'assumptions':['Input standard uncertainties are supplied by the user and expressed in the same units as their associated inputs.','SOC concentration, bulk density, layer thickness, and coarse-fragment uncertainties are treated as independent.','The result quantifies stated input uncertainty only; spatial sampling variability and model-form uncertainty require separate treatment.'],
      'guardrails':_guardrails(),
    }
    result['result_fingerprint']=_hash(result)
    return result


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise SoilCarbonUncertaintyV0900Error('project packet request must be an object')
    project_id=_safe_text(payload.get('project_id'),'project_id',True); actor=_safe_text(payload.get('actor_ref') or 'system:sustainable-catalyst-lab','actor_ref',True)
    analysis_payload=payload.get('analysis')
    if not isinstance(analysis_payload,dict): raise SoilCarbonUncertaintyV0900Error('analysis object is required')
    analysis=change_uncertainty(analysis_payload)
    object_id=_safe_text(payload.get('object_id') or f"model-run:soc-uncertainty-{analysis['result_fingerprint'][:16]}",'object_id',True)
    obj={'object_id':object_id,'object_type':'model-run','project_id':project_id,'version':'1.0.0','status':'draft','payload':{
      'model_key':'soc-spatial-uncertainty-v0900','model_version':MODEL_VERSION,'lab_release_version':LAB_RELEASE_VERSION,'domain_version':DOMAIN_VERSION,
      'output_summary':{'mode':analysis['mode'],'mean_stock_change_Mg_C_ha':analysis['mean_stock_change_Mg_C_ha'],'standard_error_Mg_C_ha':analysis['standard_error_Mg_C_ha'],'confidence_level':analysis['confidence_level'],'confidence_interval_Mg_C_ha':analysis['confidence_interval_Mg_C_ha'],'confidence_interval_excludes_zero':analysis['confidence_interval_excludes_zero']},
      'result_fingerprint':analysis['result_fingerprint'],'interpretation':analysis['interpretation'],'guardrails':analysis['guardrails']},
      'source_refs':[], 'provenance_refs':['provenance:soc-uncertainty-model-run']}
    event={'provenance_id':'provenance:soc-uncertainty-model-run','event_type':'modeled','object_id':object_id,'actor_ref':actor,'details':{'model_version':MODEL_VERSION,'result_fingerprint':analysis['result_fingerprint'],'uncertainty_basis':'replicate-sampling-variability'}}
    packet={'schema':PROJECT_PACKET_SCHEMA,'objects':[obj],'provenance':[event],'links':[]}
    return {'ok':True,'domain_version':DOMAIN_VERSION,'lab_release_version':LAB_RELEASE_VERSION,'packet':packet,'analysis':analysis,'packet_fingerprint':_hash(packet)}


def _guardrails() -> dict[str,bool]:
    return {
      'sample_uncertainty_is_not_total_uncertainty':True,'spatial_representativeness_not_determined':True,'outliers_not_removed_automatically':True,
      'kriging_not_performed':True,'variogram_not_inferred':True,'finite_population_correction_not_inferred':True,'correlations_not_inferred':True,
      'equivalent_soil_mass_not_implemented':True,'causal_attribution_not_established':True,'additionality_not_determined':True,'permanence_not_determined':True,
      'co2e_not_inferred':True,'verification_not_performed':True,'credit_eligibility_not_determined':True,
    }


def policies() -> dict[str,Any]:
    return {'ok':True,'domain_version':DOMAIN_VERSION,'lab_release_version':LAB_RELEASE_VERSION,'capabilities':{
      'replicate_stock_summary':True,'student_t_confidence_intervals':True,'coordinate_coverage_diagnostics':True,'area_weighted_stratified_estimate':True,
      'paired_change_uncertainty':True,'independent_change_uncertainty':True,'confidence_threshold':True,'first_order_input_uncertainty_propagation':True,
      'carbon_project_packet_handoff':True,'deterministic_fingerprints':True},'supported_confidence_levels':list(SUPPORTED_CONFIDENCE),'guardrails':_guardrails()}


def schema() -> dict[str,Any]:
    return {'ok':True,'domain_version':DOMAIN_VERSION,'lab_release_version':LAB_RELEASE_VERSION,'schemas':{
      'replicate_summary':REPLICATE_SCHEMA,'stratified_estimate':STRATIFIED_SCHEMA,'change_uncertainty':CHANGE_UNCERTAINTY_SCHEMA,'layer_input_uncertainty':PROPAGATION_SCHEMA},
      'units':{'stock':'Mg C/ha','standard_error':'Mg C/ha','change':'Mg C/ha','annualized_change':'Mg C/ha/yr','distance':'km'},
      'statistical_scope':{'replicate_variability':'sample standard deviation and standard error','confidence_interval':'two-sided Student-t for replicate means/change; normal coverage for user-supplied first-order input uncertainty','spatial_diagnostics':'coordinate extent and nearest-neighbor distance only; no representativeness inference'},
      'guardrails':_guardrails()}


def health() -> dict[str,Any]:
    return {'ok':True,'status':'soc-spatial-variability-uncertainty-ready','domain_version':DOMAIN_VERSION,'lab_release_version':LAB_RELEASE_VERSION,'compute_core_version':ENGINE_VERSION,
      'replicate_uncertainty':True,'stratified_estimation':True,'paired_change_uncertainty':True,'independent_change_uncertainty':True,'input_uncertainty_propagation':True,'geostatistical_interpolation':False,'guardrails':_guardrails()}
