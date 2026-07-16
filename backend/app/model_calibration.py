from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

import numpy as np
from scipy.optimize import least_squares

VERSION = "0.30.2"
STUDY_SCHEMA = "sc-lab-model-calibration-study/0.30.2"
RESULT_SCHEMA = "sc-lab-model-calibration-result/0.30.2"
VALIDATION_SCHEMA = "sc-lab-model-validation/0.30.2"
COMPARISON_SCHEMA = "sc-lab-model-comparison/0.30.2"
BUNDLE_SCHEMA = "sc-lab-model-calibration-bundle/0.30.2"
MAX_ROWS = 10000
MAX_FEATURES = 20
MAX_PARAMETERS = 64

class ModelCalibrationError(ValueError):
    pass

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()

def _text(value: Any, limit: int = 4000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]

def _float(value: Any, default: float | None = None) -> float | None:
    try:
        n = float(value)
        return n if math.isfinite(n) else default
    except (TypeError, ValueError):
        return default

def health() -> dict[str, Any]:
    return {
        "ok": True, "status": "ready", "version": VERSION,
        "studySchema": STUDY_SCHEMA, "resultSchema": RESULT_SCHEMA,
        "validationSchema": VALIDATION_SCHEMA, "comparisonSchema": COMPARISON_SCHEMA,
        "modelTypes": ["linear-multivariate", "polynomial-univariate", "exponential-univariate", "logistic-univariate"],
        "objectives": ["least-squares", "weighted-least-squares", "robust-huber", "robust-soft-l1"],
        "capabilities": {"parameterFitting": True, "holdoutValidation": True, "confidenceIntervals": True, "residualDiagnostics": True, "modelComparison": True, "calibrationProvenance": True, "arbitraryFormula": False, "arbitraryCode": False},
        "limits": {"rows": MAX_ROWS, "features": MAX_FEATURES, "parameters": MAX_PARAMETERS},
    }

def policies() -> dict[str, Any]:
    return {
        "version": VERSION,
        "modelTypes": [
            {"id":"linear-multivariate","description":"Intercept plus one coefficient per numeric feature."},
            {"id":"polynomial-univariate","description":"Single-feature polynomial with degree 1 through 5."},
            {"id":"exponential-univariate","description":"offset + scale × exp(rate × x)."},
            {"id":"logistic-univariate","description":"bounded four-parameter logistic response."},
        ],
        "objectives": ["least-squares", "weighted-least-squares", "robust-huber", "robust-soft-l1"],
        "holdout": {"minimumFraction": 0.0, "maximumFraction": 0.5, "defaultFraction": 0.2, "seeded": True},
        "confidenceLevel": 0.95,
        "registeredModelFormsOnly": True,
        "arbitraryFormula": False,
        "arbitraryCode": False,
        "serverBackedRegistry": False,
    }

def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows") or payload.get("dataset") or []
    if not isinstance(rows, list) or not rows:
        raise ModelCalibrationError("A non-empty dataset row array is required.")
    if len(rows) > MAX_ROWS:
        raise ModelCalibrationError(f"Dataset exceeds the {MAX_ROWS}-row limit.")
    return [r for r in rows if isinstance(r, dict)]

def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("study") if isinstance(payload.get("study"), dict) else payload
    features = [str(x).strip()[:160] for x in source.get("features", []) if str(x).strip()]
    response = _text(source.get("response"), 160)
    model_type = _text(source.get("modelType"), 80).lower() or "linear-multivariate"
    if model_type not in {x["id"] for x in policies()["modelTypes"]}:
        raise ModelCalibrationError("Unsupported registered model type.")
    if not response: raise ModelCalibrationError("A response column is required.")
    if not features: raise ModelCalibrationError("At least one feature column is required.")
    if len(features) > MAX_FEATURES: raise ModelCalibrationError(f"No more than {MAX_FEATURES} features are allowed.")
    if model_type != "linear-multivariate" and len(features) != 1:
        raise ModelCalibrationError("The selected model type requires exactly one feature.")
    degree = max(1, min(5, int(source.get("degree") or 2)))
    objective = _text(source.get("objective"), 80).lower() or "least-squares"
    if objective not in policies()["objectives"]: raise ModelCalibrationError("Unsupported objective function.")
    holdout = _float(source.get("holdoutFraction"), 0.2)
    holdout = max(0.0, min(0.5, holdout if holdout is not None else 0.2))
    study = {
        "schema": STUDY_SCHEMA, "version": VERSION, "recordType": "model-calibration-study",
        "id": _text(source.get("id"), 180) or f"model-calibration-study-{_hash(source)[:16]}",
        "title": _text(source.get("title"), 500) or "Untitled model calibration",
        "datasetId": _text(source.get("datasetId"), 180),
        "experimentProtocolId": _text(source.get("experimentProtocolId"), 180),
        "designStudyId": _text(source.get("designStudyId"), 180),
        "modelType": model_type, "features": features, "response": response, "weightColumn": _text(source.get("weightColumn"), 160),
        "degree": degree, "objective": objective, "holdoutFraction": holdout, "seed": int(source.get("seed") or 42),
        "initialParameters": source.get("initialParameters") if isinstance(source.get("initialParameters"), dict) else {},
        "parameterBounds": source.get("parameterBounds") if isinstance(source.get("parameterBounds"), dict) else {},
        "units": source.get("units") if isinstance(source.get("units"), dict) else {},
        "notes": _text(source.get("notes"), 12000), "sourceIds": list(source.get("sourceIds") or [])[:200],
        "createdAt": source.get("createdAt") or _now(), "updatedAt": _now(),
    }
    study["studyHash"] = _hash({k:v for k,v in study.items() if k not in {"studyHash","updatedAt"}})
    return study

