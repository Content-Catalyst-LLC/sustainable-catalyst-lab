from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
from scipy import stats

from .advanced_statistical_modeling import (
    AdvancedStatisticalModelingError,
    _basis as _asm_basis,
    cross_validate as _asm_cross_validate,
    fit as _asm_fit,
    normalize_study as _asm_normalize_study,
    predict as _asm_predict,
)
from .platform_core_v3_object_mapping_v01050 import build_core_object_binding

VERSION = "0.121.0"
ENGINE_VERSION = "4.1.0"
SCHEMA = "sc-lab-statistical-modeling-diagnostics-studio/0.121.0"
SNAPSHOT_SCHEMA = "sc-lab-statistical-modeling-diagnostics-snapshot/0.121.0"
MAX_ROWS = 5_000
MAX_FEATURES = 40
MAX_CANDIDATES = 12
MAX_CALIBRATION_BINS = 50

FAMILIES = {"gaussian", "binomial-logit", "poisson-log"}
ESTIMATORS = {"ols", "weighted-least-squares", "huber", "ridge", "lasso", "elastic-net", "glm"}
DIAGNOSTIC_FAMILIES = {
    "residual-summary", "normality", "heteroskedasticity", "independence", "multicollinearity",
    "influence", "observed-vs-predicted", "calibration", "classification", "deviance", "dispersion"
}
FIGURE_FAMILIES = {
    "observed-predicted", "residual-fitted", "residual-qq", "residual-scale-location",
    "coefficient-forest", "leverage-cooks", "calibration-reliability", "prediction-error",
    "deviance-residual", "cv-comparison"
}

class StatisticalModelingDiagnosticsError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code


def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode()).hexdigest()

def _dict(v: Any, label: str) -> dict[str, Any]:
    if v is None: return {}
    if not isinstance(v, dict): raise StatisticalModelingDiagnosticsError(f"{label} must be an object.")
    return copy.deepcopy(v)

def _list(v: Any, label: str, maximum: int = 1000) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise StatisticalModelingDiagnosticsError(f"{label} must be an array.")
    if len(v)>maximum: raise StatisticalModelingDiagnosticsError(f"{label} exceeds {maximum} entries.",413)
    return copy.deepcopy(v)

def _text(v: Any, label: str, maximum: int=500, required: bool=False) -> str:
    s=str(v or '').strip()
    if required and not s: raise StatisticalModelingDiagnosticsError(f"{label} is required.")
    if len(s)>maximum: raise StatisticalModelingDiagnosticsError(f"{label} exceeds {maximum} characters.")
    return s

def _finite(v: Any, label: str, default: float|None=None) -> float:
    if v is None and default is not None: return default
    try: x=float(v)
    except (TypeError,ValueError) as exc: raise StatisticalModelingDiagnosticsError(f"{label} must be numeric.") from exc
    if not math.isfinite(x): raise StatisticalModelingDiagnosticsError(f"{label} must be finite.")
    return x

def _clean(v: Any) -> Any:
    if isinstance(v,(np.floating,float)):
        x=float(v); return x if math.isfinite(x) else None
    if isinstance(v,(np.integer,)): return int(v)
    if isinstance(v,(np.bool_,)): return bool(v)
    if isinstance(v,dict): return {str(k):_clean(x) for k,x in v.items()}
    if isinstance(v,list): return [_clean(x) for x in v]
    return v

def _dataset(payload: dict[str,Any]) -> tuple[str,list[dict[str,Any]]]:
    src=payload.get('dataset') if isinstance(payload.get('dataset'),dict) else payload
    dataset_id=_text(src.get('id') or src.get('dataset_id') or src.get('datasetId') or 'dataset','dataset id',180,True)
    rows=src.get('rows')
    if not isinstance(rows,list) or not rows: raise StatisticalModelingDiagnosticsError('dataset.rows must be a non-empty array.')
    if len(rows)>MAX_ROWS: raise StatisticalModelingDiagnosticsError(f'dataset exceeds {MAX_ROWS} rows.',413)
    if any(not isinstance(r,dict) for r in rows): raise StatisticalModelingDiagnosticsError('Every dataset row must be an object.')
    return dataset_id,copy.deepcopy(rows)

