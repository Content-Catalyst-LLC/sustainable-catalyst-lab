from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from .platform_core_v3_object_mapping_v01050 import build_core_object_binding

VERSION = "0.120.0"
ENGINE_VERSION = "4.0.0"
SCHEMA = "sc-lab-exploratory-data-analysis-studio/0.120.0"
SNAPSHOT_SCHEMA = "sc-lab-exploratory-data-analysis-snapshot/0.120.0"
MAX_ROWS = 50_000
MAX_COLUMNS = 256
MAX_PREVIEW_ROWS = 100
MAX_GROUPS = 200
MAX_COMPONENTS = 20

CORRELATION_METHODS = {"pearson", "spearman"}
OUTLIER_METHODS = {"iqr", "modified-z", "zscore"}
TRANSFORMATIONS = {"center", "standardize", "minmax", "log1p", "sqrt", "winsorize"}
FIGURE_FAMILIES = {
    "histogram", "ecdf", "box", "violin", "raincloud", "ridge", "scatter",
    "correlation-matrix", "missingness-matrix", "group-summary", "pca-scree", "pca-biplot"
}

class EDAStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 1000, required: bool = False) -> str:
    s = str(value or "").strip()
    if required and not s:
        raise EDAStudioError(f"{label} is required.")
    if len(s) > maximum:
        raise EDAStudioError(f"{label} exceeds {maximum} characters.")
    return s


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise EDAStudioError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum: int = 1000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise EDAStudioError(f"{label} must be an array.")
    if len(value) > maximum:
        raise EDAStudioError(f"{label} exceeds {maximum} entries.", 413)
    return copy.deepcopy(value)


def _finite(value: Any) -> float | None:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def _clean(value: Any) -> Any:
    if isinstance(value, (np.floating, float)):
        n = float(value)
        return n if math.isfinite(n) else None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    return value


def _rows(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[str]]:
    if not isinstance(payload, dict):
        raise EDAStudioError("EDA request must be an object.")
    raw = payload.get("dataset") if isinstance(payload.get("dataset"), dict) else payload
    dataset_id = _text(raw.get("id") or raw.get("dataset_id") or raw.get("datasetId") or "dataset", "dataset id", 180, True)
    rows = raw.get("rows")
    if not isinstance(rows, list):
        raise EDAStudioError("dataset.rows must be an array of objects.")
    if len(rows) > MAX_ROWS:
        raise EDAStudioError(f"dataset exceeds {MAX_ROWS} rows for the interactive EDA runtime.", 413)
    if any(not isinstance(r, dict) for r in rows):
        raise EDAStudioError("Every dataset row must be an object.")
    declared = raw.get("columns")
    if declared is not None and not isinstance(declared, list):
        raise EDAStudioError("dataset.columns must be an array when supplied.")
    columns = [str(x) for x in declared] if declared else []
    if not columns:
        seen: set[str] = set()
        for row in rows:
            for key in row:
                k = str(key)
                if k not in seen:
                    seen.add(k); columns.append(k)
    if len(columns) > MAX_COLUMNS:
        raise EDAStudioError(f"dataset exceeds {MAX_COLUMNS} columns.", 413)
    if len(set(columns)) != len(columns):
        raise EDAStudioError("dataset.columns contains duplicate names.")
    normalized = [{c: row.get(c) for c in columns} for row in rows]
    return dataset_id, normalized, columns


def _frame(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[str], pd.DataFrame]:
    dataset_id, rows, columns = _rows(payload)
    df = pd.DataFrame(rows, columns=columns)
    return dataset_id, rows, columns, df


def _numeric_columns(df: pd.DataFrame, requested: Any = None) -> list[str]:
    if requested is not None:
        cols = _list(requested, "columns", MAX_COLUMNS)
        out = []
        for c in cols:
            c = str(c)
            if c not in df.columns:
                raise EDAStudioError(f"Unknown column: {c}")
            series = pd.to_numeric(df[c], errors="coerce")
            if series.notna().sum() == 0:
                raise EDAStudioError(f"Column is not numeric: {c}")
            out.append(c)
        return out
    out=[]
    for c in df.columns:
        s=pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() and s.notna().sum() >= max(1, int(df[c].notna().sum()*0.8)):
            out.append(str(c))
    return out


