from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

VERSION = "0.30.0"
PROTOCOL_SCHEMA = "sc-lab-experiment-protocol/0.30.0"
RUN_SCHEMA = "sc-lab-experiment-run/0.30.0"
COMPARISON_SCHEMA = "sc-lab-experiment-comparison/0.30.0"
REPORT_SCHEMA = "sc-lab-experiment-report/0.30.0"
BUNDLE_SCHEMA = "sc-lab-experiment-bundle/0.30.0"
MAX_VARIABLES = 100
MAX_STEPS = 200
MAX_RUNS = 100

class ExperimentFrameworkError(ValueError):
    pass

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()

def _text(value: Any, limit: int = 4000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]

def _list(value: Any, limit: int) -> list[Any]:
    return list(value)[:limit] if isinstance(value, list) else []

def _number(value: Any) -> float | None:
    try:
        n=float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None

def health() -> dict[str, Any]:
    return {
        "ok": True, "status": "ready", "version": VERSION,
        "protocolSchema": PROTOCOL_SCHEMA, "runSchema": RUN_SCHEMA,
        "comparisonSchema": COMPARISON_SCHEMA, "reportSchema": REPORT_SCHEMA,
        "capabilities": {
            "protocols": True, "hypotheses": True, "variablesAndControls": True,
            "procedures": True, "runHistories": True, "replicationRecords": True,
            "resultComparison": True, "experimentReports": True,
            "preregistrationMetadata": True, "arbitraryCode": False,
            "serverBackedRegistry": False,
        },
        "limits": {"variables": MAX_VARIABLES, "procedureSteps": MAX_STEPS, "comparisonRuns": MAX_RUNS},
    }

def policies() -> dict[str, Any]:
    return {
        "version": VERSION,
        "designTypes": ["observational", "controlled", "randomized-controlled", "factorial", "crossover", "simulation", "field-study", "replication"],
        "variableRoles": ["independent", "dependent", "control", "covariate", "confounder", "derived"],
        "protocolStates": ["draft", "preregistered", "active", "completed", "suspended", "archived"],
        "runStates": ["planned", "running", "completed", "failed", "excluded"],
        "requiredForReadiness": ["title", "hypothesis", "objective", "variables", "procedure", "analysisPlan"],
        "arbitraryCode": False,
    }

def normalize_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    source=payload.get("protocol") if isinstance(payload.get("protocol"),dict) else payload
    variables=[]
    for i,row in enumerate(_list(source.get("variables"),MAX_VARIABLES),1):
        if not isinstance(row,dict): continue
        name=_text(row.get("name"),200)
        if not name: continue
        variables.append({
            "id": _text(row.get("id"),160) or f"variable-{i}",
            "name": name,
            "label": _text(row.get("label"),300) or name,
            "role": _text(row.get("role"),40).lower() or "dependent",
            "dataType": _text(row.get("dataType"),40).lower() or "number",
            "unit": _text(row.get("unit"),80),
            "measurementMethod": _text(row.get("measurementMethod"),1000),
            "allowedValues": _list(row.get("allowedValues"),100),
        })
    steps=[]
    for i,row in enumerate(_list(source.get("procedure"),MAX_STEPS),1):
        if isinstance(row,str): row={"action":row}
        if not isinstance(row,dict): continue
        action=_text(row.get("action") or row.get("description"),2000)
        if action: steps.append({"order":i,"action":action,"duration":_text(row.get("duration"),100),"safety":_text(row.get("safety"),1000),"checkpoint":bool(row.get("checkpoint"))})
    controls=[]
    for row in _list(source.get("controls"),100):
        if isinstance(row,str): row={"name":row}
        if isinstance(row,dict) and _text(row.get("name"),300):
            controls.append({"name":_text(row.get("name"),300),"description":_text(row.get("description"),1000),"value":row.get("value"),"unit":_text(row.get("unit"),80)})
    protocol={
        "schema": PROTOCOL_SCHEMA, "version": VERSION, "recordType": "experiment-protocol",
        "id": _text(source.get("id"),180) or f"experiment-protocol-{_hash(source)[:16]}",
        "title": _text(source.get("title"),500) or "Untitled experiment protocol",
        "domain": _text(source.get("domain"),200),
        "designType": _text(source.get("designType"),80).lower() or "controlled",
        "status": _text(source.get("status"),40).lower() or "draft",
        "objective": _text(source.get("objective"),4000),
        "hypothesis": _text(source.get("hypothesis"),4000),
        "nullHypothesis": _text(source.get("nullHypothesis"),4000),
        "rationale": _text(source.get("rationale"),8000),
        "variables": variables, "controls": controls, "procedure": steps,
        "samplePlan": source.get("samplePlan") if isinstance(source.get("samplePlan"),dict) else {},
        "analysisPlan": _text(source.get("analysisPlan"),8000),
        "randomization": _text(source.get("randomization"),2000),
        "blinding": _text(source.get("blinding"),2000),
        "inclusionCriteria": [_text(x,1000) for x in _list(source.get("inclusionCriteria"),100) if _text(x,1000)],
        "exclusionCriteria": [_text(x,1000) for x in _list(source.get("exclusionCriteria"),100) if _text(x,1000)],
        "methodIds": [_text(x,200) for x in _list(source.get("methodIds"),100) if _text(x,200)],
        "sourceIds": [_text(x,200) for x in _list(source.get("sourceIds"),200) if _text(x,200)],
        "evidenceIds": [_text(x,200) for x in _list(source.get("evidenceIds"),200) if _text(x,200)],
        "preregistration": source.get("preregistration") if isinstance(source.get("preregistration"),dict) else {},
        "createdAt": source.get("createdAt") or _now(), "updatedAt": _now(),
    }
    protocol["protocolHash"]=_hash({k:v for k,v in protocol.items() if k not in {"protocolHash","updatedAt"}})
    return protocol