def _study_payload(payload: dict[str,Any]) -> dict[str,Any]:
    dataset_id,rows=_dataset(payload)
    model=_dict(payload.get('model') or payload.get('study'),'model')
    if not model:
        keys={'id','title','family','estimator','modelType','features','response','weightColumn','standardize','alpha','l1Ratio','splineFeature','knots','confidenceLevel','classificationThreshold','maxIterations','tolerance','provenance'}
        model={k:copy.deepcopy(payload[k]) for k in keys if k in payload}
    if not model: raise StatisticalModelingDiagnosticsError('model specification is required.')
    model.setdefault('id',_text(payload.get('model_id') or 'model','model id',180,True))
    model.setdefault('title',model['id'])
    model['datasetId']=dataset_id
    try: study=_asm_normalize_study(model)
    except AdvancedStatisticalModelingError as exc: raise StatisticalModelingDiagnosticsError(str(exc)) from exc
    return {'dataset_id':dataset_id,'rows':rows,'study':study}

def schema_info() -> dict[str,Any]:
    return {'ok':True,'schema':SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,'snapshot_schema':SNAPSHOT_SCHEMA,
            'max_rows':MAX_ROWS,'max_features':MAX_FEATURES,'max_candidates':MAX_CANDIDATES}

def catalog() -> dict[str,Any]:
    return {'ok':True,'version':VERSION,'families':sorted(FAMILIES),'estimators':sorted(ESTIMATORS),
            'diagnostic_families':sorted(DIAGNOSTIC_FAMILIES),'figure_families':sorted(FIGURE_FAMILIES),
            'comparison_metrics':['cross-validation-primary','aic','bic'],
            'analysis_families':['fit','coefficients','diagnostics','prediction','cross-validation','comparison','visualization','snapshot']}

def manifest() -> dict[str,Any]:
    return {'ok':True,'status':'statistical-modeling-diagnostics-studio-ready','version':VERSION,'engine_version':ENGINE_VERSION,
            'gaussian_models':True,'robust_regression':True,'regularized_regression':True,'binomial_glm':True,'poisson_glm':True,
            'coefficient_intervals':True,'residual_diagnostics':True,'influence_diagnostics':True,'multicollinearity_diagnostics':True,
            'calibration_diagnostics':True,'cross_validation':True,'prediction_evaluation':True,'reproducible_snapshots':True,
            'source_rows_immutable':True,'automatic_feature_selection':False,'automatic_model_selection':False,
            'automatic_significance_labels':False,'automatic_causal_inference':False,'automatic_scientific_validity_certification':False,
            'automatic_core_submission':False,'determine_truth':False}

def health() -> dict[str,Any]:
    return {**manifest(),'schema':SCHEMA,'family_count':len(FAMILIES),'estimator_count':len(ESTIMATORS),
            'diagnostic_family_count':len(DIAGNOSTIC_FAMILIES),'figure_family_count':len(FIGURE_FAMILIES)}

def normalize_model_spec(payload: dict[str,Any]) -> dict[str,Any]:
    info=_study_payload(payload); study=info['study']
    return {'ok':True,'schema':f'{SCHEMA}/model-spec','version':VERSION,'dataset_id':info['dataset_id'],'model':study,
            'source_rows_immutable':True,'automatic_feature_selection':False,
            'model_spec_hash':_hash({'dataset_id':info['dataset_id'],'study':study})}

def fit_model(payload: dict[str,Any]) -> dict[str,Any]:
    info=_study_payload(payload)
    try: fitted=_asm_fit({'study':info['study'],'rows':info['rows']})['result']
    except AdvancedStatisticalModelingError as exc: raise StatisticalModelingDiagnosticsError(str(exc)) from exc
    fitted=copy.deepcopy(fitted)
    fitted['version']=VERSION; fitted['studio_schema']=SCHEMA; fitted['dataset_id']=info['dataset_id']
    fitted['source_rows_immutable']=True
    fitted['automatic_significance_labels']=False
    fitted['automatic_causal_inference']=False
    fitted['automatic_model_selection']=False
    fitted['scientific_validity_certified']=False
    fitted['diagnostic_note']='Coefficient p-values/intervals, when available, are reported as declared model diagnostics; the Studio does not label terms significant or causal.'
    fitted['studio_result_hash']=_hash({k:v for k,v in fitted.items() if k!='studio_result_hash'})
    return {'ok':True,'version':VERSION,'result':_clean(fitted)}

