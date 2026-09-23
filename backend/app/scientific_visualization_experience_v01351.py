from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

VERSION = "0.135.1"
ENGINE_VERSION = "16.1.0"
SCHEMA = "sc-lab-scientific-visualization-experience/0.135.1"
SNAPSHOT_SCHEMA = "sc-lab-scientific-visualization-experience-snapshot/0.135.1"
MAX_PANELS = 24
MAX_REFS = 50000

VIEW_MODES = {"analysis", "figure", "under-the-hood", "evidence"}
PANEL_FAMILIES = {
    "primary-figure", "empirical-distribution", "residual-diagnostics", "sensitivity-influence",
    "diagnostics-matrix", "model-architecture", "data-provenance", "multivariate-surface",
    "spatial-temporal", "assumptions-evidence", "renderer-capabilities", "linked-objects",
}
CAPABILITY_FAMILIES = {
    "svg2d", "canvas2d", "webgl2", "webgpu", "3d-scenes", "4d-state-space", "spatial-raster",
    "uncertainty-distributions", "scientific-markup", "linked-views", "provenance", "publication-export",
}
PRESENTATION_PROFILES = {"research", "publication", "diagnostics", "model-internals", "presentation"}


class ScientificVisualizationExperienceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()


def _list(v: Any, label: str, maximum: int = MAX_REFS) -> list[Any]:
    if v is None:
        return []
    if not isinstance(v, list):
        raise ScientificVisualizationExperienceError(f"{label} must be an array.")
    if len(v) > maximum:
        raise ScientificVisualizationExperienceError(f"{label} exceeds configured maximum of {maximum}.")
    return v


def _refs(v: Any, label: str) -> list[str]:
    return [str(x)[:300] for x in _list(v, label)]


def schema_info():
    return {
        "ok": True,
        "schema": SCHEMA,
        "snapshot_schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "view_modes": sorted(VIEW_MODES),
        "limits": {"panels": MAX_PANELS, "refs": MAX_REFS},
    }


def catalog():
    return {
        "ok": True,
        "version": VERSION,
        "panel_families": sorted(PANEL_FAMILIES),
        "capability_families": sorted(CAPABILITY_FAMILIES),
        "presentation_profiles": sorted(PRESENTATION_PROFILES),
        "panel_family_count": len(PANEL_FAMILIES),
        "capability_family_count": len(CAPABILITY_FAMILIES),
        "presentation_profile_count": len(PRESENTATION_PROFILES),
        "fabricated_scientific_values": False,
        "automatic_scientific_interpretation": False,
        "automatic_core_submission": False,
    }


def manifest():
    return {
        "ok": True,
        "status": "scientific-visualization-experience-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "graph_studio_overhaul": True,
        "multi_panel_analysis_canvas": True,
        "under_the_hood_graphics": True,
        "data_aware_panels": True,
        "missing_scientific_objects_remain_explicit": True,
        "v01140_design_system_bridge": True,
        "v01160_linked_views_bridge": True,
        "v01190_layout_intelligence_bridge": True,
        "v01330_diagnostic_reference_bridge": True,
        "v01340_evidence_reference_bridge": True,
        "v01350_competing_model_reference_bridge": True,
        "automatic_scientific_interpretation": False,
        "automatic_evidence_promotion": False,
        "automatic_core_submission": False,
    }


def health():
    return {
        **manifest(),
        "schema": SCHEMA,
        "panel_family_count": len(PANEL_FAMILIES),
        "capability_family_count": len(CAPABILITY_FAMILIES),
        "presentation_profile_count": len(PRESENTATION_PROFILES),
        "api_route_count": 32,
    }


