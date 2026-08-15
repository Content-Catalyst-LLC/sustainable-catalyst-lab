from __future__ import annotations

import hashlib
import json
import statistics
from collections import defaultdict
from copy import deepcopy
from typing import Any

from .integrated_research_beta_v0600 import capability_matrix as integrated_capability_matrix, health as integrated_beta_health
from .scientific_audit_v0590 import health as scientific_audit_health
from .scientific_workflow_composer import health as workflow_composer_health

VERSION = "0.60.1"
SNAPSHOT_SCHEMA = "sc-lab-beta-runtime-snapshot/0.60.1"
SOAK_SCHEMA = "sc-lab-beta-integration-soak/0.60.1"
PACKET_SCHEMA = "sc-lab-beta-field-diagnostic-packet/0.60.1"
MAX_OBSERVATIONS = 80
MAX_ERROR_CATEGORIES = 24
ALLOWED_ENDPOINTS = {
    "diagnostics", "integrated-beta", "scientific-audit", "compute-hardening", "workflow-composer"
}
FORBIDDEN_KEYS = {
    "rows", "records", "rawdata", "dataset", "datasetspayload", "inputs", "secrets", "credentials",
    "password", "token", "apikey", "api_key", "authorization", "cookie", "modelpayload", "sourcecontent",
}


class BetaFieldDiagnosticsError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 160) -> str:
    return str(value or "").strip()[:limit]


def _safe_int(value: Any, default: int = 0, minimum: int = 0, maximum: int = 1_000_000) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _safe_float(value: Any, default: float = 0.0, minimum: float = 0.0, maximum: float = 120_000.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    if parsed != parsed or parsed in {float("inf"), float("-inf")}:
        parsed = default
    return max(minimum, min(maximum, parsed))


def _scan_forbidden(value: Any, path: str = "$", depth: int = 0) -> None:
    if depth > 14:
        raise BetaFieldDiagnosticsError("Diagnostic metadata nesting is too deep.")
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).replace("-", "").replace("_", "").lower()
            if normalized in {x.replace("_", "") for x in FORBIDDEN_KEYS}:
                raise BetaFieldDiagnosticsError(f"Field diagnostics accept runtime metadata only; prohibited field at {path}.{key}.")
            _scan_forbidden(item, f"{path}.{key}", depth + 1)
    elif isinstance(value, list):
        if len(value) > 500:
            raise BetaFieldDiagnosticsError("Diagnostic metadata arrays are bounded to 500 items.")
        for index, item in enumerate(value):
            _scan_forbidden(item, f"{path}[{index}]", depth + 1)


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "betaStabilizationRelease": True,
        "metadataOnlyDiagnostics": True,
        "boundedUserInitiatedSoak": True,
        "maxSoakObservations": MAX_OBSERVATIONS,
        "externalTelemetryAuthorized": False,
        "backgroundMonitoringAuthorized": False,
        "automaticRepairAuthorized": False,
        "automaticScientificStateMutationAuthorized": False,
        "rawScientificDataAccepted": False,
        "credentialsAccepted": False,
        "humanReviewRequired": True,
    }


def health() -> dict[str, Any]:
    beta = integrated_beta_health()
    audit = scientific_audit_health()
    workflow = workflow_composer_health()
    matrix = integrated_capability_matrix()
    ok = bool(beta.get("ok")) and bool(audit.get("ok", True)) and bool(workflow.get("ok", True)) and bool(matrix.get("ok"))
    return {
        "ok": ok,
        "status": "beta-field-diagnostics-ready" if ok else "integration-dependency-warning",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "integratedBetaVersion": beta.get("version", "0.60.0"),
        "capabilityHash": matrix.get("capabilityHash"),
        "metadataOnly": True,
        "boundedSoak": True,
        "automaticRepair": False,
        "externalTelemetry": False,
        "humanReviewRequired": True,
    }


def scenarios() -> dict[str, Any]:
    rows = [
        ("wp-proxy-roundtrip", "WordPress REST → compute proxy round trip", ["diagnostics", "integrated-beta"]),
        ("integrated-beta-health", "Integrated beta capability line", ["integrated-beta"]),
        ("audit-boundary", "Scientific audit boundary", ["scientific-audit"]),
        ("compute-path", "Large-workload compute health", ["compute-hardening"]),
        ("workflow-path", "Scientific workflow health", ["workflow-composer"]),
        ("cross-studio-cycle", "Cross-studio same-cycle availability", sorted(ALLOWED_ENDPOINTS)),
        ("transient-recovery", "Recovery after a transient endpoint failure", sorted(ALLOWED_ENDPOINTS)),
        ("sustained-stability", "Bounded repeated endpoint stability", sorted(ALLOWED_ENDPOINTS)),
    ]
    body = [{"id": key, "label": label, "endpoints": endpoints} for key, label, endpoints in rows]
    return {"ok": True, "version": VERSION, "scenarios": body, "scenarioHash": _hash(body)}