def coefficient_report(payload: dict[str,Any]) -> dict[str,Any]:
    result=_dict(payload.get('result'),'result')
    if not result: result=fit_model(payload)['result']
    study=_dict(result.get('study'),'result.study'); family=study.get('family')
    rows=[]
    for c in result.get('coefficients') or []:
        row=copy.deepcopy(c); est=row.get('estimate')
        row['significance_label']=None
        row['automatic_interpretation']=False
        if isinstance(est,(int,float)) and family=='binomial-logit':
            row['effect_scale']='odds-ratio'; row['effect_estimate']=math.exp(float(est))
            row['effect_confidence_low']=math.exp(float(row['confidenceLow'])) if isinstance(row.get('confidenceLow'),(int,float)) else None
            row['effect_confidence_high']=math.exp(float(row['confidenceHigh'])) if isinstance(row.get('confidenceHigh'),(int,float)) else None
        elif isinstance(est,(int,float)) and family=='poisson-log':
            row['effect_scale']='rate-ratio'; row['effect_estimate']=math.exp(float(est))
            row['effect_confidence_low']=math.exp(float(row['confidenceLow'])) if isinstance(row.get('confidenceLow'),(int,float)) else None
            row['effect_confidence_high']=math.exp(float(row['confidenceHigh'])) if isinstance(row.get('confidenceHigh'),(int,float)) else None
        else:
            row['effect_scale']='coefficient'; row['effect_estimate']=est
            row['effect_confidence_low']=row.get('confidenceLow'); row['effect_confidence_high']=row.get('confidenceHigh')
        rows.append(_clean(row))
    out={'ok':True,'schema':f'{SCHEMA}/coefficient-report','version':VERSION,'model_id':study.get('id'),'family':family,
         'coefficients':rows,'automatic_significance_labels':False,'automatic_causal_interpretation':False,
         'classical_inference_available':bool((result.get('inference') or {}).get('available'))}
    out['report_hash']=_hash(out); return out

def _fit_and_rows(payload: dict[str,Any]) -> tuple[dict[str,Any],list[dict[str,Any]]]:
    _,rows=_dataset(payload)
    result=_dict(payload.get('result'),'result')
    if not result: result=fit_model(payload)['result']
    return result,rows

def _design(result: dict[str,Any], rows: list[dict[str,Any]]) -> tuple[dict[str,Any],np.ndarray,np.ndarray,np.ndarray,np.ndarray,list[str]]:
    study=_asm_normalize_study(result.get('study') or {})
    usable=[]
    for row in rows:
        try:
            r=dict(row)
            for k in list(study['features'])+[study['response']]: r[k]=float(row[k])
            if study.get('weightColumn'): r[study['weightColumn']]=float(row[study['weightColumn']])
            usable.append(r)
        except Exception: pass
    if not usable: raise StatisticalModelingDiagnosticsError('No usable rows remain for diagnostics.')
    state=((result.get('design') or {}).get('state') or {})
    X,labels,_=_asm_basis(study,usable,state)
    y=np.asarray([float(r[study['response']]) for r in usable])
    beta=np.asarray(result.get('coefficientVector') or [],dtype=float)
    if beta.size!=X.shape[1]: raise StatisticalModelingDiagnosticsError('Fitted coefficient vector does not match design matrix.')
    eta=X@beta
    if study['family']=='binomial-logit': pred=1/(1+np.exp(-np.clip(eta,-60,60)))
    elif study['family']=='poisson-log': pred=np.exp(np.clip(eta,-30,30))
    else: pred=eta
    residual=y-pred
    return study,X,y,pred,residual,labels

