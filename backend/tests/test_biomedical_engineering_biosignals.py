from __future__ import annotations

import math

from app.biomedical_engineering_biosignals import (
    VERSION,
    analyze_signal,
    batch_execute,
    catalog,
    execute,
)


def test_contract_and_benchmarks() -> None:
    data = catalog()

    assert VERSION == "0.23.0"
    assert len(data["categories"]) == 8
    assert len(data["methods"]) == 48
    assert len(data["benchmarks"]) == 48

    for benchmark in data["benchmarks"]:
        result = execute(
            benchmark["methodId"],
            benchmark["inputs"],
        )
        assert math.isclose(
            float(result["value"]),
            float(benchmark["expected"]),
            rel_tol=1e-8,
            abs_tol=float(benchmark["tolerance"]),
        )


def test_waveform_analysis() -> None:
    result = analyze_signal(
        [-1, 1, -1, 1],
        100,
    )

    assert result["sampleCount"] == 4
    assert result["durationSeconds"] == 0.03
    assert result["rms"] == 1
    assert result["peakToPeak"] == 2
    assert result["zeroCrossingCount"] == 3
    assert result["zeroCrossingRate"] == 100


def test_batch_row_isolation() -> None:
    result = batch_execute(
        [
            {
                "methodId": "heart-rate-from-rr",
                "inputs": {"rrSeconds": 0.8},
            },
            {
                "methodId": "heart-rate-from-rr",
                "inputs": {"rrSeconds": 0},
            },
            {
                "methodId": "signal-quality-index",
                "inputs": {
                    "snrDb": 20,
                    "missingPercent": 2,
                    "clippingPercent": 1,
                },
            },
        ]
    )

    assert result["rowCount"] == 3
    assert result["successCount"] == 2
    assert result["errorCount"] == 1
    assert result["results"][0]["ok"] is True
    assert result["results"][1]["ok"] is False