def _clean_dataset(study: dict[str, Any], rows: list[dict[str, Any]]):
    feature_names = study["features"]; response = study["response"]; weight_col = study.get("weightColumn")
    X=[]; y=[]; w=[]; kept=[]; dropped=0
    for row in rows:
        vals=[_float(row.get(name)) for name in feature_names]; target=_float(row.get(response))
        if target is None or any(v is None for v in vals): dropped += 1; continue
        X.append(vals); y.append(target); kept.append(row)
        weight = _float(row.get(weight_col), 1.0) if weight_col else 1.0
        w.append(max(1e-12, weight if weight is not None else 1.0))
    if len(X) < max(4, len(feature_names)+2): raise ModelCalibrationError("Too few complete numeric rows for calibration.")
    return np.asarray(X,float), np.asarray(y,float), np.asarray(w,float), kept, dropped

def _parameter_names(study):
    t=study["modelType"]
    if t=="linear-multivariate": return ["intercept"]+[f"beta:{x}" for x in study["features"]]
    if t=="polynomial-univariate": return [f"c{i}" for i in range(study["degree"]+1)]
    if t=="exponential-univariate": return ["offset","scale","rate"]
    return ["lower","upper","rate","midpoint"]

def _defaults(study, X, y):
    t=study["modelType"]
    if t=="linear-multivariate":
        A=np.column_stack([np.ones(len(X)),X]); return np.linalg.lstsq(A,y,rcond=None)[0]
    if t=="polynomial-univariate":
        coeff=np.polyfit(X[:,0],y,study["degree"])[::-1]; return coeff
    if t=="exponential-univariate": return np.array([float(np.min(y)), max(float(np.ptp(y)),1.0), 0.1])
    return np.array([float(np.min(y)),float(np.max(y)),1.0,float(np.median(X[:,0]))])

def _predict(study, p, X):
    t=study["modelType"]
    if t=="linear-multivariate": return p[0]+X@p[1:]
    x=X[:,0]
    if t=="polynomial-univariate": return sum(p[i]*(x**i) for i in range(len(p)))
    if t=="exponential-univariate": return p[0]+p[1]*np.exp(np.clip(p[2]*x,-60,60))
    lower,upper,rate,mid=p; return lower+(upper-lower)/(1+np.exp(np.clip(-rate*(x-mid),-60,60)))

def _bounds(study,names):
    lo=[]; hi=[]; custom=study.get("parameterBounds") or {}
    for name in names:
        row=custom.get(name) if isinstance(custom.get(name),dict) else {}
        lo.append(_float(row.get("low"), -np.inf)); hi.append(_float(row.get("high"), np.inf))
    return np.asarray(lo,float),np.asarray(hi,float)

def _metrics(y,pred):
    res=y-pred; sse=float(np.sum(res**2)); n=len(y); mean=float(np.mean(y)); sst=float(np.sum((y-mean)**2))
    return {"count":n,"rmse":float(np.sqrt(np.mean(res**2))),"mae":float(np.mean(np.abs(res))),"bias":float(np.mean(res)),"rSquared":float(1-sse/sst) if sst>0 else None,"maxAbsoluteError":float(np.max(np.abs(res))),"sse":sse}

def _diagnostics(y,pred):
    r=y-pred; denom=float(np.sum(r**2)); dw=float(np.sum(np.diff(r)**2)/denom) if len(r)>1 and denom>0 else None
    return {"meanResidual":float(np.mean(r)),"residualStd":float(np.std(r,ddof=1)) if len(r)>1 else 0.0,"durbinWatson":dw,"quantiles":{"q05":float(np.quantile(r,.05)),"q50":float(np.quantile(r,.5)),"q95":float(np.quantile(r,.95))},"residuals":[float(x) for x in r[:2000]]}

