# Sustainable Catalyst Lab v0.59.0 R1 — Scientific Audit Validation Dependency & Installer Repair

R1 repairs the release-validation environment for v0.59.0. The original v0.59.0 artifact correctly reached the scientific/security regression gate, but the inherited v0.39.1 security/privacy contract test imports `jsonschema` and the v0.59.0 development/validation dependency file did not declare it. The result was `ModuleNotFoundError: No module named 'jsonschema'` before Git preparation.

## Repair

- Declares `jsonschema>=4.20,<5` in `backend/requirements-dev.txt`.
- Adds a focused R1 regression test that requires the declaration and verifies Draft 2020-12 validation is available.
- Requires `jsonschema` in the installer import/preflight list.
- Uses an isolated `.sc-lab-v0590-r1-venv` so the incomplete pre-R1 v0.59 environment is not silently reused.
- Preserves the original v0.59.0 scientific audit implementation, WordPress release number, platform compatibility, navigation, and scientific safety boundaries.

## Release identity

- WordPress release: 0.59.0
- Repair line: R1
- Platform compatibility: 1.0.0
- Automatic certification/publication/high-stakes decisions: disabled
- Arbitrary code execution: disabled

## Operator outcome

The installer must not prepare, commit, or push the repository unless dependency preflight and the complete v0.59.0-R1 release gate succeed.
