from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from statistics import NormalDist
from typing import Any

from .scientific_literature_provenance_v0630 import normalize_source

VERSION = "0.64.0"
PROTOCOL_SCHEMA = "sc-lab-systematic-evidence-synthesis-protocol/0.64.0"
EFFECT_SCHEMA = "sc-lab-study-effect-estimate/0.64.0"
REPLICATION_SCHEMA = "sc-lab-replication-assessment/0.64.0"
META_SCHEMA = "sc-lab-meta-analysis-result/0.64.0"
PACKET_SCHEMA = "sc-lab-systematic-evidence-synthesis-packet/0.64.0"
MAX_SOURCES = 500
MAX_EFFECTS = 500
MAX_CLAIMS = 100
MAX_REVIEWS = 100

EFFECT_METRICS = {
    "generic", "mean-difference", "standardized-mean-difference",
    "log-odds-ratio", "log-risk-ratio", "fisher-z-correlation",
}
MODEL_CHOICES = {"fixed-effect", "random-effects"}
REVIEW_DECISIONS = {"accept", "accept-with-qualification", "block", "reopen"}
FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64", "individualdata", "participantdata",
}


class SystematicEvidenceSynthesisError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, default: str = "") -> str:
    text = _text(value, 180)
    safe = "".join(ch for ch in text if ch.isalnum() or ch in "-_.:")
    return safe or default


def _ids(value: Any, limit: int = MAX_CLAIMS) -> list[str]:
    if not isinstance(value, list):
        return []
    out=[]
    for raw in value[:limit]:
        v=_id(raw)
        if v and v not in out: out.append(v)
    return out


def _notes(value: Any, limit: int = 40) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(x, 800) for x in value[:limit] if _text(x,800)]


def _float(value: Any, name: str) -> float:
    try:
        x=float(value)
    except (TypeError, ValueError):
        raise SystematicEvidenceSynthesisError(f"{name} must be numeric.")
    if not math.isfinite(x):
        raise SystematicEvidenceSynthesisError(f"{name} must be finite.")
    return x


