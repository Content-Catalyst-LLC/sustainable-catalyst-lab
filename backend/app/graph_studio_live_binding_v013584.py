from __future__ import annotations

VERSION = "0.135.8.4"
ROUTE_COUNT = 12
OBJECT_TYPES = (
    "source", "dataset", "transform", "binding", "method", "execution",
    "uncertainty", "renderer", "figure", "evidence", "core-reference",
)
RELATION_TYPES = (
    "sourced-from", "transformed-by", "binds", "conditions", "maps", "executes",
    "quantifies", "visualizes", "renders", "supports", "registered-as",
)
EXPLORATION_MODES = ("all", "upstream", "downstream", "focus")
PERSISTED_FIELDS = ("project_id", "figure_id", "renderer_mode", "provenance_layout", "selected_node", "exploration_mode", "relation_filter")


def health():
    return {
        "ok": True,
        "version": VERSION,
        "api_route_count": ROUTE_COUNT,
        "live_project_binding": True,
        "project_state_persistence": True,
        "advanced_provenance_exploration": True,
        "presentation_state_mutates_science": False,
    }


def binding_contract():
    return {
        "ok": True,
        "version": VERSION,
        "binding_priority": ["persisted-project-figure", "latest-project-figure", "active-graph", "illustrative-bootstrap"],
        "project_collections": ["visualizations", "reportFigures"],
        "missing_binding_is_inferred": False,
        "automatic_figure_creation": False,
    }


def persistence_contract():
    return {
        "ok": True,
        "version": VERSION,
        "scope": "presentation-binding-state",
        "persisted_fields": list(PERSISTED_FIELDS),
        "scientific_rows_persisted_by_binding_layer": False,
        "scientific_claims_persisted_by_binding_layer": False,
        "project_scoped": True,
    }


def provenance_contract():
    return {
        "ok": True,
        "version": VERSION,
        "object_types": list(OBJECT_TYPES),
        "relation_types": list(RELATION_TYPES),
        "exploration_modes": list(EXPLORATION_MODES),
        "layouts": ["layered", "radial", "swimlane"],
        "structural_path_is_causal_path": False,
        "missing_edges_are_inferred": False,
    }


def acceptance_report():
    return {
        "ok": True,
        "version": VERSION,
        "renderer_31_hosts": 1,
        "primary_viewports": 1,
        "live_binding_bar": 1,
        "project_store_subscription": True,
        "binding_restored_after_reload": True,
        "provenance_layout_persisted": True,
        "provenance_focus_persisted": True,
        "legacy_primary_owners": 0,
    }


def compatibility():
    return {
        "ok": True,
        "version": VERSION,
        "bootstrap_0135831_retained": True,
        "recovery_013583_retained": True,
        "renderer_013582_retained_underneath": True,
        "platform_core_minimum": "3.0.0",
    }


def binding_plan(payload: dict):
    project_id = str(payload.get("project_id") or "").strip() or None
    figure_id = str(payload.get("figure_id") or "").strip() or None
    available = payload.get("available_figure_ids") or []
    if not isinstance(available, list):
        available = []
    resolved = figure_id if figure_id and figure_id in available else (available[0] if available else None)
    return {
        "ok": True,
        "version": VERSION,
        "project_id": project_id,
        "requested_figure_id": figure_id,
        "resolved_figure_id": resolved,
        "resolution": "requested" if resolved and resolved == figure_id else ("latest-declared" if resolved else "unbound"),
        "invented_figure_id": False,
    }


def restore_plan(payload: dict):
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    project_id = str(payload.get("project_id") or "").strip() or None
    same_project = bool(project_id and state.get("project_id") == project_id)
    return {
        "ok": True,
        "version": VERSION,
        "same_project": same_project,
        "restore_figure_id": state.get("figure_id") if same_project else None,
        "restore_renderer_mode": state.get("renderer_mode") if same_project else None,
        "restore_provenance_layout": state.get("provenance_layout") if same_project else None,
        "restore_selected_node": state.get("selected_node") if same_project else None,
        "cross_project_binding_reused": False,
    }


def provenance_plan(payload: dict):
    selected = str(payload.get("selected_node") or "").strip() or None
    mode = str(payload.get("mode") or "all").strip().lower()
    if mode not in EXPLORATION_MODES:
        mode = "all"
    relation = str(payload.get("relation_filter") or "all").strip() or "all"
    return {
        "ok": True,
        "version": VERSION,
        "selected_node": selected if selected in OBJECT_TYPES else None,
        "mode": mode,
        "relation_filter": relation if relation == "all" or relation in RELATION_TYPES else "all",
        "inferred_relationships": False,
        "causal_interpretation": False,
    }


def selection_plan(payload: dict):
    node_id = str(payload.get("node_id") or "").strip()
    return {
        "ok": True,
        "version": VERSION,
        "node_id": node_id if node_id in OBJECT_TYPES else None,
        "selection_is_presentation_state": True,
        "selection_changes_evidence_weight": False,
        "selection_changes_claim_status": False,
    }


def object_types():
    return {"ok": True, "version": VERSION, "object_types": list(OBJECT_TYPES)}


def relation_types():
    return {"ok": True, "version": VERSION, "relation_types": list(RELATION_TYPES)}


def exploration_modes():
    return {"ok": True, "version": VERSION, "exploration_modes": list(EXPLORATION_MODES)}
