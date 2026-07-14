from __future__ import annotations

from app.instrumentation_live_visualization import (
    VERSION,
    build_snapshot,
    contract,
    execute,
)


def test_contract_and_benchmarks() -> None:
    data = contract()
    assert VERSION == "0.25.2"
    assert len(data["modes"]) == 8
    assert len(data["analysisMethods"]) == 16
    assert len(data["benchmarks"]) == 16
    assert len(data["channelTemplates"]) == 8
    assert len(data["connectionStates"]) == 8
    assert len(data["eventTypes"]) == 8

    for benchmark in data["benchmarks"]:
        result = execute(benchmark["methodId"], benchmark["inputs"])
        assert result["value"] == benchmark["expected"]


def test_snapshot_detects_threshold_and_gap_events() -> None:
    snapshot = build_snapshot(
        [
            {"timestamp": 1, "channel": "temperature", "value": 20},
            {"timestamp": 2, "channel": "temperature", "value": 26},
            {"timestamp": 9, "channel": "temperature", "value": 21},
        ],
        {
            "temperature": {
                "warningLow": 10,
                "warningHigh": 20,
                "actionLow": 5,
                "actionHigh": 25,
            }
        },
        3,
        "online",
    )
    assert snapshot["summary"]["connectionState"] == "online"
    assert snapshot["summary"]["channelCount"] == 1
    assert {event["type"] for event in snapshot["events"]} == {"action", "warning", "gap"}


def test_ring_buffer_is_bounded() -> None:
    result = execute(
        "append-ring-buffer",
        {
            "existing": [{"timestamp": 1, "channel": "x", "value": 1}],
            "incoming": [
                {"timestamp": 2, "channel": "x", "value": 2},
                {"timestamp": 3, "channel": "x", "value": 3},
            ],
            "maximumPoints": 2,
        },
    )
    assert [item["value"] for item in result["value"]] == [2.0, 3.0]