def _vif(X: np.ndarray, labels:list[str]) -> list[dict[str,Any]]:
    out=[]
    for j in range(1,X.shape[1]):
        target=X[:,j]; other=np.delete(X,j,axis=1)
        if np.std(target)<=1e-15: r2=1.0
        else:
            b=np.linalg.lstsq(other,target,rcond=None)[0]; fit=other@b
            sst=float(np.sum((target-target.mean())**2)); sse=float(np.sum((target-fit)**2)); r2=1-sse/max(sst,1e-300)
        vif=None if r2>=1-1e-12 else 1/max(1-r2,1e-12)
        out.append({'term':labels[j] if j<len(labels) else f'x{j}','vif':_clean(vif),'automatic_threshold_classification':False})
    return out

def _auc(y: np.ndarray,p:np.ndarray) -> float|None:
    pos=np.sum(y==1); neg=np.sum(y==0)
    if pos==0 or neg==0:return None
    ranks=stats.rankdata(p); return float((ranks[y==1].sum()-pos*(pos+1)/2)/(pos*neg))

def diagnose_model(payload: dict[str,Any]) -> dict[str,Any]:
    result,rows=_fit_and_rows(payload); study,X,y,pred,residual,labels=_design(result,rows)
    n,k=X.shape; fam=study['family']; out={'ok':True,'schema':f'{SCHEMA}/diagnostics','version':VERSION,'model_id':study.get('id'),'family':fam,'n':n,
      'residual_summary':{'mean':_clean(np.mean(residual)),'std':_clean(np.std(residual,ddof=1)) if n>1 else 0.0,'rmse':_clean(np.sqrt(np.mean(residual**2))),'mae':_clean(np.mean(np.abs(residual))),
                          'q05':_clean(np.quantile(residual,.05)),'q50':_clean(np.quantile(residual,.5)),'q95':_clean(np.quantile(residual,.95))},
      'automatic_assumption_pass_fail':False,'automatic_model_rejection':False,'automatic_scientific_validity_certification':False}
    denom=float(np.sum(residual**2)); out['independence']={'durbin_watson':_clean(np.sum(np.diff(residual)**2)/denom) if n>1 and denom>0 else None,'ordered_rows_assumed_meaningful':bool(payload.get('row_order_meaningful',False))}
    if fam=='gaussian':
        normal={'test':'Shapiro-Wilk' if 3<=n<=5000 else 'not-run','statistic':None,'p_value':None,'automatic_normality_conclusion':False}
        if 3<=n<=5000:
            sh=stats.shapiro(residual); normal.update(statistic=float(sh.statistic),p_value=float(sh.pvalue))
        out['normality']=normal
        z=residual**2; Z=X
        try:
            bz=np.linalg.lstsq(Z,z,rcond=None)[0]; fit=Z@bz; sst=float(np.sum((z-z.mean())**2)); r2=1-float(np.sum((z-fit)**2))/max(sst,1e-300); lm=n*max(0.0,r2); df=max(1,Z.shape[1]-1)
            out['heteroskedasticity']={'test':'Breusch-Pagan-style LM','statistic':lm,'df':df,'p_value':float(stats.chi2.sf(lm,df)),'automatic_heteroskedasticity_conclusion':False}
        except Exception: out['heteroskedasticity']={'test':'not-computed','automatic_heteroskedasticity_conclusion':False}
        out['multicollinearity']={'vif':_vif(X,labels),'automatic_problem_terms':False}
        try:
            H=X@np.linalg.pinv(X.T@X)@X.T; leverage=np.clip(np.diag(H),0,1); mse=float(np.sum(residual**2)/max(n-k,1)); cooks=(residual**2/(max(k,1)*max(mse,1e-300)))*(leverage/np.maximum((1-leverage)**2,1e-12))
            out['influence']={'rows':[{'index':i,'leverage':float(leverage[i]),'cooks_distance':float(cooks[i])} for i in range(n)],'automatic_exclusion':False}
        except Exception: out['influence']={'rows':[],'automatic_exclusion':False}
    elif fam=='binomial-logit':
        threshold=float(study.get('classificationThreshold',.5)); cls=(pred>=threshold).astype(int); yy=y.astype(int)
        tp=int(np.sum((cls==1)&(yy==1))); tn=int(np.sum((cls==0)&(yy==0))); fp=int(np.sum((cls==1)&(yy==0))); fn=int(np.sum((cls==0)&(yy==1)))
        out['classification']={'threshold':threshold,'tp':tp,'tn':tn,'fp':fp,'fn':fn,'accuracy':(tp+tn)/n,'sensitivity':tp/max(tp+fn,1),'specificity':tn/max(tn+fp,1),'roc_auc':_auc(yy,pred),'automatic_threshold_optimization':False}
        bins=min(max(int(payload.get('calibration_bins',10)),2),MAX_CALIBRATION_BINS); edges=np.linspace(0,1,bins+1); cal=[]
        for i in range(bins):
            mask=(pred>=edges[i])&((pred<edges[i+1]) if i<bins-1 else (pred<=edges[i+1]))
            if mask.any(): cal.append({'low':float(edges[i]),'high':float(edges[i+1]),'count':int(mask.sum()),'mean_predicted':float(pred[mask].mean()),'observed_fraction':float(y[mask].mean())})
        out['calibration']={'brier_score':float(np.mean((pred-y)**2)),'bins':cal,'automatic_calibration_conclusion':False}
    else:
        mu=np.clip(pred,1e-12,None); pearson=(y-mu)/np.sqrt(mu); term=np.where(y>0,2*(y*np.log(np.clip(y/mu,1e-300,None))-(y-mu)),2*mu); dev=np.sign(y-mu)*np.sqrt(np.maximum(term,0))
        out['deviance']={'pearson_residuals':_clean(pearson.tolist()),'deviance_residuals':_clean(dev.tolist()),'pearson_dispersion':float(np.sum(pearson**2)/max(n-k,1)),'automatic_overdispersion_conclusion':False,'observed_zero_fraction':float(np.mean(y==0)),'predicted_zero_fraction':float(np.mean(np.exp(-mu)))}
    out['diagnostics_hash']=_hash({k:v for k,v in out.items() if k!='diagnostics_hash'}); return _clean(out)


