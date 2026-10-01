from pathlib import Path

import pytest

from app.reproducible_protocol_notebook_v01540 import (
    MANIFEST_SCHEMA,
    ProtocolNotebookError,
    ProtocolNotebookWorkspaceManager,
    VERSION,
)


def manager(tmp_path: Path) -> ProtocolNotebookWorkspaceManager:
    return ProtocolNotebookWorkspaceManager(str(tmp_path / "rpn.sqlite3"), True, 20, 20, 1000)


def protocol_payload():
    return {
        "title": "Response-surface protocol",
        "purpose": "Reproduce a bounded response-surface exploration.",
        "steps": ["Load registered model", "Apply declared parameters", "Run registered compute method", "Review result references"],
        "methodRefs": ["simulation.parameter_sweep"],
        "acceptanceCriteria": ["All requested samples return finite values", "Result references are preserved"],
        "inputRefs": [{"ref": "dataset:example", "kind": "dataset"}],
        "workspaceRefs": [{"ref": "4dws:example", "kind": "4d-workspace"}],
        "parameters": {"samples": 21},
    }


def notebook_payload(protocol_id: str):
    return {
        "title": "Response-surface notebook",
        "protocolId": protocol_id,
        "cells": [
            {"type": "markdown", "text": "Reproduction notebook"},
            {"type": "parameter", "name": "samples", "value": 21, "units": "count"},
            {"type": "compute-call", "method": "simulation.parameter_sweep", "inputs": {"model": "logistic_growth", "parameter": "rate", "values": [0.1, 0.2], "fixed": {"initial": 1, "capacity": 100, "time": 10}}, "requested_outputs": ["summary", "values"]},
            {"type": "workspace-ref", "ref": "4dws:example", "label": "4D workspace"},
        ],
        "workspaceRefs": [{"ref": "4dws:example", "kind": "4d-workspace"}],
        "computeRefs": [{"ref": "result:example", "kind": "compute-result", "method": "simulation.parameter_sweep"}],
        "notes": {"review": "Human review required"},
    }


def test_health_and_policies(tmp_path):
    m = manager(tmp_path)
    h = m.health()
    assert h["ok"] is True
    assert h["version"] == VERSION
    assert h["immutableProtocolRevisions"] is True
    assert h["immutableNotebookRevisions"] is True
    assert h["registeredComputeCells"] is True
    assert h["arbitraryCodeExecution"] is False
    p = m.policies()
    assert p["archiveInsteadOfDelete"] is True
    assert p["computeCellMode"] == "registered-method-specification-only"
    assert p["automaticExecution"] is False


def test_protocol_lifecycle_is_immutable(tmp_path):
    m = manager(tmp_path)
    created = m.create_protocol("project:test", protocol_payload(), "tester")
    pid = created["protocol"]["id"]
    assert created["revisions"][0]["revision"] == 1
    payload = protocol_payload(); payload["steps"].append("Record limitations")
    revised = m.revise_protocol(pid, payload, "tester")
    assert revised["revisions"][0]["revision"] == 2
    assert revised["revisions"][1]["revision"] == 1
    assert revised["revisions"][0]["revisionHash"] != revised["revisions"][1]["revisionHash"]
    archived = m.archive_protocol(pid, "tester")
    assert archived["protocol"]["status"] == "archived"
    with pytest.raises(ProtocolNotebookError):
        m.revise_protocol(pid, payload, "tester")


def test_notebook_lifecycle_and_protocol_binding(tmp_path):
    m = manager(tmp_path)
    p = m.create_protocol("project:test", protocol_payload(), "tester")
    pid = p["protocol"]["id"]
    nb = m.create_notebook("project:test", notebook_payload(pid), "tester")
    nid = nb["notebook"]["id"]
    assert nb["notebook"]["protocolId"] == pid
    assert nb["revisions"][0]["cells"][2]["type"] == "compute-call"
    assert nb["revisions"][0]["cells"][2]["method"] == "simulation.parameter_sweep"
    payload = notebook_payload(pid); payload["cells"].append({"type": "result-ref", "ref": "result:second", "label": "Second run"})
    revised = m.revise_notebook(nid, payload, "tester")
    assert revised["revisions"][0]["revision"] == 2
    assert len(revised["revisions"][0]["cells"]) == 5
    archived = m.archive_notebook(nid, "tester")
    assert archived["notebook"]["status"] == "archived"


def test_notebook_rejects_arbitrary_code_cell(tmp_path):
    m = manager(tmp_path)
    payload = {"title": "Bad notebook", "cells": [{"type": "python", "text": "print(1)"}]}
    with pytest.raises(ProtocolNotebookError) as exc:
        m.create_notebook("project:test", payload, "tester")
    assert "Unsupported notebook cell type" in exc.value.detail


def test_cross_project_protocol_binding_rejected(tmp_path):
    m = manager(tmp_path)
    p = m.create_protocol("project:a", protocol_payload(), "tester")
    with pytest.raises(ProtocolNotebookError):
        m.create_notebook("project:b", notebook_payload(p["protocol"]["id"]), "tester")


def test_reproduction_manifest_and_verification(tmp_path):
    m = manager(tmp_path)
    p = m.create_protocol("project:test", protocol_payload(), "tester")
    nb = m.create_notebook("project:test", notebook_payload(p["protocol"]["id"]), "tester")
    manifest = m.reproduction_manifest(nb["notebook"]["id"])["manifest"]
    assert manifest["schema"] == MANIFEST_SCHEMA
    assert manifest["protocol"]["revisionHash"]
    assert manifest["notebook"]["revisionHash"]
    assert manifest["computeCellMethods"] == ["simulation.parameter_sweep"]
    assert manifest["arbitraryCodeExecution"] is False
    verification = m.verify_manifest({"manifest": manifest})
    assert verification["ok"] is True
    tampered = dict(manifest); tampered["projectId"] = "project:tampered"
    assert m.verify_manifest({"manifest": tampered})["ok"] is False


def test_lists_are_project_scoped(tmp_path):
    m = manager(tmp_path)
    pa = m.create_protocol("project:a", protocol_payload(), "tester")
    m.create_protocol("project:b", protocol_payload(), "tester")
    m.create_notebook("project:a", notebook_payload(pa["protocol"]["id"]), "tester")
    assert m.list_protocols("project:a")["count"] == 1
    assert m.list_protocols("project:b")["count"] == 1
    assert m.list_notebooks("project:a")["count"] == 1
    assert m.list_notebooks("project:b")["count"] == 0