def calibrate(payload: dict[str, Any]) -> dict[str, Any]:
    study=normalize_study(payload); rows=_rows(payload); X,y,w,kept,dropped=_clean_dataset(study,rows)
    rng=np.random.default_rng(study["seed"]); indices=np.arange(len(y)); rng.shuffle(indices)
    hold_n=int(round(len(y)*study["holdoutFraction"])); hold_n=min(max(0,hold_n),max(0,len(y)-max(3,len(study["features"])+1)))
    hold_idx=indices[:hold_n]; train_idx=indices[hold_n:]
    Xtr,ytr,wtr=X[train_idx],y[train_idx],w[train_idx]
    names=_parameter_names(study); p0=np.asarray([_float(study["initialParameters"].get(n)) for n in names],dtype=object)
    defaults=_defaults(study,Xtr,ytr); p0=np.asarray([defaults[i] if p0[i] is None else float(p0[i]) for i in range(len(names))],float)
    lo,hi=_bounds(study,names); p0=np.maximum(np.minimum(p0,np.where(np.isfinite(hi),hi-1e-12,hi)),np.where(np.isfinite(lo),lo+1e-12,lo))
    objective=study["objective"]; loss={"least-squares":"linear","weighted-least-squares":"linear","robust-huber":"huber","robust-soft-l1":"soft_l1"}[objective]
    def residual(p):
        r=_predict(study,p,Xtr)-ytr
        return r*np.sqrt(wtr) if objective=="weighted-least-squares" else r
    fit=least_squares(residual,p0,bounds=(lo,hi),loss=loss,max_nfev=5000)
    params={n:float(v) for n,v in zip(names,fit.x)}; train_pred=_predict(study,fit.x,Xtr)
    hold_pred=_predict(study,fit.x,X[hold_idx]) if hold_n else np.asarray([],float)
    train_metrics=_metrics(ytr,train_pred); hold_metrics=_metrics(y[hold_idx],hold_pred) if hold_n else None
    dof=max(1,len(ytr)-len(fit.x)); sigma2=float(np.sum((ytr-train_pred)**2)/dof)
    ci={}; condition=None
    try:
        jtj=fit.jac.T@fit.jac; condition=float(np.linalg.cond(jtj)); cov=np.linalg.pinv(jtj)*sigma2; se=np.sqrt(np.maximum(np.diag(cov),0))
        for n,v,s in zip(names,fit.x,se): ci[n]={"estimate":float(v),"standardError":float(s),"lower95":float(v-1.96*s),"upper95":float(v+1.96*s)}
    except Exception:
        for n,v in params.items(): ci[n]={"estimate":v,"standardError":None,"lower95":None,"upper95":None}
    k=len(fit.x); n=len(ytr); sse=max(train_metrics["sse"],1e-300); aic=float(n*math.log(sse/n)+2*k); bic=float(n*math.log(sse/n)+k*math.log(max(n,1)))
    result={"schema":RESULT_SCHEMA,"version":VERSION,"recordType":"model-calibration-result","id":f"model-calibration-result-{_hash([study['studyHash'],params])[:16]}","title":f"Calibration: {study['title']}","studyId":study["id"],"studyHash":study["studyHash"],"modelType":study["modelType"],"parameterNames":names,"parameters":params,"confidenceIntervals":ci,"objective":objective,"success":bool(fit.success),"status":int(fit.status),"message":str(fit.message),"iterations":int(fit.nfev),"trainMetrics":train_metrics,"holdoutMetrics":hold_metrics,"residualDiagnostics":_diagnostics(ytr,train_pred),"conditionNumber":condition,"aic":aic,"bic":bic,"rowCounts":{"supplied":len(rows),"usable":len(y),"dropped":dropped,"training":len(train_idx),"holdout":hold_n},"split":{"seed":study["seed"],"holdoutFraction":study["holdoutFraction"],"trainingIndices":[int(x) for x in train_idx],"holdoutIndices":[int(x) for x in hold_idx]},"provenance":{"serviceVersion":VERSION,"algorithm":"scipy.optimize.least_squares","registeredModelForm":True,"datasetHash":_hash(rows),"studyHash":study["studyHash"]},"createdAt":_now()}
    result["resultHash"]=_hash({k:v for k,v in result.items() if k!="resultHash"})
    validation=validate_result({"study":study,"result":result,"rows":rows})
    return {"ok":True,"study":study,"result":result,"validation":validation}

