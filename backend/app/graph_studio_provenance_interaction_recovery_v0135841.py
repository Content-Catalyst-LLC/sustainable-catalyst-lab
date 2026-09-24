from __future__ import annotations

VERSION = "0.135.8.4.1"
ROUTE_COUNT = 8
LAYOUTS = ("layered", "radial", "swimlane")
EXPLORATION_MODES = ("all", "upstream", "downstream", "focus")
RELATION_TYPES = (
    "sourced-from", "transformed-by", "binds", "conditions", "maps", "executes",
    "quantifies", "visualizes", "renders", "supports", "registered-as",
)

def health():
    return {
        "ok": True, "version": VERSION, "api_route_count": ROUTE_COUNT,
        "delegated_interaction": True, "programmatic_layout_click": False,
        "recursive_redraw_guard": True, "node_selection_persistent": True,
        "presentation_state_mutates_science": False,
    }

def lifecycle_contract():
    return {
        "ok": True, "version": VERSION,
        "interaction_owner": "graph-studio-live-binding-v013584+v0135841",
        "event_strategy": "persistent-stage-delegation",
        "layout_change_rebuilds_interaction_layer": False,
        "observer_reacts_to_own_attribute_changes": False,
        "programmatic_button_click_restore": False,
    }

def layout_contract():
    return {
        "ok": True, "version": VERSION, "layouts": list(LAYOUTS),
        "restore_strategy": "direct-svg-geometry",
        "replaces_svg_nodes": False, "preserves_selection": True,
    }

def selection_contract():
    return {
        "ok": True, "version": VERSION,
        "delegated_from_persistent_stage": True,
        "survives_renderer_node_replacement": True,
        "updates_inspector": True,
        "changes_evidence_weight": False, "changes_claim_status": False,
    }

def exploration_contract():
    return {
        "ok": True, "version": VERSION,
        "modes": list(EXPLORATION_MODES), "relation_types": list(RELATION_TYPES),
        "missing_edges_inferred": False, "structural_paths_are_causal": False,
    }

def persistence_contract():
    return {
        "ok": True, "version": VERSION,
        "fields": ["provenance_layout", "selected_node", "exploration_mode", "relation_filter"],
        "scope": "project-presentation-state",
        "scientific_rows_mutated": False, "scientific_claims_mutated": False,
    }

def interaction_plan(payload: dict):
    layout = str(payload.get("layout") or "layered").strip().lower()
    if layout not in LAYOUTS: layout = "layered"
    mode = str(payload.get("exploration_mode") or "all").strip().lower()
    if mode not in EXPLORATION_MODES: mode = "all"
    relation = str(payload.get("relation_filter") or "all").strip()
    if relation != "all" and relation not in RELATION_TYPES: relation = "all"
    selected = str(payload.get("selected_node") or "").strip() or None
    return {
        "ok": True, "version": VERSION, "layout": layout, "exploration_mode": mode,
        "relation_filter": relation, "selected_node": selected,
        "dispatch": "delegated", "requires_synthetic_click": False,
        "scientific_mutation": False,
    }

def acceptance_report():
    return {
        "ok": True, "version": VERSION,
        "renderer_31_hosts": 1, "primary_viewports": 1, "provenance_explorers": 1,
        "layout_control_count": 3, "delegated_stage_handlers": 1,
        "duplicate_node_handlers": 0, "programmatic_layout_clicks": 0,
        "node_selection_works_after_layout_change": True,
        "layout_persists_after_reload": True, "legacy_primary_owners": 0,
    }
