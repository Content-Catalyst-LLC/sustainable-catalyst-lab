from __future__ import annotations

import pytest

from app.biochemistry_batch_analysis import (
    VERSION,
    BiochemistryBatchError,
    run_batch,
)


def test_batch_reference() -> None:
    result = run_batch(
        "bc.michaelis_menten",
        [
            {
                "sample": "sample-1",
                "vmax": 100,
                "substrate": 2,
                "km": 0.5,
            },
            {
                "sample": "sample-2",
                "vmax": 100,
                "substrate": 3,
                "km": 0.5,
            },
            {
                "sample": "sample-3",
                "vmax": 100,
                "substrate": 1,
                "km": 0.5,
            },
        ],
    )

    assert VERSION == "0.21.2"
    assert result["analysisEngineVersion"] == "0.21.0"
    assert result["rowCount"] == 3
    assert result["successCount"] == 3
    assert result["errorCount"] == 0
    assert result["statistics"]["velocity"]["n"] == 3
    assert result["statistics"]["velocity"]["mean"] > 0


def test_batch_isolates_invalid_row() -> None:
    result = run_batch(
        "bc.michaelis_menten",
        [
            {
                "sample": "valid",
                "vmax": 100,
                "substrate": 2,
                "km": 0.5,
            },
            {
                "sample": "invalid",
                "vmax": "not-a-number",
                "substrate": 2,
                "km": 0.5,
            },
        ],
    )

    assert result["successCount"] == 1
    assert result["errorCount"] == 1
    assert result["status"] == "review"
    assert len(result["flags"]) >= 1


def test_empty_batch_is_rejected() -> None:
    with pytest.raises(BiochemistryBatchError):
        run_batch("bc.michaelis_menten", [])