def normalize_runtime_snapshot(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    _scan_forbidden(source)
    runtime = source.get("runtime") if isinstance(source.get("runtime"), dict) else source
    connectivity = runtime.get("connectivity") if isinstance(runtime.get("connectivity"), dict) else {}
    storage = runtime.get("storage") if isinstance(runtime.get("storage"), dict) else {}
    integrity = runtime.get("integrity") if isinstance(runtime.get("integrity"), dict) else {}
    dom = runtime.get("dom") if isinstance(runtime.get("dom"), dict) else {}
    raw_errors = runtime.get("errorCategories") if isinstance(runtime.get("errorCategories"), list) else []
    errors = sorted(set(_text(item, 80) for item in raw_errors[:MAX_ERROR_CATEGORIES] if _text(item, 80)))
    visibility = _text(runtime.get("visibility") or "unknown", 24).lower()
    if visibility not in {"visible", "hidden", "prerender", "unknown"}:
        visibility = "unknown"
    normalized = {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "release": _text(runtime.get("release"), 32),
        "platformVersion": _text(runtime.get("platformVersion"), 32),
        "activeModule": _text(runtime.get("activeModule"), 80),
        "visibility": visibility,
        "online": bool(runtime.get("online", True)),
        "connectivity": {
            "wordpressRest": bool(connectivity.get("wordpressRest")),
            "computeBackend": bool(connectivity.get("computeBackend")),
        },
        "storage": {
            "projectStore": bool(storage.get("projectStore")),
            "localStorage": bool(storage.get("localStorage")),
            "sessionStorage": bool(storage.get("sessionStorage")),
        },
        "integrity": {
            "state": _text(integrity.get("state") or "unknown", 40).lower(),
            "partialInstallRisk": bool(integrity.get("partialInstallRisk", False)),
        },
        "dom": {
            "primaryRailCount": _safe_int(dom.get("primaryRailCount"), 0, 0, 20),
            "applicationCardCount": _safe_int(dom.get("applicationCardCount"), 0, 0, 20),
            "graphStudioPresent": bool(dom.get("graphStudioPresent")),
            "workflowWorkspacePresent": bool(dom.get("workflowWorkspacePresent")),
        },
        "errorCategories": errors,
    }
    normalized["snapshotHash"] = _hash(normalized)
    return normalized


def integration_probe(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    snapshot = normalize_runtime_snapshot(source.get("runtime") if isinstance(source.get("runtime"), dict) else source)
    server = health()
    probes: list[dict[str, Any]] = []

    def add(key: str, label: str, status: str, domain: str, detail: str) -> None:
        probes.append({"id": key, "label": label, "status": status, "domain": domain, "detail": detail})

    release = snapshot["release"]
    add("release", "WordPress release line", "pass" if release == VERSION else ("warn" if not release else "fail"), "release-line", f"observed={release or 'missing'} expected={VERSION}")
    add("integrity", "Release integrity", "pass" if snapshot["integrity"]["state"] == "verified" and not snapshot["integrity"]["partialInstallRisk"] else "fail", "integrity", snapshot["integrity"]["state"])
    add("wp-rest", "WordPress REST availability", "pass" if snapshot["connectivity"]["wordpressRest"] else "fail", "wordpress-rest", "reachable" if snapshot["connectivity"]["wordpressRest"] else "unreachable")
    add("compute", "Compute backend availability", "pass" if snapshot["connectivity"]["computeBackend"] else "fail", "compute-backend", "reachable" if snapshot["connectivity"]["computeBackend"] else "unreachable")
    add("project-store", "Active project store", "pass" if snapshot["storage"]["projectStore"] else "warn", "project-persistence", "available" if snapshot["storage"]["projectStore"] else "not detected")
    nav_ok = snapshot["dom"]["primaryRailCount"] == 6 and snapshot["dom"]["applicationCardCount"] >= 3 and snapshot["dom"]["graphStudioPresent"] and snapshot["dom"]["workflowWorkspacePresent"]
    add("presentation", "Beta presentation contract", "pass" if nav_ok else "warn", "browser-runtime", f"rail={snapshot['dom']['primaryRailCount']} cards={snapshot['dom']['applicationCardCount']}")
    add("server-capabilities", "Integrated server capability line", "pass" if server["ok"] else "fail", "backend-capabilities", server["status"])
    add("browser-online", "Browser connectivity", "pass" if snapshot["online"] else "warn", "network", "online" if snapshot["online"] else "offline")
    if snapshot["errorCategories"]:
        add("recent-errors", "Recent categorized runtime errors", "warn", "browser-runtime", ", ".join(snapshot["errorCategories"][:8]))
    else:
        add("recent-errors", "Recent categorized runtime errors", "pass", "browser-runtime", "none")

    failures = [row for row in probes if row["status"] == "fail"]
    warnings = [row for row in probes if row["status"] == "warn"]
    status = "fail" if failures else ("warn" if warnings else "pass")
    domains = sorted(set(row["domain"] for row in failures + warnings))
    hints = []
    hint_map = {
        "release-line": "Confirm the v0.60.1 WordPress ZIP is active and the backend/repository promotion completed.",
        "integrity": "Run the Lab runtime health endpoint and compare plugin, manifest, and platform version lines before further use.",
        "wordpress-rest": "Check WordPress REST routing, nonce/session state, and hosting/WAF rules for /wp-json/sc-lab/v1/.",
        "compute-backend": "Check the configured Python compute origin, backend health, and WordPress compute proxy response.",
        "project-persistence": "Confirm the project store initialized before saving beta evidence; avoid destructive repair while data is unavailable.",
        "browser-runtime": "Reload the Lab shell, verify the six-destination rail, and inspect the first categorized runtime failure before adding UI changes.",
        "backend-capabilities": "Use the integrated-beta capability matrix to locate the unavailable scientific subsystem.",
        "network": "Retry after connectivity returns; do not interpret an offline probe as a scientific failure.",
    }
    for domain in domains:
        if domain in hint_map:
            hints.append(hint_map[domain])
    core = {"version": VERSION, "snapshotHash": snapshot["snapshotHash"], "status": status, "probes": probes, "failureDomains": domains, "repairHints": hints}
    return {"ok": status != "fail", **core, "probeHash": _hash(core), "humanReviewRequired": True, "automaticRepairAuthorized": False}


def _normalize_observations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    source = payload if isinstance(payload, dict) else {}
    _scan_forbidden(source)
    raw = source.get("observations") if isinstance(source.get("observations"), list) else []
    if not raw:
        raise BetaFieldDiagnosticsError("A bounded set of endpoint observations is required for the integration soak.")
    if len(raw) > MAX_OBSERVATIONS:
        raise BetaFieldDiagnosticsError(f"Integration soak is bounded to {MAX_OBSERVATIONS} endpoint observations.")
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        endpoint = _text(item.get("endpoint"), 40).lower()
        if endpoint not in ALLOWED_ENDPOINTS:
            raise BetaFieldDiagnosticsError(f"Unsupported soak endpoint label: {endpoint or 'missing'}")
        status = _safe_int(item.get("status"), 0, 0, 599)
        ok = bool(item.get("ok")) and (status == 0 or 200 <= status < 400)
        error = _text(item.get("errorCategory"), 40).lower()
        out.append({
            "cycle": _safe_int(item.get("cycle"), 1, 1, 24),
            "endpoint": endpoint,
            "ok": ok,
            "status": status,
            "latencyMs": round(_safe_float(item.get("latencyMs"), 0.0), 3),
            "errorCategory": error if error in {"", "timeout", "network", "http", "parse", "aborted"} else "other",
        })
    if not out:
        raise BetaFieldDiagnosticsError("No valid integration-soak observations were provided.")
    return sorted(out, key=lambda row: (row["cycle"], row["endpoint"]))


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def analyze_soak(payload: dict[str, Any]) -> dict[str, Any]:
    observations = _normalize_observations(payload)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        grouped[row["endpoint"]].append(row)
    endpoint_summaries = []
    for endpoint in sorted(ALLOWED_ENDPOINTS):
        rows = grouped.get(endpoint, [])
        if not rows:
            endpoint_summaries.append({"endpoint": endpoint, "samples": 0, "successRate": 0.0, "p50LatencyMs": 0.0, "p95LatencyMs": 0.0, "flaps": 0, "status": "missing"})
            continue
        latencies = [row["latencyMs"] for row in rows]
        success = sum(1 for row in rows if row["ok"])
        states = [row["ok"] for row in rows]
        flaps = sum(1 for a, b in zip(states, states[1:]) if a != b)
        success_rate = success / len(rows)
        p95 = _percentile(latencies, 0.95)
        status = "fail" if success_rate < 0.75 else ("warn" if success_rate < 1.0 or p95 > 5000 or flaps > 0 else "pass")
        endpoint_summaries.append({
            "endpoint": endpoint,
            "samples": len(rows),
            "successRate": round(success_rate, 4),
            "meanLatencyMs": round(statistics.fmean(latencies), 3),
            "p50LatencyMs": round(_percentile(latencies, 0.50), 3),
            "p95LatencyMs": round(p95, 3),
            "maxLatencyMs": round(max(latencies), 3),
            "flaps": flaps,
            "status": status,
        })

    by_cycle: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        by_cycle[row["cycle"]].append(row)
    complete_cycles = sum(1 for rows in by_cycle.values() if {r["endpoint"] for r in rows} >= ALLOWED_ENDPOINTS)
    fully_green_cycles = sum(1 for rows in by_cycle.values() if {r["endpoint"] for r in rows} >= ALLOWED_ENDPOINTS and all(r["ok"] for r in rows))
    failures = [row for row in endpoint_summaries if row["status"] == "fail"]
    warnings = [row for row in endpoint_summaries if row["status"] in {"warn", "missing"}]
    status = "fail" if failures else ("warn" if warnings else "pass")

    scenario_rows = []
    scenario_defs = scenarios()["scenarios"]
    summary_by_endpoint = {row["endpoint"]: row for row in endpoint_summaries}
    for scenario in scenario_defs:
        required = scenario["endpoints"]
        rows = [summary_by_endpoint[e] for e in required]
        if scenario["id"] == "cross-studio-cycle":
            s = "pass" if complete_cycles and fully_green_cycles == complete_cycles else ("fail" if complete_cycles == 0 else "warn")
        elif scenario["id"] == "transient-recovery":
            had_failure = any(not row["ok"] for row in observations)
            recovered = any(
                (not earlier["ok"] and later["ok"] and earlier["endpoint"] == later["endpoint"] and earlier["cycle"] < later["cycle"])
                for earlier in observations for later in observations
            )
            s = "pass" if not had_failure or recovered else "warn"
        else:
            s = "fail" if any(r["status"] in {"fail", "missing"} for r in rows) else ("warn" if any(r["status"] == "warn" for r in rows) else "pass")
        scenario_rows.append({"id": scenario["id"], "label": scenario["label"], "status": s})

    core = {
        "schema": SOAK_SCHEMA,
        "version": VERSION,
        "status": status,
        "observationCount": len(observations),
        "cycleCount": len(by_cycle),
        "completeCycles": complete_cycles,
        "fullyGreenCycles": fully_green_cycles,
        "endpoints": endpoint_summaries,
        "scenarios": scenario_rows,
    }
    return {"ok": status != "fail", **core, "soakHash": _hash({"observations": observations, "summary": core}), "humanReviewRequired": True}


def build_diagnostic_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BetaFieldDiagnosticsError("Diagnostic packet input must be an object.")
    snapshot = normalize_runtime_snapshot(payload.get("runtime") if isinstance(payload.get("runtime"), dict) else {})
    probe = integration_probe({"runtime": snapshot})
    soak_input = payload.get("soak") if isinstance(payload.get("soak"), dict) else payload
    if isinstance(soak_input.get("observations"), list):
        soak = analyze_soak(soak_input)
    elif isinstance(payload.get("soakResult"), dict):
        soak = deepcopy(payload["soakResult"])
        expected = _text(soak.get("soakHash"), 64)
        if len(expected) != 64:
            raise BetaFieldDiagnosticsError("A verified soak result or raw bounded observations are required.")
    else:
        raise BetaFieldDiagnosticsError("Run the bounded integration soak before building a field-diagnostic packet.")
    packet = {
        "schema": PACKET_SCHEMA,
        "version": VERSION,
        "release": snapshot["release"],
        "platformVersion": snapshot["platformVersion"],
        "snapshotHash": snapshot["snapshotHash"],
        "probeHash": probe["probeHash"],
        "soakHash": soak["soakHash"],
        "probeStatus": probe["status"],
        "soakStatus": soak["status"],
        "failureDomains": probe["failureDomains"],
        "repairHints": probe["repairHints"],
        "boundaries": {
            "metadataOnly": True,
            "rawScientificDataIncluded": False,
            "credentialsIncluded": False,
            "externalTelemetry": False,
            "automaticRepair": False,
            "humanReviewRequired": True,
        },
    }
    packet["packetHash"] = _hash(packet)
    return {"ok": True, "packet": packet}


def verify_diagnostic_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") if isinstance(payload, dict) else None
    if not isinstance(packet, dict):
        raise BetaFieldDiagnosticsError("A diagnostic packet is required for verification.")
    supplied = _text(packet.get("packetHash"), 64).lower()
    core = deepcopy(packet)
    core.pop("packetHash", None)
    expected = _hash(core)
    return {"ok": supplied == expected and len(supplied) == 64, "version": VERSION, "suppliedHash": supplied, "expectedHash": expected}
