from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

from .linked_views_v0790 import LinkedViewsError, normalize_view as normalize_v0790_view
from .scientific_visualization_design_system_v01140 import (
    VisualizationDesignSystemError,
    build_export_plan as build_v01140_export_plan,
    compose_small_multiples as compose_v01140_small_multiples,
)

VERSION = "0.116.0"
ENGINE_VERSION = "3.2.0"
SCHEMA = "sc-lab-interactive-scientific-dashboards/0.116.0"
DASHBOARD_SCHEMA = "sc-lab-interactive-scientific-dashboard/0.116.0"
STATE_SCHEMA = "sc-lab-scientific-dashboard-state/0.116.0"
MAX_PANELS = 48
MAX_LINKS = 256
MAX_CONTROLS = 64
MAX_SELECTION_VALUES = 10000
MAX_PROVENANCE_REFS = 5000

INTERACTION_CHANNELS = {"selection", "brush", "filter", "cursor", "state-axis", "parameter", "time-window"}
CONTROL_TYPES = {"category-filter", "range-filter", "time-window", "parameter", "toggle", "search"}
RENDERERS = {"svg2d", "canvas3d", "canvas4d", "webgl2", "webgpu"}
LAYOUT_TYPES = {"grid", "rows", "columns", "masonry"}
EXPORT_MODES = {"dashboard-view", "figure-set", "publication-sheet", "state-bundle"}


class InteractiveDashboardError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 1200, required: bool = False) -> str:
    s = str(value or "").strip()
    if required and not s:
        raise InteractiveDashboardError(f"{label} is required.")
    if len(s) > maximum:
        raise InteractiveDashboardError(f"{label} exceeds {maximum} characters.")
    return s


def _list(value: Any, label: str, maximum: int) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise InteractiveDashboardError(f"{label} must be an array.")
    if len(value) > maximum:
        raise InteractiveDashboardError(f"{label} exceeds {maximum} entries.", 413)
    return value


def _id(value: Any, fallback: str, label: str = "id") -> str:
    return _text(value or fallback, label, 160, True)




def schema_info() -> dict[str, Any]:
    return {
        "ok": True, "schema": SCHEMA, "dashboard_schema": DASHBOARD_SCHEMA, "state_schema": STATE_SCHEMA,
        "version": VERSION, "engine_version": ENGINE_VERSION, "panel_limit": MAX_PANELS,
        "link_limit": MAX_LINKS, "control_limit": MAX_CONTROLS, "api_route_count": 18,
        "interaction_channels": sorted(INTERACTION_CHANNELS), "control_types": sorted(CONTROL_TYPES),
    }

def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "interaction_channels": sorted(INTERACTION_CHANNELS),
        "control_types": sorted(CONTROL_TYPES),
        "renderers": sorted(RENDERERS),
        "layout_types": sorted(LAYOUT_TYPES),
        "export_modes": sorted(EXPORT_MODES),
        "publication_design_system": "0.114.0",
        "statistical_graphics": "0.115.0",
        "linked_views_engine": "0.79.0",
    }