def effect_report(payload: dict[str,Any]) -> dict[str,Any]:
    report=coefficient_report(payload)
    return {'ok':True,'schema':f'{SCHEMA}/effect-report','version':VERSION,'model_id':report.get('model_id'),'family':report.get('family'),
            'effects':[{'term':r.get('term'),'effect_scale':r.get('effect_scale'),'effect_estimate':r.get('effect_estimate'),'confidence_low':r.get('effect_confidence_low'),'confidence_high':r.get('effect_confidence_high'),'significance_label':None,'automatic_interpretation':False} for r in report.get('coefficients',[])],
            'automatic_significance_labels':False,'automatic_causal_interpretation':False}

def assumption_audit(payload: dict[str,Any]) -> dict[str,Any]:
    d=diagnose_model(payload)
    keys=['normality','heteroskedasticity','independence','multicollinearity','influence','classification','calibration','deviance']
    return {'ok':True,'schema':f'{SCHEMA}/assumption-audit','version':VERSION,'model_id':d.get('model_id'),'family':d.get('family'),
            'diagnostics':{k:d[k] for k in keys if k in d},'automatic_assumption_pass_fail':False,'automatic_model_rejection':False,
            'note':'Diagnostics are reported for researcher judgment; the Studio does not convert diagnostic p-values or heuristics into automatic pass/fail decisions.'}

