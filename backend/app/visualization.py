from __future__ import annotations

import csv
import io
import math
from typing import Any

import numpy as np

VERSION = "0.27.4"
MAX_POINTS = 2000
MAX_GRID_CELLS = 10000

PROFILES: list[dict[str, Any]] = [
    {"id":"time-series","title":"Time series","description":"Ordered x/y values for differential equations, sampled signals, and convergence histories.","compatibleMethods":["numerics.ode_first_order","numerics.interpolation"]},
    {"id":"spectrum","title":"Frequency spectrum","description":"Amplitude or power against frequency for FFT outputs.","compatibleMethods":["signal.fft_spectrum"]},
    {"id":"uncertainty-distribution","title":"Uncertainty distribution","description":"Histogram, confidence interval, mean, and median for Monte Carlo and bootstrap outputs.","compatibleMethods":["uncertainty.monte_carlo_propagation","uncertainty.bootstrap_mean_interval"]},
    {"id":"sensitivity-tornado","title":"Sensitivity tornado","description":"Ranked signed derivatives or elasticities.","compatibleMethods":["sensitivity.local_finite_difference"]},
    {"id":"parameter-sweep","title":"Parameter sweep","description":"Output response across an ordered parameter sequence.","compatibleMethods":["simulation.parameter_sweep"]},
    {"id":"convergence","title":"Convergence diagnostics","description":"Absolute error and runtime across refinement levels.","compatibleMethods":["benchmark-convergence"]},
    {"id":"scatter-line","title":"Scatter and fitted line","description":"Observed or queried points connected in numeric order.","compatibleMethods":["numerics.interpolation"]},
    {"id":"heatmap","title":"Heatmap and contour projection","description":"A bounded two-dimensional numeric grid rendered as an accessible heatmap.","compatibleMethods":["custom-grid"]},
]

AUTO_TYPES = {
    "numerics.ode_first_order":"time-series",
    "signal.fft_spectrum":"spectrum",
    "uncertainty.monte_carlo_propagation":"uncertainty-distribution",
    "uncertainty.bootstrap_mean_interval":"uncertainty-distribution",
    "sensitivity.local_finite_difference":"sensitivity-tornado",
    "simulation.parameter_sweep":"parameter-sweep",
    "numerics.interpolation":"scatter-line",
}

class VisualizationInputError(ValueError):
    pass

def catalog() -> dict[str, Any]:
    return {
        "schema":"sc-lab-numerical-visualization-catalog/1.0",
        "version":VERSION,
        "profiles":PROFILES,
        "formats":["svg","png","csv","json"],
        "accessibility":{"svgTitle":True,"svgDescription":True,"tabularFallback":True,"reducedMotion":True},
        "limits":{"maxPoints":MAX_POINTS,"maxGridCells":MAX_GRID_CELLS},
    }

def _finite_number(value: Any) -> float:
    try: number=float(value)
    except (TypeError,ValueError): raise VisualizationInputError("Visualization values must be numeric.")
    if not math.isfinite(number): raise VisualizationInputError("Visualization values must be finite.")
    return number

def _series(values: Any, name: str, minimum: int=1, maximum: int=100000) -> list[float]:
    if not isinstance(values,list) or not minimum <= len(values) <= maximum:
        raise VisualizationInputError(f"{name} must contain between {minimum} and {maximum} values.")
    return [_finite_number(v) for v in values]

def _downsample(x: list[float], y: list[float], limit: int) -> tuple[list[float],list[float]]:
    if len(x)!=len(y): raise VisualizationInputError("Visualization x and y arrays must have equal length.")
    if len(x)<=limit: return x,y
    indices=np.linspace(0,len(x)-1,limit,dtype=int)
    return [x[i] for i in indices],[y[i] for i in indices]

def _extent(values: list[float]) -> list[float]:
    return [float(min(values)),float(max(values))] if values else [0.0,0.0]