def _scan_forbidden(value: Any, path: str = "$") -> None:
    normalized_forbidden={k.replace("_","").replace("-","") for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            normalized=str(key).replace("-","").replace("_","").lower()
            if normalized in normalized_forbidden:
                raise SystematicEvidenceSynthesisError(
                    f"Evidence synthesis accepts aggregate study metadata/effect estimates only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value): _scan_forbidden(child, f"{path}[{i}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True, "version": VERSION,
        "systematicEvidenceSynthesis": True, "fixedEffectMetaAnalysis": True, "randomEffectsMetaAnalysis": True,
        "heterogeneityDiagnostics": True, "leaveOneOutSensitivity": True, "replicationAssessment": True,
        "contradictoryFindingsPreserved": True, "humanSynthesisReviewRequired": True,
        "rawParticipantDataAccepted": False, "rawStudyDataAccepted": False,
        "automaticStudyQualityScoringAuthorized": False, "automaticPublicationBiasCorrectionAuthorized": False,
        "automaticTruthInferenceAuthorized": False, "automaticCausalCertificationAuthorized": False,
        "automaticPublicationAuthorized": False, "networkFetchDuringSynthesisAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True, "status": "systematic-evidence-synthesis-ready", "version": VERSION, "platformVersion": "1.0.0",
        "effectMetrics": sorted(EFFECT_METRICS), "models": sorted(MODEL_CHOICES), "heterogeneityEstimator": "dersimonian-laird",
        "humanSynthesisReviewRequired": True, "rawParticipantDataAccepted": False,
        "automaticTruthInference": False, "automaticCausalCertification": False, "publicationBiasCorrection": False,
        "networkFetchDuringSynthesis": False, "arbitraryCode": False,
    }


def _review_history(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list): return []
    out=[]
    for i, raw in enumerate(value[:MAX_REVIEWS]):
        if not isinstance(raw, dict): continue
        _scan_forbidden(raw)
        decision=_text(raw.get("decision"),50).lower()
        if decision not in REVIEW_DECISIONS: continue
        row={
            "id":_id(raw.get("id"),f"synthesis-review-{i+1}"), "decision":decision,
            "rationale":_text(raw.get("rationale"),2400), "reviewerRole":_text(raw.get("reviewerRole") or "researcher",80),
            "reviewedAt":_text(raw.get("reviewedAt"),64),
        }
        row["reviewHash"]=_hash(row); out.append(row)
    return out


def normalize_protocol(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw=payload if isinstance(payload,dict) else {}; _scan_forbidden(raw)
    metric=_text(raw.get("effectMetric") or "generic",80).lower()
    if metric not in EFFECT_METRICS: raise SystematicEvidenceSynthesisError(f"Unsupported effect metric: {metric}")
    model=_text(raw.get("modelChoice") or "random-effects",60).lower()
    if model not in MODEL_CHOICES: raise SystematicEvidenceSynthesisError(f"Unsupported model choice: {model}")
    try: min_studies=int(raw.get("minStudies") or 2)
    except (TypeError,ValueError): raise SystematicEvidenceSynthesisError("minStudies must be an integer.")
    if not 2 <= min_studies <= 100: raise SystematicEvidenceSynthesisError("minStudies must be between 2 and 100.")
    protocol={
        "schema":PROTOCOL_SCHEMA,"version":VERSION,"id":_id(raw.get("id"),"synthesis-1"),
        "title":_text(raw.get("title") or "Scientific evidence synthesis",500),
        "researchQuestion":_text(raw.get("researchQuestion"),2000), "claimIds":_ids(raw.get("claimIds")),
        "effectMetric":metric,"modelChoice":model,"heterogeneityEstimator":"dersimonian-laird","minStudies":min_studies,
        "inclusionCriteria":_notes(raw.get("inclusionCriteria")),"exclusionCriteria":_notes(raw.get("exclusionCriteria")),
        "scopeNote":_text(raw.get("scopeNote"),2400),"reviewHistory":_review_history(raw.get("reviewHistory")),
    }
    protocol["protocolHash"]=_hash(protocol)
    return protocol


def record_synthesis_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise SystematicEvidenceSynthesisError("Synthesis review requires protocol and review metadata.")
    protocol=normalize_protocol(payload.get("protocol") if isinstance(payload.get("protocol"),dict) else {})
    review=payload.get("review") if isinstance(payload.get("review"),dict) else {}; _scan_forbidden(review)
    decision=_text(review.get("decision"),50).lower()
    if decision not in REVIEW_DECISIONS: raise SystematicEvidenceSynthesisError("Review decision must be accept, accept-with-qualification, block, or reopen.")
    rationale=_text(review.get("rationale"),2400)
    if decision != "reopen" and len(rationale)<4: raise SystematicEvidenceSynthesisError("Synthesis review decisions require a rationale.")
    row={"id":_id(review.get("id"),f"{protocol['id']}-review-{len(protocol['reviewHistory'])+1}"),"decision":decision,"rationale":rationale,"reviewerRole":_text(review.get("reviewerRole") or "researcher",80),"reviewedAt":_text(review.get("reviewedAt"),64)}
    row["reviewHash"]=_hash(row)
    base=deepcopy(protocol);base.pop("protocolHash",None);base["reviewHistory"]=[*protocol["reviewHistory"],row]
    return {"ok":True,"version":VERSION,"review":row,"protocol":normalize_protocol(base)}


def normalize_effect(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw=payload if isinstance(payload,dict) else {}; _scan_forbidden(raw)
    metric=_text(raw.get("effectMetric") or "generic",80).lower()
    if metric not in EFFECT_METRICS: raise SystematicEvidenceSynthesisError(f"Unsupported effect metric: {metric}")
    effect=_float(raw.get("effect"),"effect")
    if raw.get("standardError") not in (None,""):
        se=_float(raw.get("standardError"),"standardError")
    elif raw.get("variance") not in (None,""):
        variance=_float(raw.get("variance"),"variance")
        if variance<=0: raise SystematicEvidenceSynthesisError("variance must be > 0.")
        se=math.sqrt(variance)
    elif raw.get("ciLow") not in (None,"") and raw.get("ciHigh") not in (None,""):
        lo=_float(raw.get("ciLow"),"ciLow"); hi=_float(raw.get("ciHigh"),"ciHigh")
        if hi<=lo: raise SystematicEvidenceSynthesisError("ciHigh must be greater than ciLow.")
        se=(hi-lo)/(2*1.959963984540054)
    else:
        raise SystematicEvidenceSynthesisError("Aggregate effect estimates require standardError, variance, or a 95% confidence interval.")
    if se<=0: raise SystematicEvidenceSynthesisError("standardError must be > 0.")
    n=None
    if raw.get("sampleSize") not in (None,""):
        try:n=int(raw.get("sampleSize"))
        except (TypeError,ValueError): raise SystematicEvidenceSynthesisError("sampleSize must be an integer.")
        if n<=0: raise SystematicEvidenceSynthesisError("sampleSize must be > 0.")
    source_id=_id(raw.get("sourceId"))
    if not source_id: raise SystematicEvidenceSynthesisError("Effect estimates require a sourceId from the v0.63 literature registry.")
    row={
        "schema":EFFECT_SCHEMA,"version":VERSION,"id":_id(raw.get("id"),f"effect-{source_id}"),"sourceId":source_id,
        "claimIds":_ids(raw.get("claimIds")),"effectMetric":metric,"effect":effect,"standardError":se,"variance":se*se,
        "sampleSize":n,"subgroup":_text(raw.get("subgroup"),180),"replicationOfSourceId":_id(raw.get("replicationOfSourceId")),
        "estimateLabel":_text(raw.get("estimateLabel"),200),"note":_text(raw.get("note"),1600),
        "sourceHash":_text(raw.get("sourceHash"),64).lower(),
    }
    row["effectHash"]=_hash(row); return row


def _source_gate(source: dict[str,Any]) -> str:
    if source.get("status") in {"retracted","withdrawn"}: return "excluded"
    rows=source.get("reviewHistory") if isinstance(source.get("reviewHistory"),list) else []
    decision=rows[-1].get("decision") if rows else None
    if decision=="exclude": return "excluded"
    if decision=="include": return "reviewed"
    if decision=="include-with-caution": return "reviewed-with-caution"
    return "needs-review"


def _pool(effects:list[dict[str,Any]], model:str) -> dict[str,Any]:
    ys=[x["effect"] for x in effects]; variances=[x["variance"] for x in effects]; k=len(ys)
    wi=[1/v for v in variances]; sw=sum(wi); fixed=sum(w*y for w,y in zip(wi,ys))/sw
    q=sum(w*(y-fixed)**2 for w,y in zip(wi,ys)); df=max(k-1,0)
    c=sw-(sum(w*w for w in wi)/sw) if sw>0 else 0
    tau2=max(0.0,(q-df)/c) if df>0 and c>0 else 0.0
    i2=max(0.0, ((q-df)/q)*100.0) if q>0 and df>0 else 0.0
    weights=[1/(v+tau2) for v in variances] if model=="random-effects" else wi
    sw2=sum(weights); pooled=sum(w*y for w,y in zip(weights,ys))/sw2; se=math.sqrt(1/sw2)
    z=NormalDist().inv_cdf(0.975); lo=pooled-z*se; hi=pooled+z*se
    p=2*(1-NormalDist().cdf(abs(pooled/se))) if se>0 else 0.0
    normalized=[w/sw2 for w in weights]
    return {"k":k,"model":model,"pooledEffect":pooled,"standardError":se,"ciLow":lo,"ciHigh":hi,"pValueApprox":p,"q":q,"qDf":df,"iSquaredPercent":i2,"tauSquared":tau2,"weights":normalized}


def _leave_one_out(effects:list[dict[str,Any]], model:str) -> list[dict[str,Any]]:
    if len(effects)<3:return []
    out=[]
    for i,e in enumerate(effects):
        subset=effects[:i]+effects[i+1:]; r=_pool(subset,model)
        out.append({"omittedEffectId":e["id"],"pooledEffect":r["pooledEffect"],"ciLow":r["ciLow"],"ciHigh":r["ciHigh"],"iSquaredPercent":r["iSquaredPercent"]})
    return out


def _replications(effects:list[dict[str,Any]]) -> list[dict[str,Any]]:
    by_source:dict[str,list[dict[str,Any]]]={}
    for e in effects: by_source.setdefault(e["sourceId"],[]).append(e)
    out=[]
    for repl in effects:
        original_id=repl.get("replicationOfSourceId")
        if not original_id: continue
        originals=by_source.get(original_id,[])
        if not originals:
            out.append({"replicationEffectId":repl["id"],"replicationSourceId":repl["sourceId"],"originalSourceId":original_id,"gate":"missing-original","directionAgreement":None,"differenceZ":None});continue
        original=originals[0]
        denom=math.sqrt(original["variance"]+repl["variance"]); zdiff=abs(repl["effect"]-original["effect"])/denom if denom>0 else None
        same=(original["effect"]==0 and repl["effect"]==0) or (original["effect"]*repl["effect"]>0)
        if not same: gate="discordant-direction"
        elif zdiff is not None and zdiff>1.959963984540054: gate="direction-consistent-different-magnitude"
        else: gate="directionally-consistent"
        out.append({"replicationEffectId":repl["id"],"replicationSourceId":repl["sourceId"],"originalSourceId":original_id,"originalEffectId":original["id"],"gate":gate,"directionAgreement":same,"differenceZ":zdiff})
    return out


def meta_analyze(payload: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(payload,dict): raise SystematicEvidenceSynthesisError("Meta-analysis requires protocol, literature sources, and aggregate effect estimates.")
    _scan_forbidden({k:v for k,v in payload.items() if k not in {"protocol","sources","effects"}})
    protocol=normalize_protocol(payload.get("protocol") if isinstance(payload.get("protocol"),dict) else {})
    sources=[normalize_source(x) for x in (payload.get("sources") or [])[:MAX_SOURCES] if isinstance(x,dict)] if isinstance(payload.get("sources"),list) else []
    effects=[normalize_effect(x) for x in (payload.get("effects") or [])[:MAX_EFFECTS] if isinstance(x,dict)] if isinstance(payload.get("effects"),list) else []
    source_by_id={s["id"]:s for s in sources}
    unresolved=sorted({e["sourceId"] for e in effects if e["sourceId"] not in source_by_id})
    metric_mismatch=[e["id"] for e in effects if e["effectMetric"]!=protocol["effectMetric"]]
    eligible=[]; unreviewed=[]; excluded=[]
    for e in effects:
        s=source_by_id.get(e["sourceId"])
        if not s: continue
        gate=_source_gate(s)
        if gate in {"reviewed","reviewed-with-caution"} and e["effectMetric"]==protocol["effectMetric"]: eligible.append(e)
        elif gate=="needs-review": unreviewed.append(e["sourceId"])
        else: excluded.append(e["sourceId"])
    result=None
    if len(eligible)>=protocol["minStudies"]: result=_pool(eligible,protocol["modelChoice"])
    replication_rows=_replications(eligible)
    latest=protocol["reviewHistory"][-1] if protocol["reviewHistory"] else None
    decision=latest.get("decision") if latest else None
    if decision=="block": gate="blocked"
    elif unresolved: gate="needs-source"
    elif unreviewed: gate="needs-source-review"
    elif metric_mismatch: gate="needs-effect-harmonization"
    elif len(eligible)<protocol["minStudies"]: gate="needs-evidence"
    elif result and result["iSquaredPercent"]>=75 and decision!="accept-with-qualification": gate="heterogeneous"
    elif decision in {"accept","accept-with-qualification"}: gate="synthesis-reviewed"
    else: gate="needs-review"
    claim_coverage={cid:sum(cid in e["claimIds"] for e in eligible) for cid in protocol["claimIds"]}
    response={
        "ok":True,"version":VERSION,"schema":META_SCHEMA,"gate":gate,"protocol":protocol,
        "sourceCount":len(sources),"effectCount":len(effects),"eligibleEffectCount":len(eligible),
        "unresolvedSourceIds":unresolved,"unreviewedSourceIds":sorted(set(unreviewed)),"excludedSourceIds":sorted(set(excluded)),
        "metricMismatchEffectIds":sorted(metric_mismatch),"claimCoverage":claim_coverage,
        "metaAnalysis":result,"leaveOneOut":_leave_one_out(eligible,protocol["modelChoice"]),"replicationRows":replication_rows,
        "boundaries":{
            "aggregateEffectsOnly":True,"contradictoryAndReplicationFindingsPreserved":True,
            "automaticTruthInference":False,"automaticCausalCertification":False,"publicationBiasCorrection":False,
            "humanSynthesisReviewRequired":True,
        },
    }
    response["synthesisHash"]=_hash(response); return response


def build_synthesis_packet(payload: dict[str,Any]) -> dict[str,Any]:
    analysis=meta_analyze(payload)
    protocol=analysis["protocol"]
    effects=[normalize_effect(x) for x in (payload.get("effects") or [])[:MAX_EFFECTS] if isinstance(x,dict)] if isinstance(payload.get("effects"),list) else []
    packet={
        "ok":True,"version":VERSION,"schema":PACKET_SCHEMA,"protocolId":protocol["id"],"protocolHash":protocol["protocolHash"],
        "gate":analysis["gate"],"synthesisHash":analysis["synthesisHash"],"metaAnalysis":analysis["metaAnalysis"],
        "replicationRows":analysis["replicationRows"],"claimCoverage":analysis["claimCoverage"],
        "effectRecords":[{"id":e["id"],"sourceId":e["sourceId"],"claimIds":e["claimIds"],"effectMetric":e["effectMetric"],"effect":e["effect"],"standardError":e["standardError"],"sampleSize":e["sampleSize"],"subgroup":e["subgroup"],"replicationOfSourceId":e["replicationOfSourceId"],"effectHash":e["effectHash"]} for e in effects],
        "unresolvedSourceIds":analysis["unresolvedSourceIds"],"unreviewedSourceIds":analysis["unreviewedSourceIds"],"excludedSourceIds":analysis["excludedSourceIds"],
        "boundaries":analysis["boundaries"],
    }
    packet["packetHash"]=_hash(packet); return packet


def verify_synthesis_packet(payload: dict[str,Any]) -> dict[str,Any]:
    packet=payload.get("packet") if isinstance(payload,dict) and isinstance(payload.get("packet"),dict) else payload
    if not isinstance(packet,dict): raise SystematicEvidenceSynthesisError("Packet verification requires a synthesis packet.")
    supplied=_text(packet.get("packetHash"),64).lower(); base=deepcopy(packet);base.pop("packetHash",None); expected=_hash(base)
    return {"ok":supplied==expected,"version":VERSION,"suppliedHash":supplied,"expectedHash":expected,"schema":packet.get("schema")}