def normalize_panel(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InteractiveDashboardError("panel must be an object.")
    panel_id = _id(payload.get("id") or payload.get("panel_id") or payload.get("panelId"), f"panel-{index+1}", "panel id")
    renderer = _text(payload.get("renderer") or "svg2d", "renderer", 40, True).lower()
    if renderer not in RENDERERS:
        raise InteractiveDashboardError(f"Unsupported renderer: {renderer}")
    figure_kind = _text(payload.get("figure_kind") or payload.get("figureKind") or payload.get("kind") or "scatter", "figure kind", 80, True)
    source_refs = [_text(x, "source ref", 500, True) for x in _list(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs", MAX_PROVENANCE_REFS)]
    out = {
        "id": panel_id,
        "title": _text(payload.get("title") or "Scientific view", "panel title", 240, True),
        "renderer": renderer,
        "figure_kind": figure_kind,
        "figure_ref": payload.get("figure_ref") or payload.get("figureRef"),
        "dataset_ref": payload.get("dataset_ref") or payload.get("datasetRef"),
        "source_refs": source_refs,
        "spec": copy.deepcopy(payload.get("spec")) if isinstance(payload.get("spec"), dict) else None,
        "position": copy.deepcopy(payload.get("position")) if isinstance(payload.get("position"), dict) else {},
        "scale_groups": copy.deepcopy(payload.get("scale_groups") or payload.get("scaleGroups") or {}),
        "interaction_scope": _text(payload.get("interaction_scope") or payload.get("interactionScope") or "dashboard", "interaction scope", 80, True),
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_control(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InteractiveDashboardError("control must be an object.")
    kind = _text(payload.get("type") or "category-filter", "control type", 60, True).lower()
    if kind not in CONTROL_TYPES:
        raise InteractiveDashboardError(f"Unsupported control type: {kind}")
    targets = [_text(x, "control target", 160, True) for x in _list(payload.get("target_panel_ids") or payload.get("targetPanelIds"), "target_panel_ids", MAX_PANELS)]
    key = _text(payload.get("key"), "control key", 160, kind != "toggle")
    out = {
        "id": _id(payload.get("id"), f"control-{index+1}", "control id"),
        "type": kind,
        "label": _text(payload.get("label") or key or kind.replace("-", " ").title(), "control label", 180, True),
        "key": key or None,
        "target_panel_ids": targets,
        "value": copy.deepcopy(payload.get("value")),
        "domain": copy.deepcopy(payload.get("domain")),
        "operator": _text(payload.get("operator") or "equals", "operator", 60, True),
        "enabled": bool(payload.get("enabled", True)),
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_link(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InteractiveDashboardError("link must be an object.")
    channel = _text(payload.get("channel") or "selection", "link channel", 60, True).lower()
    if channel not in INTERACTION_CHANNELS:
        raise InteractiveDashboardError(f"Unsupported interaction channel: {channel}")
    source = _id(payload.get("source_panel_id") or payload.get("sourcePanelId"), "", "source panel id")
    targets = [_text(x, "target panel id", 160, True) for x in _list(payload.get("target_panel_ids") or payload.get("targetPanelIds"), "target_panel_ids", MAX_PANELS)]
    if not targets:
        raise InteractiveDashboardError("link requires at least one target panel id.")
    direction = _text(payload.get("direction") or "forward", "direction", 40, True).lower()
    if direction not in {"forward", "bidirectional"}:
        raise InteractiveDashboardError("direction must be forward or bidirectional.")
    out = {
        "id": _id(payload.get("id"), f"link-{index+1}", "link id"),
        "source_panel_id": source,
        "target_panel_ids": targets,
        "channel": channel,
        "key": _text(payload.get("key"), "link key", 160) or None,
        "direction": direction,
        "enabled": bool(payload.get("enabled", True)),
        "transform": copy.deepcopy(payload.get("transform")) if isinstance(payload.get("transform"), dict) else None,
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_dashboard(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InteractiveDashboardError("dashboard request must be an object.")
    raw_panels = _list(payload.get("panels"), "panels", MAX_PANELS)
    if not raw_panels:
        raise InteractiveDashboardError("dashboard requires at least one panel.")
    panels = [normalize_panel(p, i) for i, p in enumerate(raw_panels)]
    ids = [p["id"] for p in panels]
    if len(ids) != len(set(ids)):
        raise InteractiveDashboardError("panel ids must be unique.")
    controls = [normalize_control(c, i) for i, c in enumerate(_list(payload.get("controls"), "controls", MAX_CONTROLS))]
    links = [normalize_link(l, i) for i, l in enumerate(_list(payload.get("links"), "links", MAX_LINKS))]
    known = set(ids)
    for control in controls:
        unknown = [x for x in control["target_panel_ids"] if x not in known]
        if unknown:
            raise InteractiveDashboardError(f"control references unknown panels: {', '.join(unknown)}")
    for link in links:
        if link["source_panel_id"] not in known or any(x not in known for x in link["target_panel_ids"]):
            raise InteractiveDashboardError("link references an unknown panel.")
    layout = copy.deepcopy(payload.get("layout") or {})
    layout_type = _text(layout.get("type") or "grid", "layout type", 40, True).lower()
    if layout_type not in LAYOUT_TYPES:
        raise InteractiveDashboardError(f"Unsupported layout type: {layout_type}")
    columns = max(1, min(8, int(layout.get("columns") or min(3, len(panels)))))
    normalized_layout = {
        "type": layout_type,
        "columns": columns,
        "gap_px": max(0, min(80, int(layout.get("gap_px") or layout.get("gapPx") or 18))),
        "responsive": {
            "desktop_columns": columns,
            "tablet_columns": min(columns, 2),
            "mobile_columns": 1,
        },
    }
    dashboard = {
        "schema": DASHBOARD_SCHEMA,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "id": _id(payload.get("id"), "scientific-dashboard", "dashboard id"),
        "title": _text(payload.get("title") or "Scientific dashboard", "dashboard title", 240, True),
        "panels": panels,
        "controls": controls,
        "links": links,
        "layout": normalized_layout,
        "shared_context": copy.deepcopy(payload.get("shared_context") or payload.get("sharedContext") or {}),
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
        "boundaries": {
            "automatic_link_inference": False,
            "automatic_cross_dataset_join": False,
            "automatic_statistical_inference": False,
            "automatic_scientific_validity_certification": False,
            "automatic_truth_determination": False,
        },
    }
    dashboard["fingerprint"] = _hash({k: v for k, v in dashboard.items() if k != "fingerprint"})
    return {"ok": True, "dashboard": dashboard}


def compose_small_multiples(payload: dict[str, Any]) -> dict[str, Any]:
    raw = _list(payload.get("panels"), "panels", MAX_PANELS)
    if not raw:
        raise InteractiveDashboardError("small multiples require at least one panel.")
    panels = [normalize_panel(p, i) for i, p in enumerate(raw)]
    try:
        design = compose_v01140_small_multiples({
            "panels": [{"id": p["id"], "title": p["title"], "figure_ref": p.get("figure_ref"), "spec": p.get("spec")} for p in panels],
            "columns": payload.get("columns") or min(3, len(panels)),
            "shared_x": bool(payload.get("shared_x", payload.get("sharedX", False))),
            "shared_y": bool(payload.get("shared_y", payload.get("sharedY", False))),
        })
    except VisualizationDesignSystemError as exc:
        raise InteractiveDashboardError(str(exc), getattr(exc, "status_code", 400)) from exc
    return {
        "ok": True,
        "schema": f"{SCHEMA}/small-multiples",
        "version": VERSION,
        "composition": design,
        "panels": panels,
        "synchronized_selection": bool(payload.get("synchronized_selection", True)),
        "automatic_scale_harmonization": False,
        "automatic_statistical_comparison": False,
    }


def propagate_interaction(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or {})["dashboard"]
    event = payload.get("event") or {}
    if not isinstance(event, dict):
        raise InteractiveDashboardError("event must be an object.")
    source = _id(event.get("source_panel_id") or event.get("sourcePanelId"), "", "event source panel id")
    channel = _text(event.get("channel") or "selection", "event channel", 60, True).lower()
    if channel not in INTERACTION_CHANNELS:
        raise InteractiveDashboardError(f"Unsupported interaction channel: {channel}")
    if source not in {p["id"] for p in dashboard["panels"]}:
        raise InteractiveDashboardError("event source panel is unknown.")
    value = copy.deepcopy(event.get("value"))
    if isinstance(value, list) and len(value) > MAX_SELECTION_VALUES:
        raise InteractiveDashboardError(f"interaction value exceeds {MAX_SELECTION_VALUES} selected values.", 413)
    updates = []
    for link in dashboard["links"]:
        if not link["enabled"] or link["channel"] != channel:
            continue
        targets = []
        if source == link["source_panel_id"]:
            targets = link["target_panel_ids"]
        elif link["direction"] == "bidirectional" and source in link["target_panel_ids"]:
            targets = [link["source_panel_id"]] + [t for t in link["target_panel_ids"] if t != source]
        for target in targets:
            updates.append({
                "panel_id": target,
                "channel": channel,
                "key": link.get("key"),
                "value": value,
                "link_id": link["id"],
                "link_fingerprint": link["fingerprint"],
            })
    result = {
        "ok": True,
        "schema": f"{SCHEMA}/interaction-event",
        "version": VERSION,
        "source_panel_id": source,
        "channel": channel,
        "updates": updates,
        "propagation_count": len(updates),
        "automatic_data_mutation": False,
        "automatic_cross_dataset_join": False,
    }
    result["event_fingerprint"] = _hash({k: v for k, v in result.items() if k != "event_fingerprint"})
    return result


def build_filter_state(payload: dict[str, Any]) -> dict[str, Any]:
    filters = _list(payload.get("filters"), "filters", MAX_CONTROLS)
    normalized = []
    for i, f in enumerate(filters):
        if not isinstance(f, dict):
            raise InteractiveDashboardError(f"filters[{i}] must be an object.")
        normalized.append({
            "key": _text(f.get("key"), f"filters[{i}].key", 160, True),
            "operator": _text(f.get("operator") or "equals", f"filters[{i}].operator", 60, True),
            "value": copy.deepcopy(f.get("value")),
            "source_panel_id": f.get("source_panel_id") or f.get("sourcePanelId"),
            "target_panel_ids": copy.deepcopy(f.get("target_panel_ids") or f.get("targetPanelIds") or []),
        })
    state = {
        "schema": f"{STATE_SCHEMA}/filters",
        "version": VERSION,
        "filters": normalized,
        "filter_count": len(normalized),
        "declarative_only": True,
        "automatic_query_execution": False,
    }
    state["fingerprint"] = _hash({k: v for k, v in state.items() if k != "fingerprint"})
    return {"ok": True, "state": state}


def synchronize_scales(payload: dict[str, Any]) -> dict[str, Any]:
    groups = _list(payload.get("groups"), "groups", 64)
    out = []
    for i, group in enumerate(groups):
        if not isinstance(group, dict):
            raise InteractiveDashboardError(f"groups[{i}] must be an object.")
        axis = _text(group.get("axis") or "x", f"groups[{i}].axis", 8, True).lower()
        if axis not in {"x", "y", "z", "color"}:
            raise InteractiveDashboardError("scale axis must be x, y, z, or color.")
        domains = _list(group.get("declared_domains") or group.get("declaredDomains"), f"groups[{i}].declared_domains", MAX_PANELS)
        numeric = []
        for j, d in enumerate(domains):
            if not isinstance(d, (list, tuple)) or len(d) != 2:
                raise InteractiveDashboardError(f"groups[{i}].declared_domains[{j}] must be [min,max].")
            lo, hi = float(d[0]), float(d[1])
            if not math.isfinite(lo) or not math.isfinite(hi) or lo > hi:
                raise InteractiveDashboardError("declared scale domains must be finite and ordered.")
            numeric.append([lo, hi])
        if not numeric:
            raise InteractiveDashboardError("scale synchronization requires declared_domains; v0.116 does not infer domains from hidden data.", 422)
        resolved = [min(d[0] for d in numeric), max(d[1] for d in numeric)]
        out.append({
            "id": _id(group.get("id"), f"scale-group-{i+1}", "scale group id"),
            "axis": axis,
            "panel_ids": [_text(x, "panel id", 160, True) for x in _list(group.get("panel_ids") or group.get("panelIds"), "panel_ids", MAX_PANELS)],
            "declared_domains": numeric,
            "synchronized_domain": resolved,
        })
    return {"ok": True, "schema": f"{SCHEMA}/scale-sync", "version": VERSION, "groups": out, "automatic_domain_inference": False}


def snapshot_state(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or {})["dashboard"]
    state = {
        "schema": STATE_SCHEMA,
        "version": VERSION,
        "dashboard_id": dashboard["id"],
        "dashboard_fingerprint": dashboard["fingerprint"],
        "filters": copy.deepcopy(payload.get("filters") or []),
        "selections": copy.deepcopy(payload.get("selections") or {}),
        "parameters": copy.deepcopy(payload.get("parameters") or {}),
        "time_window": copy.deepcopy(payload.get("time_window") or payload.get("timeWindow")),
        "panel_view_state": copy.deepcopy(payload.get("panel_view_state") or payload.get("panelViewState") or {}),
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
    }
    state["state_fingerprint"] = _hash({k: v for k, v in state.items() if k != "state_fingerprint"})
    return {"ok": True, "state": state, "automatic_persistence": False}


def restore_plan(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or {})["dashboard"]
    state = payload.get("state") or {}
    if not isinstance(state, dict):
        raise InteractiveDashboardError("state must be an object.")
    compatible = state.get("dashboard_id") == dashboard["id"] and state.get("dashboard_fingerprint") == dashboard["fingerprint"]
    steps = [] if not compatible else ["restore-filters", "restore-parameters", "restore-time-window", "restore-panel-view-state", "restore-selections-last"]
    return {
        "ok": True,
        "schema": f"{STATE_SCHEMA}/restore-plan",
        "version": VERSION,
        "compatible": bool(compatible),
        "steps": steps,
        "requires_explicit_apply": True,
        "automatic_restore": False,
        "conflict_reason": None if compatible else "dashboard-identity-or-fingerprint-mismatch",
    }


def provenance_trace(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or payload)["dashboard"]
    panels = []
    refs = set()
    for panel in dashboard["panels"]:
        panel_refs = set(panel.get("source_refs") or [])
        if panel.get("dataset_ref"):
            panel_refs.add(str(panel["dataset_ref"]))
        if panel.get("figure_ref"):
            panel_refs.add(str(panel["figure_ref"]))
        refs.update(panel_refs)
        panels.append({"panel_id": panel["id"], "source_refs": sorted(panel_refs), "panel_fingerprint": panel["fingerprint"]})
    return {
        "ok": True,
        "schema": f"{SCHEMA}/provenance-trace",
        "version": VERSION,
        "dashboard_id": dashboard["id"],
        "dashboard_fingerprint": dashboard["fingerprint"],
        "panels": panels,
        "source_refs": sorted(refs),
        "source_ref_count": len(refs),
        "automatic_source_inference": False,
    }


def accessibility_audit(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or payload)["dashboard"]
    issues = []
    for panel in dashboard["panels"]:
        spec = panel.get("spec") or {}
        if not _text(spec.get("title") or panel.get("title"), "title", 300):
            issues.append({"panel_id": panel["id"], "issue": "missing-title", "severity": "error"})
        accessibility = spec.get("accessibility") if isinstance(spec, dict) else None
        if not isinstance(accessibility, dict) or not (accessibility.get("alt_text") or accessibility.get("long_description") or accessibility.get("table_ref")):
            issues.append({"panel_id": panel["id"], "issue": "missing-accessibility-description", "severity": "warning"})
    blockers = [x for x in issues if x["severity"] == "error"]
    return {
        "ok": True,
        "schema": f"{SCHEMA}/accessibility-audit",
        "version": VERSION,
        "dashboard_accessible": len(blockers) == 0,
        "issues": issues,
        "blocker_count": len(blockers),
        "keyboard_navigation": True,
        "focus_visible": True,
        "reduced_motion_supported": True,
        "non_color_encodings_required": True,
        "automatic_alt_text_inference": False,
    }


def export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or {})["dashboard"]
    mode = _text(payload.get("mode") or "dashboard-view", "export mode", 60, True).lower()
    if mode not in EXPORT_MODES:
        raise InteractiveDashboardError(f"Unsupported export mode: {mode}")
    panel_exports = []
    for panel in dashboard["panels"]:
        if isinstance(panel.get("spec"), dict):
            try:
                plan = build_v01140_export_plan({"spec": panel["spec"], "profile": payload.get("profile") or "web-responsive", "formats": payload.get("formats") or ["svg", "pdf", "png", "json"]})
            except Exception as exc:
                plan = {"ok": False, "reason": str(exc), "automatic_file_write": False}
        else:
            plan = {"ok": True, "deferred": True, "reason": "panel carries a reference rather than an inline figure spec", "automatic_file_write": False}
        panel_exports.append({"panel_id": panel["id"], "export": plan})
    return {
        "ok": True,
        "schema": f"{SCHEMA}/export-plan",
        "version": VERSION,
        "mode": mode,
        "dashboard_id": dashboard["id"],
        "dashboard_fingerprint": dashboard["fingerprint"],
        "panel_exports": panel_exports,
        "include_dashboard_state": True,
        "include_provenance": True,
        "include_shared_context": True,
        "automatic_file_write": False,
    }


def build_publication_dashboard(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or payload)["dashboard"]
    access = accessibility_audit({"dashboard": dashboard})
    provenance = provenance_trace({"dashboard": dashboard})
    export = export_plan({"dashboard": dashboard, "mode": payload.get("export_mode") or "publication-sheet", "profile": payload.get("profile") or "journal-double", "formats": payload.get("formats") or ["svg", "pdf", "png", "json"]})
    readiness = access["dashboard_accessible"] and all((x["export"].get("ok") or x["export"].get("deferred")) for x in export["panel_exports"])
    return {
        "ok": True,
        "schema": f"{SCHEMA}/publication-dashboard",
        "version": VERSION,
        "dashboard": dashboard,
        "accessibility": access,
        "provenance": provenance,
        "export_plan": export,
        "publication_ready": bool(readiness),
        "scientific_validity_certified": False,
        "automatic_statistical_inference": False,
        "automatic_truth_determination": False,
    }


def core_visual_plan(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = normalize_dashboard(payload.get("dashboard") or payload)["dashboard"]
    visuals = []
    for panel in dashboard["panels"]:
        visuals.append({
            "visual_ref": panel.get("figure_ref") or f"lab:dashboard-panel:{dashboard['id']}:{panel['id']}",
            "visual_type": "scientific-dashboard-panel",
            "view_ref": panel["id"],
            "source_refs": panel.get("source_refs") or [],
            "metadata": {
                "lab_dashboard_version": VERSION,
                "dashboard_id": dashboard["id"],
                "dashboard_fingerprint": dashboard["fingerprint"],
                "panel_fingerprint": panel["fingerprint"],
                "renderer": panel["renderer"],
                "figure_kind": panel["figure_kind"],
            },
        })
    return {
        "ok": True,
        "schema": f"{SCHEMA}/core-visual-plan",
        "version": VERSION,
        "session_id": payload.get("session_id") or payload.get("sessionId"),
        "visual_bindings": visuals,
        "binding_count": len(visuals),
        "automatic_core_submission": False,
        "dashboard_remains_authoritative_in_lab": True,
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "interactive-scientific-dashboards-small-multiples-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "panel_limit": MAX_PANELS,
        "link_limit": MAX_LINKS,
        "control_limit": MAX_CONTROLS,
        "interaction_channel_count": len(INTERACTION_CHANNELS),
        "control_type_count": len(CONTROL_TYPES),
        "publication_design_system": "0.114.0",
        "statistical_graphics": "0.115.0",
        "linked_views_engine": "0.79.0",
        "features": {
            "responsive_dashboards": True,
            "scientific_small_multiples": True,
            "linked_brushing": True,
            "linked_selection": True,
            "linked_filtering": True,
            "cursor_coordination": True,
            "time_window_coordination": True,
            "parameter_coordination": True,
            "declared_scale_synchronization": True,
            "state_snapshots": True,
            "restore_plans": True,
            "provenance_tracing": True,
            "accessibility_auditing": True,
            "publication_export_planning": True,
            "core_visual_planning": True,
        },
        "boundaries": {
            "automatic_link_inference": False,
            "automatic_scale_domain_inference": False,
            "automatic_cross_dataset_join": False,
            "automatic_query_execution": False,
            "automatic_state_persistence": False,
            "automatic_core_submission": False,
            "automatic_statistical_inference": False,
            "automatic_scientific_validity_certification": False,
            "automatic_truth_determination": False,
        },
    }


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA}