def normalize_experience(payload: dict[str, Any]):
    if not isinstance(payload, dict):
        raise ScientificVisualizationExperienceError("payload must be an object.")
    mode = str(payload.get("view_mode") or "analysis").lower()
    if mode not in VIEW_MODES:
        raise ScientificVisualizationExperienceError(f"view_mode must be one of {sorted(VIEW_MODES)}.")
    profile = str(payload.get("presentation_profile") or "research").lower()
    if profile not in PRESENTATION_PROFILES:
        raise ScientificVisualizationExperienceError(f"presentation_profile must be one of {sorted(PRESENTATION_PROFILES)}.")
    row = {
        "experience_ref": str(payload.get("experience_ref") or f"visual-experience:{_hash(payload)[:16]}")[:300],
        "project_ref": payload.get("project_ref"),
        "session_ref": payload.get("session_ref"),
        "figure_ref": payload.get("figure_ref"),
        "view_mode": mode,
        "presentation_profile": profile,
        "dataset_refs": _refs(payload.get("dataset_refs"), "dataset_refs"),
        "model_refs": _refs(payload.get("model_refs"), "model_refs"),
        "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"),
        "diagnostic_refs": _refs(payload.get("diagnostic_refs"), "diagnostic_refs"),
        "researcher_declared": True,
        "automatic_semantic_mutation": False,
    }
    row["experience_hash"] = _hash(row)
    return {"ok": True, "version": VERSION, "experience": row}


def capability_map(payload: dict[str, Any]):
    declared = set(_refs(payload.get("available_capabilities"), "available_capabilities"))
    rows = []
    for name in sorted(CAPABILITY_FAMILIES):
        rows.append({
            "capability": name,
            "state": "available" if name in declared else "available-in-runtime",
            "active_for_current_figure": name in declared,
            "automatic_activation": False,
        })
    return {"ok": True, "version": VERSION, "capabilities": rows, "capability_count": len(rows)}


def compose_workspace(payload: dict[str, Any]):
    requested = _refs(payload.get("panel_families"), "panel_families")
    requested = requested or [
        "primary-figure", "empirical-distribution", "residual-diagnostics", "sensitivity-influence",
        "data-provenance", "model-architecture", "diagnostics-matrix", "assumptions-evidence",
        "multivariate-surface", "spatial-temporal", "renderer-capabilities", "linked-objects",
    ]
    if len(requested) > MAX_PANELS:
        raise ScientificVisualizationExperienceError(f"panel_families exceeds configured maximum of {MAX_PANELS}.")
    unknown = [x for x in requested if x not in PANEL_FAMILIES]
    if unknown:
        raise ScientificVisualizationExperienceError(f"unknown panel families: {unknown}")
    spans = {
        "primary-figure": "12", "empirical-distribution": "4", "residual-diagnostics": "4",
        "sensitivity-influence": "4", "data-provenance": "6", "model-architecture": "6",
        "diagnostics-matrix": "4", "assumptions-evidence": "4", "multivariate-surface": "6",
        "spatial-temporal": "6", "renderer-capabilities": "4", "linked-objects": "4",
    }
    panels = [{"panel_family": x, "grid_span": spans[x], "scientific_values_must_be_bound": x not in {"renderer-capabilities", "model-architecture", "data-provenance", "linked-objects"}} for x in requested]
    out = {
        "layout": "scientific-analysis-canvas",
        "grid_columns": 12,
        "panels": panels,
        "panel_count": len(panels),
        "linked_selection": True,
        "empty_scientific_panels_show_missing_state": True,
        "fabricate_missing_scientific_values": False,
    }
    out["composition_hash"] = _hash(out)
    return {"ok": True, "version": VERSION, "workspace": out}


def primary_figure_plan(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "plan": {"figure_ref": payload.get("figure_ref"), "role": "primary", "preserve_renderer": True, "preserve_axes": True, "preserve_uncertainty_semantics": True, "presentation_only_changes": True}}


def analytical_panels_plan(payload: dict[str, Any]):
    bindings = copy.deepcopy(payload.get("bindings") or {})
    return {"ok": True, "version": VERSION, "panels": {
        "empirical_distribution": {"source": bindings.get("response_values_ref"), "state": "linked" if bindings.get("response_values_ref") else "not-linked"},
        "residual_diagnostics": {"source": bindings.get("residuals_ref"), "state": "linked" if bindings.get("residuals_ref") else "not-linked"},
        "sensitivity_influence": {"source": bindings.get("sensitivity_ref"), "state": "linked" if bindings.get("sensitivity_ref") else "not-linked"},
        "diagnostics_matrix": {"source": bindings.get("diagnostic_refs") or [], "state": "linked" if bindings.get("diagnostic_refs") else "not-linked"},
    }, "fabricate_missing_scientific_values": False}


