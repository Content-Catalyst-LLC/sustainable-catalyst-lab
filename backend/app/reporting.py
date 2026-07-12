from __future__ import annotations

import base64
import hashlib
import io
import json
import math
from html import escape
from typing import Any, Iterable

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPORT_SCHEMA = "sc-lab-report/1.0"
HANDOFF_SCHEMA = "sc-decision-studio-analysis-packet/2.0"
MAX_ANALYSES = 12
MAX_TABLE_ROWS = 80
MAX_TEXT = 12000


class ReportValidationError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _text(value: Any, limit: int = MAX_TEXT) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("\x00", "")[:limit]


def _sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _flatten(value: Any, prefix: str = "", depth: int = 0, rows: list[tuple[str, str]] | None = None) -> list[tuple[str, str]]:
    if rows is None:
        rows = []
    if len(rows) >= MAX_TABLE_ROWS:
        return rows
    if depth > 4:
        rows.append((prefix or "value", _text(value, 500)))
        return rows
    if isinstance(value, dict):
        for key, item in value.items():
            if len(rows) >= MAX_TABLE_ROWS:
                break
            path = f"{prefix}.{key}" if prefix else str(key)
            _flatten(item, path, depth + 1, rows)
    elif isinstance(value, list):
        if len(value) <= 12 and all(not isinstance(item, (dict, list)) for item in value):
            rows.append((prefix or "value", ", ".join(_text(item, 160) for item in value)))
        else:
            rows.append((prefix or "value", f"{len(value)} records"))
    else:
        rows.append((prefix or "value", _text(value, 800)))
    return rows


