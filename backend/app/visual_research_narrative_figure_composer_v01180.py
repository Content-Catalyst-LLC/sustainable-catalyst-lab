from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

VERSION = "0.118.0"
ENGINE_VERSION = "3.4.0"
SCHEMA = "sc-lab-visual-research-narrative-figure-composer/0.118.0"
NARRATIVE_SCHEMA = "sc-lab-visual-research-narrative/0.118.0"
FIGURE_SCHEMA = "sc-lab-narrative-figure-reference/0.118.0"
MAX_SECTIONS = 64
MAX_FIGURES = 256
MAX_BLOCKS = 1024
MAX_REFS = 5000
MAX_ANNOTATIONS = 1000

SECTION_TYPES = {
    "abstract", "introduction", "methods", "results", "discussion", "conclusion",
    "limitations", "figure-story", "evidence", "appendix", "supplement",
}
BLOCK_TYPES = {
    "paragraph", "figure", "figure-plate", "dashboard", "scene", "finding", "method",
    "evidence", "reference-panel", "callout", "equation", "table", "limitations",
}
FIGURE_KINDS = {
    "statistical-figure", "scientific-figure", "dashboard", "small-multiples", "scientific-3d-4d-scene",
    "map", "table", "equation", "image", "diagram", "model-view", "uncertainty-view",
}
NARRATIVE_FORMATS = {"journal-article", "research-report", "technical-memo", "methods-note", "slide-narrative", "web-story", "supplement"}
EXPORT_FORMATS = {"html", "pdf", "svg", "png", "tiff", "json", "research-package"}


class VisualResearchNarrativeError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 2400, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise VisualResearchNarrativeError(f"{label} is required.")
    if len(text) > maximum:
        raise VisualResearchNarrativeError(f"{label} exceeds {maximum} characters.")
    return text


def _list(value: Any, label: str, maximum: int) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise VisualResearchNarrativeError(f"{label} must be an array.")
    if len(value) > maximum:
        raise VisualResearchNarrativeError(f"{label} exceeds {maximum} entries.", 413)
    return copy.deepcopy(value)


def _refs(value: Any, label: str = "refs", maximum: int = MAX_REFS) -> list[str]:
    refs: list[str] = []
    for raw in _list(value, label, maximum):
        ref = _text(raw, label[:-1] if label.endswith("s") else label, 1200, True)
        if ref not in refs:
            refs.append(ref)
    return refs


def _id(value: Any, fallback: str, label: str = "id") -> str:
    return _text(value or fallback, label, 180, True)


