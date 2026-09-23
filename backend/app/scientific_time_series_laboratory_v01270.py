from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2, skew, kurtosis

VERSION = "0.127.0"
ENGINE_VERSION = "8.0.0"
SCHEMA = "sc-lab-scientific-time-series-laboratory/0.127.0"
SNAPSHOT_SCHEMA = "sc-lab-scientific-time-series-snapshot/0.127.0"
MAX_ROWS = 100_000
MAX_LAG = 512
MAX_FORECAST_HORIZON = 4096
MAX_CHANGEPOINTS = 64

METHOD_FAMILIES = {
    "frequency-audit", "trend-seasonal-decomposition", "acf-pacf", "stationarity-diagnostics",
    "differencing", "autoregression", "conditional-arima", "exponential-smoothing",
    "local-linear-trend-state-space", "rolling-origin-evaluation", "residual-diagnostics",
    "change-point-regime-analysis", "robust-anomaly-screening", "cross-correlation", "spectral-analysis",
}

FIGURE_FAMILIES = {
    "time-series-line", "seasonal-overlay", "trend-seasonal-remainder", "acf", "pacf",
    "rolling-statistics", "forecast-fan", "forecast-residuals", "rolling-error", "calibration-by-horizon",
    "change-point-timeline", "regime-bands", "anomaly-overlay", "cross-correlation", "periodogram",
    "state-space-components", "small-multiple-series", "forecast-comparison",
}


class TimeSeriesLaboratoryError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise TimeSeriesLaboratoryError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise TimeSeriesLaboratoryError(f"{label} must be finite.")
    return out


def _integer(value: Any, label: str, minimum: int = 0, maximum: int | None = None) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise TimeSeriesLaboratoryError(f"{label} must be an integer.") from exc
    if out < minimum or (maximum is not None and out > maximum):
        hi = f" and <= {maximum}" if maximum is not None else ""
        raise TimeSeriesLaboratoryError(f"{label} must be >= {minimum}{hi}.")
    return out


def _series(payload: dict[str, Any], value_key: str = "value") -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TimeSeriesLaboratoryError("payload must be an object.")
    rows = payload.get("rows")
    if rows is not None:
        if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) for r in rows):
            raise TimeSeriesLaboratoryError("rows must be a non-empty array of objects.")
        if len(rows) > MAX_ROWS:
            raise TimeSeriesLaboratoryError(f"rows cannot exceed {MAX_ROWS} records.", 413)
        time_col = str(payload.get("time") or "time")
        value_col = str(payload.get(value_key) or value_key)
        raw_t = [r.get(time_col) for r in rows]
        raw_y = [r.get(value_col) for r in rows]
    else:
        raw_y = payload.get("values")
        raw_t = payload.get("times")
        if not isinstance(raw_y, list) or not raw_y:
            raise TimeSeriesLaboratoryError("values must be a non-empty array when rows are not supplied.")
        if len(raw_y) > MAX_ROWS:
            raise TimeSeriesLaboratoryError(f"values cannot exceed {MAX_ROWS} records.", 413)
        if raw_t is None:
            raw_t = list(range(len(raw_y)))
        if not isinstance(raw_t, list) or len(raw_t) != len(raw_y):
            raise TimeSeriesLaboratoryError("times must be an array with the same length as values.")
    y = np.asarray([_finite(v, f"value[{i}]") for i, v in enumerate(raw_y)], dtype=float)
    labels = [str(x) for x in raw_t]
    time_kind = "numeric"
    try:
        t = np.asarray([float(x) for x in raw_t], dtype=float)
        if not np.all(np.isfinite(t)):
            raise ValueError
    except Exception:
        parsed = pd.to_datetime(raw_t, utc=True, errors="coerce")
        if parsed.isna().any():
            raise TimeSeriesLaboratoryError("times must be all numeric or all parseable datetimes.")
        t = parsed.astype("int64").to_numpy(dtype=float) / 1e9
        time_kind = "datetime"
        labels = [x.isoformat() for x in parsed]
    if len(y) < 3:
        raise TimeSeriesLaboratoryError("at least three observations are required.")
    dt = np.diff(t)
    if np.any(dt <= 0):
        raise TimeSeriesLaboratoryError("time values must be strictly increasing in supplied order; automatic sorting is disabled.")
    return {"time": t, "values": y, "labels": labels, "time_kind": time_kind}