def model_architecture_graph(payload: dict[str, Any]):
    nodes = _list(payload.get("nodes"), "nodes", 200) or [
        {"id": "dataset", "label": "Dataset", "kind": "data"},
        {"id": "transform", "label": "Transform", "kind": "processing"},
        {"id": "model", "label": "Model / method", "kind": "model"},
        {"id": "inference", "label": "Inference / solver", "kind": "compute"},
        {"id": "output", "label": "Predictions + uncertainty", "kind": "output"},
        {"id": "figure", "label": "Scientific figure", "kind": "visual"},
    ]
    edges = _list(payload.get("edges"), "edges", 400) or [
        {"from": "dataset", "to": "transform"}, {"from": "transform", "to": "model"},
        {"from": "model", "to": "inference"}, {"from": "inference", "to": "output"},
        {"from": "output", "to": "figure"},
    ]
    graph = {"nodes": copy.deepcopy(nodes), "edges": copy.deepcopy(edges), "declarative_not_executed": True, "automatic_model_inference": False}
    graph["graph_hash"] = _hash(graph)
    return {"ok": True, "version": VERSION, "graph": graph}


def provenance_pipeline(payload: dict[str, Any]):
    stages = _list(payload.get("stages"), "stages", 200) or ["source", "dataset", "transform", "binding", "renderer", "figure"]
    rows = [{"order": i + 1, "stage": str(stage), "source_ref": None} if not isinstance(stage, dict) else {"order": i + 1, **copy.deepcopy(stage)} for i, stage in enumerate(stages)]
    return {"ok": True, "version": VERSION, "pipeline": rows, "lineage_preserved": True, "automatic_provenance_inference": False}


def linked_view_plan(payload: dict[str, Any]):
    channels = _refs(payload.get("channels"), "channels") or ["selection", "brush", "cursor", "parameter", "time-window"]
    return {"ok": True, "version": VERSION, "channels": channels, "source_view_refs": _refs(payload.get("source_view_refs"), "source_view_refs"), "target_view_refs": _refs(payload.get("target_view_refs"), "target_view_refs"), "declared_domain_sync_only": True, "automatic_join_inference": False}


def evidence_assumption_panel(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "panel": {"assumption_refs": _refs(payload.get("assumption_refs"), "assumption_refs"), "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"), "diagnostic_refs": _refs(payload.get("diagnostic_refs"), "diagnostic_refs"), "evidence_weight_not_inferred": True, "assumption_state_not_inferred": True}}


def renderer_stack_plan(payload: dict[str, Any]):
    preferred = str(payload.get("preferred_renderer") or "auto")
    return {"ok": True, "version": VERSION, "stack": ["SVG2D", "Canvas2D", "WebGL2", "WebGPU"], "preferred_renderer": preferred, "renderer_negotiation_explicit": True, "scientific_semantics_renderer_independent": True}


def presentation_profile(payload: dict[str, Any]):
    profile = str(payload.get("profile") or "research").lower()
    if profile not in PRESENTATION_PROFILES:
        raise ScientificVisualizationExperienceError(f"profile must be one of {sorted(PRESENTATION_PROFILES)}.")
    settings = {
        "research": {"density": "high", "provenance": "visible", "diagnostics": "visible"},
        "publication": {"density": "medium", "provenance": "caption", "diagnostics": "supporting"},
        "diagnostics": {"density": "high", "provenance": "visible", "diagnostics": "prominent"},
        "model-internals": {"density": "high", "provenance": "visible", "architecture": "prominent"},
        "presentation": {"density": "low", "provenance": "footer", "diagnostics": "summary"},
    }[profile]
    return {"ok": True, "version": VERSION, "profile": profile, "settings": settings, "presentation_only": True}


def responsive_layout_plan(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "breakpoints": [
        {"min_width": 1280, "columns": 12, "control_rail": "sticky"},
        {"min_width": 900, "columns": 8, "control_rail": "sticky"},
        {"min_width": 0, "columns": 1, "control_rail": "stacked"},
    ], "panel_order_semantics_preserved": True}


def interaction_contract(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "interaction": {"cross_highlight": True, "linked_cursor": True, "linked_brush": True, "object_drill_down": True, "full_screen": True, "presentation_mutation_only": True, "automatic_data_mutation": False}}


