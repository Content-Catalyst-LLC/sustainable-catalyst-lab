from __future__ import annotations

from app.models import ReportRequest
from app.reporting import generate_report_pdf, validate_report


def sample_payload() -> dict:
    return {
        "reportType": "technical-report",
        "title": "Composer validation report",
        "subtitle": "Lab v0.9.5",
        "executiveSummary": "A bounded validation fixture.",
        "pageSize": "LETTER",
        "project": {"id": "project-1", "name": "Validation project", "schemaVersion": "0.9.5"},
        "analyses": [
            {
                "id": "analysis-1",
                "methodId": "validation.example",
                "methodVersion": "1.0.0",
                "title": "Validation example",
                "inputs": {"x": 2.0},
                "outputs": {"y": 4.0},
                "status": "validated",
            }
        ],
        "includeAudit": True,
        "composition": {
            "format": "sc-lab-report-composition/1.0",
            "applicationVersion": "0.9.5",
            "id": "composition-1",
            "templateId": "technical-report",
            "title": "Composer validation report",
            "sections": [
                {
                    "id": "section-1",
                    "type": "methods",
                    "title": "Methods",
                    "enabled": True,
                    "content": "Method narrative preserved by both PDF engines.",
                }
            ],
            "createdAt": "2026-07-12T12:00:00Z",
            "updatedAt": "2026-07-12T12:00:00Z",
        },
        "sections": ["methods"],
    }


def test_report_request_preserves_composition() -> None:
    model = ReportRequest(**sample_payload())
    dumped = model.model_dump()
    assert dumped["composition"]["format"] == "sc-lab-report-composition/1.0"
    assert dumped["sections"] == ["methods"]


def test_report_validation_preserves_composition() -> None:
    normalized = validate_report(ReportRequest(**sample_payload()).model_dump())
    assert normalized["composition"]["sections"][0]["title"] == "Methods"


def test_vector_pdf_accepts_composition() -> None:
    pdf, metadata = generate_report_pdf(ReportRequest(**sample_payload()).model_dump())
    assert pdf.startswith(b"%PDF")
    assert metadata["byteLength"] == len(pdf)
    assert metadata["pageCount"] >= 1