def validate_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    p=normalize_protocol(payload)
    blockers=[]; warnings=[]
    if not p["title"] or p["title"]=="Untitled experiment protocol": blockers.append("A specific protocol title is required.")
    if not p["hypothesis"]: blockers.append("A testable hypothesis is required.")
    if not p["objective"]: blockers.append("An experiment objective is required.")
    if not p["variables"]: blockers.append("At least one variable is required.")
    if not any(v["role"]=="independent" for v in p["variables"]): warnings.append("No independent variable is identified.")
    if not any(v["role"]=="dependent" for v in p["variables"]): blockers.append("At least one dependent variable is required.")
    if not p["procedure"]: blockers.append("At least one procedure step is required.")
    if not p["analysisPlan"]: blockers.append("A prespecified analysis plan is required.")
    if p["designType"] in {"controlled","randomized-controlled","factorial","crossover"} and not p["controls"]: warnings.append("The selected design normally requires a control condition.")
    if p["designType"]=="randomized-controlled" and not p["randomization"]: warnings.append("Randomization is not documented.")
    if not p["sourceIds"]: warnings.append("No supporting research source is linked.")
    score=max(0,100-len(blockers)*18-len(warnings)*5)
    return {"ok":not blockers,"ready":not blockers,"score":score,"blockingIssues":blockers,"warnings":warnings,"protocol":p,"evaluatedAt":_now()}

def build_run(payload: dict[str, Any]) -> dict[str, Any]:
    p=normalize_protocol(payload.get("protocol") or {})
    source=payload.get("run") if isinstance(payload.get("run"),dict) else payload
    observations=_list(source.get("observations"),5000)
    results=source.get("results") if isinstance(source.get("results"),(dict,list)) else {}
    run={
        "schema": RUN_SCHEMA,"version":VERSION,"recordType":"experiment-run",
        "id":_text(source.get("id"),180) or f"experiment-run-{_hash(source)[:16]}",
        "title":_text(source.get("title"),500) or f"Run of {p['title']}",
        "protocolId":p["id"],"protocolHash":p["protocolHash"],
        "replicate":max(1,int(source.get("replicate") or 1)),
        "status":_text(source.get("status"),40).lower() or "completed",
        "startedAt":source.get("startedAt") or _now(),"completedAt":source.get("completedAt") or _now(),
        "operator":_text(source.get("operator"),300),"location":_text(source.get("location"),500),
        "environment":source.get("environment") if isinstance(source.get("environment"),dict) else {},
        "deviations":[_text(x,2000) for x in _list(source.get("deviations"),200) if _text(x,2000)],
        "observations":observations,"results":results,
        "exclusionReason":_text(source.get("exclusionReason"),2000),
        "warnings":[_text(x,1000) for x in _list(source.get("warnings"),200) if _text(x,1000)],
        "createdAt":source.get("createdAt") or _now(),"updatedAt":_now(),
    }
    run["resultHash"]=_hash(results); run["runHash"]=_hash({k:v for k,v in run.items() if k not in {"runHash","updatedAt"}})
    return run

