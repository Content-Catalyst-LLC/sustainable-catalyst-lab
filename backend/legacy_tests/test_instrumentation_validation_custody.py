from __future__ import annotations

from app.instrumentation_validation_custody import (
    VERSION,
    contract,
    create_custody_event,
    create_dossier,
    create_manifest,
    execute,
    verify_custody_chain,
)


def test_contract_and_benchmarks() -> None:
    data = contract()
    assert VERSION == "0.25.3"
    assert len(data["validationProfiles"]) == 8
    assert len(data["acceptanceStates"]) == 8
    assert len(data["provenanceEventTypes"]) == 8
    assert len(data["deviationTypes"]) == 8
    assert len(data["analysisMethods"]) == 16
    assert len(data["benchmarks"]) == 16

    for benchmark in data["benchmarks"]:
        result = execute(benchmark["methodId"], benchmark["inputs"])
        assert result["value"] == benchmark["expected"]


def test_custody_chain_detects_tampering() -> None:
    first = create_custody_event(
        "SAMPLE-1",
        "received",
        "analyst-a",
        "intake",
        1,
    )
    second = create_custody_event(
        "SAMPLE-1",
        "transferred",
        "analyst-b",
        "lab",
        2,
        first["eventHash"],
    )
    valid = verify_custody_chain([first, second])
    assert valid["valid"] is True

    tampered = dict(second)
    tampered["location"] = "unknown"
    invalid = verify_custody_chain([first, tampered])
    assert invalid["valid"] is False
    assert "event-2-hash" in invalid["problems"]


def test_manifest_and_dossier() -> None:
    manifest = create_manifest(
        {
            "instrument": {"id": "INST-1", "model": "SC-100"},
            "calibration": {"status": "accepted"},
            "measurements": [1, 2, 3],
        },
        {"projectId": "PROJECT-1"},
    )
    assert len(manifest["manifestHash"]) == 64
    assert len(manifest["componentHashes"]) == 3

    first = create_custody_event(
        "SAMPLE-1",
        "received",
        "analyst-a",
        "intake",
        1,
    )
    dossier = create_dossier(
        {
            "instrument-identity": {"score": 100},
            "calibration-acceptance": {"score": 95},
            "measurement-quality": {"score": 92},
            "custody-chain-integrity": {"score": 100},
        },
        manifest,
        [first],
        [{"type": "review-incomplete", "closed": False}],
        {"reviewer": "QA"},
    )
    assert dossier["disposition"] == "conditionally-accepted"
    assert len(dossier["dossierHash"]) == 64