def _interval_summary(t: np.ndarray, tolerance: float = 1e-6) -> dict[str, Any]:
    d = np.diff(t)
    median = float(np.median(d))
    mean = float(np.mean(d))
    sd = float(np.std(d))
    cv = float(sd / abs(mean)) if mean else None
    max_rel = float(np.max(np.abs(d - median)) / abs(median)) if median else float("inf")
    return {
        "median_interval": median, "mean_interval": mean, "interval_sd": sd,
        "interval_cv": cv, "max_relative_deviation": max_rel,
        "regular": bool(max_rel <= tolerance), "tolerance": float(tolerance),
    }


def schema_info() -> dict[str, Any]:
    return {"ok": True, "schema": SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION,
            "snapshot_schema": SNAPSHOT_SCHEMA,
            "limits": {"rows": MAX_ROWS, "max_lag": MAX_LAG, "forecast_horizon": MAX_FORECAST_HORIZON, "changepoints": MAX_CHANGEPOINTS}}


def catalog() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "method_families": sorted(METHOD_FAMILIES), "figure_families": sorted(FIGURE_FAMILIES),
            "automatic_frequency_inference": False, "automatic_model_selection": False, "automatic_stationarity_decision": False,
            "automatic_causal_interpretation": False}


def manifest() -> dict[str, Any]:
    return {"ok": True, "status": "scientific-time-series-laboratory-ready", "version": VERSION, "engine_version": ENGINE_VERSION,
            "time_series_profiling": True, "decomposition": True, "acf_pacf": True, "forecasting": True,
            "state_space": True, "change_point_analysis": True, "spectral_analysis": True, "rolling_evaluation": True,
            "forecast_uncertainty": True, "automatic_frequency_inference": False, "automatic_model_selection": False,
            "automatic_stationarity_decision": False, "automatic_changepoint_significance": False,
            "automatic_causal_interpretation": False, "automatic_scientific_validity_certification": False,
            "automatic_core_submission": False, "determine_truth": False}


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "method_family_count": len(METHOD_FAMILIES), "figure_family_count": len(FIGURE_FAMILIES)}


def normalize_series(payload: dict[str, Any]) -> dict[str, Any]:
    s = _series(payload)
    obj = {"schema": SCHEMA, "version": VERSION, "id": str(payload.get("id") or "time-series")[:180],
           "title": str(payload.get("title") or "Scientific time series")[:400], "time_kind": s["time_kind"],
           "times": s["labels"], "time_numeric": s["time"].tolist(), "values": s["values"].tolist(), "row_count": len(s["values"]),
           "units": str(payload.get("units") or "unspecified")[:120], "provenance": copy.deepcopy(payload.get("provenance") or {}),
           "boundaries": {"automatic_sorting": False, "automatic_frequency_inference": False, "automatic_imputation": False, "automatic_causal_interpretation": False}}
    obj["series_hash"] = _hash({k: v for k, v in obj.items() if k != "series_hash"})
    return {"ok": True, "version": VERSION, "series": obj}


def frequency_audit(payload: dict[str, Any]) -> dict[str, Any]:
    s = _series(payload); tol = _finite(payload.get("tolerance", 1e-6), "tolerance")
    if tol < 0: raise TimeSeriesLaboratoryError("tolerance must be non-negative.")
    out = _interval_summary(s["time"], tol)
    return {"ok": True, "version": VERSION, **out, "automatic_resampling": False, "frequency_certified": False,
            "interpretation": "Regularity is a descriptive property of supplied timestamps; domain sampling semantics remain researcher-declared."}