def validate_report(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ReportValidationError("A report JSON object is required.")
    title = _text(payload.get("title"), 240).strip()
    if not title:
        raise ReportValidationError("Report title is required.")
    analyses = payload.get("analyses")
    if analyses is None and isinstance(payload.get("analysis"), dict):
        analyses = [payload["analysis"]]
    if not isinstance(analyses, list) or not analyses:
        raise ReportValidationError("At least one analysis is required.")
    if len(analyses) > MAX_ANALYSES:
        raise ReportValidationError(f"A report can contain at most {MAX_ANALYSES} analyses.")
    for index, analysis in enumerate(analyses):
        if not isinstance(analysis, dict):
            raise ReportValidationError(f"Analysis {index + 1} must be an object.")
        if not _text(analysis.get("methodId"), 128):
            raise ReportValidationError(f"Analysis {index + 1} is missing methodId.")
        if not isinstance(analysis.get("inputs", {}), dict):
            raise ReportValidationError(f"Analysis {index + 1} inputs must be an object.")
    page_size = str(payload.get("pageSize", "LETTER")).upper()
    if page_size not in {"LETTER", "A4"}:
        raise ReportValidationError("pageSize must be LETTER or A4.")
    report_type = str(payload.get("reportType", "technical-report"))
    if report_type not in {"technical-report", "decision-brief", "evidence-packet", "executive-summary"}:
        raise ReportValidationError("Unsupported reportType.")
    normalized = dict(payload)
    normalized.update(
        {
            "schema": REPORT_SCHEMA,
            "schemaVersion": "1.0",
            "title": title,
            "subtitle": _text(payload.get("subtitle"), 600),
            "executiveSummary": _text(payload.get("executiveSummary"), 8000),
            "reportType": report_type,
            "pageSize": page_size,
            "analyses": analyses,
        }
    )
    normalized["audit"] = dict(normalized.get("audit") or {})
    normalized["audit"].update(
        {
            "reportFingerprint": fingerprint({k: v for k, v in normalized.items() if k != "audit"}),
            "analysisCount": len(analyses),
            "reportEngine": "reportlab-vector-pdf",
        }
    )
    return normalized


def validate_handoff(packet: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise ReportValidationError("A Decision Studio packet object is required.")
    packet_type = str(packet.get("packetType", ""))
    if packet_type not in {"scientific-analysis", "scientific-report"}:
        raise ReportValidationError("Unsupported Decision Studio packet type.")
    if not isinstance(packet.get("origin"), dict):
        raise ReportValidationError("Packet origin is required.")
    analyses = packet.get("analyses") or ([packet["analysis"]] if isinstance(packet.get("analysis"), dict) else [])
    if not analyses or len(analyses) > MAX_ANALYSES:
        raise ReportValidationError("Decision Studio packet must contain one to twelve analyses.")
    if len(_canonical(packet)) > 2_000_000:
        raise ReportValidationError("Decision Studio packet exceeds 2 MB.")
    return {
        "schema": "sc-lab-handoff-validation/1.0",
        "status": "VALIDATED",
        "packetType": packet_type,
        "analysisCount": len(analyses),
        "chartCount": len(packet.get("charts") or []),
        "sceneCount": len(packet.get("scenes") or []),
        "tableCount": len(packet.get("tables") or []),
        "packetFingerprint": fingerprint(packet),
    }


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("LabTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=colors.HexColor("#111820"), spaceAfter=10),
        "subtitle": ParagraphStyle("LabSubtitle", parent=base["Normal"], fontName="Helvetica", fontSize=11, leading=16, textColor=colors.HexColor("#4f5c66"), spaceAfter=20),
        "h1": ParagraphStyle("LabH1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#111820"), spaceBefore=12, spaceAfter=8),
        "h2": ParagraphStyle("LabH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=colors.HexColor("#8f1111"), spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("LabBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.2, textColor=colors.HexColor("#20292f"), spaceAfter=7),
        "small": ParagraphStyle("LabSmall", parent=base["BodyText"], fontName="Helvetica", fontSize=7.5, leading=10, textColor=colors.HexColor("#59636d"), spaceAfter=4),
        "mono": ParagraphStyle("LabMono", parent=base["Code"], fontName="Courier", fontSize=7.6, leading=10, textColor=colors.HexColor("#1f2930"), backColor=colors.HexColor("#f2f4f5"), borderPadding=6, spaceAfter=7),
        "center": ParagraphStyle("LabCenter", parent=base["Normal"], alignment=TA_CENTER, fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#59636d")),
    }


def _table(rows: Iterable[tuple[str, str]], styles: dict[str, ParagraphStyle], col_widths: tuple[float, float]) -> Table:
    data = [[Paragraph("<b>Field</b>", styles["small"]), Paragraph("<b>Value</b>", styles["small"])]]
    for key, value in list(rows)[:MAX_TABLE_ROWS]:
        data.append([Paragraph(escape(_text(key, 300)), styles["small"]), Paragraph(escape(_text(value, 1800)).replace("\n", "<br/>"), styles["small"])])
    table = Table(data, colWidths=list(col_widths), repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9edef")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111820")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c9d0d5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _chart(spec: dict[str, Any], width: float = 500, height: float = 235) -> Drawing | None:
    data = spec.get("data") if isinstance(spec, dict) else None
    if not isinstance(data, list) or len(data) < 2:
        return None
    x_key = str(spec.get("xKey") or "x")
    y_keys = list(spec.get("yKeys") or ["y"])[:4]
    chart_type = str(spec.get("type") or "line")
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 0, width, height, fillColor=colors.white, strokeColor=colors.HexColor("#cbd2d7"), strokeWidth=0.6))
    left, right, top, bottom = 48.0, 15.0, 18.0, 34.0
    plot_w, plot_h = width - left - right, height - top - bottom
    palette = [colors.HexColor("#c60000"), colors.HexColor("#1f5c78"), colors.HexColor("#5a6d2a"), colors.HexColor("#805a82")]

    def finite(value: Any) -> float | None:
        try:
            n = float(value)
        except (TypeError, ValueError):
            return None
        return n if math.isfinite(n) else None

    x_values = [finite(row.get(x_key)) if isinstance(row, dict) else None for row in data]
    numeric_x = all(value is not None for value in x_values)
    if not numeric_x:
        x_values = [float(i) for i in range(len(data))]
    all_y = [finite(row.get(key)) for row in data if isinstance(row, dict) for key in y_keys]
    y_values = [value for value in all_y if value is not None]
    if not y_values:
        return None
    x_min, x_max = min(x_values), max(x_values)
    raw_y_min, raw_y_max = min(y_values), max(y_values)
    if raw_y_min >= 0:
        y_min, y_max = 0.0, raw_y_max
    elif raw_y_max <= 0:
        y_min, y_max = raw_y_min, 0.0
    else:
        y_min, y_max = raw_y_min, raw_y_max
    if x_min == x_max:
        x_max = x_min + 1.0
    if y_min == y_max:
        y_max = y_min + 1.0
    y_span = y_max - y_min
    if raw_y_min < 0:
        y_min -= y_span * 0.06
    if raw_y_max > 0 and raw_y_min < 0:
        y_max += y_span * 0.06
    elif raw_y_min >= 0:
        y_max += y_span * 0.08

    def sx(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return bottom + (value - y_min) / (y_max - y_min) * plot_h

    for tick in range(5):
        frac = tick / 4
        y = bottom + plot_h * frac
        drawing.add(Line(left, y, left + plot_w, y, strokeColor=colors.HexColor("#e0e4e7"), strokeWidth=0.4))
        value = y_min + (y_max - y_min) * frac
        drawing.add(String(left - 5, y - 2.5, f"{value:.3g}", textAnchor="end", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor("#59636d")))
    drawing.add(Line(left, bottom, left + plot_w, bottom, strokeColor=colors.HexColor("#27323a"), strokeWidth=0.8))
    drawing.add(Line(left, bottom, left, bottom + plot_h, strokeColor=colors.HexColor("#27323a"), strokeWidth=0.8))

    if chart_type == "bar":
        key = y_keys[0]
        bar_w = max(4.0, plot_w / max(1, len(data)) * 0.62)
        zero = sy(0)
        for index, row in enumerate(data):
            value = finite(row.get(key)) if isinstance(row, dict) else None
            if value is None:
                continue
            center = left + (index + 0.5) / len(data) * plot_w
            y = sy(value)
            drawing.add(Rect(center - bar_w / 2, min(y, zero), bar_w, max(0.7, abs(y - zero)), fillColor=palette[0], strokeColor=None))
    else:
        for series_index, key in enumerate(y_keys):
            previous: tuple[float, float] | None = None
            color = palette[series_index % len(palette)]
            for index, row in enumerate(data):
                value = finite(row.get(key)) if isinstance(row, dict) else None
                if value is None:
                    previous = None
                    continue
                point = (sx(float(x_values[index])), sy(value))
                if chart_type != "scatter" and previous is not None:
                    drawing.add(Line(previous[0], previous[1], point[0], point[1], strokeColor=color, strokeWidth=1.5))
                drawing.add(Circle(point[0], point[1], 1.7 if len(data) < 100 else 1.0, fillColor=color, strokeColor=None))
                previous = point
    drawing.add(String(width / 2, 10, _text(spec.get("xLabel") or x_key, 80), textAnchor="middle", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#59636d")))
    return drawing


def _bullet_list(values: list[Any], styles: dict[str, ParagraphStyle]) -> list[Paragraph]:
    return [Paragraph(f"- {escape(_text(item, 1600))}", styles["body"]) for item in values]


def _page_decor(canvas: Any, doc: Any) -> None:
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setStrokeColor(colors.HexColor("#c60000"))
    canvas.setLineWidth(1.2)
    canvas.line(doc.leftMargin, height - 26, width - doc.rightMargin, height - 26)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#59636d"))
    canvas.drawString(doc.leftMargin, 20, "Sustainable Catalyst Lab - auditable scientific report")
    canvas.drawRightString(width - doc.rightMargin, 20, f"Page {doc.page}")
    canvas.restoreState()


def generate_report_pdf(payload: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    report = validate_report(payload)
    page_size = LETTER if report["pageSize"] == "LETTER" else A4
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.50 * inch,
        title=report["title"],
        author="Sustainable Catalyst Lab",
        subject=report["reportType"],
    )
    styles = _styles()
    usable = page_size[0] - doc.leftMargin - doc.rightMargin
    story: list[Any] = []
    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph(escape(report["title"]), styles["title"]))
    if report["subtitle"]:
        story.append(Paragraph(escape(report["subtitle"]), styles["subtitle"]))
    meta_rows = [
        ("Report type", report["reportType"].replace("-", " ").title()),
        ("Generated", _text(report.get("createdAt") or report.get("audit", {}).get("generatedAt") or "")),
        ("Project", _text((report.get("project") or {}).get("name") or "Unassigned")),
        ("Analyses", str(len(report["analyses"]))),
        ("Report fingerprint", report["audit"]["reportFingerprint"]),
    ]
    story.append(_table(meta_rows, styles, (1.35 * inch, usable - 1.35 * inch)))
    story.append(Spacer(1, 0.14 * inch))
    if report["executiveSummary"]:
        story.append(Paragraph("Executive summary", styles["h1"]))
        story.append(Paragraph(escape(report["executiveSummary"]).replace("\n", "<br/>"), styles["body"]))
    composition = report.get("composition")
    if isinstance(composition, dict) and isinstance(composition.get("sections"), list):
        enabled_sections = [section for section in composition["sections"] if isinstance(section, dict) and section.get("enabled", True)]
        if enabled_sections:
            story.append(Paragraph("Composed report sections", styles["h1"]))
            for section in enabled_sections:
                story.append(Paragraph(escape(_text(section.get("title") or section.get("type") or "Report section", 240)), styles["h2"]))
                narrative = _text(section.get("content"), 12000)
                if narrative:
                    story.append(Paragraph(escape(narrative).replace("\n", "<br/>"), styles["body"]))
    story.append(Paragraph("Report scope and audit boundary", styles["h1"]))
    story.append(Paragraph("This report preserves the supplied calculations, equations, assumptions, warnings, source references, validation states, and software metadata. Generated results remain subject to the stated method domain and do not replace professional review where required.", styles["body"]))
    story.append(PageBreak())

    for index, analysis in enumerate(report["analyses"], start=1):
        title = _text(analysis.get("title") or analysis.get("methodId") or f"Analysis {index}", 240)
        method_id = _text(analysis.get("methodId"), 128)
        method_version = _text(analysis.get("methodVersion"), 64)
        status = _text(analysis.get("status") or "unreviewed", 64)
        story.append(Paragraph(f"{index}. {escape(title)}", styles["h1"]))
        story.append(_table(
            [
                ("Method", method_id),
                ("Method version", method_version),
                ("Domain", _text(analysis.get("domain"), 120)),
                ("Validation state", status),
                ("Created", _text(analysis.get("createdAt"), 80)),
            ],
            styles,
            (1.35 * inch, usable - 1.35 * inch),
        ))
        if analysis.get("subtitle"):
            story.append(Paragraph(escape(_text(analysis["subtitle"], 1200)), styles["body"]))
        if analysis.get("equation"):
            story.append(Paragraph("Equation or method", styles["h2"]))
            story.append(Paragraph(escape(_text(analysis["equation"], 4000)), styles["mono"]))
        inputs = _flatten(analysis.get("inputs") or {})
        if inputs:
            story.append(Paragraph("Inputs", styles["h2"]))
            story.append(_table(inputs, styles, (1.9 * inch, usable - 1.9 * inch)))
        outputs = _flatten(analysis.get("outputs") or {})
        if outputs:
            story.append(Paragraph("Outputs", styles["h2"]))
            story.append(_table(outputs, styles, (2.1 * inch, usable - 2.1 * inch)))
        chart = _chart(analysis.get("chartSpec") or {}, width=min(usable, 500), height=235)
        if chart is not None:
            story.append(Paragraph("Figure", styles["h2"]))
            story.append(KeepTogether([chart, Paragraph(escape(_text((analysis.get("chartSpec") or {}).get("subtitle") or f"Generated from {method_id}.", 800)), styles["center"])]))
        assumptions = _sequence(analysis.get("assumptions"))
        if assumptions:
            story.append(Paragraph("Assumptions", styles["h2"]))
            story.extend(_bullet_list(assumptions, styles))
        warnings = _sequence(analysis.get("warnings"))
        if warnings:
            story.append(Paragraph("Warnings and limitations", styles["h2"]))
            story.extend(_bullet_list(warnings, styles))
        validation = analysis.get("validation")
        if validation:
            story.append(KeepTogether([
                Paragraph("Validation record", styles["h2"]),
                _table(_flatten(validation), styles, (2.0 * inch, usable - 2.0 * inch)),
            ]))
        sources = _sequence(analysis.get("sources"))
        if sources:
            story.append(Paragraph("Sources", styles["h2"]))
            story.extend(_bullet_list(sources, styles))
        runtime = analysis.get("runtime") or analysis.get("execution") or analysis.get("codeRuntime")
        if runtime:
            story.append(KeepTogether([
                Paragraph("Code and runtime metadata", styles["h2"]),
                _table(_flatten(runtime), styles, (2.0 * inch, usable - 2.0 * inch)),
            ]))
        if report.get("includeAudit", True) and analysis.get("audit"):
            story.append(KeepTogether([
                Paragraph("Analysis audit", styles["h2"]),
                _table(_flatten(analysis["audit"]), styles, (2.0 * inch, usable - 2.0 * inch)),
            ]))
        if index < len(report["analyses"]):
            story.append(PageBreak())

    doc.build(story, onFirstPage=_page_decor, onLaterPages=_page_decor)
    pdf = buffer.getvalue()
    page_count = max(1, pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages"))
    metadata = {
        "schema": "sc-lab-report-result/1.0",
        "status": "VALIDATED",
        "filename": f"{report['title'].lower().replace(' ', '-')[:80] or 'lab-report'}.pdf",
        "mimeType": "application/pdf",
        "byteLength": len(pdf),
        "pageCount": page_count,
        "reportFingerprint": report["audit"]["reportFingerprint"],
        "pdfFingerprint": hashlib.sha256(pdf).hexdigest(),
        "engine": "reportlab-vector-pdf",
    }
    return pdf, metadata


def report_pdf_response(payload: dict[str, Any]) -> dict[str, Any]:
    pdf, metadata = generate_report_pdf(payload)
    return {**metadata, "dataBase64": base64.b64encode(pdf).decode("ascii")}
