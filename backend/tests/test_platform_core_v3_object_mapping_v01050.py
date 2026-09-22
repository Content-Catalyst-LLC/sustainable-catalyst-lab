import pytest

from app.platform_core_v3_object_mapping_v01050 import (
    CORE_OBJECT_BINDING_PATH,
    LAB_VERSION,
    PlatformCoreV3ObjectMappingError,
    build_core_object_binding,
    build_core_object_binding_batch,
    catalog,
    health,
    map_legacy_typed_handoff,
    normalize_object,
)


def test_catalog_and_health_define_twenty_reference_first_mappings():
    c = catalog()
    h = health()
    assert c["lab_release_version"] == LAB_VERSION == "0.105.0"
    assert c["required_core_release"] == "3.0.0"
    assert c["mapping_count"] == 20
    assert h["mapping_count"] == 20
    assert c["boundaries"]["lab_objects_remain_authoritative"] is True
    assert c["boundaries"]["object_payloads_copied_to_core"] is False
    assert c["boundaries"]["automatic_core_submission"] is False
    by_type = {item["lab_type"]: item for item in c["mappings"]}
    assert by_type["evidence-record"]["core_object_type"] == "evidence"
    assert by_type["scientific-figure"]["later_specialized_binding"] == "visual"
    assert by_type["reproducibility-package"]["later_specialized_binding"] == "package"


def test_normalize_builds_stable_lab_authoritative_reference():
    out = normalize_object({
        "object_type": "dataset",
        "local_id": "soil sample/42",
        "version": "2026.09",
        "visibility": "private",
        "content_hash": "a" * 64,
        "metadata": {"title": "SOC observations"},
    })["object"]
    assert out["core_object_type"] == "dataset"
    assert out["object_ref"] == "lab:dataset:soil%20sample%2F42"
    assert out["version_ref"].endswith(":version:2026.09")
    assert out["lab_visibility"] == "private"
    assert out["core_visibility"] == "internal"
    assert out["authority"] == "product:sustainable-catalyst-lab"
    assert len(out["mapping_hash"]) == 64


def test_alias_and_content_hash_are_normalized_without_copying_content():
    source = {"values": [1, 2, 3], "unit": "kg"}
    out = normalize_object({
        "object_type": "evidence",
        "id": "ev-1",
        "content": source,
    })["object"]
    assert out["lab_object_type"] == "evidence-record"
    assert out["core_object_type"] == "evidence"
    assert len(out["content_hash"]) == 64
    assert "content" not in out


def test_builds_exact_core_v3_reference_first_object_binding_request():
    result = build_core_object_binding({
        "session_id": "session-123",
        "object": {
            "object_type": "model",
            "id": "carbon-model-7",
            "content_hash": "b" * 64,
            "role": "method",
            "visibility": "public",
        },
    })
    assert result["target_path"] == CORE_OBJECT_BINDING_PATH
    assert result["automatic_submission"] is False
    assert result["request_body"] == {"data": result["data"]}
    assert result["data"]["session_id"] == "session-123"
    assert result["data"]["object_type"] == "model"
    assert result["data"]["object_ref"] == "lab:model:carbon-model-7"
    assert result["data"]["role"] == "method"
    assert result["data"]["metadata"]["underlying_object_remains_authoritative_in_lab"] is True


def test_batch_is_deterministic_and_rejects_duplicate_refs():
    result = build_core_object_binding_batch({
        "session_id": "session-1",
        "objects": [
            {"object_type": "dataset", "id": "d1"},
            {"object_type": "experiment", "id": "e1"},
            {"object_type": "scientific-figure", "id": "f1"},
        ],
    })
    assert result["count"] == 3
    assert len(result["batch_hash"]) == 64
    assert [x["data"]["object_type"] for x in result["bindings"]] == ["dataset", "experiment", "scientific-figure"]

    with pytest.raises(PlatformCoreV3ObjectMappingError):
        build_core_object_binding_batch({
            "session_id": "session-1",
            "objects": [
                {"object_type": "dataset", "id": "same"},
                {"object_type": "dataset", "id": "same"},
            ],
        })


def test_legacy_v0381_handoff_maps_to_core_v3_object_binding():
    result = map_legacy_typed_handoff({
        "session_id": "core-session-9",
        "handoff": {
            "id": "handoff-1",
            "sourceProduct": "sustainable-catalyst-lab",
            "targetProduct": "knowledge-library",
            "entityType": "reproducibility-package",
            "contractVersion": "sc-research-reproducibility-package/1.0",
            "resource": {
                "id": "package-7",
                "sha256": "c" * 64,
                "metadata": {"title": "Reproduction package"},
            },
            "provenance": {"actor": "researcher"},
        },
    })
    mapped = result["core_mapping"]
    assert result["automatic_submission"] is False
    assert result["automatic_execution"] is False
    assert mapped["data"]["session_id"] == "core-session-9"
    assert mapped["data"]["object_type"] == "reproducibility-package"
    assert mapped["data"]["object_ref"] == "lab:reproducibility-package:package-7"
    assert mapped["data"]["metadata"]["lab_metadata"]["legacy_typed_handoff_id"] == "handoff-1"
    assert mapped["data"]["metadata"]["lab_provenance"]["actor"] == "researcher"


def test_rejects_unsupported_type_bad_hash_and_legacy_contract_mismatch():
    with pytest.raises(PlatformCoreV3ObjectMappingError):
        normalize_object({"object_type": "mystery", "id": "x"})
    with pytest.raises(PlatformCoreV3ObjectMappingError):
        normalize_object({"object_type": "dataset", "id": "x", "content_hash": "not-sha256"})
    with pytest.raises(PlatformCoreV3ObjectMappingError):
        map_legacy_typed_handoff({
            "session_id": "s",
            "entityType": "dataset",
            "contractVersion": "wrong",
            "resource": {"id": "d", "sha256": "d" * 64},
        })
