from __future__ import annotations

import base64

from fastapi.testclient import TestClient

from app.main import app
from app.reporting import _flatten, generate_report_pdf, validate_handoff, validate_report

client = TestClient(app)


def analysis() -> dict:
    return {
        "schema": "sc-lab-analysis/1.0",
        "schemaVersion": "1.0",
        "id": "analysis-test",
        "methodId": "kinetic",
        "methodVersion": "0.10.0",
        "title": "Kinetic energy reference analysis",
        "subtitle": "Deterministic mechanics calculation",
        "domain": "physics",
        "createdAt": "2026-07-12T00:00:00Z",
        "status": "VALIDATED",
        "inputs": {"mass": 10, "velocity": 5},
        "outputs": {"kineticEnergyJ": 125, "momentumKgMs": 50},
        "equation": "KE = 1/2 mv^2; p = mv",
        "assumptions": ["Classical non-relativistic mechanics."],
        "warnings": [],
        "validation": {"status": "VALIDATED", "benchmark": "known reference"},
        "sources": ["Sustainable Catalyst Lab method contract"],
        "chartSpec": {
            "type": "bar",
            "xKey": "label",
            "yKeys": ["value"],
            "data": [
                {"label": "Kinetic energy", "value": 125},
                {"label": "Momentum", "value": 50},
            ],
            "xLabel": "Metric",
            "yLabel": "Value",
        },
        "audit": {"inputFingerprint": "abc", "outputFingerprint": "def"},
    }


def report() -> dict:
    return {
        "reportType": "technical-report",
        "title": "Sustainable Catalyst Lab validation report",
        "subtitle": "PDF and Decision Studio handoff test",
        "executiveSummary": "This report verifies deterministic calculation, validation, and audit metadata.",
        "pageSize": "LETTER",
        "project": {"id": "project-test", "name": "Test project", "schemaVersion": "0.10.0"},
        "analyses": [analysis()],
        "includeAudit": True,
    }



def test_nested_report_fields_are_flattened() -> None:
    rows = _flatten({"ratedCapacity": {"value": 120, "unit": "kW"}, "profile": [1, 2, 3]})
    assert ("ratedCapacity.value", "120") in rows
    assert ("ratedCapacity.unit", "kW") in rows
    assert ("profile", "1, 2, 3") in rows

def test_report_contract_and_pdf_generation() -> None:
    normalized = validate_report(report())
    assert normalized["schema"] == "sc-lab-report/1.0"
    assert normalized["audit"]["reportFingerprint"]
    pdf, metadata = generate_report_pdf(report())
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 4000
    assert metadata["status"] == "VALIDATED"
    assert metadata["pageCount"] >= 1
    assert metadata["pdfFingerprint"]


def test_report_api_validate_and_pdf() -> None:
    validated = client.post("/v1/reports/validate", json=report())
    assert validated.status_code == 200
    assert validated.json()["status"] == "VALIDATED"
    response = client.post("/v1/reports/pdf", json=report())
    assert response.status_code == 200
    body = response.json()
    pdf = base64.b64decode(body["dataBase64"])
    assert pdf.startswith(b"%PDF-")
    assert body["byteLength"] == len(pdf)
    assert body["engine"] == "reportlab-vector-pdf"


def test_report_rejects_missing_analysis() -> None:
    payload = report()
    payload["analyses"] = []
    response = client.post("/v1/reports/validate", json=payload)
    assert response.status_code == 422


def test_decision_studio_packet_validation() -> None:
    packet = {
        "packetType": "scientific-report",
        "schemaVersion": "2.0",
        "origin": {"application": "Sustainable Catalyst Lab", "version": "0.10.0"},
        "createdAt": "2026-07-12T00:00:00Z",
        "report": {"title": "Test report"},
        "analyses": [analysis()],
        "charts": [],
        "scenes": [],
        "tables": [],
        "audit": {},
    }
    result = validate_handoff(packet)
    assert result["status"] == "VALIDATED"
    assert result["analysisCount"] == 1
    response = client.post("/v1/handoffs/decision-studio/validate", json={"packet": packet})
    assert response.status_code == 200
    assert response.json()["packetFingerprint"]