def validate_result(payload: dict[str, Any]) -> dict[str, Any]:
    study=normalize_study(payload); result=payload.get("result") if isinstance(payload.get("result"),dict) else {}
    rows=_rows(payload); X,y,_,_,dropped=_clean_dataset(study,rows); names=_parameter_names(study)
    params=result.get("parameters") if isinstance(result.get("parameters"),dict) else {}
    if any(name not in params for name in names): raise ModelCalibrationError("Calibration result is missing required parameters.")
    p=np.asarray([float(params[n]) for n in names],float); pred=_predict(study,p,X); metrics=_metrics(y,pred); diagnostics=_diagnostics(y,pred)
    record={"schema":VALIDATION_SCHEMA,"version":VERSION,"recordType":"model-validation","id":f"model-validation-{_hash([study['id'],params,rows])[:16]}","title":f"Validation: {study['title']}","studyId":study["id"],"calibrationResultId":result.get("id"),"metrics":metrics,"residualDiagnostics":diagnostics,"rowCounts":{"supplied":len(rows),"usable":len(y),"dropped":dropped},"passed":bool(metrics["count"]>=3 and math.isfinite(metrics["rmse"])),"createdAt":_now()}
    record["validationHash"]=_hash({k:v for k,v in record.items() if k!="validationHash"})
    return record

def compare_models(payload: dict[str, Any]) -> dict[str, Any]:
    results=[r for r in payload.get("results",[]) if isinstance(r,dict)]
    if len(results)<2: raise ModelCalibrationError("At least two calibration results are required.")
    rows=[]
    for r in results:
        hold=r.get("holdoutMetrics") or {}; train=r.get("trainMetrics") or {}
        score=hold.get("rmse") if hold.get("rmse") is not None else train.get("rmse")
        rows.append({"resultId":r.get("id"),"title":r.get("title"),"modelType":r.get("modelType"),"rmse":score,"holdoutRMSE":hold.get("rmse"),"trainRMSE":train.get("rmse"),"rSquared":hold.get("rSquared") if hold else train.get("rSquared"),"aic":r.get("aic"),"bic":r.get("bic"),"parameterCount":len(r.get("parameters") or {})})
    rows.sort(key=lambda x:(float('inf') if x["rmse"] is None else x["rmse"],float('inf') if x["bic"] is None else x["bic"]))
    record={"schema":COMPARISON_SCHEMA,"version":VERSION,"recordType":"model-comparison","id":f"model-comparison-{_hash(rows)[:16]}","title":_text(payload.get("title"),500) or "Scientific model comparison","ranking":rows,"recommendedResultId":rows[0]["resultId"],"selectionPolicy":"lowest holdout RMSE, falling back to training RMSE and BIC","createdAt":_now()}
    record["comparisonHash"]=_hash({k:v for k,v in record.items() if k!="comparisonHash"})
    return record

def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    study=normalize_study(payload); result=payload.get("result") if isinstance(payload.get("result"),dict) else {}; validation=payload.get("validation") if isinstance(payload.get("validation"),dict) else {}
    lines=[f"# Model calibration report: {study['title']}","",f"- Model type: {study['modelType']}",f"- Objective: {study['objective']}",f"- Dataset: {study.get('datasetId') or 'inline dataset'}",f"- Calibration hash: {result.get('resultHash') or 'not supplied'}","","## Parameters"]
    for name,value in (result.get("parameters") or {}).items():
        ci=(result.get("confidenceIntervals") or {}).get(name,{})
        lines.append(f"- {name}: {value:.8g}" + (f" (95% CI {ci.get('lower95'):.8g} to {ci.get('upper95'):.8g})" if isinstance(ci.get('lower95'),(int,float)) else ""))
    lines += ["","## Calibration metrics",f"- Training RMSE: {(result.get('trainMetrics') or {}).get('rmse')}",f"- Holdout RMSE: {(result.get('holdoutMetrics') or {}).get('rmse')}",f"- AIC: {result.get('aic')}",f"- BIC: {result.get('bic')}","","## Validation",f"- Passed: {validation.get('passed')}",f"- Validation RMSE: {(validation.get('metrics') or {}).get('rmse')}","","## Limitations",study.get("notes") or "No limitations were recorded."]
    report={"schema":"sc-lab-model-calibration-report/0.30.2","version":VERSION,"recordType":"model-calibration-report","id":f"model-calibration-report-{_hash([study.get('id'),result.get('id')])[:16]}","title":f"Model calibration report: {study['title']}","studyId":study["id"],"resultId":result.get("id"),"validationId":validation.get("id"),"markdown":"\n".join(lines),"createdAt":_now()}
    report["reportHash"]=_hash({k:v for k,v in report.items() if k!="reportHash"})
    return report

def verify(payload: dict[str, Any]) -> dict[str, Any]:
    record=payload.get("record") if isinstance(payload.get("record"),dict) else payload
    candidates=[("resultHash",None),("validationHash",None),("comparisonHash",None),("reportHash",None),("studyHash","updatedAt")]
    for field,exclude in candidates:
        if field in record:
            expected=record.get(field); source={k:v for k,v in record.items() if k!=field and (exclude is None or k!=exclude)}; actual=_hash(source)
            return {"ok":expected==actual,"field":field,"expected":expected,"actual":actual,"version":VERSION}
    raise ModelCalibrationError("No supported calibration hash field was found.")