def accessibility_audit(payload: dict[str, Any]):
    issues = []
    if payload.get("color_only_encoding") is True:
        issues.append("color-only-encoding")
    if payload.get("missing_accessible_table") is True:
        issues.append("missing-accessible-table")
    return {"ok": True, "version": VERSION, "issues": issues, "issue_count": len(issues), "audit_is_not_certification": True}


def quality_audit(payload: dict[str, Any]):
    checks = {
        "figure_ref_present": bool(payload.get("figure_ref")),
        "source_ref_present": bool(payload.get("source_ref")),
        "method_ref_present": bool(payload.get("method_ref")),
        "units_declared": bool(payload.get("units_declared")),
        "provenance_ref_present": bool(payload.get("provenance_ref")),
    }
    return {"ok": True, "version": VERSION, "checks": checks, "complete_check_count": sum(checks.values()), "quality_score": None, "automatic_publication_readiness_certification": False}


def visualization_plan(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "figure_ref": payload.get("figure_ref"), "panel_families": _refs(payload.get("panel_families"), "panel_families") or sorted(PANEL_FAMILIES), "reuse_existing_scientific_renderers": True, "presentation_layer_does_not_change_scientific_record": True}


def project_binding(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "project_ref": payload.get("project_ref"), "experience_ref": payload.get("experience_ref"), "reference_first": True, "automatic_project_mutation": False}


def session_binding(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "session_ref": payload.get("session_ref"), "experience_ref": payload.get("experience_ref"), "reference_first": True, "automatic_session_mutation": False}


def handoff_plan(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "target_product": payload.get("target_product"), "object_refs": _refs(payload.get("object_refs"), "object_refs"), "reference_first": True, "automatic_handoff": False}


def export_plan(payload: dict[str, Any]):
    formats = _refs(payload.get("formats"), "formats") or ["svg", "png", "pdf", "json", "csv", "accessible-table"]
    return {"ok": True, "version": VERSION, "formats": formats, "preserve_provenance": True, "preserve_accessibility": True, "automatic_export": False}


def provenance_aggregate(payload: dict[str, Any]):
    refs = _refs(payload.get("provenance_refs"), "provenance_refs")
    return {"ok": True, "version": VERSION, "provenance_refs": refs, "provenance_count": len(refs), "aggregate_hash": _hash(refs), "automatic_source_resolution": False}


def build_snapshot(payload: dict[str, Any]):
    body = copy.deepcopy(payload)
    body["version"] = VERSION
    body["schema"] = SNAPSHOT_SCHEMA
    body["presentation_changes_only"] = True
    body["snapshot_hash"] = _hash(body)
    return {"ok": True, "version": VERSION, "snapshot": body}


def revision_plan(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "base_snapshot_ref": payload.get("base_snapshot_ref"), "changes": copy.deepcopy(payload.get("changes") or []), "scientific_semantic_changes_require_separate_scientific_revision": True, "automatic_revision_application": False}


def core_visual_object_plan(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "core_object_type": "visual-research-object", "figure_refs": _refs(payload.get("figure_refs"), "figure_refs"), "scene_refs": _refs(payload.get("scene_refs"), "scene_refs"), "dashboard_refs": _refs(payload.get("dashboard_refs"), "dashboard_refs"), "reference_first": True, "core_owns_semantic_visual_object": True, "lab_owns_scientific_rendering": True, "automatic_core_submission": False}


def readiness_report(payload: dict[str, Any]):
    required = ["figure_ref", "source_ref", "method_ref"]
    missing = [x for x in required if not payload.get(x)]
    return {"ok": True, "version": VERSION, "missing": missing, "ready_for_visual_review": not missing, "scientific_validity_certified": False}


def status_report(payload: dict[str, Any]):
    return {"ok": True, "version": VERSION, "status": "visual-experience-configured", "view_mode": payload.get("view_mode") or "analysis", "figure_ref": payload.get("figure_ref"), "scientific_validity_certified": False}


def interpretation_boundaries_report(payload: dict[str, Any] | None = None):
    return {
        "ok": True, "version": VERSION,
        "fabricate_missing_scientific_values": False,
        "automatic_scientific_interpretation": False,
        "automatic_evidence_promotion": False,
        "automatic_model_selection": False,
        "automatic_causal_inference": False,
        "automatic_scientific_validity_certification": False,
        "automatic_core_submission": False,
        "determine_truth": False,
    }