def compare_runs(payload: dict[str, Any]) -> dict[str, Any]:
    runs=[build_run({"protocol":payload.get("protocol") or {},"run":r}) for r in _list(payload.get("runs"),MAX_RUNS) if isinstance(r,dict)]
    if len(runs)<2: raise ExperimentFrameworkError("At least two experiment runs are required for comparison.")
    keys=sorted(set().union(*[set(r.get("results",{}).keys()) for r in runs if isinstance(r.get("results"),dict)]))
    metrics=[]
    tolerance=max(0.0,float(payload.get("relativeTolerance") or 0.05))
    for key in keys:
        vals=[_number(r.get("results",{}).get(key)) for r in runs]
        vals=[v for v in vals if v is not None]
        if len(vals)>=2:
            mean=sum(vals)/len(vals); span=max(vals)-min(vals); rel=span/max(abs(mean),1e-15)
            metrics.append({"key":key,"count":len(vals),"mean":mean,"minimum":min(vals),"maximum":max(vals),"range":span,"relativeRange":rel,"withinTolerance":rel<=tolerance})
    consistent=bool(metrics) and all(m["withinTolerance"] for m in metrics)
    result={"schema":COMPARISON_SCHEMA,"version":VERSION,"recordType":"experiment-comparison","runIds":[r["id"] for r in runs],"runHashes":[r["runHash"] for r in runs],"relativeTolerance":tolerance,"metrics":metrics,"replicationStatus":"consistent" if consistent else "review-required","createdAt":_now()}
    result["comparisonHash"]=_hash(result)
    return result

def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    p=normalize_protocol(payload.get("protocol") or {})
    runs=[build_run({"protocol":p,"run":r}) for r in _list(payload.get("runs"),MAX_RUNS) if isinstance(r,dict)]
    comparison=compare_runs({"protocol":p,"runs":runs,"relativeTolerance":payload.get("relativeTolerance",0.05)}) if len(runs)>=2 else None
    sections=[
        {"title":"Objective","content":p["objective"]},
        {"title":"Hypothesis","content":p["hypothesis"]},
        {"title":"Design","content":f"{p['designType']} design with {len(p['variables'])} variables, {len(p['controls'])} controls, and {len(p['procedure'])} procedure steps."},
        {"title":"Analysis plan","content":p["analysisPlan"]},
        {"title":"Run summary","content":f"{len(runs)} run(s) recorded."},
        {"title":"Replication","content":comparison["replicationStatus"] if comparison else "Not evaluated"},
    ]
    markdown=f"# {p['title']}\n\n## Objective\n{p['objective']}\n\n## Hypothesis\n{p['hypothesis']}\n\n## Method\n{sections[2]['content']}\n\n## Analysis plan\n{p['analysisPlan']}\n\n## Runs\n{len(runs)} run(s) recorded.\n"
    report={"schema":REPORT_SCHEMA,"version":VERSION,"recordType":"experiment-report","title":p["title"],"protocolId":p["id"],"protocolHash":p["protocolHash"],"runIds":[r["id"] for r in runs],"sections":sections,"comparison":comparison,"markdown":markdown,"createdAt":_now()}
    report["reportHash"]=_hash(report)
    return report

def verify(payload: dict[str, Any]) -> dict[str, Any]:
    record=payload.get("record") if isinstance(payload.get("record"),dict) else payload
    schema=record.get("schema")
    if schema==PROTOCOL_SCHEMA:
        expected=record.get("protocolHash"); key="protocolHash"
    elif schema==RUN_SCHEMA:
        expected=record.get("runHash"); key="runHash"
    elif schema==REPORT_SCHEMA:
        expected=record.get("reportHash"); key="reportHash"
    elif schema==COMPARISON_SCHEMA:
        expected=record.get("comparisonHash"); key="comparisonHash"
    else:
        expected=record.get("runHash") or record.get("reportHash") or record.get("comparisonHash") or record.get("protocolHash")
        key="runHash" if record.get("runHash") else ("reportHash" if record.get("reportHash") else ("comparisonHash" if record.get("comparisonHash") else "protocolHash"))
    if not expected: raise ExperimentFrameworkError("A supported experiment record hash is required.")
    excluded={key}
    if key in {"protocolHash","runHash"}: excluded.add("updatedAt")
    actual=_hash({k:v for k,v in record.items() if k not in excluded})
    return {"ok":actual==expected,"expectedHash":expected,"actualHash":actual,"verifiedAt":_now()}
