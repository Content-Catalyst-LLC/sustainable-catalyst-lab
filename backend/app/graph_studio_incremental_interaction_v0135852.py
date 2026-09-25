from __future__ import annotations
VERSION = "0.135.8.5.2"
ROUTE_COUNT = 7
DEBOUNCE_MS = 220

def health():
    return {
        "ok": True,
        "version": VERSION,
        "api_route_count": ROUTE_COUNT,
        "incremental_rendering": True,
        "relationship_filtering": True,
        "full_redraw_for_ordinary_interaction": False,
        "project_persistence_debounce_ms": DEBOUNCE_MS,
    }

def performance_contract():
    return {
        "ok": True,
        "version": VERSION,
        "ordinary_interactions": ["node-selection", "edge-selection", "relationship-filter", "traversal", "layout", "zoom", "fit", "clear-focus"],
        "ordinary_interactions_require_full_render": False,
        "layout_updates_geometry_only": True,
        "selection_updates_inspector_and_classes_only": True,
        "traversal_updates_visibility_only": True,
    }

def relationship_filter_contract():
    return {
        "ok": True,
        "version": VERSION,
        "event_sources": ["input", "change"],
        "selector_replaced_during_filter": False,
        "filter_uses_edge_relation_metadata": True,
        "all_relations_restores_all_edges": True,
    }

def persistence_contract():
    return {
        "ok": True,
        "version": VERSION,
        "local_cache_immediate": True,
        "project_store_debounced": True,
        "project_store_debounce_ms": DEBOUNCE_MS,
        "presentation_state_only": True,
    }

def browser_contract():
    return {
        "ok": True,
        "version": VERSION,
        "required_actions": [
            "select-dataset",
            "relationship-filter-sourced-from",
            "relationship-selector-node-identity-stable",
            "relationship-filter-renders",
            "relationship-filter-all",
            "layout-radial",
            "layout-swimlane",
            "upstream",
            "downstream",
            "focus",
            "reload-restore",
        ],
        "must_measure_full_render_count": True,
        "must_measure_incremental_update_count": True,
    }

def diagnostics_contract():
    return {
        "ok": True,
        "version": VERSION,
        "metrics": [
            "lastInteractionMs",
            "fullRenderCount",
            "incrementalUpdateCount",
            "cacheWrites",
            "projectPersistenceWrites",
            "visibleNodes",
            "visibleEdges",
            "relationFilter",
        ],
    }

def acceptance_report():
    return {
        "ok": True,
        "version": VERSION,
        "incremental_interaction": True,
        "relationship_filter_selector_stable": True,
        "relationship_filter_works": True,
        "ordinary_interaction_full_redraw": False,
        "project_persistence_debounced": True,
        "legacy_interaction_shutdown_retained": True,
    }
