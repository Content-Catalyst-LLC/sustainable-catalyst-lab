from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import copy
import json
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any

from .distributed_dispatcher import DispatcherError

VERSION = "0.32.1"
WORKFLOW_SCHEMA = "sc-lab-scientific-workflow/0.32.1"
RUN_SCHEMA = "sc-lab-workflow-run/0.32.1"
NODE_SCHEMA = "sc-lab-workflow-node-run/0.32.1"
EVENT_SCHEMA = "sc-lab-workflow-event/0.32.1"
CHECKPOINT_SCHEMA = "sc-lab-workflow-checkpoint/0.32.1"
RECOVERY_SCHEMA = "sc-lab-workflow-recovery-plan/0.32.1"
DB_SCHEMA_VERSION = 2
RUN_STATES = {"pending", "running", "completed", "failed", "cancelled"}
NODE_STATES = {"waiting", "queued", "running", "completed", "reused", "failed", "skipped", "cancelled"}
TERMINAL_NODE_STATES = {"completed", "reused", "failed", "skipped", "cancelled"}
SUCCESS_NODE_STATES = {"completed", "reused"}
CONDITION_OPERATORS = {"exists", "truthy", "falsy", "equals", "notEquals", "greaterThan", "greaterThanOrEqual", "lessThan", "lessThanOrEqual", "in", "notIn", "contains"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")


class WorkflowError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 2000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _int(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def _deep_get(value: Any, path: str) -> Any:
    current = value
    if not path:
        return current
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise WorkflowError(f"Binding source path was not found: {path}")
    return copy.deepcopy(current)


def _deep_set(target: dict[str, Any], path: str, value: Any) -> None:
    parts = [part for part in path.split(".") if part]
    if not parts:
        raise WorkflowError("Binding targetPath is required.")
    current: dict[str, Any] = target
    for part in parts[:-1]:
        child = current.get(part)
        if child is None:
            child = {}
            current[part] = child
        if not isinstance(child, dict):
            raise WorkflowError(f"Binding target path crosses a non-object value: {path}")
        current = child
    current[parts[-1]] = copy.deepcopy(value)


def _normalize_condition(value: Any, node_id: str, depth: int = 0) -> dict[str, Any] | None:
    if value in (None, {}, []):
        return None
    if depth > 12 or not isinstance(value, dict):
        raise WorkflowError(f"Workflow node {node_id} contains an invalid condition.")
    for key in ("all", "any"):
        if key in value:
            items = value.get(key)
            if not isinstance(items, list) or not items:
                raise WorkflowError(f"Workflow node {node_id} condition {key} requires a non-empty array.")
            return {key: [_normalize_condition(item, node_id, depth + 1) for item in items]}
    if "not" in value:
        child = _normalize_condition(value.get("not"), node_id, depth + 1)
        if child is None:
            raise WorkflowError(f"Workflow node {node_id} condition not requires a child condition.")
        return {"not": child}
    source = _text(value.get("source") or value.get("path"), 500)
    operator = _text(value.get("operator"), 40) or "truthy"
    if not source:
        raise WorkflowError(f"Workflow node {node_id} condition requires a source path.")
    if not (source.startswith("run.inputs") or source.startswith("run.context") or source.startswith("nodes.")):
        raise WorkflowError(f"Workflow node {node_id} condition source must begin with run.inputs, run.context, or nodes.")
    if operator not in CONDITION_OPERATORS:
        raise WorkflowError(f"Workflow node {node_id} condition operator is unsupported: {operator}")
    condition = {"source": source, "operator": operator}
    if "value" in value:
        condition["value"] = copy.deepcopy(value.get("value"))
    return condition


def _condition_result(condition: dict[str, Any] | None, run_inputs: dict[str, Any], run_context: dict[str, Any], node_rows: dict[str, sqlite3.Row]) -> tuple[bool, dict[str, Any]]:
    if not condition:
        return True, {"matched": True, "reason": "no-condition"}
    if "all" in condition:
        children = [_condition_result(item, run_inputs, run_context, node_rows) for item in condition["all"]]
        return all(item[0] for item in children), {"operator": "all", "children": [item[1] for item in children]}
    if "any" in condition:
        children = [_condition_result(item, run_inputs, run_context, node_rows) for item in condition["any"]]
        return any(item[0] for item in children), {"operator": "any", "children": [item[1] for item in children]}
    if "not" in condition:
        matched, detail = _condition_result(condition["not"], run_inputs, run_context, node_rows)
        return (not matched), {"operator": "not", "child": detail}
    nodes: dict[str, Any] = {}
    for node_id, row in node_rows.items():
        nodes[node_id] = {
            "status": row["status"],
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "skipReason": row["skip_reason"] if "skip_reason" in row.keys() else None,
        }
    root = {"run": {"inputs": run_inputs, "context": run_context}, "nodes": nodes}
    source = condition["source"]
    exists = True
    try:
        actual = _deep_get(root, source)
    except WorkflowError:
        exists = False
        actual = None
    operator = condition["operator"]
    expected = condition.get("value")
    if operator == "exists": matched = exists
    elif operator == "truthy": matched = bool(actual) if exists else False
    elif operator == "falsy": matched = not bool(actual) if exists else True
    elif operator == "equals": matched = exists and actual == expected
    elif operator == "notEquals": matched = (not exists) or actual != expected
    elif operator == "greaterThan": matched = exists and actual > expected
    elif operator == "greaterThanOrEqual": matched = exists and actual >= expected
    elif operator == "lessThan": matched = exists and actual < expected
    elif operator == "lessThanOrEqual": matched = exists and actual <= expected
    elif operator == "in": matched = exists and isinstance(expected, (list, tuple, set)) and actual in expected
    elif operator == "notIn": matched = (not exists) or not isinstance(expected, (list, tuple, set)) or actual not in expected
    elif operator == "contains": matched = exists and isinstance(actual, (list, tuple, set, str, dict)) and expected in actual
    else: matched = False
    return matched, {"source": source, "operator": operator, "exists": exists, "actual": actual, "expected": expected, "matched": matched}


def policies(max_nodes: int = 100, max_runs: int = 5000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "checkpoint-aware-conditional-scientific-workflow-orchestrator",
        "definitions": {
            "typedNodes": True,
            "acyclicGraphsRequired": True,
            "immutableRunSnapshots": True,
            "declarativeConditions": True,
            "arbitraryConditionCode": False,
            "maximumNodes": max_nodes,
        },
        "execution": {
            "dependencyAwareScheduling": True,
            "dispatcherBackedNodes": True,
            "parallelReadyNodes": True,
            "nodeRetriesDelegatedToDispatcher": True,
            "automaticDownstreamBlocking": True,
            "conditionalSkipping": True,
            "checkpointResumeContext": True,
            "manualReconciliation": True,
        },
        "recovery": {
            "partialRunRecovery": True,
            "newRunForRecovery": True,
            "completedNodeReuse": True,
            "checkpointReuse": True,
            "downstreamClosure": True,
            "operatorAuditTrail": True,
        },
        "handoffs": {
            "resultBindings": True,
            "artifactInputs": True,
            "dependencyArtifactPropagation": True,
            "checkpointArtifacts": True,
            "arbitraryCode": False,
            "arbitraryCallbackUrls": False,
        },
        "provenance": {
            "definitionHash": True,
            "runTimeline": True,
            "queueIdentifiers": True,
            "nodeResults": True,
            "checkpointHistory": True,
            "recoveryLineage": True,
        },
        "limits": {"workflowRuns": max_runs},
    }


def normalize_workflow(payload: dict[str, Any], max_nodes: int = 100) -> dict[str, Any]:
    source = payload.get("workflow") if isinstance(payload.get("workflow"), dict) else payload
    workflow_id = _text(source.get("id"), 180) or f"workflow-{secrets.token_hex(8)}"
    if not ID_RE.match(workflow_id):
        raise WorkflowError("Workflow ID must contain only letters, numbers, dots, underscores, and hyphens.")
    raw_nodes = source.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise WorkflowError("A workflow requires at least one node.")
    if len(raw_nodes) > max_nodes:
        raise WorkflowError(f"A workflow may contain at most {max_nodes} nodes.")

    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for index, raw in enumerate(raw_nodes):
        if not isinstance(raw, dict):
            raise WorkflowError(f"Workflow node {index + 1} must be an object.")
        node_id = _text(raw.get("id"), 180)
        if not node_id or not ID_RE.match(node_id):
            raise WorkflowError(f"Workflow node {index + 1} has an invalid ID.")
        if node_id in node_ids:
            raise WorkflowError(f"Duplicate workflow node ID: {node_id}")
        node_ids.add(node_id)
        method = _text(raw.get("method") or raw.get("methodId"), 180)
        if not method:
            raise WorkflowError(f"Workflow node {node_id} requires a registered method.")
        depends_on = []
        for dependency in raw.get("dependsOn") if isinstance(raw.get("dependsOn"), list) else []:
            dependency_id = _text(dependency, 180)
            if dependency_id and dependency_id not in depends_on:
                depends_on.append(dependency_id)
        bindings = []
        for binding in raw.get("bindings") if isinstance(raw.get("bindings"), list) else []:
            if not isinstance(binding, dict):
                raise WorkflowError(f"Workflow node {node_id} contains an invalid binding.")
            from_node = _text(binding.get("fromNode"), 180)
            source_path = _text(binding.get("sourcePath") or binding.get("source"), 500)
            target_path = _text(binding.get("targetPath") or binding.get("target"), 500)
            if not from_node or not source_path or not target_path:
                raise WorkflowError(f"Workflow node {node_id} bindings require fromNode, sourcePath, and targetPath.")
            if from_node not in depends_on:
                raise WorkflowError(f"Workflow node {node_id} binding source {from_node} must also be listed in dependsOn.")
            bindings.append({"fromNode": from_node, "sourcePath": source_path, "targetPath": target_path})
        nodes.append({
            "schema": "sc-lab-workflow-node/0.32.1",
            "id": node_id,
            "title": _text(raw.get("title"), 300) or node_id.replace("-", " ").replace("_", " ").title(),
            "method": method,
            "dependsOn": depends_on,
            "bindings": bindings,
            "condition": _normalize_condition(raw.get("condition") or raw.get("when"), node_id),
            "request": copy.deepcopy(raw.get("request")) if isinstance(raw.get("request"), dict) else {},
            "priority": _int(raw.get("priority"), 50, 0, 100),
            "maxAttempts": _int(raw.get("maxAttempts"), 3, 1, 20),
            "timeoutSeconds": _int(raw.get("timeoutSeconds"), 300, 1, 86400),
            "leaseSeconds": _int(raw.get("leaseSeconds"), 300, 30, 3600),
            "requiredPackages": [_text(item, 100) for item in raw.get("requiredPackages", [])[:128] if _text(item, 100)] if isinstance(raw.get("requiredPackages"), list) else [],
            "requiredTags": [_text(item, 80) for item in raw.get("requiredTags", [])[:64] if _text(item, 80)] if isinstance(raw.get("requiredTags"), list) else [],
            "targetPreference": [_text(item, 80) for item in raw.get("targetPreference", [])[:8] if _text(item, 80)] if isinstance(raw.get("targetPreference"), list) else [],
            "minimumMemoryMb": _int(raw.get("minimumMemoryMb"), 128, 128, 1048576),
            "gpuRequired": bool(raw.get("gpuRequired", False)),
            "checkpointingRequired": bool(raw.get("checkpointingRequired", False)),
            "artifactInputs": [copy.deepcopy(item) for item in raw.get("artifactInputs", [])[:100] if isinstance(item, dict)] if isinstance(raw.get("artifactInputs"), list) else [],
            "artifactOutputs": [copy.deepcopy(item) for item in raw.get("artifactOutputs", [])[:100] if isinstance(item, dict)] if isinstance(raw.get("artifactOutputs"), list) else [],
            "metadata": copy.deepcopy(raw.get("metadata")) if isinstance(raw.get("metadata"), dict) else {},
        })

    by_id = {node["id"]: node for node in nodes}
    for node in nodes:
        for dependency in node["dependsOn"]:
            if dependency == node["id"]:
                raise WorkflowError(f"Workflow node {node['id']} cannot depend on itself.")
            if dependency not in by_id:
                raise WorkflowError(f"Workflow node {node['id']} references unknown dependency {dependency}.")

    indegree = {node_id: 0 for node_id in by_id}
    downstream: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    for node in nodes:
        indegree[node["id"]] = len(node["dependsOn"])
        for dependency in node["dependsOn"]:
            downstream[dependency].append(node["id"])
    ready = sorted([node_id for node_id, count in indegree.items() if count == 0])
    order: list[str] = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for child in sorted(downstream[node_id]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
                ready.sort()
    if len(order) != len(nodes):
        cyclic = sorted(node_id for node_id, count in indegree.items() if count > 0)
        raise WorkflowError(f"Workflow dependency graph contains a cycle involving: {', '.join(cyclic)}")

    workflow = {
        "schema": WORKFLOW_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-workflow",
        "id": workflow_id,
        "title": _text(source.get("title"), 300) or "Scientific workflow",
        "description": _text(source.get("description"), 4000),
        "projectId": _text(source.get("projectId") or source.get("project_id"), 180) or "default",
        "nodes": nodes,
        "topologicalOrder": order,
        "entryNodes": [node_id for node_id in order if not by_id[node_id]["dependsOn"]],
        "terminalNodes": [node_id for node_id in order if not downstream[node_id]],
        "metadata": copy.deepcopy(source.get("metadata")) if isinstance(source.get("metadata"), dict) else {},
        "createdAt": source.get("createdAt") or _now(),
    }
    workflow["definitionHash"] = _hash({key: value for key, value in workflow.items() if key not in {"createdAt", "definitionHash"}})
    return workflow


class WorkflowOrchestrator:
    def __init__(self, db_path: str, dispatcher: Any, max_nodes: int = 100, max_runs: int = 5000, history_limit: int = 20000):
        self.db_path = str(db_path)
        self.dispatcher = dispatcher
        self.max_nodes = max(1, min(1000, int(max_nodes)))
        self.max_runs = max(100, min(100000, int(max_runs)))
        self.history_limit = max(100, min(1000000, int(history_limit)))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _migrate(self) -> None:
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS workflow_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS workflow_definitions(
              id TEXT PRIMARY KEY, definition_hash TEXT NOT NULL, project_id TEXT NOT NULL,
              title TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_definitions_project ON workflow_definitions(project_id, updated_at DESC);
            CREATE TABLE IF NOT EXISTS workflow_runs(
              id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, definition_hash TEXT NOT NULL,
              project_id TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL,
              inputs_json TEXT NOT NULL, context_json TEXT NOT NULL, error_text TEXT,
              created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_runs_lookup ON workflow_runs(workflow_id, status, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_workflow_runs_project ON workflow_runs(project_id, created_at DESC);
            CREATE TABLE IF NOT EXISTS workflow_node_runs(
              run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
              node_id TEXT NOT NULL, status TEXT NOT NULL, queue_id TEXT,
              payload_json TEXT NOT NULL, result_json TEXT, error_text TEXT,
              created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL,
              PRIMARY KEY(run_id, node_id)
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_node_queue ON workflow_node_runs(queue_id);
            CREATE INDEX IF NOT EXISTS idx_workflow_node_status ON workflow_node_runs(run_id, status);
            CREATE TABLE IF NOT EXISTS workflow_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
              node_id TEXT, event_type TEXT NOT NULL, payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_events_run ON workflow_events(run_id, id DESC);
            CREATE TABLE IF NOT EXISTS workflow_checkpoints(
              id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
              node_id TEXT NOT NULL, sequence INTEGER NOT NULL, queue_id TEXT, artifact_id TEXT,
              progress REAL, message TEXT, state_json TEXT NOT NULL, source TEXT NOT NULL,
              created_at TEXT NOT NULL, UNIQUE(run_id,node_id,sequence)
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_node ON workflow_checkpoints(run_id,node_id,sequence DESC);
            """)
            run_columns = {row["name"] for row in con.execute("PRAGMA table_info(workflow_runs)").fetchall()}
            for name, ddl in {
                "recovery_of_run_id": "TEXT",
                "recovery_generation": "INTEGER NOT NULL DEFAULT 0",
                "recovery_policy_json": "TEXT",
            }.items():
                if name not in run_columns:
                    con.execute(f"ALTER TABLE workflow_runs ADD COLUMN {name} {ddl}")
            node_columns = {row["name"] for row in con.execute("PRAGMA table_info(workflow_node_runs)").fetchall()}
            for name, ddl in {
                "skip_reason": "TEXT",
                "latest_checkpoint_id": "TEXT",
                "checkpoint_json": "TEXT",
                "checkpoint_at": "TEXT",
                "recovery_source_run_id": "TEXT",
                "recovery_source_node_id": "TEXT",
                "recovery_generation": "INTEGER NOT NULL DEFAULT 0",
            }.items():
                if name not in node_columns:
                    con.execute(f"ALTER TABLE workflow_node_runs ADD COLUMN {name} {ddl}")
            con.execute("INSERT INTO workflow_meta(key,value) VALUES('schema_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(DB_SCHEMA_VERSION),))

    @staticmethod
    def _loads(value: str | None) -> Any:
        return json.loads(value) if value else None

    def _event(self, con: sqlite3.Connection, run_id: str, node_id: str | None, event_type: str, payload: Any | None = None) -> None:
        con.execute(
            "INSERT INTO workflow_events(run_id,node_id,event_type,payload_json,created_at) VALUES(?,?,?,?,?)",
            (run_id, node_id, event_type, _stable(payload if payload is not None else {}), _now()),
        )
        con.execute("DELETE FROM workflow_events WHERE id NOT IN (SELECT id FROM workflow_events ORDER BY id DESC LIMIT ?)", (self.history_limit,))

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        workflow = normalize_workflow(payload, self.max_nodes)
        return {
            "ok": True,
            "valid": True,
            "version": VERSION,
            "workflow": workflow,
            "nodeCount": len(workflow["nodes"]),
            "edgeCount": sum(len(node["dependsOn"]) for node in workflow["nodes"]),
            "parallelEntryCount": len(workflow["entryNodes"]),
        }

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        workflow = normalize_workflow(payload, self.max_nodes)
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute("SELECT definition_hash,created_at FROM workflow_definitions WHERE id=?", (workflow["id"],)).fetchone()
            created_at = existing["created_at"] if existing else now
            workflow["createdAt"] = created_at
            con.execute(
                """INSERT INTO workflow_definitions(id,definition_hash,project_id,title,status,payload_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET definition_hash=excluded.definition_hash,
                project_id=excluded.project_id,title=excluded.title,status='active',payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (workflow["id"], workflow["definitionHash"], workflow["projectId"], workflow["title"], "active", _stable(workflow), created_at, now),
            )
            con.execute("COMMIT")
        return {"ok": True, "created": existing is None, "updated": existing is not None and existing["definition_hash"] != workflow["definitionHash"], "workflow": workflow}

    def list(self, project_id: str = "", limit: int = 100) -> dict[str, Any]:
        limit = max(1, min(1000, int(limit)))
        with self._connect() as con:
            if project_id:
                rows = con.execute("SELECT * FROM workflow_definitions WHERE project_id=? ORDER BY updated_at DESC LIMIT ?", (_text(project_id, 180), limit)).fetchall()
            else:
                rows = con.execute("SELECT * FROM workflow_definitions ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        definitions = [self._loads(row["payload_json"]) for row in rows]
        return {"ok": True, "count": len(definitions), "workflows": definitions}

    def get(self, workflow_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = con.execute("SELECT * FROM workflow_definitions WHERE id=?", (_text(workflow_id, 180),)).fetchone()
        if not row:
            raise WorkflowError("Workflow definition was not found.", 404)
        return {"ok": True, "workflow": self._loads(row["payload_json"])}

    def _node_records(self, con: sqlite3.Connection, run_id: str) -> list[sqlite3.Row]:
        return con.execute("SELECT * FROM workflow_node_runs WHERE run_id=? ORDER BY created_at,node_id", (run_id,)).fetchall()

    def _definition_node(self, definition: dict[str, Any], node_id: str) -> dict[str, Any]:
        for node in definition["nodes"]:
            if node["id"] == node_id:
                return node
        raise WorkflowError(f"Workflow node definition was not found: {node_id}")

    @staticmethod
    def _collect_artifacts(result: Any) -> list[str]:
        found: list[str] = []
        def visit(value: Any, key: str = "") -> None:
            if isinstance(value, dict):
                for child_key, child in value.items():
                    lower = child_key.lower()
                    if lower in {"artifactid", "resultartifactid", "checkpointartifactid"} and isinstance(child, str):
                        if child not in found:
                            found.append(child)
                    elif lower in {"artifactids", "artifacts", "outputartifacts"} and isinstance(child, list):
                        for item in child:
                            if isinstance(item, str) and item not in found:
                                found.append(item)
                            elif isinstance(item, dict):
                                candidate = item.get("id") or item.get("artifactId")
                                if isinstance(candidate, str) and candidate not in found:
                                    found.append(candidate)
                    visit(child, child_key)
            elif isinstance(value, list):
                for child in value:
                    visit(child, key)
        visit(result)
        return found[:100]

    @staticmethod
    def _extract_checkpoint(value: Any) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            return None
        candidates: list[dict[str, Any]] = []
        artifact_id = value.get("checkpointArtifactId")
        for key in ("latestCheckpoint", "checkpoint", "resumeCheckpoint"):
            child = value.get(key)
            if isinstance(child, dict):
                candidate = copy.deepcopy(child)
                if isinstance(artifact_id, str) and artifact_id:
                    candidate.setdefault("artifactId", artifact_id)
                candidates.append(candidate)
        if isinstance(artifact_id, str) and artifact_id and not candidates:
            candidates.append({"artifactId": artifact_id})
        for child in value.values():
            if isinstance(child, dict):
                nested = WorkflowOrchestrator._extract_checkpoint(child)
                if nested:
                    candidates.append(nested)
        if not candidates:
            return None
        checkpoint = candidates[0]
        checkpoint.setdefault("capturedAt", _now())
        return checkpoint

    @staticmethod
    def _node_succeeded(row: sqlite3.Row) -> bool:
        if row["status"] in SUCCESS_NODE_STATES:
            return True
        return row["status"] == "skipped" and row["skip_reason"] == "condition-false"

    def _capture_checkpoint(
        self,
        con: sqlite3.Connection,
        run_id: str,
        node_id: str,
        checkpoint: dict[str, Any],
        queue_id: str | None = None,
        source: str = "dispatcher-result",
        progress: float | None = None,
        message: str = "",
    ) -> dict[str, Any]:
        existing_hash = _hash(checkpoint)
        previous = con.execute(
            "SELECT * FROM workflow_checkpoints WHERE run_id=? AND node_id=? ORDER BY sequence DESC LIMIT 1",
            (run_id, node_id),
        ).fetchone()
        if previous and _hash(self._loads(previous["state_json"])) == existing_hash:
            return self._checkpoint_item(previous)
        sequence = int(previous["sequence"]) + 1 if previous else 1
        checkpoint_id = f"workflow-checkpoint-{secrets.token_hex(10)}"
        artifact_id = _text(checkpoint.get("artifactId") or checkpoint.get("checkpointArtifactId"), 220) or None
        created_at = _now()
        con.execute(
            """INSERT INTO workflow_checkpoints(id,run_id,node_id,sequence,queue_id,artifact_id,progress,message,state_json,source,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (checkpoint_id, run_id, node_id, sequence, queue_id, artifact_id, progress, _text(message, 1000), _stable(checkpoint), _text(source, 120) or "manual", created_at),
        )
        con.execute(
            "UPDATE workflow_node_runs SET latest_checkpoint_id=?,checkpoint_json=?,checkpoint_at=?,updated_at=? WHERE run_id=? AND node_id=?",
            (checkpoint_id, _stable(checkpoint), created_at, created_at, run_id, node_id),
        )
        self._event(con, run_id, node_id, "checkpoint-recorded", {"checkpointId": checkpoint_id, "sequence": sequence, "artifactId": artifact_id, "source": source})
        row = con.execute("SELECT * FROM workflow_checkpoints WHERE id=?", (checkpoint_id,)).fetchone()
        return self._checkpoint_item(row)

    def _checkpoint_item(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": CHECKPOINT_SCHEMA,
            "id": row["id"],
            "runId": row["run_id"],
            "nodeId": row["node_id"],
            "sequence": int(row["sequence"]),
            "queueId": row["queue_id"],
            "artifactId": row["artifact_id"],
            "progress": row["progress"],
            "message": row["message"],
            "state": self._loads(row["state_json"]) or {},
            "source": row["source"],
            "createdAt": row["created_at"],
        }

    def record_checkpoint(self, run_id: str, node_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload if isinstance(payload, dict) else {}
        state = payload.get("state") if isinstance(payload.get("state"), dict) else payload.get("checkpoint")
        if not isinstance(state, dict):
            state = {}
        artifact_id = _text(payload.get("artifactId") or payload.get("checkpointArtifactId"), 220)
        if artifact_id:
            state = copy.deepcopy(state)
            state["artifactId"] = artifact_id
        if not state:
            raise WorkflowError("A checkpoint requires state data or an artifact ID.")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            run = con.execute("SELECT id FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone()
            node = con.execute("SELECT * FROM workflow_node_runs WHERE run_id=? AND node_id=?", (_text(run_id, 180), _text(node_id, 180))).fetchone()
            if not run or not node:
                con.execute("ROLLBACK")
                raise WorkflowError("Workflow run or node was not found.", 404)
            item = self._capture_checkpoint(
                con, run["id"], node["node_id"], state, node["queue_id"],
                _text(payload.get("source"), 120) or "operator",
                float(payload["progress"]) if isinstance(payload.get("progress"), (int, float)) else None,
                _text(payload.get("message"), 1000),
            )
            con.execute("COMMIT")
        return {"ok": True, "checkpoint": item}

    def checkpoints(self, run_id: str, node_id: str = "", limit: int = 100) -> dict[str, Any]:
        limit = max(1, min(1000, int(limit)))
        with self._connect() as con:
            if not con.execute("SELECT id FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone():
                raise WorkflowError("Workflow run was not found.", 404)
            if node_id:
                rows = con.execute("SELECT * FROM workflow_checkpoints WHERE run_id=? AND node_id=? ORDER BY sequence DESC LIMIT ?", (_text(run_id, 180), _text(node_id, 180), limit)).fetchall()
            else:
                rows = con.execute("SELECT * FROM workflow_checkpoints WHERE run_id=? ORDER BY created_at DESC LIMIT ?", (_text(run_id, 180), limit)).fetchall()
        items = [self._checkpoint_item(row) for row in rows]
        return {"ok": True, "runId": run_id, "nodeId": node_id or None, "count": len(items), "checkpoints": items}

    def _workload_for_node(self, run: sqlite3.Row, definition: dict[str, Any], node: dict[str, Any], node_rows: dict[str, sqlite3.Row]) -> dict[str, Any]:
        request = copy.deepcopy(node["request"])
        dependency_results: dict[str, Any] = {}
        dependency_artifacts: list[str] = []
        artifact_inputs = copy.deepcopy(node["artifactInputs"])
        for dependency in node["dependsOn"]:
            dep_row = node_rows[dependency]
            result = self._loads(dep_row["result_json"])
            dependency_results[dependency] = result
            for artifact_id in self._collect_artifacts(result):
                if artifact_id not in dependency_artifacts:
                    dependency_artifacts.append(artifact_id)
                    artifact_inputs.append({"artifactId": artifact_id, "sourceNodeId": dependency, "role": "workflow-dependency"})
        for binding in node["bindings"]:
            source = dependency_results.get(binding["fromNode"])
            value = _deep_get({"result": source}, binding["sourcePath"])
            _deep_set(request, binding["targetPath"], value)
        request.setdefault("workflowContext", {})
        if not isinstance(request["workflowContext"], dict):
            raise WorkflowError(f"Workflow node {node['id']} request.workflowContext must be an object.")
        current_row = node_rows[node["id"]]
        resume_checkpoint = self._loads(current_row["checkpoint_json"])
        if isinstance(resume_checkpoint, dict):
            artifact_id = _text(resume_checkpoint.get("artifactId") or resume_checkpoint.get("checkpointArtifactId"), 220)
            if artifact_id and not any(item.get("artifactId") == artifact_id for item in artifact_inputs if isinstance(item, dict)):
                artifact_inputs.append({"artifactId": artifact_id, "sourceNodeId": node["id"], "role": "workflow-checkpoint"})
        request["workflowContext"].update({
            "workflowId": run["workflow_id"],
            "workflowRunId": run["id"],
            "workflowNodeId": node["id"],
            "definitionHash": run["definition_hash"],
            "dependsOn": node["dependsOn"],
            "dependencyResults": dependency_results,
            "dependencyArtifactIds": dependency_artifacts,
            "runInputs": self._loads(run["inputs_json"]) or {},
            "runContext": self._loads(run["context_json"]) or {},
            "resumeCheckpoint": resume_checkpoint,
            "recoveryGeneration": int(run["recovery_generation"] or 0),
            "recoveryOfRunId": run["recovery_of_run_id"],
        })
        return {
            "id": f"{run['id']}-{node['id']}",
            "title": f"{definition['title']} — {node['title']}",
            "method": node["method"],
            "projectId": run["project_id"],
            "priority": node["priority"],
            "maxAttempts": node["maxAttempts"],
            "timeoutSeconds": node["timeoutSeconds"],
            "leaseSeconds": node["leaseSeconds"],
            "requiredPackages": node["requiredPackages"],
            "requiredTags": node["requiredTags"],
            "targetPreference": node["targetPreference"],
            "minimumMemoryMb": node["minimumMemoryMb"],
            "gpuRequired": node["gpuRequired"],
            "checkpointingRequired": node["checkpointingRequired"],
            "request": request,
            "artifactInputs": artifact_inputs,
            "artifactOutputs": copy.deepcopy(node["artifactOutputs"]),
        }

    def _schedule_ready(self, con: sqlite3.Connection, run: sqlite3.Row, definition: dict[str, Any]) -> int:
        rows = self._node_records(con, run["id"])
        by_id = {row["node_id"]: row for row in rows}
        scheduled = 0
        run_inputs = self._loads(run["inputs_json"]) or {}
        run_context = self._loads(run["context_json"]) or {}
        for node_id in definition["topologicalOrder"]:
            row = by_id[node_id]
            if row["status"] != "waiting":
                continue
            node = self._definition_node(definition, node_id)
            dependency_rows = [by_id[dep] for dep in node["dependsOn"]]
            if any(dep["status"] in {"failed", "cancelled"} or (dep["status"] == "skipped" and dep["skip_reason"] != "condition-false") for dep in dependency_rows):
                now = _now()
                con.execute("UPDATE workflow_node_runs SET status='skipped',skip_reason='upstream-failure',error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", ("A dependency did not complete successfully.", now, now, run["id"], node_id))
                self._event(con, run["id"], node_id, "skipped", {"reason": "upstream-failure", "dependencyStates": [dep["status"] for dep in dependency_rows]})
                by_id[node_id] = con.execute("SELECT * FROM workflow_node_runs WHERE run_id=? AND node_id=?", (run["id"], node_id)).fetchone()
                continue
            if not all(self._node_succeeded(dep) for dep in dependency_rows):
                continue
            try:
                matched, condition_detail = _condition_result(node.get("condition"), run_inputs, run_context, by_id)
            except (TypeError, ValueError) as exc:
                now = _now()
                con.execute("UPDATE workflow_node_runs SET status='failed',error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (_text(f"Condition evaluation failed: {exc}", 2000), now, now, run["id"], node_id))
                self._event(con, run["id"], node_id, "condition-error", {"error": str(exc)})
                by_id[node_id] = con.execute("SELECT * FROM workflow_node_runs WHERE run_id=? AND node_id=?", (run["id"], node_id)).fetchone()
                continue
            if not matched:
                now = _now()
                result = {"conditionMatched": False, "condition": condition_detail}
                con.execute("UPDATE workflow_node_runs SET status='skipped',skip_reason='condition-false',result_json=?,error_text=NULL,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (_stable(result), now, now, run["id"], node_id))
                self._event(con, run["id"], node_id, "condition-skipped", condition_detail)
                by_id[node_id] = con.execute("SELECT * FROM workflow_node_runs WHERE run_id=? AND node_id=?", (run["id"], node_id)).fetchone()
                continue
            if node.get("condition"):
                self._event(con, run["id"], node_id, "condition-matched", condition_detail)
            workload = self._workload_for_node(run, definition, node, by_id)
            try:
                queued = self.dispatcher.enqueue(workload)["queueItem"]
            except DispatcherError as exc:
                raise WorkflowError(str(exc)) from exc
            now = _now()
            con.execute("UPDATE workflow_node_runs SET status='queued',queue_id=?,skip_reason=NULL,started_at=COALESCE(started_at,?),updated_at=? WHERE run_id=? AND node_id=?", (queued["id"], now, now, run["id"], node_id))
            self._event(con, run["id"], node_id, "queued", {"queueId": queued["id"], "workloadHash": queued["workload"].get("workloadHash"), "checkpointId": row["latest_checkpoint_id"]})
            by_id[node_id] = con.execute("SELECT * FROM workflow_node_runs WHERE run_id=? AND node_id=?", (run["id"], node_id)).fetchone()
            scheduled += 1
        return scheduled

    def start_run(self, workflow_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload if isinstance(payload, dict) else {}
        workflow = self.get(workflow_id)["workflow"]
        run_id = _text(payload.get("id"), 180) or f"workflow-run-{secrets.token_hex(10)}"
        if not ID_RE.match(run_id):
            raise WorkflowError("Workflow run ID is invalid.")
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            if con.execute("SELECT id FROM workflow_runs WHERE id=?", (run_id,)).fetchone():
                con.execute("ROLLBACK")
                raise WorkflowError("Workflow run ID already exists.", 409)
            active = con.execute("SELECT COUNT(*) FROM workflow_runs WHERE status IN ('pending','running')").fetchone()[0]
            if active >= self.max_runs:
                con.execute("ROLLBACK")
                raise WorkflowError("Workflow run capacity reached.", 429)
            inputs = payload.get("inputs") if isinstance(payload.get("inputs"), dict) else {}
            context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
            con.execute(
                "INSERT INTO workflow_runs(id,workflow_id,definition_hash,project_id,status,definition_json,inputs_json,context_json,recovery_generation,created_at,started_at,updated_at) VALUES(?,?,?,?,?,?,?,?,0,?,?,?)",
                (run_id, workflow["id"], workflow["definitionHash"], workflow["projectId"], "running", _stable(workflow), _stable(inputs), _stable(context), now, now, now),
            )
            for node in workflow["nodes"]:
                con.execute(
                    "INSERT INTO workflow_node_runs(run_id,node_id,status,payload_json,recovery_generation,created_at,updated_at) VALUES(?,?, 'waiting',?,0,?,?)",
                    (run_id, node["id"], _stable(node), now, now),
                )
            self._event(con, run_id, None, "run-started", {"workflowId": workflow["id"], "definitionHash": workflow["definitionHash"]})
            run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (run_id,)).fetchone()
            self._schedule_ready(con, run, workflow)
            con.execute("COMMIT")
        return self.run(run_id, reconcile=False)

    def _sync_dispatch_states(self, con: sqlite3.Connection, run: sqlite3.Row, definition: dict[str, Any]) -> int:
        changed = 0
        for row in self._node_records(con, run["id"]):
            if row["status"] not in {"queued", "running"} or not row["queue_id"]:
                continue
            try:
                queue_item = self.dispatcher.queue_item(row["queue_id"])["queueItem"]
            except DispatcherError:
                continue
            queue_status = queue_item["status"]
            now = _now()
            checkpoint = self._extract_checkpoint(queue_item.get("result"))
            if checkpoint:
                self._capture_checkpoint(con, run["id"], row["node_id"], checkpoint, row["queue_id"], "dispatcher-result")
            if queue_status in {"leased", "running"} and row["status"] != "running":
                con.execute("UPDATE workflow_node_runs SET status='running',started_at=COALESCE(started_at,?),updated_at=? WHERE run_id=? AND node_id=?", (now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "running", {"queueId": row["queue_id"], "workerId": queue_item.get("workerId")})
                changed += 1
            elif queue_status == "completed" and row["status"] != "completed":
                con.execute("UPDATE workflow_node_runs SET status='completed',result_json=?,error_text=NULL,skip_reason=NULL,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (_stable(queue_item.get("result")), now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "completed", {"queueId": row["queue_id"], "resultHash": _hash(queue_item.get("result"))})
                changed += 1
            elif queue_status in {"failed", "dead-lettered", "cancelled"} and row["status"] not in TERMINAL_NODE_STATES:
                con.execute("UPDATE workflow_node_runs SET status='failed',result_json=?,error_text=?,skip_reason=NULL,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (_stable(queue_item.get("result")), _text(queue_item.get("error") or f"Dispatcher status: {queue_status}", 2000), now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "failed", {"queueId": row["queue_id"], "queueStatus": queue_status, "failure": queue_item.get("failure"), "checkpointAvailable": bool(checkpoint)})
                changed += 1
        return changed

    def reconcile(self, run_id: str) -> dict[str, Any]:
        run_id = _text(run_id, 180)
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (run_id,)).fetchone()
            if not run:
                con.execute("ROLLBACK")
                raise WorkflowError("Workflow run was not found.", 404)
            if run["status"] in {"completed", "failed", "cancelled"}:
                con.execute("COMMIT")
                return self.run(run_id, reconcile=False)
            definition = self._loads(run["definition_json"])
            changed = self._sync_dispatch_states(con, run, definition)
            run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (run_id,)).fetchone()
            scheduled = self._schedule_ready(con, run, definition)
            rows = self._node_records(con, run_id)
            now = _now()
            if any(row["status"] == "failed" for row in rows):
                for row in rows:
                    if row["status"] == "waiting":
                        con.execute("UPDATE workflow_node_runs SET status='skipped',skip_reason='upstream-failure',error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", ("Workflow stopped after an upstream node failure.", now, now, run_id, row["node_id"]))
                        self._event(con, run_id, row["node_id"], "skipped", {"reason": "upstream-failure"})
                con.execute("UPDATE workflow_runs SET status='failed',error_text=?,completed_at=?,updated_at=? WHERE id=?", ("One or more workflow nodes failed.", now, now, run_id))
                self._event(con, run_id, None, "run-failed", {"failedNodes": [row["node_id"] for row in rows if row["status"] == "failed"]})
            elif rows and all(self._node_succeeded(row) for row in rows):
                con.execute("UPDATE workflow_runs SET status='completed',error_text=NULL,completed_at=?,updated_at=? WHERE id=?", (now, now, run_id))
                self._event(con, run_id, None, "run-completed", {"nodeCount": len(rows), "conditionSkipped": [row["node_id"] for row in rows if row["status"] == "skipped"]})
            else:
                con.execute("UPDATE workflow_runs SET status='running',updated_at=? WHERE id=?", (now, run_id))
            con.execute("COMMIT")
        result = self.run(run_id, reconcile=False)
        result["reconciliation"] = {"changedNodes": changed, "scheduledNodes": scheduled}
        return result

    def run(self, run_id: str, reconcile: bool = True) -> dict[str, Any]:
        if reconcile:
            return self.reconcile(run_id)
        with self._connect() as con:
            run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone()
            if not run:
                raise WorkflowError("Workflow run was not found.", 404)
            nodes = self._node_records(con, run["id"])
        node_items = []
        for row in nodes:
            node_items.append({
                "schema": NODE_SCHEMA,
                "runId": row["run_id"],
                "nodeId": row["node_id"],
                "status": row["status"],
                "queueId": row["queue_id"],
                "definition": self._loads(row["payload_json"]),
                "result": self._loads(row["result_json"]),
                "error": row["error_text"],
                "skipReason": row["skip_reason"],
                "latestCheckpointId": row["latest_checkpoint_id"],
                "latestCheckpoint": self._loads(row["checkpoint_json"]),
                "checkpointAt": row["checkpoint_at"],
                "recoverySourceRunId": row["recovery_source_run_id"],
                "recoverySourceNodeId": row["recovery_source_node_id"],
                "recoveryGeneration": int(row["recovery_generation"] or 0),
                "createdAt": row["created_at"],
                "startedAt": row["started_at"],
                "completedAt": row["completed_at"],
                "updatedAt": row["updated_at"],
            })
        counts = {state: 0 for state in NODE_STATES}
        for node in node_items:
            counts[node["status"]] += 1
        return {
            "ok": True,
            "run": {
                "schema": RUN_SCHEMA,
                "version": VERSION,
                "recordType": "workflow-run",
                "id": run["id"],
                "workflowId": run["workflow_id"],
                "definitionHash": run["definition_hash"],
                "projectId": run["project_id"],
                "status": run["status"],
                "inputs": self._loads(run["inputs_json"]),
                "context": self._loads(run["context_json"]),
                "error": run["error_text"],
                "recoveryOfRunId": run["recovery_of_run_id"],
                "recoveryGeneration": int(run["recovery_generation"] or 0),
                "recoveryPolicy": self._loads(run["recovery_policy_json"]),
                "createdAt": run["created_at"],
                "startedAt": run["started_at"],
                "completedAt": run["completed_at"],
                "updatedAt": run["updated_at"],
                "nodeCounts": counts,
                "nodes": node_items,
            },
        }

    def runs(self, workflow_id: str = "", project_id: str = "", status: str = "", limit: int = 100) -> dict[str, Any]:
        limit = max(1, min(1000, int(limit)))
        clauses: list[str] = []
        params: list[Any] = []
        if workflow_id:
            clauses.append("workflow_id=?")
            params.append(_text(workflow_id, 180))
        if project_id:
            clauses.append("project_id=?")
            params.append(_text(project_id, 180))
        if status:
            if status not in RUN_STATES:
                raise WorkflowError("Unsupported workflow run status.")
            clauses.append("status=?")
            params.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(limit)
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM workflow_runs{where} ORDER BY created_at DESC LIMIT ?", params).fetchall()
        items = [{
            "schema": RUN_SCHEMA,
            "id": row["id"],
            "workflowId": row["workflow_id"],
            "projectId": row["project_id"],
            "definitionHash": row["definition_hash"],
            "status": row["status"],
            "error": row["error_text"],
            "recoveryOfRunId": row["recovery_of_run_id"],
            "recoveryGeneration": int(row["recovery_generation"] or 0),
            "createdAt": row["created_at"],
            "startedAt": row["started_at"],
            "completedAt": row["completed_at"],
            "updatedAt": row["updated_at"],
        } for row in rows]
        return {"ok": True, "count": len(items), "runs": items}

    def _descendants(self, definition: dict[str, Any], seeds: set[str]) -> set[str]:
        downstream: dict[str, set[str]] = {node["id"]: set() for node in definition["nodes"]}
        for node in definition["nodes"]:
            for dependency in node["dependsOn"]:
                downstream[dependency].add(node["id"])
        result = set(seeds)
        queue = list(seeds)
        while queue:
            current = queue.pop(0)
            for child in downstream.get(current, set()):
                if child not in result:
                    result.add(child)
                    queue.append(child)
        return result

    def recovery_plan(self, run_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload if isinstance(payload, dict) else {}
        with self._connect() as con:
            run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone()
            if not run:
                raise WorkflowError("Workflow run was not found.", 404)
            rows = self._node_records(con, run["id"])
            definition = self._loads(run["definition_json"])
        known = {row["node_id"] for row in rows}
        explicit = payload.get("restartNodes") if isinstance(payload.get("restartNodes"), list) else []
        seeds = {_text(item, 180) for item in explicit if _text(item, 180)}
        unknown = sorted(seeds - known)
        if unknown:
            raise WorkflowError(f"Unknown recovery node IDs: {', '.join(unknown)}")
        if not seeds:
            seeds = {row["node_id"] for row in rows if row["status"] in {"failed", "cancelled"} or (row["status"] == "skipped" and row["skip_reason"] == "upstream-failure")}
        if not seeds:
            raise WorkflowError("No failed nodes were found. Provide restartNodes to recover a completed run.")
        include_downstream = payload.get("includeDownstream", True) is not False
        restart = self._descendants(definition, seeds) if include_downstream else set(seeds)
        reusable: list[str] = []
        checkpoints: list[dict[str, Any]] = []
        blocked: list[str] = []
        for row in rows:
            if row["node_id"] in restart:
                if row["checkpoint_json"]:
                    checkpoints.append({"nodeId": row["node_id"], "checkpointId": row["latest_checkpoint_id"], "checkpoint": self._loads(row["checkpoint_json"])})
                continue
            if self._node_succeeded(row):
                reusable.append(row["node_id"])
            else:
                restart.add(row["node_id"])
                blocked.append(row["node_id"])
        return {
            "ok": True,
            "plan": {
                "schema": RECOVERY_SCHEMA,
                "sourceRunId": run["id"],
                "workflowId": run["workflow_id"],
                "sourceStatus": run["status"],
                "sourceRecoveryGeneration": int(run["recovery_generation"] or 0),
                "restartSeedNodes": sorted(seeds),
                "restartNodes": [node_id for node_id in definition["topologicalOrder"] if node_id in restart],
                "reuseNodes": [node_id for node_id in definition["topologicalOrder"] if node_id in reusable],
                "checkpointCandidates": checkpoints,
                "forcedRestartNodes": blocked,
                "includeDownstream": include_downstream,
                "resumeFromCheckpoints": payload.get("resumeFromCheckpoints", True) is not False,
                "createdAt": _now(),
            },
        }

    def recover(self, run_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload if isinstance(payload, dict) else {}
        plan = self.recovery_plan(run_id, payload)["plan"]
        now = _now()
        new_run_id = _text(payload.get("id"), 180) or f"workflow-recovery-{secrets.token_hex(10)}"
        if not ID_RE.match(new_run_id):
            raise WorkflowError("Recovery run ID is invalid.")
        operator = _text(payload.get("operatorId"), 180) or "operator"
        reason = _text(payload.get("reason"), 1000) or "partial workflow recovery"
        resume = plan["resumeFromCheckpoints"]
        restart = set(plan["restartNodes"])
        reuse = set(plan["reuseNodes"])
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            source_run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone()
            if not source_run:
                con.execute("ROLLBACK")
                raise WorkflowError("Workflow run was not found.", 404)
            if source_run["status"] not in {"completed", "failed", "cancelled"}:
                con.execute("ROLLBACK")
                raise WorkflowError("Only terminal workflow runs can be recovered. Cancel or finish the source run first.", 409)
            if con.execute("SELECT id FROM workflow_runs WHERE id=?", (new_run_id,)).fetchone():
                con.execute("ROLLBACK")
                raise WorkflowError("Recovery run ID already exists.", 409)
            generation = int(source_run["recovery_generation"] or 0) + 1
            definition = self._loads(source_run["definition_json"])
            policy = {"operatorId": operator, "reason": reason, **plan}
            con.execute(
                """INSERT INTO workflow_runs(id,workflow_id,definition_hash,project_id,status,definition_json,inputs_json,context_json,error_text,
                recovery_of_run_id,recovery_generation,recovery_policy_json,created_at,started_at,updated_at)
                VALUES(?,?,?,?, 'running',?,?,?,?,?,?,?,?,?,?)""",
                (new_run_id, source_run["workflow_id"], source_run["definition_hash"], source_run["project_id"], source_run["definition_json"], source_run["inputs_json"], source_run["context_json"], None, source_run["id"], generation, _stable(policy), now, now, now),
            )
            source_rows = {row["node_id"]: row for row in self._node_records(con, source_run["id"])}
            for node in definition["nodes"]:
                source = source_rows[node["id"]]
                if node["id"] in reuse:
                    status = "skipped" if source["status"] == "skipped" else "reused"
                    con.execute(
                        """INSERT INTO workflow_node_runs(run_id,node_id,status,queue_id,payload_json,result_json,error_text,skip_reason,
                        latest_checkpoint_id,checkpoint_json,checkpoint_at,recovery_source_run_id,recovery_source_node_id,recovery_generation,
                        created_at,started_at,completed_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_run_id, node["id"], status, None, source["payload_json"], source["result_json"], None, source["skip_reason"], source["latest_checkpoint_id"], source["checkpoint_json"], source["checkpoint_at"], source_run["id"], source["node_id"], generation, now, now, now, now),
                    )
                    self._event(con, new_run_id, node["id"], "node-reused", {"sourceRunId": source_run["id"], "sourceNodeId": source["node_id"], "sourceStatus": source["status"]})
                else:
                    checkpoint_json = source["checkpoint_json"] if resume and node["id"] in restart else None
                    checkpoint_id = source["latest_checkpoint_id"] if checkpoint_json else None
                    checkpoint_at = source["checkpoint_at"] if checkpoint_json else None
                    con.execute(
                        """INSERT INTO workflow_node_runs(run_id,node_id,status,payload_json,latest_checkpoint_id,checkpoint_json,checkpoint_at,
                        recovery_source_run_id,recovery_source_node_id,recovery_generation,created_at,updated_at)
                        VALUES(?,?, 'waiting',?,?,?,?,?,?,?,?,?)""",
                        (new_run_id, node["id"], source["payload_json"], checkpoint_id, checkpoint_json, checkpoint_at, source_run["id"], source["node_id"], generation, now, now),
                    )
                    if checkpoint_json:
                        self._event(con, new_run_id, node["id"], "checkpoint-reused", {"sourceRunId": source_run["id"], "checkpointId": checkpoint_id})
            self._event(con, new_run_id, None, "run-recovered", {"sourceRunId": source_run["id"], "generation": generation, "restartNodes": plan["restartNodes"], "reuseNodes": plan["reuseNodes"], "operatorId": operator, "reason": reason})
            new_run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (new_run_id,)).fetchone()
            scheduled = self._schedule_ready(con, new_run, definition)
            con.execute("COMMIT")
        result = self.run(new_run_id, reconcile=False)
        result["recovery"] = {"plan": plan, "scheduledNodes": scheduled}
        return result

    def restart_node(self, run_id: str, node_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = copy.deepcopy(payload) if isinstance(payload, dict) else {}
        payload["restartNodes"] = [node_id]
        payload.setdefault("includeDownstream", True)
        return self.recover(run_id, payload)

    def cancel(self, run_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload if isinstance(payload, dict) else {}
        reason = _text(payload.get("reason"), 1000) or "workflow run cancelled by operator"
        operator = _text(payload.get("operatorId"), 180) or "operator"
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            run = con.execute("SELECT * FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone()
            if not run:
                con.execute("ROLLBACK")
                raise WorkflowError("Workflow run was not found.", 404)
            if run["status"] == "completed":
                con.execute("ROLLBACK")
                raise WorkflowError("Completed workflow runs cannot be cancelled.")
            for row in self._node_records(con, run["id"]):
                if row["status"] in TERMINAL_NODE_STATES:
                    continue
                if row["queue_id"]:
                    try:
                        self.dispatcher.cancel_queue_item(row["queue_id"], {"operatorId": operator, "reason": reason})
                    except DispatcherError:
                        pass
                con.execute("UPDATE workflow_node_runs SET status='cancelled',error_text=?,skip_reason=NULL,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (reason, now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "cancelled", {"operatorId": operator, "reason": reason})
            con.execute("UPDATE workflow_runs SET status='cancelled',error_text=?,completed_at=?,updated_at=? WHERE id=?", (reason, now, now, run["id"]))
            self._event(con, run["id"], None, "run-cancelled", {"operatorId": operator, "reason": reason})
            con.execute("COMMIT")
        return self.run(run_id, reconcile=False)

    def timeline(self, run_id: str, limit: int = 500) -> dict[str, Any]:
        limit = max(1, min(2000, int(limit)))
        with self._connect() as con:
            if not con.execute("SELECT id FROM workflow_runs WHERE id=?", (_text(run_id, 180),)).fetchone():
                raise WorkflowError("Workflow run was not found.", 404)
            rows = con.execute("SELECT * FROM workflow_events WHERE run_id=? ORDER BY id DESC LIMIT ?", (_text(run_id, 180), limit)).fetchall()
        events = [{
            "schema": EVENT_SCHEMA,
            "id": row["id"],
            "runId": row["run_id"],
            "nodeId": row["node_id"],
            "eventType": row["event_type"],
            "payload": self._loads(row["payload_json"]),
            "createdAt": row["created_at"],
        } for row in rows]
        return {"ok": True, "runId": run_id, "count": len(events), "events": events}

    def health(self) -> dict[str, Any]:
        path = Path(self.db_path)
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            definitions = con.execute("SELECT COUNT(*) FROM workflow_definitions").fetchone()[0]
            runs = con.execute("SELECT COUNT(*) FROM workflow_runs").fetchone()[0]
            active = con.execute("SELECT COUNT(*) FROM workflow_runs WHERE status IN ('pending','running')").fetchone()[0]
            recoveries = con.execute("SELECT COUNT(*) FROM workflow_runs WHERE recovery_of_run_id IS NOT NULL").fetchone()[0]
            checkpoints = con.execute("SELECT COUNT(*) FROM workflow_checkpoints").fetchone()[0]
            conditional = con.execute("SELECT COUNT(*) FROM workflow_node_runs WHERE skip_reason='condition-false'").fetchone()[0]
            reused = con.execute("SELECT COUNT(*) FROM workflow_node_runs WHERE status='reused'").fetchone()[0]
            nodes = con.execute("SELECT status,COUNT(*) n FROM workflow_node_runs GROUP BY status").fetchall()
            schema = con.execute("SELECT value FROM workflow_meta WHERE key='schema_version'").fetchone()
        counts = {state: 0 for state in NODE_STATES}
        counts.update({row["status"]: row["n"] for row in nodes})
        return {
            "ok": integrity == "ok",
            "status": "ready" if integrity == "ok" else "degraded",
            "version": VERSION,
            "architecture": "checkpoint-aware-conditional-scientific-workflow-orchestrator",
            "storage": "sqlite-wal",
            "schemaVersion": int(schema["value"]) if schema else DB_SCHEMA_VERSION,
            "databasePath": self.db_path,
            "databaseBytes": path.stat().st_size if path.exists() else 0,
            "definitionCount": definitions,
            "runCount": runs,
            "activeRunCount": active,
            "recoveryRunCount": recoveries,
            "checkpointCount": checkpoints,
            "conditionalSkipCount": conditional,
            "reusedNodeCount": reused,
            "nodeCounts": counts,
            "dagValidation": True,
            "dependencyAwareScheduling": True,
            "parallelReadyNodes": True,
            "declarativeConditions": True,
            "checkpointHistory": True,
            "partialRecovery": True,
            "resultBindings": True,
            "artifactHandoffs": True,
            "dispatcherBacked": True,
            "integrityCheck": integrity,
        }

