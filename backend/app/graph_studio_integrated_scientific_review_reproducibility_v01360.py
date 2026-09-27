
from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone
from . import graph_studio_review_workspace_consolidation_v0135210 as workspace
from . import graph_studio_review_closure_v0135200 as closure
from . import graph_studio_cross_review_synthesis_v0135190 as crossreview
from . import graph_studio_review_reproduction_v0135170 as reproduction

VERSION = "0.136.0"
ROUTE_COUNT = 18
BOUNDARY = (
    "Integrated scientific review and reproducibility orchestration assembles review, verification, "
    "impact, reproduction, dissent, closure, and publication-readiness records into one workspace. "
    "It does not establish scientific truth, validity, causal correctness, evidentiary weight, "
    "consensus, reviewer superiority, or publication acceptance."
)

def _now(): return datetime.now(timezone.utc).isoformat()
def _canon(v): return json.dumps(v, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def _fp(v): return hashlib.sha256(_canon(v).encode('utf-8')).hexdigest()
def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default

def default_policy():
    return {
        "singleIntegratedWorkspace": True,
        "deterministicWorkspaceIntegration": True,
        "reviewToReproductionUnification": True,
        "publicationReadinessIntegration": True,
        "incrementalRendererOnly": True,
        "automaticScientificValidity": False,
        "automaticPublicationAcceptance": False,
        "truthRanking": False,
        "causalInference": False,
        "evidenceWeightInference": False,
    }

def _workspace(raw):
    return workspace.normalize_workspace(raw)

def _closure(raw):
    return closure.build_closure(raw)

def _synthesis(raw):
    result = crossreview.normalize_synthesis(raw)
    return result.get('record') if result.get('ok') else None

def review_summary(payload):
    raw = payload if isinstance(payload,dict) else {}
    ws = _workspace(raw)
    syn = _synthesis(raw) or {}
    matrix = crossreview.resolution_matrix({"synthesis": syn}).get("rows", []) if syn else []
    disagreements = crossreview.disagreement_register({"synthesis": syn}).get("items", []) if syn else []
    verification = crossreview.verification_matrix({"synthesis": syn}).get("items", []) if syn else []
    impacts = crossreview.revision_impact_matrix({"synthesis": syn}).get("items", []) if syn else []
    return {
        "ok": ws.get('ok', False),
        "version": VERSION,
        "projectId": ws.get('state',{}).get('projectId','unbound-project'),
        "reviewThreadCount": ws.get('state',{}).get('counts',{}).get('reviewThreads',0),
        "resolutionRecordCount": ws.get('state',{}).get('counts',{}).get('resolutionRecords',0),
        "reviewerPanelCount": ws.get('state',{}).get('counts',{}).get('reviewerPanels',0),
        "verificationBundleCount": ws.get('state',{}).get('counts',{}).get('verificationBundles',0),
        "impactAnalysisCount": ws.get('state',{}).get('counts',{}).get('impactAnalyses',0),
        "crossReviewRows": len(matrix),
        "disagreementCount": len(disagreements),
        "verificationMatrixCount": len(verification),
        "revisionImpactMatrixCount": len(impacts),
        "boundary": BOUNDARY,
    }

def reproducibility_summary(payload):
    raw = payload if isinstance(payload,dict) else {}
    ws = _workspace(raw)
    syn = _synthesis(raw) or {}
    reps = crossreview.reproduction_matrix({"synthesis": syn}).get("items", []) if syn else []
    terminal_failures = []
    for item in reps:
        state = str(_get(item, 'state', 'status', default='')).lower()
        if state in {'failed','failure','error','rejected'}:
            terminal_failures.append(_get(item,'id','reproductionId', default='unknown'))
    return {
        "ok": ws.get('ok', False),
        "version": VERSION,
        "projectId": ws.get('state',{}).get('projectId','unbound-project'),
        "reproductionBridgeCount": ws.get('state',{}).get('counts',{}).get('reproductionBridges',0),
        "reproductionMatrixCount": len(reps),
        "failedTerminalReproductions": terminal_failures,
        "requiresHumanInterpretation": True,
        "boundary": BOUNDARY,
    }

def normalize_workspace(payload):
    raw = payload if isinstance(payload,dict) else {}
    ws = _workspace(raw)
    clos = _closure(raw)
    ready = closure.readiness_report(raw)
    summary = review_summary(raw)
    repro = reproducibility_summary(raw)
    integrated = {
        "schema": "sc-lab-integrated-scientific-review-reproducibility-workspace/0.136.0",
        "version": VERSION,
        "projectId": ws.get('state',{}).get('projectId','unbound-project'),
        "workspace": ws.get('state'),
        "closure": clos.get('package'),
        "readiness": ready,
        "reviewSummary": summary,
        "reproducibilitySummary": repro,
        "createdAt": _now(),
        "boundary": BOUNDARY,
    }
    integrated["workspaceDigest"] = ws.get('state',{}).get('stateDigest')
    integrated["integrationDigest"] = _fp({k:v for k,v in integrated.items() if k not in {'createdAt','integrationDigest'}})
    return {"ok": bool(ws.get('ok') and clos.get('ok') and ready.get('ok')), "version": VERSION, "workspace": integrated, "boundary": BOUNDARY}

def validate_workspace(payload):
    norm = normalize_workspace(payload)
    if not norm.get('ok'):
        return norm
    errors=[]; warnings=[]
    ws = norm['workspace']
    readiness = ws.get('readiness',{})
    if readiness.get('state') == 'not-ready':
        warnings.append('workspace integrates a closure package that is not publication-ready')
    if ws.get('workspace',{}).get('fullGraphRedraw') is not False:
        errors.append('integrated workspace must preserve incremental renderer ownership')
    return {"ok": not errors, "version": VERSION, "workspace": ws, "errors": errors, "warnings": warnings, "boundary": BOUNDARY}

def integrate(payload):
    return normalize_workspace(payload)

def certify(payload):
    ws_audit = workspace.certify(payload)
    valid = validate_workspace(payload)
    readiness = closure.readiness_report(payload)
    out = {
        "ok": bool(ws_audit.get('ok') and valid.get('ok')),
        "version": VERSION,
        "workspaceCertification": ws_audit,
        "integrationValidation": valid,
        "readiness": readiness,
        "integratedCertification": True,
        "automaticScientificValidity": False,
        "automaticPublicationAcceptance": False,
        "boundary": BOUNDARY,
    }
    out['certificationDigest'] = _fp({k:v for k,v in out.items() if k != 'certificationDigest'})
    return out

def project_workspace_packet(payload):
    integ = normalize_workspace(payload)
    if not integ.get('ok'):
        return integ
    pkt = {
        "schema": "sc-lab-project-workspace-packet/0.136.0",
        "version": VERSION,
        "projectId": integ['workspace']['projectId'],
        "integratedReviewWorkspace": integ['workspace'],
        "boundary": BOUNDARY,
    }
    pkt['packetDigest'] = _fp({k:v for k,v in pkt.items() if k != 'packetDigest'})
    return {"ok": True, "version": VERSION, "packet": pkt, "boundary": BOUNDARY}

def workspace_digest(payload):
    integ = normalize_workspace(payload)
    return {"ok": integ.get('ok', False), "version": VERSION, "projectId": integ.get('workspace',{}).get('projectId'), "workspaceDigest": integ.get('workspace',{}).get('workspaceDigest'), "integrationDigest": integ.get('workspace',{}).get('integrationDigest'), "boundary": BOUNDARY}

def status(payload):
    integ = normalize_workspace(payload)
    readiness = integ.get('workspace',{}).get('readiness',{})
    return {"ok": integ.get('ok', False), "version": VERSION, "projectId": integ.get('workspace',{}).get('projectId'), "state": readiness.get('state','unknown'), "administrativelyReady": readiness.get('administratively_ready'), "boundary": BOUNDARY}

def compatibility_report(payload):
    return {
        "ok": True,
        "version": VERSION,
        "compatibleModules": {
            "reviewWorkspaceConsolidation": workspace.VERSION,
            "reviewClosure": closure.VERSION,
            "crossReviewSynthesis": crossreview.VERSION,
            "reviewReproductionBridge": reproduction.VERSION,
        },
        "boundary": BOUNDARY,
    }

def contract():
    return {"ok": True, "version": VERSION, "route_count": ROUTE_COUNT, "policy": default_policy(), "boundary": BOUNDARY}

def acceptance_report():
    return {"ok": True, "version": VERSION, **default_policy(), "integratedCertification": True, "route_count": ROUTE_COUNT, "boundary": BOUNDARY}

def health():
    return {"ok": True, "version": VERSION, "api_route_count": ROUTE_COUNT, "integrated_scientific_review_reproducibility_workspace": True, "boundary": BOUNDARY}

def release_gates():
    return {"ok": True, "version": VERSION, "requiredRouteCount": ROUTE_COUNT, "integratedScientificReviewReproducibilityWorkspace": True, "deterministicWorkspaceIntegration": True, "reviewToReproductionUnification": True, "publicationReadinessIntegration": True, "automaticScientificValidity": False, "automaticPublicationAcceptance": False, "fullGraphRedraw": False, "boundary": BOUNDARY}