def _table(columns: list[dict[str,str]], rows: list[dict[str,Any]], limit: int=250) -> dict[str,Any]:
    return {"columns":columns,"rows":rows[:limit],"truncated":len(rows)>limit,"rowCount":len(rows)}

def _line_spec(method: str, outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    if method=="numerics.ode_first_order": x=_series(outputs.get("time"),"time",2); y=_series(outputs.get("values"),"values",2); x_label=options.get("xLabel") or "Time"; y_label=options.get("yLabel") or "Value"
    elif method=="numerics.interpolation": x=_series(outputs.get("query"),"query",1); y=_series(outputs.get("values"),"values",1); x_label=options.get("xLabel") or "Query"; y_label=options.get("yLabel") or "Interpolated value"
    else: x=_series(outputs.get("x"),"x",2); y=_series(outputs.get("y"),"y",2); x_label=options.get("xLabel") or "X"; y_label=options.get("yLabel") or "Y"
    x,y=_downsample(x,y,int(options.get("maxPoints") or 1200)); rows=[{"x":a,"y":b} for a,b in zip(x,y)]
    return {"kind":"line","xLabel":x_label,"yLabel":y_label,"series":[{"id":"primary","label":options.get("seriesLabel") or y_label,"points":rows}],"domain":{"x":_extent(x),"y":_extent(y)},"table":_table([{"key":"x","label":x_label},{"key":"y","label":y_label}],rows)}

def _spectrum_spec(outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    x=_series(outputs.get("frequencyHz"),"frequencyHz",2); key="power" if options.get("measure")=="power" and isinstance(outputs.get("power"),list) else "amplitude"; y=_series(outputs.get(key),key,2); x,y=_downsample(x,y,int(options.get("maxPoints") or 1400)); rows=[{"frequencyHz":a,key:b} for a,b in zip(x,y)]
    return {"kind":"line","xLabel":"Frequency (Hz)","yLabel":"Power" if key=="power" else "Amplitude","series":[{"id":key,"label":"Power spectrum" if key=="power" else "Amplitude spectrum","points":[{"x":a,"y":b} for a,b in zip(x,y)]}],"domain":{"x":_extent(x),"y":_extent(y)},"annotations":[{"type":"vertical-line","x":outputs.get("peakFrequencyHz"),"label":"Peak frequency"}],"table":_table([{"key":"frequencyHz","label":"Frequency (Hz)"},{"key":key,"label":key.title()}],rows)}

def _histogram_spec(outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    hist=outputs.get("histogram") or {}; edges=hist.get("edges"); counts=hist.get("counts")
    if isinstance(edges,list) and isinstance(counts,list) and len(edges)==len(counts)+1 and counts:
        e=_series(edges,"histogram.edges",2); c=_series(counts,"histogram.counts",1); rows=[{"lower":e[i],"upper":e[i+1],"midpoint":(e[i]+e[i+1])/2,"count":c[i]} for i in range(len(c))]
    else:
        minimum=_finite_number(outputs.get("minimum",outputs.get("confidenceInterval",[0,1])[0])); maximum=_finite_number(outputs.get("maximum",outputs.get("confidenceInterval",[0,1])[-1])); mean=_finite_number(outputs.get("mean",outputs.get("bootstrapMean",outputs.get("sampleMean",(minimum+maximum)/2))));
        if minimum==maximum: maximum=minimum+1
        rows=[{"lower":minimum,"upper":mean,"midpoint":(minimum+mean)/2,"count":1},{"lower":mean,"upper":maximum,"midpoint":(mean+maximum)/2,"count":1}]
    values=[row["count"] for row in rows]; mids=[row["midpoint"] for row in rows]
    annotations=[]
    if isinstance(outputs.get("confidenceInterval"),list) and len(outputs["confidenceInterval"])==2:
        annotations.append({"type":"interval","lower":_finite_number(outputs["confidenceInterval"][0]),"upper":_finite_number(outputs["confidenceInterval"][1]),"label":f"{round(float(outputs.get('confidence',0.95))*100)}% confidence interval"})
    for key,label in (("mean","Mean"),("bootstrapMean","Bootstrap mean"),("sampleMean","Sample mean"),("median","Median")):
        if outputs.get(key) is not None: annotations.append({"type":"vertical-line","x":_finite_number(outputs[key]),"label":label})
    return {"kind":"histogram","xLabel":options.get("xLabel") or "Output value","yLabel":"Frequency","bars":[{"x":row["midpoint"],"y":row["count"],"lower":row["lower"],"upper":row["upper"]} for row in rows],"domain":{"x":_extent(mids),"y":[0,max(values) if values else 0]},"annotations":annotations,"table":_table([{"key":"lower","label":"Lower bound"},{"key":"upper","label":"Upper bound"},{"key":"count","label":"Count"}],rows)}

def _sensitivity_spec(outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    raw=outputs.get("sensitivities") or []
    if not isinstance(raw,list) or not raw: raise VisualizationInputError("Sensitivity output does not contain sensitivities.")
    metric="elasticity" if options.get("measure")=="elasticity" else "derivative"; rows=[]
    for row in raw[:50]:
        value=row.get(metric)
        if value is None: continue
        rows.append({"label":str(row.get("variable") or "variable")[:80],"value":_finite_number(value),"baseline":row.get("baseline"),"step":row.get("step")})
    rows.sort(key=lambda row:abs(row["value"]),reverse=True)
    return {"kind":"horizontal-bars","xLabel":metric.title(),"yLabel":"Variable","bars":rows,"domain":{"x":_extent([0.0]+[r["value"] for r in rows])},"table":_table([{"key":"label","label":"Variable"},{"key":"value","label":metric.title()},{"key":"baseline","label":"Baseline"},{"key":"step","label":"Step"}],rows)}

def _sweep_spec(outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    raw=outputs.get("rows") or []
    if not isinstance(raw,list) or not raw: raise VisualizationInputError("Parameter sweep output does not contain rows.")
    rows=[{"parameterValue":_finite_number(row.get("parameterValue")),"output":_finite_number(row.get("output"))} for row in raw]
    x=[r["parameterValue"] for r in rows]; y=[r["output"] for r in rows]; x,y=_downsample(x,y,int(options.get("maxPoints") or 1400)); rows=[{"parameterValue":a,"output":b} for a,b in zip(x,y)]
    return {"kind":"line","xLabel":str(outputs.get("parameter") or "Parameter"),"yLabel":options.get("yLabel") or "Model output","series":[{"id":"sweep","label":str(outputs.get("model") or "Parameter sweep"),"points":[{"x":a,"y":b} for a,b in zip(x,y)]}],"domain":{"x":_extent(x),"y":_extent(y)},"table":_table([{"key":"parameterValue","label":str(outputs.get("parameter") or "Parameter")},{"key":"output","label":"Output"}],rows)}

def _convergence_spec(outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    raw=outputs.get("rows") or []
    if not isinstance(raw,list) or not raw: raise VisualizationInputError("Convergence output does not contain rows.")
    rows=[{"level":int(row.get("level",i+1)),"absoluteError":_finite_number(row.get("absoluteError")),"runtimeMs":_finite_number(row.get("runtimeMs",0))} for i,row in enumerate(raw)]
    points=[{"x":r["level"],"y":r["absoluteError"]} for r in rows]
    return {"kind":"line","scale":{"y":"log" if all(r["absoluteError"]>0 for r in rows) else "linear"},"xLabel":"Refinement level","yLabel":"Absolute error","series":[{"id":"error","label":"Absolute error","points":points}],"domain":{"x":_extent([p["x"] for p in points]),"y":_extent([p["y"] for p in points])},"table":_table([{"key":"level","label":"Level"},{"key":"absoluteError","label":"Absolute error"},{"key":"runtimeMs","label":"Runtime (ms)"}],rows)}

def _heatmap_spec(outputs: dict[str,Any], options: dict[str,Any]) -> dict[str,Any]:
    x=_series(outputs.get("xValues") or outputs.get("x"),"xValues",2,200); y=_series(outputs.get("yValues") or outputs.get("y"),"yValues",2,200); grid=outputs.get("zMatrix") or outputs.get("grid")
    if not isinstance(grid,list) or len(grid)!=len(y) or len(x)*len(y)>MAX_GRID_CELLS: raise VisualizationInputError("Heatmap grid dimensions are invalid or exceed the 10,000-cell limit.")
    cells=[]
    for yi,row in enumerate(grid):
        if not isinstance(row,list) or len(row)!=len(x): raise VisualizationInputError("Every heatmap row must match xValues length.")
        for xi,value in enumerate(row): cells.append({"x":x[xi],"y":y[yi],"z":_finite_number(value),"xIndex":xi,"yIndex":yi})
    z=[c["z"] for c in cells]
    return {"kind":"heatmap","xLabel":options.get("xLabel") or "X","yLabel":options.get("yLabel") or "Y","xValues":x,"yValues":y,"cells":cells,"domain":{"x":_extent(x),"y":_extent(y),"z":_extent(z)},"table":_table([{"key":"x","label":options.get("xLabel") or "X"},{"key":"y","label":options.get("yLabel") or "Y"},{"key":"z","label":options.get("zLabel") or "Value"}],cells)}

def build_spec(payload: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(payload,dict): raise VisualizationInputError("Visualization request must be an object.")
    method=str(payload.get("method") or payload.get("methodId") or "custom-grid")[:128]
    outputs=payload.get("outputs") or payload.get("result") or {}
    if isinstance(outputs,dict) and isinstance(outputs.get("outputs"),dict): outputs=outputs["outputs"]
    if not isinstance(outputs,dict): raise VisualizationInputError("outputs must be an object.")
    options=payload.get("visualization") or payload.get("options") or {}
    if not isinstance(options,dict): options={}
    requested=str(options.get("type") or "auto").lower(); kind=AUTO_TYPES.get(method,"heatmap" if any(k in outputs for k in ("zMatrix","grid")) else "time-series") if requested=="auto" else requested
    if kind in {"time-series","scatter-line"}: core=_line_spec(method,outputs,options)
    elif kind=="spectrum": core=_spectrum_spec(outputs,options)
    elif kind=="uncertainty-distribution": core=_histogram_spec(outputs,options)
    elif kind=="sensitivity-tornado": core=_sensitivity_spec(outputs,options)
    elif kind=="parameter-sweep": core=_sweep_spec(outputs,options)
    elif kind=="convergence": core=_convergence_spec(outputs,options)
    elif kind in {"heatmap","contour","surface-projection"}: core=_heatmap_spec(outputs,options)
    else: raise VisualizationInputError("Unsupported registered visualization type.")
    title=str(options.get("title") or next((p["title"] for p in PROFILES if p["id"]==kind),"Scientific visualization"))[:160]
    description=str(options.get("description") or f"{title} generated from the governed numerical result for {method}.")[:600]
    spec={"schema":"sc-lab-scientific-visualization/1.0","version":VERSION,"method":method,"visualizationType":kind,"title":title,"description":description,"accessibility":{"role":"img","title":title,"description":description,"tabularFallback":True},"exports":["svg","png","csv","json"],**core}
    return spec

def csv_text(spec: dict[str,Any]) -> str:
    table=spec.get("table") or {}; columns=table.get("columns") or []; rows=table.get("rows") or []
    stream=io.StringIO(); writer=csv.writer(stream); writer.writerow([c.get("label") or c.get("key") for c in columns]);
    for row in rows: writer.writerow([row.get(c.get("key")) for c in columns])
    return stream.getvalue()
