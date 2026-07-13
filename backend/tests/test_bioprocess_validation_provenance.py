from __future__ import annotations

from copy import deepcopy

from app.bioprocess_validation_provenance import (
    VERSION,
    contract,
    create_dossier,
    create_record,
    evaluate,
    verify_ledger,
)


def test_contract_counts() -> None:
    data = contract()

    assert VERSION == "0.22.3"
    assert len(data["profiles"]) == 8
    assert len(data["eventTypes"]) == 5
    assert len(data["dispositions"]) == 5


def test_cross_batch_consistency_passes() -> None:
    result = evaluate(
        "cross-batch-consistency",
        [
            {
                "batchId": "B-001",
                "yield": 82,
                "titer": 3.9,
                "cycleTime": 72,
            },
            {
                "batchId": "B-002",
                "yield": 84,
                "titer": 4.0,
                "cycleTime": 70,
            },
            {
                "batchId": "B-003",
                "yield": 83,
                "titer": 4.1,
                "cycleTime": 71,
            },
        ],
    )

    assert result["decision"] == "pass"
    assert result["failedCheckCount"] == 0
    assert result["metrics"]["batchCount"] == 3


def test_cpp_and_release_readiness_failures() -> None:
    cpp = evaluate(
        "cpp-conformance",
        [
            {
                "parameter": "temperature",
                "value": 37,
                "low": 35,
                "high": 39,
            },
            {
                "parameter": "pH",
                "value": 6.2,
                "low": 6.8,
                "high": 7.2,
            },
        ],
    )
    release = evaluate(
        "release-readiness",
        [
            {
                "checkId": "C-1",
                "category": "major",
                "critical": True,
                "status": "open",
                "evidence": "",
            }
        ],
    )

    assert cpp["decision"] == "fail"
    assert cpp["metrics"]["actionExcursionCount"] == 1
    assert release["decision"] == "fail"
    assert release["metrics"]["failedCriticalCheckCount"] == 1


def test_hold_time_stability() -> None:
    result = evaluate(
        "hold-time-stability",
        [
            {"time": 0, "value": 100},
            {"time": 2, "value": 99},
            {"time": 4, "value": 98},
        ],
        {
            "maximumAbsoluteChangePercent": 3,
            "maximumSlopePercentPerHour": 1,
        },
    )

    assert result["decision"] == "pass"
    assert result["metrics"]["absoluteChangePercent"] == 2


def test_provenance_chain_and_tamper_detection() -> None:
    first = create_record(
        {"summary": {"status": "normal"}},
        {
            "recordId": "record-1",
            "timestamp": "2026-07-13T20:00:00+00:00",
            "eventType": "monitoring-analysis",
            "batchId": "B-001",
        },
    )
    second = create_record(
        {"decision": "pass"},
        {
            "recordId": "record-2",
            "timestamp": "2026-07-13T20:05:00+00:00",
            "eventType": "validation-decision",
            "batchId": "B-001",
        },
        first["recordHash"],
    )

    valid = verify_ledger([first, second])
    assert valid["valid"] is True

    tampered = deepcopy([first, second])
    tampered[1]["payload"]["decision"] = "fail"
    invalid = verify_ledger(tampered)

    assert invalid["valid"] is False
    assert invalid["results"][1]["payloadValid"] is False


def test_dossier_release_readiness() -> None:
    validation = evaluate(
        "cqa-conformance",
        [
            {
                "attribute": "purity",
                "value": 98.5,
                "low": 95,
                "high": 100,
            }
        ],
    )
    record = create_record(
        validation,
        {
            "recordId": "validation-1",
            "timestamp": "2026-07-13T20:10:00+00:00",
            "eventType": "validation-decision",
            "batchId": "B-001",
        },
    )
    dossier = create_dossier(
        [validation],
        {"batchId": "B-001"},
        [record],
        "release",
    )

    assert dossier["summary"]["releaseReady"] is True
    assert dossier["summary"]["ledgerValid"] is True
    assert len(dossier["dossierHash"]) == 64