def _moving_average(y: np.ndarray, window: int) -> np.ndarray:
    n=len(y); h=window//2; out=np.full(n, np.nan)
    for i in range(n):
        lo=max(0,i-h); hi=min(n,i+h+1)
        if hi-lo >= max(2, window//2): out[i]=float(np.mean(y[lo:hi]))
    return out


def decompose_series(payload: dict[str, Any]) -> dict[str, Any]:
    s=_series(payload); y=s["values"]; period=_integer(payload.get("period"),"period",2,min(len(y)//2,512))
    trend=_moving_average(y, period if period%2 else period+1)
    detr=y-trend
    seasonal_pattern=[]
    for phase in range(period):
        vals=detr[phase::period]; vals=vals[np.isfinite(vals)]; seasonal_pattern.append(float(np.mean(vals)) if len(vals) else 0.0)
    seasonal_pattern=np.asarray(seasonal_pattern); seasonal_pattern-=np.mean(seasonal_pattern)
    seasonal=np.asarray([seasonal_pattern[i%period] for i in range(len(y))])
    remainder=y-trend-seasonal
    return {"ok":True,"version":VERSION,"period":period,"trend":[None if not np.isfinite(x) else float(x) for x in trend],
            "seasonal":seasonal.tolist(),"seasonal_pattern":seasonal_pattern.tolist(),
            "remainder":[None if not np.isfinite(x) else float(x) for x in remainder],
            "method":"declared-period-additive-moving-average","automatic_period_selection":False,"automatic_seasonality_certification":False}


def autocorrelation(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; max_lag=_integer(payload.get("max_lag",min(40,len(y)//3)),"max_lag",1,min(MAX_LAG,len(y)-1))
    z=y-np.mean(y); den=float(np.dot(z,z)); vals=[1.0]
    for k in range(1,max_lag+1): vals.append(float(np.dot(z[:-k],z[k:])/den) if den else 0.0)
    return {"ok":True,"version":VERSION,"lags":list(range(max_lag+1)),"acf":vals,"significance_labels_assigned":False}


def partial_autocorrelation(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; max_lag=_integer(payload.get("max_lag",min(20,len(y)//4)),"max_lag",1,min(MAX_LAG,len(y)//2))
    out=[1.0]
    for k in range(1,max_lag+1):
        target=y[k:]; X=np.column_stack([np.ones(len(target))]+[y[k-j-1:len(y)-j-1] for j in range(k)])
        beta=np.linalg.lstsq(X,target,rcond=None)[0]; out.append(float(beta[-1]))
    return {"ok":True,"version":VERSION,"lags":list(range(max_lag+1)),"pacf":out,"method":"ols-ar-k-last-lag","significance_labels_assigned":False}


def stationarity_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; n=len(y); lags=_integer(payload.get("adf_lags",min(2,max(0,n//20))),"adf_lags",0,min(20,max(0,n//5)))
    dy=np.diff(y)
    if len(dy)<=lags+2: raise TimeSeriesLaboratoryError("series too short for declared ADF lag order.")
    target=dy[lags:]; cols=[np.ones(len(target)), y[lags:-1]]
    for j in range(1,lags+1): cols.append(dy[lags-j:-j])
    X=np.column_stack(cols); beta=np.linalg.lstsq(X,target,rcond=None)[0]; resid=target-X@beta
    dof=max(1,len(target)-X.shape[1]); s2=float(np.dot(resid,resid)/dof); cov=np.linalg.pinv(X.T@X)*s2; se=float(math.sqrt(max(0,cov[1,1]))); adf_t=float(beta[1]/se) if se else None
    x=np.arange(n,dtype=float); slope=float(np.linalg.lstsq(np.column_stack([np.ones(n),x]),y,rcond=None)[0][1])
    chunks=np.array_split(y,min(4,n)); means=[float(np.mean(c)) for c in chunks if len(c)]; variances=[float(np.var(c,ddof=1)) if len(c)>1 else 0.0 for c in chunks if len(c)]
    centered=y-np.mean(y); cs=np.cumsum(centered); denom=float(np.var(y,ddof=1)) if n>1 else 0.0; kpss_like=float(np.sum(cs*cs)/(n*n*denom)) if denom>0 else None
    return {"ok":True,"version":VERSION,"linear_trend_slope":slope,"segment_means":means,"segment_variances":variances,
            "adf_regression":{"lagged_level_coefficient":float(beta[1]),"t_statistic":adf_t,"lag_order":lags},
            "kpss_like_level_statistic":kpss_like,"automatic_stationarity_decision":False,"unit_root_certified":False,
            "note":"Diagnostics are reported without automatic critical-value decisions; researcher chooses stationarity transformations."}


def difference_series(payload: dict[str, Any]) -> dict[str, Any]:
    s=_series(payload); d=_integer(payload.get("order",1),"order",0,3); y=s["values"].copy()
    for _ in range(d): y=np.diff(y)
    return {"ok":True,"version":VERSION,"order":d,"values":y.tolist(),"source_length":len(s["values"]),"result_length":len(y),"automatic_order_selection":False}


def _fit_ar_values(y: np.ndarray, p: int) -> dict[str, Any]:
    if p<0 or p>=len(y)-2: raise TimeSeriesLaboratoryError("AR order must be non-negative and leave at least three fitted observations.")
    if p==0:
        mu=float(np.mean(y)); fitted=np.full(len(y),mu); resid=y-fitted; coef=[mu]
    else:
        target=y[p:]; X=np.column_stack([np.ones(len(target))]+[y[p-j-1:len(y)-j-1] for j in range(p)])
        beta=np.linalg.lstsq(X,target,rcond=None)[0]; fit_tail=X@beta; fitted=np.full(len(y),np.nan); fitted[p:]=fit_tail; resid=target-fit_tail; coef=beta.tolist()
    res=np.asarray(resid[np.isfinite(resid)] if isinstance(resid,np.ndarray) else resid,dtype=float); rss=float(np.dot(res,res)); n=max(1,len(res)); k=len(coef); sigma2=rss/n if n else 0.0
    aic=float(n*math.log(max(sigma2,1e-15))+2*k); bic=float(n*math.log(max(sigma2,1e-15))+k*math.log(n))
    return {"coefficients":coef,"fitted":[None if not np.isfinite(v) else float(v) for v in fitted],"residuals":res.tolist(),"sigma":float(math.sqrt(max(sigma2,0))),"aic":aic,"bic":bic}


def fit_autoregression(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; p=_integer(payload.get("order",1),"order",0,min(MAX_LAG,len(y)-3)); r=_fit_ar_values(y,p)
    return {"ok":True,"version":VERSION,"model":"AR","order":p,**r,"automatic_order_selection":False,"model_selected":False}


def _difference_array(y: np.ndarray,d:int)->np.ndarray:
    out=y.copy()
    for _ in range(d): out=np.diff(out)
    return out


def _fit_arma_css(y: np.ndarray,p:int,q:int,iterations:int=8)->dict[str,Any]:
    start=max(p,q); n=len(y)
    if n-start<5: raise TimeSeriesLaboratoryError("series is too short for declared ARMA orders.")
    resid=np.zeros(n,dtype=float); beta=None; fitted=np.full(n,np.nan)
    for _ in range(iterations):
        target=y[start:]; cols=[np.ones(len(target))]
        for j in range(1,p+1): cols.append(y[start-j:n-j])
        for j in range(1,q+1): cols.append(resid[start-j:n-j])
        X=np.column_stack(cols); beta=np.linalg.lstsq(X,target,rcond=None)[0]; pred=X@beta; resid=np.zeros(n,dtype=float); resid[start:]=target-pred; fitted[start:]=pred
    rr=resid[start:]; rss=float(np.dot(rr,rr)); m=len(rr); k=len(beta); sigma2=rss/max(1,m)
    return {"coefficients":beta.tolist(),"fitted":[None if not np.isfinite(v) else float(v) for v in fitted],"residuals":rr.tolist(),"residual_full":resid,
            "sigma":float(math.sqrt(max(sigma2,0))),"aic":float(m*math.log(max(sigma2,1e-15))+2*k),"bic":float(m*math.log(max(sigma2,1e-15))+k*math.log(max(1,m))),"start":start}


def fit_arima(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; p=_integer(payload.get("p",1),"p",0,20); d=_integer(payload.get("d",0),"d",0,2); q=_integer(payload.get("q",0),"q",0,20)
    yd=_difference_array(y,d); r=_fit_arma_css(yd,p,q,_integer(payload.get("iterations",8),"iterations",2,50))
    return {"ok":True,"version":VERSION,"model":"conditional-ARIMA","order":{"p":p,"d":d,"q":q},
            **{k:v for k,v in r.items() if k!='residual_full'},"estimation":"conditional-least-squares","automatic_order_selection":False,"model_selected":False}


def exponential_smoothing(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; alpha=_finite(payload.get("alpha",0.3),"alpha"); beta=_finite(payload.get("beta",0.1),"beta"); gamma=_finite(payload.get("gamma",0.1),"gamma")
    for name,val in [('alpha',alpha),('beta',beta),('gamma',gamma)]:
        if not 0<=val<=1: raise TimeSeriesLaboratoryError(f"{name} must be between 0 and 1.")
    period=_integer(payload.get("period",0),"period",0,min(512,max(0,len(y)//2)))
    level=float(y[0]); trend=float(y[1]-y[0]); seasonal=np.zeros(max(period,1),dtype=float)
    if period>=2 and len(y)>=2*period:
        base=float(np.mean(y[:period])); seasonal=np.asarray([float(y[i]-base) for i in range(period)])
    fitted=np.full(len(y),np.nan); fitted[0]=level
    for i in range(1,len(y)):
        si=seasonal[i%period] if period>=2 else 0.0; pred=level+trend+si; fitted[i]=pred; prev_level=level
        level=alpha*(y[i]-si)+(1-alpha)*(level+trend); trend=beta*(level-prev_level)+(1-beta)*trend
        if period>=2: seasonal[i%period]=gamma*(y[i]-level)+(1-gamma)*si
    resid=y[1:]-fitted[1:]
    return {"ok":True,"version":VERSION,"model":"additive-holt-winters" if period>=2 else "holt-linear",
            "alpha":alpha,"beta":beta,"gamma":gamma if period>=2 else None,"period":period or None,
            "level":level,"trend":trend,"seasonal":seasonal.tolist() if period>=2 else [],
            "fitted":[None if not np.isfinite(v) else float(v) for v in fitted],"residuals":resid.tolist(),"sigma":float(np.std(resid,ddof=1)) if len(resid)>1 else 0.0,
            "automatic_parameter_optimization":False,"automatic_period_selection":False}


def state_space_local_linear_trend(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)["values"]; ql=_finite(payload.get("level_variance",0.01),"level_variance"); qt=_finite(payload.get("trend_variance",0.001),"trend_variance"); r=_finite(payload.get("observation_variance",1.0),"observation_variance")
    if min(ql,qt,r)<0 or r==0: raise TimeSeriesLaboratoryError("state/observation variances must be non-negative and observation_variance > 0.")
    x=np.array([y[0], y[1]-y[0]],dtype=float); P=np.eye(2)*max(r,1.0); F=np.array([[1.,1.],[0.,1.]]); H=np.array([[1.,0.]]); Q=np.diag([ql,qt]); R=np.array([[r]])
    levels=[]; trends=[]; innovations=[]; innovation_vars=[]
    for obs in y:
        xp=F@x; Pp=F@P@F.T+Q; innov=float(obs-(H@xp)[0]); S=float((H@Pp@H.T+R)[0,0]); K=(Pp@H.T/S).reshape(2); x=xp+K*innov; P=(np.eye(2)-np.outer(K,H.reshape(2)))@Pp
        levels.append(float(x[0])); trends.append(float(x[1])); innovations.append(innov); innovation_vars.append(S)
    return {"ok":True,"version":VERSION,"model":"local-linear-trend-state-space","level":levels,"trend":trends,"innovations":innovations,"innovation_variance":innovation_vars,
            "declared_variances":{"level":ql,"trend":qt,"observation":r},"automatic_variance_estimation":False,"automatic_regime_inference":False}


def _forecast_ar(y:np.ndarray,p:int,h:int)->tuple[list[float],float]:
    f=_fit_ar_values(y,p); coef=np.asarray(f['coefficients']); hist=list(map(float,y)); out=[]
    for _ in range(h):
        if p==0: v=float(coef[0])
        else: v=float(coef[0]+sum(coef[j]*hist[-j] for j in range(1,p+1)))
        out.append(v); hist.append(v)
    return out,float(f['sigma'])


def _forecast_arima(y:np.ndarray,p:int,d:int,q:int,h:int,iterations:int=8)->tuple[list[float],float]:
    yd=_difference_array(y,d); fit=_fit_arma_css(yd,p,q,iterations); beta=np.asarray(fit['coefficients']); resid=list(map(float,fit['residual_full'])); hist=list(map(float,yd)); diffs=[]
    for _ in range(h):
        v=float(beta[0]); idx=1
        for j in range(1,p+1): v+=float(beta[idx])*hist[-j]; idx+=1
        for j in range(1,q+1): v+=float(beta[idx])*(resid[-j] if len(resid)>=j else 0.0); idx+=1
        diffs.append(v); hist.append(v); resid.append(0.0)
    out=diffs
    if d>=1:
        last=float(y[-1]); out1=[]
        if d==1:
            for dv in diffs: last+=dv; out1.append(last)
        else:
            first_diff=float(y[-1]-y[-2]);
            for dd in diffs: first_diff+=dd; last+=first_diff; out1.append(last)
        out=out1
    return list(map(float,out)),float(fit['sigma'])


def _forecast_ets(y:np.ndarray,payload:dict[str,Any],h:int)->tuple[list[float],float]:
    fit=exponential_smoothing({"values":y.tolist(),**{k:payload[k] for k in ('alpha','beta','gamma','period') if k in payload}}); level=float(fit['level']); trend=float(fit['trend']); season=fit.get('seasonal') or []; period=fit.get('period') or 0; out=[]
    for k in range(1,h+1): out.append(level+k*trend+(float(season[(len(y)+k-1)%period]) if period else 0.0))
    return out,float(fit['sigma'])


def forecast(payload: dict[str, Any]) -> dict[str, Any]:
    s=_series(payload); y=s['values']; h=_integer(payload.get('horizon',10),'horizon',1,MAX_FORECAST_HORIZON); model=str(payload.get('model') or 'ar').lower(); spec=payload.get('model_spec') or {}
    if model=='ar': point,sigma=_forecast_ar(y,_integer(spec.get('order',1),'order',0,min(50,len(y)-3)),h)
    elif model=='arima': point,sigma=_forecast_arima(y,_integer(spec.get('p',1),'p',0,20),_integer(spec.get('d',0),'d',0,2),_integer(spec.get('q',0),'q',0,20),h,_integer(spec.get('iterations',8),'iterations',2,50))
    elif model in {'ets','exponential-smoothing'}: point,sigma=_forecast_ets(y,spec,h)
    elif model in {'state-space','local-linear-trend'}:
        ss=state_space_local_linear_trend({"values":y.tolist(),**spec}); level=ss['level'][-1]; trend=ss['trend'][-1]; point=[float(level+(k+1)*trend) for k in range(h)]; sigma=float(math.sqrt(spec.get('observation_variance',1.0)))
    else: raise TimeSeriesLaboratoryError("model must be ar, arima, ets, or state-space.")
    z=_finite(payload.get('interval_z',1.96),'interval_z'); lower=[float(v-z*sigma*math.sqrt(k+1)) for k,v in enumerate(point)]; upper=[float(v+z*sigma*math.sqrt(k+1)) for k,v in enumerate(point)]
    return {"ok":True,"version":VERSION,"model":model,"horizon":h,"point_forecast":point,"lower":lower,"upper":upper,"interval_z":z,
            "interval_semantics":"model-residual-scale heuristic; not guaranteed coverage","automatic_model_selection":False,"forecast_is_observed_evidence":False}


def rolling_origin_evaluation(payload: dict[str, Any]) -> dict[str, Any]:
    s=_series(payload); y=s['values']; min_train=_integer(payload.get('min_train',max(10,len(y)//2)),'min_train',5,len(y)-1); step=_integer(payload.get('step',1),'step',1,1000); model=str(payload.get('model') or 'ar'); spec=payload.get('model_spec') or {}; errors=[]; rows=[]
    for end in range(min_train,len(y),step):
        if end>=len(y): break
        fp={"values":y[:end].tolist(),"model":model,"model_spec":spec,"horizon":1}; pred=forecast(fp)['point_forecast'][0]; actual=float(y[end]); err=actual-pred; errors.append(err); rows.append({"train_end_index":end-1,"test_index":end,"actual":actual,"forecast":pred,"error":err})
    if not errors: raise TimeSeriesLaboratoryError("rolling evaluation produced no test origins.")
    e=np.asarray(errors); return {"ok":True,"version":VERSION,"origins":rows,"metrics":{"mae":float(np.mean(np.abs(e))),"rmse":float(np.sqrt(np.mean(e*e))),"bias":float(np.mean(e))},
            "automatic_model_selection":False,"temporal_order_preserved":True}


def residual_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    r=payload.get('residuals')
    if not isinstance(r,list) or len(r)<5: raise TimeSeriesLaboratoryError("residuals must contain at least five values.")
    y=np.asarray([_finite(v,f'residual[{i}]') for i,v in enumerate(r)],dtype=float); max_lag=_integer(payload.get('max_lag',min(20,len(y)//4)),'max_lag',1,min(MAX_LAG,len(y)-1)); z=y-np.mean(y); den=float(np.dot(z,z)); ac=[]
    for k in range(1,max_lag+1): ac.append(float(np.dot(z[:-k],z[k:])/den) if den else 0.0)
    n=len(y); q=float(n*(n+2)*sum((rho*rho)/(n-k) for k,rho in enumerate(ac,start=1))); p=float(chi2.sf(q,max_lag))
    return {"ok":True,"version":VERSION,"mean":float(np.mean(y)),"sd":float(np.std(y,ddof=1)),"skew":float(skew(y,bias=False)),"excess_kurtosis":float(kurtosis(y,bias=False)),
            "acf":ac,"ljung_box":{"Q":q,"df":max_lag,"p_value":p},"automatic_accept_reject_decision":False,"model_validity_certified":False}


def _sse(x:np.ndarray)->float:
    if len(x)==0:return 0.0
    d=x-np.mean(x);return float(np.dot(d,d))


def change_point_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)['values']; min_size=_integer(payload.get('min_size',max(3,len(y)//20)),'min_size',2,max(2,len(y)//3)); max_breaks=_integer(payload.get('max_breaks',5),'max_breaks',0,min(MAX_CHANGEPOINTS,max(0,len(y)//min_size-1))); penalty=_finite(payload.get('penalty',0.0),'penalty'); segments=[(0,len(y))]; breaks=[]
    for _ in range(max_breaks):
        best=None
        for si,(a,b) in enumerate(segments):
            if b-a<2*min_size: continue
            parent=_sse(y[a:b])
            for c in range(a+min_size,b-min_size+1):
                gain=parent-_sse(y[a:c])-_sse(y[c:b])
                if best is None or gain>best[0]: best=(gain,si,c)
        if best is None or best[0]<=penalty: break
        gain,si,c=best; a,b=segments.pop(si); segments.extend([(a,c),(c,b)]); segments.sort(); breaks.append({"index":c,"gain":float(gain)})
    return {"ok":True,"version":VERSION,"changepoints":sorted(breaks,key=lambda x:x['index']),"segments":[{"start":a,"end_exclusive":b,"mean":float(np.mean(y[a:b])),"sd":float(np.std(y[a:b],ddof=1)) if b-a>1 else 0.0} for a,b in segments],
            "penalty":penalty,"automatic_significance_test":False,"structural_break_certified":False}


def regime_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    cp=change_point_analysis(payload); regimes=[]
    for i,s in enumerate(cp['segments']): regimes.append({"regime":i+1,**s,"interpretation":"descriptive-segment"})
    return {"ok":True,"version":VERSION,"regimes":regimes,"changepoints":cp['changepoints'],"automatic_regime_labeling":False,"causal_regime_interpretation":False}


def anomaly_screen(payload: dict[str, Any]) -> dict[str, Any]:
    y=_series(payload)['values']; threshold=_finite(payload.get('threshold',3.5),'threshold'); med=float(np.median(y)); mad=float(np.median(np.abs(y-med))); scale=1.4826*mad; scores=np.zeros(len(y)) if scale==0 else (y-med)/scale; flags=[{"index":i,"value":float(v),"robust_z":float(scores[i])} for i,v in enumerate(y) if abs(scores[i])>=threshold]
    return {"ok":True,"version":VERSION,"median":med,"mad":mad,"threshold":threshold,"flags":flags,"automatic_exclusion":False,"anomaly_is_error":False}


def cross_correlation(payload: dict[str, Any]) -> dict[str, Any]:
    x=payload.get('x_values'); y=payload.get('y_values')
    if not isinstance(x,list) or not isinstance(y,list) or len(x)!=len(y) or len(x)<5: raise TimeSeriesLaboratoryError("x_values and y_values must have equal length >= 5.")
    a=np.asarray([_finite(v,f'x[{i}]') for i,v in enumerate(x)]); b=np.asarray([_finite(v,f'y[{i}]') for i,v in enumerate(y)]); max_lag=_integer(payload.get('max_lag',min(20,len(a)//4)),'max_lag',0,min(MAX_LAG,len(a)-2)); rows=[]
    for lag in range(-max_lag,max_lag+1):
        if lag<0: aa=a[-lag:]; bb=b[:len(b)+lag]
        elif lag>0: aa=a[:-lag]; bb=b[lag:]
        else: aa=a; bb=b
        corr=float(np.corrcoef(aa,bb)[0,1]) if len(aa)>2 and np.std(aa)>0 and np.std(bb)>0 else 0.0; rows.append({"lag":lag,"correlation":corr,"n":len(aa)})
    return {"ok":True,"version":VERSION,"cross_correlation":rows,"lag_sign_convention":"positive lag compares x[t] with y[t+lag]","automatic_lead_lag_causality":False,"significance_labels_assigned":False}


def spectral_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    s=_series(payload); audit=_interval_summary(s['time'],_finite(payload.get('tolerance',1e-6),'tolerance'))
    if not audit['regular'] and 'sampling_interval' not in payload: raise TimeSeriesLaboratoryError("irregular timestamps require an explicit sampling_interval or prior resampling outside this endpoint.")
    dt=_finite(payload.get('sampling_interval',audit['median_interval']),'sampling_interval');
    if dt<=0: raise TimeSeriesLaboratoryError("sampling_interval must be > 0.")
    y=s['values']-np.mean(s['values']); n=len(y); fft=np.fft.rfft(y); power=(np.abs(fft)**2)/n; freq=np.fft.rfftfreq(n,d=dt); rows=[]
    for f,p in zip(freq[1:],power[1:]): rows.append({"frequency":float(f),"period":float(1/f) if f>0 else None,"power":float(p)})
    top=sorted(rows,key=lambda r:r['power'],reverse=True)[:min(10,len(rows))]
    return {"ok":True,"version":VERSION,"sampling_interval":dt,"spectrum":rows,"top_components":top,"automatic_cycle_certification":False,"spectral_peak_significance_tested":False}


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figs=[{"figure_type":f,"renderer":"svg-or-canvas","publication_profile":"scientific","semantic_role":"time-series-analysis"} for f in sorted(FIGURE_FAMILIES)]
    return {"ok":True,"version":VERSION,"figures":figs,"figure_count":len(figs),"uncertainty_encoding_required_for_forecasts":True,"automatic_claim_generation":False,"automatic_significance_annotation":False}


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    studio={"schema":SCHEMA,"version":VERSION,"id":str(payload.get('studio_id') or 'time-series-studio')[:180],"series_ref":str(payload.get('series_ref') or payload.get('series_id') or 'series:declared')[:300],
            "methods":copy.deepcopy(payload.get('methods') or []),"models":copy.deepcopy(payload.get('models') or []),"evaluation":copy.deepcopy(payload.get('evaluation') or {}),"provenance":copy.deepcopy(payload.get('provenance') or {}),
            "boundaries":{"automatic_model_selection":False,"automatic_stationarity_decision":False,"automatic_causal_interpretation":False}}
    studio['studio_hash']=_hash({k:v for k,v in studio.items() if k!='studio_hash'}); return {"ok":True,"version":VERSION,"studio":studio}


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"studio":copy.deepcopy(payload.get('studio') or {}),"series_ref":payload.get('series_ref'),"model_specs":copy.deepcopy(payload.get('model_specs') or []),"results":copy.deepcopy(payload.get('results') or []),"provenance":copy.deepcopy(payload.get('provenance') or {})}; snap['snapshot_hash']=_hash({k:v for k,v in snap.items() if k!='snapshot_hash'}); return {"ok":True,"version":VERSION,"snapshot":snap,"snapshot_hash":snap['snapshot_hash'],"automatic_persistence":False}


def build_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    ref=str(payload.get('snapshot_ref') or 'snapshot:declared'); return {"ok":True,"version":VERSION,"snapshot_ref":ref,"steps":["resolve immutable series/dataset reference","restore declared temporal frequency and transformations","restore declared model specification","re-run diagnostics/evaluation","compare output hashes and forecast artifacts"],"automatic_execution":False}


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"formats":payload.get('formats') or ['json','csv','svg','pdf'],"include_series_provenance":True,"include_model_specification":True,"include_forecast_intervals":True,"include_diagnostics":True,"automatic_publication":False}


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    sid=str(payload.get('session_id') or 'session:declared'); aid=str(payload.get('analysis_id') or 'time-series-analysis')
    return {"ok":True,"version":VERSION,"core_minimum_version":"3.0.0","session_id":sid,"analysis_id":aid,"object_type":"scientific-time-series-analysis","operation_plan":[{"operation":"bind-object","object_ref":aid},{"operation":"bind-visuals","source_ref":aid},{"operation":"bind-execution-lineage","source_ref":aid}],"automatic_core_submission":False,"core_mutation_performed":False}


def build_execution_lineage_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"session_id":str(payload.get('session_id') or 'session:declared'),"execution_ref":str(payload.get('execution_ref') or 'execution:time-series'),"method_ref":str(payload.get('method_ref') or 'method:time-series'),"input_refs":copy.deepcopy(payload.get('input_refs') or []),"output_refs":copy.deepcopy(payload.get('output_refs') or []),"environment_ref":payload.get('environment_ref'),"automatic_execution":False,"automatic_core_submission":False}


def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    boundaries=[
        "Temporal ordering and predictability do not establish causality.",
        "Irregular timestamps are not silently resampled or frequency-normalized.",
        "Stationarity diagnostics do not automatically select transformations or declare unit-root status.",
        "ACF/PACF and cross-correlation do not receive automatic significance or causal labels.",
        "Forecast-model families and orders are researcher-declared; no automatic winner is selected.",
        "Forecast intervals are model-dependent uncertainty statements, not guaranteed empirical coverage.",
        "Detected change points and regimes are descriptive unless separately validated under a declared inferential design.",
        "Anomaly flags are not automatically deleted or treated as measurement errors.",
        "Spectral peaks are not automatically certified as physical cycles.",
        "Time-series outputs do not automatically become evidence, findings, or claims in Platform Core.",
    ]
    return {"ok":True,"version":VERSION,"boundaries":boundaries,"causal_validity_certified":False,"stationarity_certified":False,"forecast_validity_certified":False,"scientific_validity_certified":False,"determine_truth":False}