def evaluate_predictions(payload: dict[str,Any]) -> dict[str,Any]:
    result=_dict(payload.get('result'),'result')
    if not result: raise StatisticalModelingDiagnosticsError('result is required for prediction evaluation.')
    eval_rows=_list(payload.get('evaluation_rows') or payload.get('rows'),'evaluation_rows',MAX_ROWS)
    try: predicted=_asm_predict({'result':result,'rows':eval_rows})['predictions']
    except AdvancedStatisticalModelingError as exc: raise StatisticalModelingDiagnosticsError(str(exc)) from exc
    study=result.get('study') or {}; response=study.get('response'); y=[]; p=[]
    for row,pred in zip(eval_rows,predicted):
        try: obs=float(row[response]);
        except Exception: continue
        y.append(obs);p.append(float(pred))
    if not y: raise StatisticalModelingDiagnosticsError('No evaluation rows contain a usable response.')
    y=np.asarray(y);p=np.asarray(p); fam=study.get('family'); metrics={'count':len(y)}
    if fam=='gaussian': metrics.update(rmse=float(np.sqrt(np.mean((y-p)**2))),mae=float(np.mean(np.abs(y-p))),bias=float(np.mean(y-p)))
    elif fam=='binomial-logit':
        pp=np.clip(p,1e-12,1-1e-12); metrics.update(log_loss=-float(np.mean(y*np.log(pp)+(1-y)*np.log(1-pp))),brier_score=float(np.mean((y-p)**2)),roc_auc=_auc(y.astype(int),p))
    else:
        mu=np.clip(p,1e-12,None); term=np.where(y>0,y*np.log(np.clip(y/mu,1e-300,None))-(y-mu),mu); metrics.update(poisson_deviance_mean=2*float(np.mean(term)),rmse=float(np.sqrt(np.mean((y-mu)**2))))
    out={'ok':True,'schema':f'{SCHEMA}/prediction-evaluation','version':VERSION,'model_id':study.get('id'),'family':fam,'metrics':_clean(metrics),'automatic_model_approval':False,'scientific_validity_certified':False};out['evaluation_hash']=_hash(out);return out

def cross_validate_model(payload: dict[str,Any]) -> dict[str,Any]:
    info=_study_payload(payload)
    try: cv=_asm_cross_validate({'study':info['study'],'rows':info['rows'],'folds':payload.get('folds',5),'repeats':payload.get('repeats',1),'seed':payload.get('seed',42)})['validation']
    except AdvancedStatisticalModelingError as exc: raise StatisticalModelingDiagnosticsError(str(exc)) from exc
    cv=copy.deepcopy(cv); cv['version']=VERSION;cv['automatic_model_selection']=False;cv['scientific_validity_certified']=False;cv['studio_validation_hash']=_hash(cv)
    return {'ok':True,'validation':_clean(cv)}

def compare_models(payload: dict[str,Any]) -> dict[str,Any]:
    dataset_id,rows=_dataset(payload); candidates=_list(payload.get('candidates'),'candidates',MAX_CANDIDATES)
    if len(candidates)<2: raise StatisticalModelingDiagnosticsError('At least two model candidates are required.')
    normalized_specs=[]
    for cand in candidates:
        if not isinstance(cand,dict): raise StatisticalModelingDiagnosticsError('Every model candidate must be an object.')
        try: normalized_specs.append(_asm_normalize_study({**cand,'datasetId':dataset_id}))
        except AdvancedStatisticalModelingError as exc: raise StatisticalModelingDiagnosticsError(str(exc)) from exc
    if len({x['family'] for x in normalized_specs}) != 1 or len({x['response'] for x in normalized_specs}) != 1:
        raise StatisticalModelingDiagnosticsError('Model comparison candidates must share the same response family and response column.')
    table=[]
    for cand in candidates:
        if not isinstance(cand,dict): raise StatisticalModelingDiagnosticsError('Every model candidate must be an object.')
        cp={'dataset':{'id':dataset_id,'rows':rows},'model':cand,'folds':payload.get('folds',5),'repeats':payload.get('repeats',1),'seed':payload.get('seed',42)}
        fit=fit_model(cp)['result']; cv=cross_validate_model(cp)['validation']; metrics=fit.get('metrics') or {}
        table.append({'model_id':(fit.get('study') or {}).get('id'),'title':(fit.get('study') or {}).get('title'),'family':(fit.get('study') or {}).get('family'),'estimator':(fit.get('study') or {}).get('estimator'),'primary_metric':cv.get('primaryMetric'),'validation_mean':cv.get('mean'),'validation_sd':cv.get('standardDeviation'),'aic':metrics.get('aic'),'bic':metrics.get('bic'),'result_hash':fit.get('studio_result_hash')})
    selected=_text(payload.get('selected_model_id'),'selected_model_id',180)
    if selected and selected not in {r['model_id'] for r in table}: raise StatisticalModelingDiagnosticsError('selected_model_id is not one of the declared candidates.')
    out={'ok':True,'schema':f'{SCHEMA}/model-comparison','version':VERSION,'dataset_id':dataset_id,'candidates':_clean(table),'automatic_ranking':False,'automatic_model_selection':False,'selected_model_id':selected or None,'selection_declared_by_user':bool(selected),'comparison_note':'Metrics are reported side-by-side. Candidate order is preserved; the Studio does not choose a winner.'}
    out['comparison_hash']=_hash(out);return out