def _series_numeric(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        raise EDAStudioError(f"Unknown column: {column}")
    s = pd.to_numeric(df[column], errors="coerce")
    if not s.notna().any():
        raise EDAStudioError(f"Column is not numeric: {column}")
    return s.astype(float)


def _column_kind(series: pd.Series) -> str:
    nonnull = series.dropna()
    if nonnull.empty:
        return "empty"
    if pd.api.types.is_bool_dtype(nonnull):
        return "boolean"
    numeric = pd.to_numeric(nonnull, errors="coerce")
    if numeric.notna().sum() >= max(1, int(len(nonnull) * 0.8)):
        return "numeric"
    unique = int(nonnull.astype(str).nunique())
    ratio = unique / max(len(nonnull), 1)
    return "categorical" if unique <= 50 or ratio <= 0.2 else "text"


def schema_info() -> dict[str, Any]:
    return {"ok": True, "schema": SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION,
            "max_rows": MAX_ROWS, "max_columns": MAX_COLUMNS, "max_preview_rows": MAX_PREVIEW_ROWS,
            "snapshot_schema": SNAPSHOT_SCHEMA}


def catalog() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "correlation_methods": sorted(CORRELATION_METHODS),
            "outlier_methods": sorted(OUTLIER_METHODS), "transformations": sorted(TRANSFORMATIONS),
            "figure_families": sorted(FIGURE_FAMILIES),
            "analysis_families": ["profile", "missingness", "distribution", "correlation", "group-comparison",
                                  "outlier", "relationship", "transformation-preview", "pca"]}


def manifest() -> dict[str, Any]:
    return {"ok": True, "status": "exploratory-data-analysis-studio-ready", "version": VERSION,
            "engine_version": ENGINE_VERSION, "source_rows_immutable": True, "descriptive_statistics": True,
            "missingness_analysis": True, "distribution_analysis": True, "correlation_analysis": True,
            "group_comparison": True, "robust_outlier_flags": True, "relationship_analysis": True,
            "transformation_preview": True, "pca_exploration": True, "reproducible_snapshots": True,
            "publication_visual_plans": True, "automatic_source_mutation": False,
            "automatic_hypothesis_confirmation": False, "automatic_significance_claims": False,
            "automatic_causal_inference": False, "automatic_scientific_validity_certification": False,
            "automatic_core_submission": False, "determine_truth": False}


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "analysis_family_count": 9,
            "correlation_method_count": len(CORRELATION_METHODS), "outlier_method_count": len(OUTLIER_METHODS),
            "transformation_count": len(TRANSFORMATIONS), "figure_family_count": len(FIGURE_FAMILIES)}


def normalize_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    column_types = {c: _column_kind(df[c]) for c in columns}
    out = {"schema": f"{SCHEMA}/dataset", "version": VERSION, "dataset_id": dataset_id,
           "row_count": len(rows), "column_count": len(columns), "columns": columns,
           "column_types": column_types, "source_rows_immutable": True,
           "semantic_types_inferred": False, "rows": rows}
    out["dataset_hash"] = _hash({"dataset_id": dataset_id, "columns": columns, "rows": rows})
    return out


def profile_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    profiles=[]
    for c in columns:
        s=df[c]; kind=_column_kind(s); nonnull=s.dropna(); item={"column":c,"kind":kind,"count":int(nonnull.size),
            "missing_count":int(s.isna().sum()),"missing_fraction":round(float(s.isna().mean()) if len(s) else 0.0,6),
            "distinct_count":int(nonnull.astype(str).nunique()) if not nonnull.empty else 0}
        if kind=="numeric":
            n=pd.to_numeric(s, errors="coerce").dropna().astype(float)
            if len(n):
                qs=n.quantile([.05,.25,.5,.75,.95])
                item.update({"mean":_clean(n.mean()),"std":_clean(n.std(ddof=1)) if len(n)>1 else None,
                    "min":_clean(n.min()),"q05":_clean(qs.loc[.05]),"q25":_clean(qs.loc[.25]),"median":_clean(qs.loc[.5]),
                    "q75":_clean(qs.loc[.75]),"q95":_clean(qs.loc[.95]),"max":_clean(n.max())})
        elif kind in {"categorical","boolean","text"}:
            counts=nonnull.astype(str).value_counts(dropna=False).head(10)
            item["top_values"]=[{"value":str(k),"count":int(v)} for k,v in counts.items()]
        profiles.append(item)
    result={"ok":True,"schema":f"{SCHEMA}/profile","dataset_id":dataset_id,"row_count":len(rows),"column_count":len(columns),
            "columns":profiles,"exploratory_not_confirmatory":True,"scientific_validity_certified":False}
    result["profile_hash"]=_hash(result)
    return result


