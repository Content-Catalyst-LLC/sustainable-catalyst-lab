from pathlib import Path

import jsonschema


def test_v0590_r1_declares_jsonschema_validation_dependency():
    root = Path(__file__).resolve().parents[2]
    requirements = (root / "backend" / "requirements-dev.txt").read_text().lower()
    assert "jsonschema" in requirements


def test_v0590_r1_jsonschema_draft_2020_12_validator_available():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["auditReady"],
        "properties": {"auditReady": {"type": "boolean"}},
        "additionalProperties": False,
    }
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate({"auditReady": True})