def build_visualization_plan(payload: dict[str,Any]) -> dict[str,Any]:
    result=_dict(payload.get('result'),'result')
    if not result: result=fit_model(payload)['result']
    fam=(result.get('study') or {}).get('family'); figures=['observed-predicted','coefficient-forest']
    if fam=='gaussian': figures += ['residual-fitted','residual-qq','residual-scale-location','leverage-cooks']
    elif fam=='binomial-logit': figures += ['calibration-reliability','prediction-error']
    else: figures += ['deviance-residual','prediction-error']
    out={'ok':True,'schema':f'{SCHEMA}/visualization-plan','version':VERSION,'model_id':(result.get('study') or {}).get('id'),'figures':[{'figure_family':x,'publication_profile':'research-paper','automatic_render':False} for x in figures],'uses_v01140_publication_design_system':True,'uses_v01150_statistical_graphics':True,'automatic_render':False,'automatic_scientific_interpretation':False};out['visualization_plan_hash']=_hash(out);return out

def build_studio(payload: dict[str,Any]) -> dict[str,Any]:
    fit=fit_model(payload)['result']; diag=diagnose_model({**payload,'result':fit}); coeff=coefficient_report({'result':fit}); vis=build_visualization_plan({'result':fit})
    out={'ok':True,'schema':f'{SCHEMA}/studio','version':VERSION,'model':fit,'coefficients':coeff,'diagnostics':diag,'visualization_plan':vis,'source_rows_immutable':True,'automatic_model_selection':False,'automatic_significance_labels':False,'automatic_causal_inference':False};out['studio_hash']=_hash(out);return out

def build_snapshot(payload: dict[str,Any]) -> dict[str,Any]:
    studio=_dict(payload.get('studio'),'studio') or build_studio(payload); out={'ok':True,'schema':SNAPSHOT_SCHEMA,'version':VERSION,'studio_hash':studio.get('studio_hash'),'model_id':((studio.get('model') or {}).get('study') or {}).get('id'),'content_hash':_hash(studio),'automatic_persistence':False,'reproducible':True};out['snapshot_hash']=_hash(out);return out

def build_export_plan(payload: dict[str,Any]) -> dict[str,Any]:
    formats=[str(x).lower() for x in _list(payload.get('formats') or ['json','csv','svg','pdf'],'formats',20)]
    allowed={'json','csv','svg','pdf','png'}
    if any(x not in allowed for x in formats): raise StatisticalModelingDiagnosticsError('Unsupported export format.')
    out={'ok':True,'schema':f'{SCHEMA}/export-plan','version':VERSION,'formats':formats,'include':['model-spec','coefficients','diagnostics','metrics','visualization-plan','provenance'],'automatic_file_write':False,'publication_grade_figures':True};out['export_plan_hash']=_hash(out);return out

def build_core_object_plan(payload: dict[str,Any]) -> dict[str,Any]:
    session_id=_text(payload.get('session_id'),'session_id',240,True); model_id=_text(payload.get('model_id') or ((_dict(payload.get('result'),'result').get('study') or {}).get('id')) or 'statistical-model','model_id',180,True)
    object_payload={'session_id':session_id,'object':{'object_type':'model','id':model_id,'metadata':{'lab_release_version':VERSION,'studio_schema':SCHEMA,'analysis_kind':'statistical-modeling-diagnostics','underlying_object_remains_authoritative_in_lab':True}}}
    try: binding=build_core_object_binding(object_payload)
    except Exception as exc: raise StatisticalModelingDiagnosticsError(str(exc)) from exc
    return {'ok':True,'schema':f'{SCHEMA}/core-object-plan','version':VERSION,'binding':binding,'automatic_core_submission':False,'core_executes_model':False,'core_certifies_scientific_validity':False}
