from __future__ import annotations

from copy import deepcopy

from app.molecular_analysis_validation import (
    VERSION,
    create_provenance_record,
    profiles_contract,
    validate_profile,
    verify_ledger,
)


def test_profiles_contract() -> None:
    contract = profiles_contract()

    assert VERSION == "0.21.3"
    assert contract["version"] == "0.21.3"
    assert len(contract["profiles"]) == 8


def test_precision_reference_passes() -> None:
    validation = validate_profile(
        "precision-repeatability",
        [
            {"value": 100.1},
            {"value": 99.8},
            {"value": 100.4},
            {"value": 100.0},
            {"value": 99.9},
        ],
        {
            "minimumReplicates": 3,
            "maximumCvPercent": 10,
        },
    )

    assert validation["decision"] == "pass"
    assert validation["metrics"]["n"] == 5
    assert (
        validation["metrics"][
            "coefficientOfVariationPercent"
        ]
        < 1
    )


def test_calibration_reference_passes() -> None:
    validation = validate_profile(
        "calibration-linearity",
        [
            {"concentration": 0, "signal": 1},
            {"concentration": 1, "signal": 3},
            {"concentration": 2, "signal": 5},
            {"concentration": 3, "signal": 7},
            {"concentration": 4, "signal": 9},
        ],
        {
            "minimumLevels": 5,
            "minimumRSquared": 0.99,
            "requirePositiveSlope": 1,
        },
    )

    assert validation["decision"] == "pass"
    assert validation["metrics"]["slope"] == 2
    assert validation["metrics"]["intercept"] == 1
    assert validation["metrics"]["rSquared"] == 1


def test_blank_failure_is_explicit() -> None:
    validation = validate_profile(
        "blank-background",
        [
            {"value": 0.01},
            {"value": 0.02},
            {"value": 0.5},
        ],
        {
            "minimumBlanks": 3,
            "maximumMean": 0.05,
            "maximumSingle": 0.1,
        },
    )

    assert validation["decision"] == "fail"
    assert validation["failedCheckCount"] >= 1


def test_provenance_chain_and_tamper_detection() -> None:
    first = create_provenance_record(
        {
            "methodId": "bc.michaelis_menten",
            "decision": "pass",
        },
        {
            "recordId": "record-1",
            "timestamp": "2026-07-13T18:00:00Z",
            "methodId": "bc.michaelis_menten",
            "profileId": "precision-repeatability",
        },
    )
    second = create_provenance_record(
        {
            "methodId": "bc.michaelis_menten",
            "decision": "pass",
        },
        {
            "recordId": "record-2",
            "timestamp": "2026-07-13T18:05:00Z",
            "methodId": "bc.michaelis_menten",
            "profileId": "calibration-linearity",
        },
        first["recordHash"],
    )

    assert len(first["payloadHash"]) == 64
    assert len(first["recordHash"]) == 64

    valid = verify_ledger([first, second])

    assert valid["valid"] is True
    assert valid["recordCount"] == 2

    tampered = deepcopy([first, second])
    tampered[0]["payload"]["decision"] = "fail"

    invalid = verify_ledger(tampered)

    assert invalid["valid"] is False
    assert invalid["results"][0]["hashValid"] is False