def analyze_missingness(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    n=len(df)
    per=[]
    for c in columns:
        count=int(df[c].isna().sum())
        per.append({"column":c,"missing_count":count,"missing_fraction":round(count/max(n,1),6)})
    complete=int((~df.isna().any(axis=1)).sum()) if len(columns) else n
    row_hist={}
    if len(columns):
        for k,v in df.isna().sum(axis=1).value_counts().sort_index().items(): row_hist[str(int(k))]=int(v)
    pairs=[]
    for i,a in enumerate(columns):
        for b in columns[i+1:]:
            both=int((df[a].isna() & df[b].isna()).sum())
            if both: pairs.append({"a":a,"b":b,"co_missing_count":both,"co_missing_fraction":round(both/max(n,1),6)})
    out={"ok":True,"schema":f"{SCHEMA}/missingness","dataset_id":dataset_id,"row_count":n,"complete_row_count":complete,
         "complete_row_fraction":round(complete/max(n,1),6),"columns":per,"row_missing_count_histogram":row_hist,
         "co_missing_pairs":pairs[:2000],"missingness_mechanism_inferred":False,"mcar_mar_mnar_not_determined":True}
    out["analysis_hash"]=_hash(out); return out


def analyze_distributions(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    requested=payload.get("columns")
    selected=[str(c) for c in requested] if isinstance(requested,list) else columns
    for c in selected:
        if c not in df.columns: raise EDAStudioError(f"Unknown column: {c}")
    results=[]
    for c in selected:
        s=df[c]; kind=_column_kind(s); item={"column":c,"kind":kind,"missing_count":int(s.isna().sum())}
        if kind=="numeric":
            n=pd.to_numeric(s,errors="coerce").dropna().astype(float)
            if len(n):
                q=n.quantile([.05,.25,.5,.75,.95]); med=float(n.median()); mad=float(np.median(np.abs(n.to_numpy()-med)))
                item.update({"n":int(len(n)),"mean":_clean(n.mean()),"median":med,"std":_clean(n.std(ddof=1)) if len(n)>1 else None,
                    "mad":_clean(mad),"min":_clean(n.min()),"q05":_clean(q.loc[.05]),"q25":_clean(q.loc[.25]),"q75":_clean(q.loc[.75]),
                    "q95":_clean(q.loc[.95]),"max":_clean(n.max()),"skewness":_clean(stats.skew(n,bias=False)) if len(n)>2 else None,
                    "excess_kurtosis":_clean(stats.kurtosis(n,bias=False)) if len(n)>3 else None})
        else:
            counts=s.dropna().astype(str).value_counts().head(25)
            item.update({"n":int(s.notna().sum()),"levels":[{"value":str(k),"count":int(v),"fraction":round(int(v)/max(int(s.notna().sum()),1),6)} for k,v in counts.items()]})
        results.append(item)
    out={"ok":True,"schema":f"{SCHEMA}/distributions","dataset_id":dataset_id,"distributions":results,
         "distribution_family_inferred":False,"normality_assumed":False,"exploratory_not_confirmatory":True}
    out["analysis_hash"]=_hash(out); return out


def analyze_correlations(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    method=_text(payload.get("method") or "pearson","method",40,True).lower()
    if method not in CORRELATION_METHODS: raise EDAStudioError(f"Unsupported correlation method: {method}")
    selected=_numeric_columns(df,payload.get("columns"))
    if len(selected)<2: raise EDAStudioError("At least two numeric columns are required for correlation analysis.")
    min_pairs=int(payload.get("min_pairs") or payload.get("minPairs") or 3)
    if min_pairs<2: raise EDAStudioError("min_pairs must be at least 2.")
    pairs=[]
    for i,a in enumerate(selected):
        for b in selected[i+1:]:
            pair=pd.concat([pd.to_numeric(df[a],errors="coerce"),pd.to_numeric(df[b],errors="coerce")],axis=1).dropna()
            coef=None
            if len(pair)>=min_pairs:
                coef=float(pair.iloc[:,0].corr(pair.iloc[:,1],method=method))
            pairs.append({"a":a,"b":b,"n":int(len(pair)),"coefficient":_clean(coef)})
    out={"ok":True,"schema":f"{SCHEMA}/correlations","dataset_id":dataset_id,"method":method,"columns":selected,"pairs":pairs,
         "p_values_computed":False,"significance_inferred":False,"causality_inferred":False,"exploratory_not_confirmatory":True}
    out["analysis_hash"]=_hash(out); return out


def compare_groups(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    group=_text(payload.get("group_by") or payload.get("groupBy"),"group_by",180,True)
    if group not in df.columns: raise EDAStudioError(f"Unknown group column: {group}")
    values=_numeric_columns(df,payload.get("value_columns") or payload.get("valueColumns"))
    if not values: raise EDAStudioError("At least one numeric value column is required.")
    levels=[x for x in df[group].dropna().astype(str).unique().tolist()]
    if len(levels)>MAX_GROUPS: raise EDAStudioError(f"group_by exceeds {MAX_GROUPS} observed levels.",413)
    summaries=[]
    gstr=df[group].astype("string")
    for level in levels:
        mask=gstr==level
        for c in values:
            s=pd.to_numeric(df.loc[mask,c],errors="coerce").dropna().astype(float)
            if not len(s): continue
            summaries.append({"group":level,"column":c,"n":int(len(s)),"mean":_clean(s.mean()),"median":_clean(s.median()),
                "std":_clean(s.std(ddof=1)) if len(s)>1 else None,"q25":_clean(s.quantile(.25)),"q75":_clean(s.quantile(.75)),
                "min":_clean(s.min()),"max":_clean(s.max())})
    contrasts=[]
    if len(levels)==2:
        for c in values:
            a=pd.to_numeric(df.loc[gstr==levels[0],c],errors="coerce").dropna().astype(float)
            b=pd.to_numeric(df.loc[gstr==levels[1],c],errors="coerce").dropna().astype(float)
            if len(a) and len(b):
                contrasts.append({"column":c,"group_a":levels[0],"group_b":levels[1],"mean_difference":_clean(a.mean()-b.mean()),"median_difference":_clean(a.median()-b.median())})
    out={"ok":True,"schema":f"{SCHEMA}/group-comparison","dataset_id":dataset_id,"group_by":group,"groups":levels,
         "summaries":summaries,"descriptive_contrasts":contrasts,"hypothesis_test_performed":False,"significance_inferred":False,
         "exploratory_not_confirmatory":True}
    out["analysis_hash"]=_hash(out); return out


def analyze_outliers(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    method=_text(payload.get("method") or "iqr","method",40,True).lower()
    if method not in OUTLIER_METHODS: raise EDAStudioError(f"Unsupported outlier method: {method}")
    selected=_numeric_columns(df,payload.get("columns"))
    threshold=float(payload.get("threshold") or (1.5 if method=="iqr" else 3.5 if method=="modified-z" else 3.0))
    if not math.isfinite(threshold) or threshold<=0: raise EDAStudioError("threshold must be a positive finite number.")
    analyses=[]
    for c in selected:
        s=_series_numeric(df,c); valid=s.dropna(); flags=pd.Series(False,index=s.index); rule={}
        if len(valid):
            if method=="iqr":
                q1=float(valid.quantile(.25)); q3=float(valid.quantile(.75)); iqr=q3-q1; lo=q1-threshold*iqr; hi=q3+threshold*iqr
                flags=s.lt(lo)|s.gt(hi); rule={"q25":q1,"q75":q3,"iqr":iqr,"lower":lo,"upper":hi}
            elif method=="modified-z":
                med=float(valid.median()); mad=float(np.median(np.abs(valid.to_numpy()-med)))
                if mad>0: flags=(0.6744897501960817*(s-med).abs()/mad)>threshold
                rule={"median":med,"mad":mad,"threshold":threshold}
            else:
                mean=float(valid.mean()); sd=float(valid.std(ddof=1)) if len(valid)>1 else 0.0
                if sd>0: flags=((s-mean).abs()/sd)>threshold
                rule={"mean":mean,"std":sd,"threshold":threshold}
        idx=[int(i) if isinstance(i,(int,np.integer)) else str(i) for i in s.index[flags.fillna(False)].tolist()]
        analyses.append({"column":c,"flag_count":len(idx),"row_indices":idx[:5000],"rule":_clean(rule)})
    out={"ok":True,"schema":f"{SCHEMA}/outliers","dataset_id":dataset_id,"method":method,"threshold":threshold,"columns":analyses,
         "rows_removed":False,"automatic_exclusion":False,"outlier_equals_error":False,"exploratory_not_confirmatory":True}
    out["analysis_hash"]=_hash(out); return out


def analyze_relationship(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    x=_text(payload.get("x"),"x",180,True); y=_text(payload.get("y"),"y",180,True)
    xs=_series_numeric(df,x); ys=_series_numeric(df,y); pair=pd.DataFrame({"x":xs,"y":ys}).dropna()
    if len(pair)<2: raise EDAStudioError("At least two complete x/y pairs are required.")
    pearson=float(pair.x.corr(pair.y,method="pearson")); spearman=float(pair.x.corr(pair.y,method="spearman"))
    slope=intercept=r2=None
    if pair.x.nunique()>1:
        slope,intercept=np.polyfit(pair.x.to_numpy(),pair.y.to_numpy(),1)
        pred=slope*pair.x.to_numpy()+intercept; ss_res=float(np.sum((pair.y.to_numpy()-pred)**2)); ss_tot=float(np.sum((pair.y.to_numpy()-pair.y.mean())**2)); r2=1-ss_res/ss_tot if ss_tot>0 else None
    out={"ok":True,"schema":f"{SCHEMA}/relationship","dataset_id":dataset_id,"x":x,"y":y,"n":int(len(pair)),
         "pearson":_clean(pearson),"spearman":_clean(spearman),"linear_descriptive_fit":{"slope":_clean(slope),"intercept":_clean(intercept),"r2":_clean(r2)},
         "p_values_computed":False,"causality_inferred":False,"exploratory_not_confirmatory":True}
    out["analysis_hash"]=_hash(out); return out


def plan_transformations(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    operations=_list(payload.get("operations"),"operations",100)
    if not operations: raise EDAStudioError("operations must be a non-empty array.")
    normalized=[]
    for i,op in enumerate(operations):
        if not isinstance(op,dict): raise EDAStudioError(f"operations[{i}] must be an object.")
        column=_text(op.get("column"),f"operations[{i}].column",180,True)
        if column not in df.columns: raise EDAStudioError(f"Unknown column: {column}")
        _series_numeric(df,column)
        name=_text(op.get("operation"),f"operations[{i}].operation",80,True).lower()
        if name not in TRANSFORMATIONS: raise EDAStudioError(f"Unsupported transformation: {name}")
        params=_dict(op.get("parameters"),f"operations[{i}].parameters")
        if name=="winsorize":
            lo=float(params.get("lower_quantile",.01)); hi=float(params.get("upper_quantile",.99))
            if not 0<=lo<hi<=1: raise EDAStudioError("winsorize quantiles must satisfy 0 <= lower < upper <= 1.")
            params={**params,"lower_quantile":lo,"upper_quantile":hi}
        normalized.append({"column":column,"operation":name,"parameters":params})
    out={"ok":True,"schema":f"{SCHEMA}/transformation-plan","dataset_id":dataset_id,"operations":normalized,
         "automatic_application":False,"source_dataset_mutated":False,"scientific_meaning_preserved_automatically":False}
    out["plan_hash"]=_hash(out); return out


def _apply_transform(series: pd.Series, operation: str, params: dict[str,Any]) -> pd.Series:
    s=pd.to_numeric(series,errors="coerce").astype(float)
    if operation=="center": return s-s.mean()
    if operation=="standardize":
        sd=s.std(ddof=1); return (s-s.mean())/sd if sd and math.isfinite(float(sd)) else s*0.0
    if operation=="minmax":
        lo=s.min(); hi=s.max(); return (s-lo)/(hi-lo) if hi>lo else s*0.0
    if operation=="log1p":
        offset=float(params.get("offset",0.0)); shifted=s+offset
        if (shifted.dropna() < -1).any(): raise EDAStudioError("log1p transformation has values below -1 after offset.")
        return np.log1p(shifted)
    if operation=="sqrt":
        offset=float(params.get("offset",0.0)); shifted=s+offset
        if (shifted.dropna() < 0).any(): raise EDAStudioError("sqrt transformation has negative values after offset.")
        return np.sqrt(shifted)
    if operation=="winsorize":
        l=float(params.get("lower_quantile",.01)); u=float(params.get("upper_quantile",.99)); return s.clip(s.quantile(l),s.quantile(u))
    raise EDAStudioError(f"Unsupported transformation: {operation}")


def preview_transformations(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload); plan=plan_transformations(payload)
    preview=df.copy()
    generated=[]
    for op in plan["operations"]:
        name=f"{op['column']}__{op['operation']}"
        if name in preview.columns: raise EDAStudioError(f"Generated preview column already exists: {name}")
        preview[name]=_apply_transform(preview[op["column"]],op["operation"],op["parameters"]); generated.append(name)
    limit=min(int(payload.get("preview_rows") or payload.get("previewRows") or 20),MAX_PREVIEW_ROWS)
    records=[]
    for record in preview.head(limit).to_dict(orient="records"):
        records.append({k:_clean(v) if not pd.isna(v) else None for k,v in record.items()})
    out={"ok":True,"schema":f"{SCHEMA}/transformation-preview","dataset_id":dataset_id,"plan_hash":plan["plan_hash"],
         "generated_columns":generated,"preview_rows":records,"source_dataset_mutated":False,"automatic_persistence":False}
    out["preview_hash"]=_hash(out); return out


def analyze_pca(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    selected=_numeric_columns(df,payload.get("columns"))
    if len(selected)<2: raise EDAStudioError("PCA exploration requires at least two numeric columns.")
    standardize=bool(payload.get("standardize",True)); complete=df[selected].apply(pd.to_numeric,errors="coerce").dropna()
    if len(complete)<2: raise EDAStudioError("PCA exploration requires at least two complete rows.")
    X=complete.to_numpy(dtype=float); means=X.mean(axis=0); Xc=X-means
    scales=np.ones(len(selected))
    if standardize:
        scales=Xc.std(axis=0,ddof=1)
        if np.any(scales==0): raise EDAStudioError("PCA standardization cannot use constant columns.")
        Xc=Xc/scales
    u,s,vt=np.linalg.svd(Xc,full_matrices=False); eigen=(s**2)/max(len(Xc)-1,1); total=float(eigen.sum()); ratios=eigen/total if total>0 else np.zeros_like(eigen)
    k=min(int(payload.get("components") or min(len(selected),MAX_COMPONENTS)),len(selected),MAX_COMPONENTS)
    comps=[]
    for i in range(k):
        comps.append({"component":i+1,"explained_variance":_clean(eigen[i]),"explained_variance_ratio":_clean(ratios[i]),
                      "loadings":{c:_clean(vt[i,j]) for j,c in enumerate(selected)}})
    scores=(u[:,:k]*s[:k]); score_rows=[]
    limit=min(len(scores),MAX_PREVIEW_ROWS)
    for pos,(idx,row) in enumerate(zip(complete.index[:limit],scores[:limit])):
        score_rows.append({"row_index":int(idx) if isinstance(idx,(int,np.integer)) else str(idx),**{f"PC{i+1}":_clean(row[i]) for i in range(k)}})
    out={"ok":True,"schema":f"{SCHEMA}/pca","dataset_id":dataset_id,"columns":selected,"standardize":standardize,"complete_row_count":int(len(complete)),
         "components":comps,"score_preview":score_rows,"missing_rows_excluded_from_pca":int(len(df)-len(complete)),
         "dimension_selection_inferred":False,"cluster_structure_inferred":False,"exploratory_not_confirmatory":True}
    out["analysis_hash"]=_hash(out); return out


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, rows, columns, df = _frame(payload)
    kinds={c:_column_kind(df[c]) for c in columns}; numeric=[c for c,k in kinds.items() if k=="numeric"]; categorical=[c for c,k in kinds.items() if k in {"categorical","boolean"}]
    figures=[]
    for c in numeric[:24]:
        figures.append({"figure_type":"histogram","column":c,"semantic_role":"exploratory-distribution","source_ref":f"lab:dataset:{dataset_id}","automatic_render":False})
    if len(numeric)>=2:
        figures.append({"figure_type":"correlation-matrix","columns":numeric[:30],"semantic_role":"exploratory-association","automatic_render":False})
    if categorical and numeric:
        figures.append({"figure_type":"group-summary","group_by":categorical[0],"value_columns":numeric[:8],"automatic_render":False})
    figures.append({"figure_type":"missingness-matrix","columns":columns[:60],"semantic_role":"data-quality","automatic_render":False})
    out={"ok":True,"schema":f"{SCHEMA}/visualization-plan","dataset_id":dataset_id,"figures":figures,
         "uses_publication_design_system_v01140":True,"uses_statistical_graphics_v01150":True,"uses_dashboard_runtime_v01160":True,
         "automatic_render":False,"automatic_scientific_interpretation":False}
    out["plan_hash"]=_hash(out); return out


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_dataset(payload); profile=profile_dataset(payload); missing=analyze_missingness(payload); dist=analyze_distributions(payload)
    corr=None
    try:
        if len(_numeric_columns(pd.DataFrame(normalized["rows"],columns=normalized["columns"])))>=2: corr=analyze_correlations(payload)
    except EDAStudioError: corr=None
    visual=build_visualization_plan(payload)
    out={"ok":True,"schema":f"{SCHEMA}/studio","version":VERSION,"dataset":{k:v for k,v in normalized.items() if k!="rows"},
         "profile":profile,"missingness":missing,"distributions":dist,"correlations":corr,"visualization_plan":visual,
         "exploratory_not_confirmatory":True,"source_dataset_mutated":False,"automatic_hypothesis_confirmation":False}
    out["studio_hash"]=_hash(out); return out


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    dataset=normalize_dataset(payload); settings=_dict(payload.get("settings"),"settings"); refs=_list(payload.get("analysis_refs") or payload.get("analysisRefs"),"analysis_refs",500)
    body={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"dataset_ref":f"lab:dataset:{dataset['dataset_id']}","dataset_hash":dataset["dataset_hash"],
          "settings":settings,"analysis_refs":[str(x) for x in refs],"source_rows_immutable":True}
    body["snapshot_hash"]=_hash(body)
    return {"ok":True,"snapshot":body,"automatic_persistence":False,"automatic_core_submission":False}


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    dataset=normalize_dataset(payload); formats=[str(x).lower() for x in (_list(payload.get("formats"),"formats",20) or ["json","csv","html"])]
    allowed={"json","csv","html","pdf","svg","png"}; bad=sorted(set(formats)-allowed)
    if bad: raise EDAStudioError(f"Unsupported export formats: {', '.join(bad)}")
    out={"ok":True,"schema":f"{SCHEMA}/export-plan","dataset_id":dataset["dataset_id"],"dataset_hash":dataset["dataset_hash"],"formats":formats,
         "include_provenance":True,"include_analysis_settings":True,"include_exploratory_boundary":True,"automatic_file_write":False,
         "automatic_publication":False,"scientific_validity_certified":False}
    out["plan_hash"]=_hash(out); return out


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    dataset=normalize_dataset(payload); snapshot=build_snapshot(payload); session_id=_text(payload.get("session_id") or payload.get("sessionId"),"session_id",100,True)
    local_id=_text(payload.get("analysis_id") or payload.get("analysisId") or f"eda-{dataset['dataset_id']}","analysis_id",180,True)
    binding=build_core_object_binding({"session_id":session_id,"object":{"object_type":"artifact","local_id":local_id,
        "content_hash":snapshot["snapshot"]["snapshot_hash"],"source_contract":SCHEMA,"role":"analysis",
        "metadata":{"analysis_kind":"exploratory-data-analysis","dataset_ref":f"lab:dataset:{dataset['dataset_id']}","dataset_hash":dataset["dataset_hash"],
                    "exploratory_not_confirmatory":True,"scientific_validity_certified":False},
        "provenance":{"lab_release_version":VERSION,"source_dataset_immutable":True}}})
    return {"ok":True,"schema":f"{SCHEMA}/core-object-plan","binding":binding,"automatic_core_submission":False,
            "core_determines_scientific_validity":False,"underlying_analysis_authoritative_in_lab":True}