def normalize_figure_reference(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualResearchNarrativeError("figure reference must be an object.")
    figure_ref = _text(payload.get("figure_ref") or payload.get("figureRef"), "figure_ref", 1200, True)
    kind = _text(payload.get("figure_kind") or payload.get("figureKind") or "scientific-figure", "figure_kind", 80, True).lower()
    if kind not in FIGURE_KINDS:
        raise VisualResearchNarrativeError(f"unsupported figure_kind: {kind}.")
    caption = _text(payload.get("caption"), "caption", 8000, False)
    title = _text(payload.get("title") or f"Figure {index + 1}", "figure title", 500, True)
    out = {
        "schema": FIGURE_SCHEMA,
        "id": _id(payload.get("id") or payload.get("figure_id"), f"figure-{index+1}", "figure id"),
        "figure_ref": figure_ref,
        "figure_kind": kind,
        "title": title,
        "caption": caption or None,
        "short_caption": _text(payload.get("short_caption") or payload.get("shortCaption"), "short_caption", 1000, False) or None,
        "alt_text": _text(payload.get("alt_text") or payload.get("altText"), "alt_text", 5000, False) or None,
        "source_refs": _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs"),
        "method_refs": _refs(payload.get("method_refs") or payload.get("methodRefs"), "method_refs"),
        "finding_refs": _refs(payload.get("finding_refs") or payload.get("findingRefs"), "finding_refs"),
        "evidence_refs": _refs(payload.get("evidence_refs") or payload.get("evidenceRefs"), "evidence_refs"),
        "citation_refs": _refs(payload.get("citation_refs") or payload.get("citationRefs"), "citation_refs"),
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
        "immutable_underlying_figure": True,
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_block(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualResearchNarrativeError("narrative block must be an object.")
    kind = _text(payload.get("type") or "paragraph", "block type", 80, True).lower()
    if kind not in BLOCK_TYPES:
        raise VisualResearchNarrativeError(f"unsupported block type: {kind}.")
    out = {
        "id": _id(payload.get("id"), f"block-{index+1}", "block id"),
        "type": kind,
        "title": _text(payload.get("title"), "block title", 500, False) or None,
        "text": _text(payload.get("text"), "block text", 30000, False) or None,
        "figure_refs": _refs(payload.get("figure_refs") or payload.get("figureRefs"), "figure_refs"),
        "finding_refs": _refs(payload.get("finding_refs") or payload.get("findingRefs"), "finding_refs"),
        "method_refs": _refs(payload.get("method_refs") or payload.get("methodRefs"), "method_refs"),
        "evidence_refs": _refs(payload.get("evidence_refs") or payload.get("evidenceRefs"), "evidence_refs"),
        "citation_refs": _refs(payload.get("citation_refs") or payload.get("citationRefs"), "citation_refs"),
        "source_refs": _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs"),
        "spec": copy.deepcopy(payload.get("spec")) if isinstance(payload.get("spec"), dict) else None,
    }
    if kind == "paragraph" and not out["text"]:
        raise VisualResearchNarrativeError("paragraph blocks require text.")
    if kind in {"figure", "figure-plate", "dashboard", "scene"} and not out["figure_refs"]:
        raise VisualResearchNarrativeError(f"{kind} blocks require figure_refs.")
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_section(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualResearchNarrativeError("section must be an object.")
    kind = _text(payload.get("type") or "results", "section type", 80, True).lower()
    if kind not in SECTION_TYPES:
        raise VisualResearchNarrativeError(f"unsupported section type: {kind}.")
    blocks = [normalize_block(x, i) for i, x in enumerate(_list(payload.get("blocks"), "blocks", MAX_BLOCKS))]
    out = {
        "id": _id(payload.get("id"), f"section-{index+1}", "section id"),
        "type": kind,
        "title": _text(payload.get("title") or kind.replace("-", " ").title(), "section title", 500, True),
        "blocks": blocks,
        "source_refs": _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs"),
        "method_refs": _refs(payload.get("method_refs") or payload.get("methodRefs"), "method_refs"),
        "finding_refs": _refs(payload.get("finding_refs") or payload.get("findingRefs"), "finding_refs"),
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_narrative(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualResearchNarrativeError("narrative request must be an object.")
    fmt = _text(payload.get("format") or "research-report", "format", 80, True).lower()
    if fmt not in NARRATIVE_FORMATS:
        raise VisualResearchNarrativeError(f"unsupported narrative format: {fmt}.")
    figures = [normalize_figure_reference(x, i) for i, x in enumerate(_list(payload.get("figures"), "figures", MAX_FIGURES))]
    figure_ids = [x["id"] for x in figures]
    if len(figure_ids) != len(set(figure_ids)):
        raise VisualResearchNarrativeError("figure ids must be unique.")
    figure_refs = {x["figure_ref"] for x in figures}
    sections = [normalize_section(x, i) for i, x in enumerate(_list(payload.get("sections"), "sections", MAX_SECTIONS))]
    section_ids = [x["id"] for x in sections]
    if len(section_ids) != len(set(section_ids)):
        raise VisualResearchNarrativeError("section ids must be unique.")
    for section in sections:
        for block in section["blocks"]:
            unknown = [ref for ref in block["figure_refs"] if ref not in figure_refs]
            if unknown:
                raise VisualResearchNarrativeError(f"block references unregistered figures: {', '.join(unknown)}")
    narrative = {
        "schema": NARRATIVE_SCHEMA,
        "version": VERSION,
        "id": _id(payload.get("id"), "research-narrative", "narrative id"),
        "title": _text(payload.get("title") or "Research narrative", "title", 800, True),
        "subtitle": _text(payload.get("subtitle"), "subtitle", 1000, False) or None,
        "format": fmt,
        "audience": _text(payload.get("audience") or "research", "audience", 120, True),
        "publication_profile": _text(payload.get("publication_profile") or payload.get("publicationProfile") or "journal", "publication_profile", 80, True),
        "figures": figures,
        "sections": sections,
        "source_refs": _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs"),
        "method_refs": _refs(payload.get("method_refs") or payload.get("methodRefs"), "method_refs"),
        "finding_refs": _refs(payload.get("finding_refs") or payload.get("findingRefs"), "finding_refs"),
        "evidence_refs": _refs(payload.get("evidence_refs") or payload.get("evidenceRefs"), "evidence_refs"),
        "citation_refs": _refs(payload.get("citation_refs") or payload.get("citationRefs"), "citation_refs"),
        "metadata": copy.deepcopy(payload.get("metadata") or {}),
    }
    narrative["narrative_hash"] = _hash(narrative)
    return {
        "ok": True,
        "narrative": narrative,
        "automatic_scientific_conclusion_generation": False,
        "automatic_figure_mutation": False,
        "automatic_caption_inference": False,
    }


def build_figure_plate(payload: dict[str, Any]) -> dict[str, Any]:
    raw = _list(payload.get("figures"), "figures", 12)
    if not raw:
        raise VisualResearchNarrativeError("figure plate requires at least one figure.")
    figures = [normalize_figure_reference(x, i) for i, x in enumerate(raw)]
    labels = []
    for i, fig in enumerate(figures):
        label = chr(ord("A") + i) if i < 26 else str(i + 1)
        labels.append({"panel_label": label, "figure_ref": fig["figure_ref"], "title": fig["title"]})
    columns = int(payload.get("columns") or min(2, len(figures)))
    columns = max(1, min(4, columns))
    plate = {
        "schema": "sc-lab-publication-figure-plate/0.118.0",
        "id": _id(payload.get("id"), "figure-plate", "plate id"),
        "title": _text(payload.get("title") or "Figure plate", "plate title", 500, True),
        "figures": figures,
        "panel_labels": labels,
        "layout": {"columns": columns, "rows": (len(figures) + columns - 1) // columns, "reading_order": "row-major"},
        "caption": _text(payload.get("caption"), "caption", 8000, False) or None,
    }
    plate["plate_hash"] = _hash(plate)
    return {"ok": True, "plate": plate, "automatic_figure_reordering": False, "automatic_caption_inference": False}


def build_caption_package(payload: dict[str, Any]) -> dict[str, Any]:
    figure = normalize_figure_reference(payload.get("figure") or payload, 0)
    caption = _text(payload.get("caption") or figure.get("caption"), "caption", 8000, True)
    notes = _text(payload.get("notes"), "notes", 4000, False) or None
    return {
        "ok": True,
        "caption_package": {
            "figure_ref": figure["figure_ref"],
            "title": figure["title"],
            "caption": caption,
            "notes": notes,
            "source_refs": figure["source_refs"],
            "method_refs": figure["method_refs"],
            "finding_refs": figure["finding_refs"],
            "evidence_refs": figure["evidence_refs"],
            "citation_refs": figure["citation_refs"],
        },
        "automatic_caption_inference": False,
        "automatic_result_interpretation": False,
    }


def build_annotation_layer(payload: dict[str, Any]) -> dict[str, Any]:
    figure_ref = _text(payload.get("figure_ref") or payload.get("figureRef"), "figure_ref", 1200, True)
    rows = _list(payload.get("annotations"), "annotations", MAX_ANNOTATIONS)
    annotations = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VisualResearchNarrativeError("annotation must be an object.")
        kind = _text(row.get("type") or "note", "annotation type", 80, True)
        text = _text(row.get("text"), "annotation text", 2000, True)
        annotations.append({
            "id": _id(row.get("id"), f"annotation-{i+1}", "annotation id"),
            "type": kind,
            "text": text,
            "target": copy.deepcopy(row.get("target") or {}),
            "source_refs": _refs(row.get("source_refs") or row.get("sourceRefs"), "source_refs"),
            "evidence_refs": _refs(row.get("evidence_refs") or row.get("evidenceRefs"), "evidence_refs"),
            "declared_by": _text(row.get("declared_by") or row.get("declaredBy"), "declared_by", 300, False) or None,
        })
    layer = {"schema": "sc-lab-narrative-annotation-layer/0.118.0", "figure_ref": figure_ref, "annotations": annotations}
    layer["layer_hash"] = _hash(layer)
    return {"ok": True, "annotation_layer": layer, "automatic_annotation_generation": False, "automatic_evidence_weighting": False}


def build_research_links(payload: dict[str, Any]) -> dict[str, Any]:
    target_ref = _text(payload.get("target_ref") or payload.get("targetRef"), "target_ref", 1200, True)
    links = {
        "target_ref": target_ref,
        "method_refs": _refs(payload.get("method_refs") or payload.get("methodRefs"), "method_refs"),
        "finding_refs": _refs(payload.get("finding_refs") or payload.get("findingRefs"), "finding_refs"),
        "evidence_refs": _refs(payload.get("evidence_refs") or payload.get("evidenceRefs"), "evidence_refs"),
        "citation_refs": _refs(payload.get("citation_refs") or payload.get("citationRefs"), "citation_refs"),
        "source_refs": _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs"),
    }
    links["link_hash"] = _hash(links)
    return {"ok": True, "links": links, "automatic_relationship_inference": False, "automatic_evidence_weighting": False}


def build_reference_panel(payload: dict[str, Any]) -> dict[str, Any]:
    citations = _refs(payload.get("citation_refs") or payload.get("citationRefs"), "citation_refs")
    sources = _refs(payload.get("source_refs") or payload.get("sourceRefs"), "source_refs")
    return {"ok": True, "reference_panel": {"citation_refs": citations, "source_refs": sources, "style": _text(payload.get("style") or "declared", "reference style", 80, True)}, "automatic_citation_resolution": False}


def trace_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    buckets = {"source_refs": set(narrative["source_refs"]), "method_refs": set(narrative["method_refs"]), "finding_refs": set(narrative["finding_refs"]), "evidence_refs": set(narrative["evidence_refs"]), "citation_refs": set(narrative["citation_refs"])}
    for fig in narrative["figures"]:
        for key in buckets:
            buckets[key].update(fig.get(key, []))
    for section in narrative["sections"]:
        for key in ("source_refs", "method_refs", "finding_refs"):
            buckets[key].update(section.get(key, []))
        for block in section["blocks"]:
            for key in buckets:
                buckets[key].update(block.get(key, []))
    trace = {key: sorted(values) for key, values in buckets.items()}
    trace["narrative_ref"] = f"lab:narrative:{narrative['id']}"
    trace["narrative_hash"] = narrative["narrative_hash"]
    trace["trace_hash"] = _hash(trace)
    return {"ok": True, "provenance_trace": trace, "automatic_source_resolution": False}


def build_layout_plan(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    mode = _text(payload.get("layout_mode") or payload.get("layoutMode") or "flow", "layout_mode", 80, True).lower()
    if mode not in {"flow", "journal", "report", "poster", "slide-sequence", "web-scroll"}:
        raise VisualResearchNarrativeError("unsupported layout_mode.")
    figure_count = len(narrative["figures"])
    section_count = len(narrative["sections"])
    plan = {
        "schema": "sc-lab-narrative-layout-plan/0.118.0",
        "narrative_ref": f"lab:narrative:{narrative['id']}",
        "layout_mode": mode,
        "section_order": [s["id"] for s in narrative["sections"]],
        "figure_order": [f["figure_ref"] for f in narrative["figures"]],
        "section_count": section_count,
        "figure_count": figure_count,
        "responsive": True,
        "publication_profile": narrative["publication_profile"],
    }
    plan["layout_hash"] = _hash(plan)
    return {"ok": True, "layout_plan": plan, "automatic_scientific_reordering": False, "automatic_figure_reordering": False}


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    formats = [str(x).strip().lower() for x in _list(payload.get("formats") or ["html", "pdf", "json"], "formats", 12)]
    if not formats or any(x not in EXPORT_FORMATS for x in formats):
        raise VisualResearchNarrativeError("unsupported export format.")
    plan = {
        "schema": "sc-lab-visual-research-narrative-export-plan/0.118.0",
        "narrative_ref": f"lab:narrative:{narrative['id']}",
        "narrative_hash": narrative["narrative_hash"],
        "formats": formats,
        "publication_profile": narrative["publication_profile"],
        "embed_provenance": bool(payload.get("embed_provenance", True)),
        "embed_accessibility_metadata": bool(payload.get("embed_accessibility_metadata", True)),
        "vector_first": any(x in {"pdf", "svg"} for x in formats),
    }
    plan["export_hash"] = _hash(plan)
    return {"ok": True, "export_plan": plan, "automatic_file_write": False, "automatic_publication": False}


def build_publication_package(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    provenance = trace_provenance({"narrative": narrative})["provenance_trace"]
    layout = build_layout_plan({"narrative": narrative, "layout_mode": payload.get("layout_mode") or "journal"})["layout_plan"]
    export = build_export_plan({"narrative": narrative, "formats": payload.get("formats") or ["pdf", "html", "json"]})["export_plan"]
    package = {
        "schema": "sc-lab-visual-research-publication-package/0.118.0",
        "package_ref": f"lab:publication-package:{narrative['id']}",
        "narrative": narrative,
        "provenance": provenance,
        "layout_plan": layout,
        "export_plan": export,
        "scientific_validity_certified": False,
        "publication_approved": False,
    }
    package["package_hash"] = _hash(package)
    return {"ok": True, "publication_package": package, "automatic_publication": False, "automatic_scientific_validity_certification": False}


def build_revision_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    parent_ref = _text(payload.get("parent_snapshot_ref") or payload.get("parentSnapshotRef"), "parent_snapshot_ref", 1200, False) or None
    snapshot = {
        "schema": "sc-lab-visual-research-narrative-snapshot/0.118.0",
        "narrative_ref": f"lab:narrative:{narrative['id']}",
        "narrative_hash": narrative["narrative_hash"],
        "parent_snapshot_ref": parent_ref,
        "figure_fingerprints": {f["figure_ref"]: f["fingerprint"] for f in narrative["figures"]},
        "section_fingerprints": {s["id"]: s["fingerprint"] for s in narrative["sections"]},
    }
    snapshot["snapshot_hash"] = _hash(snapshot)
    snapshot["snapshot_ref"] = f"lab:narrative-snapshot:{snapshot['snapshot_hash'][:24]}"
    return {"ok": True, "snapshot": snapshot, "automatic_persistence": False}


def build_core_visual_plan(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    session_id = _text(payload.get("session_id") or payload.get("sessionId"), "session_id", 240, True)
    source_refs = sorted(set(narrative["source_refs"] + [ref for fig in narrative["figures"] for ref in fig["source_refs"]]))
    return {
        "ok": True,
        "endpoint": "/v1/research/unified-runtime/visual-bindings",
        "request_body": {"data": {
            "session_id": session_id,
            "visual_ref": f"lab:narrative:{narrative['id']}",
            "visual_type": "visual-research-narrative",
            "source_refs": source_refs,
            "metadata": {
                "lab_release_version": VERSION,
                "narrative_hash": narrative["narrative_hash"],
                "format": narrative["format"],
                "figure_count": len(narrative["figures"]),
                "section_count": len(narrative["sections"]),
                "underlying_figures_remain_authoritative_in_lab": True,
            },
        }},
        "automatic_core_submission": False,
        "core_renders_narrative": False,
    }


def accessibility_audit(payload: dict[str, Any]) -> dict[str, Any]:
    narrative = normalize_narrative(payload.get("narrative") or payload)["narrative"]
    issues: list[dict[str, Any]] = []
    for fig in narrative["figures"]:
        if not fig.get("alt_text"):
            issues.append({"code": "missing-alt-text", "figure_ref": fig["figure_ref"]})
        if not fig.get("caption"):
            issues.append({"code": "missing-caption", "figure_ref": fig["figure_ref"]})
    if not narrative["sections"]:
        issues.append({"code": "missing-sections"})
    return {
        "ok": True,
        "accessible": not issues,
        "issues": issues,
        "figure_count": len(narrative["figures"]),
        "section_count": len(narrative["sections"]),
        "automatic_alt_text_inference": False,
        "automatic_caption_inference": False,
    }


def schema_info() -> dict[str, Any]:
    return {
        "ok": True, "schema": SCHEMA, "narrative_schema": NARRATIVE_SCHEMA, "figure_schema": FIGURE_SCHEMA,
        "version": VERSION, "engine_version": ENGINE_VERSION, "section_limit": MAX_SECTIONS,
        "figure_limit": MAX_FIGURES, "block_limit": MAX_BLOCKS, "api_route_count": 19,
    }


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "section_types": sorted(SECTION_TYPES),
        "block_types": sorted(BLOCK_TYPES),
        "figure_kinds": sorted(FIGURE_KINDS),
        "narrative_formats": sorted(NARRATIVE_FORMATS),
        "export_formats": sorted(EXPORT_FORMATS),
        "publication_design_system": "0.114.0",
        "statistical_graphics": "0.115.0",
        "interactive_dashboards": "0.116.0",
        "advanced_3d_4d": "0.117.0",
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "visual-research-narrative-figure-composer-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "features": {
            "reference_first_figure_registry": True,
            "figure_plates": True,
            "declared_captions": True,
            "evidence_aware_annotations": True,
            "methods_findings_evidence_links": True,
            "provenance_trace": True,
            "publication_layout_plans": True,
            "publication_package_plans": True,
            "revision_snapshots": True,
            "core_visual_bridge": True,
        },
        "boundaries": {
            "automatic_scientific_conclusion_generation": False,
            "automatic_figure_mutation": False,
            "automatic_caption_inference": False,
            "automatic_relationship_inference": False,
            "automatic_evidence_weighting": False,
            "automatic_publication": False,
            "automatic_core_submission": False,
            "scientific_validity_certified": False,
            "truth_determined": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "visual-research-narrative-figure-composer-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "section_type_count": len(SECTION_TYPES),
        "figure_kind_count": len(FIGURE_KINDS),
        "narrative_format_count": len(NARRATIVE_FORMATS),
        "automatic_core_submission": False,
        "scientific_validity_certified": False,
    }
