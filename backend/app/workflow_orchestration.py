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

VERSION = "0.32.0"
WORKFLOW_SCHEMA = "sc-lab-scientific-workflow/0.32.0"
RUN_SCHEMA = "sc-lab-workflow-run/0.32.0"
NODE_SCHEMA = "sc-lab-workflow-node-run/0.32.0"
EVENT_SCHEMA = "sc-lab-workflow-event/0.32.0"
DB_SCHEMA_VERSION = 1
RUN_STATES = {"pending", "running", "completed", "failed", "cancelled"}
NODE_STATES = {"waiting", "queued", "running", "completed", "failed", "skipped", "cancelled"}
TERMINAL_NODE_STATES = {"completed", "failed", "skipped", "cancelled"}
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


def policies(max_nodes: int = 100, max_runs: int = 5000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "typed-scientific-workflow-dag-orchestrator",
        "definitions": {
            "typedNodes": True,
            "acyclicGraphsRequired": True,
            "immutableRunSnapshots": True,
            "maximumNodes": max_nodes,
        },
        "execution": {
            "dependencyAwareScheduling": True,
            "dispatcherBackedNodes": True,
            "parallelReadyNodes": True,
            "nodeRetriesDelegatedToDispatcher": True,
            "automaticDownstreamBlocking": True,
            "manualReconciliation": True,
        },
        "handoffs": {
            "resultBindings": True,
            "artifactInputs": True,
            "dependencyArtifactPropagation": True,
            "arbitraryCode": False,
            "arbitraryCallbackUrls": False,
        },
        "provenance": {
            "definitionHash": True,
            "runTimeline": True,
            "queueIdentifiers": True,
            "nodeResults": True,
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
            "schema": "sc-lab-workflow-node/0.32.0",
            "id": node_id,
            "title": _text(raw.get("title"), 300) or node_id.replace("-", " ").replace("_", " ").title(),
            "method": method,
            "dependsOn": depends_on,
            "bindings": bindings,
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
            """)
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
        for node_id in definition["topologicalOrder"]:
            row = by_id[node_id]
            if row["status"] != "waiting":
                continue
            node = self._definition_node(definition, node_id)
            dependency_states = [by_id[dep]["status"] for dep in node["dependsOn"]]
            if any(state in {"failed", "cancelled", "skipped"} for state in dependency_states):
                now = _now()
                con.execute("UPDATE workflow_node_runs SET status='skipped',error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", ("A dependency did not complete successfully.", now, now, run["id"], node_id))
                self._event(con, run["id"], node_id, "skipped", {"dependencyStates": dependency_states})
                continue
            if not all(state == "completed" for state in dependency_states):
                continue
            workload = self._workload_for_node(run, definition, node, by_id)
            try:
                queued = self.dispatcher.enqueue(workload)["queueItem"]
            except DispatcherError as exc:
                raise WorkflowError(str(exc)) from exc
            now = _now()
            con.execute("UPDATE workflow_node_runs SET status='queued',queue_id=?,started_at=COALESCE(started_at,?),updated_at=? WHERE run_id=? AND node_id=?", (queued["id"], now, now, run["id"], node_id))
            self._event(con, run["id"], node_id, "queued", {"queueId": queued["id"], "workloadHash": queued["workload"].get("workloadHash")})
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
                "INSERT INTO workflow_runs(id,workflow_id,definition_hash,project_id,status,definition_json,inputs_json,context_json,created_at,started_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (run_id, workflow["id"], workflow["definitionHash"], workflow["projectId"], "running", _stable(workflow), _stable(inputs), _stable(context), now, now, now),
            )
            for node in workflow["nodes"]:
                con.execute(
                    "INSERT INTO workflow_node_runs(run_id,node_id,status,payload_json,created_at,updated_at) VALUES(?,?, 'waiting',?,?,?)",
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
            if queue_status in {"leased", "running"} and row["status"] != "running":
                con.execute("UPDATE workflow_node_runs SET status='running',started_at=COALESCE(started_at,?),updated_at=? WHERE run_id=? AND node_id=?", (now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "running", {"queueId": row["queue_id"], "workerId": queue_item.get("workerId")})
                changed += 1
            elif queue_status == "completed" and row["status"] != "completed":
                con.execute("UPDATE workflow_node_runs SET status='completed',result_json=?,error_text=NULL,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (_stable(queue_item.get("result")), now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "completed", {"queueId": row["queue_id"], "resultHash": _hash(queue_item.get("result"))})
                changed += 1
            elif queue_status in {"failed", "dead-lettered", "cancelled"} and row["status"] not in TERMINAL_NODE_STATES:
                con.execute("UPDATE workflow_node_runs SET status='failed',result_json=?,error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (_stable(queue_item.get("result")), _text(queue_item.get("error") or f"Dispatcher status: {queue_status}", 2000), now, now, run["id"], row["node_id"]))
                self._event(con, run["id"], row["node_id"], "failed", {"queueId": row["queue_id"], "queueStatus": queue_status, "failure": queue_item.get("failure")})
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
            statuses = [row["status"] for row in rows]
            now = _now()
            if any(status == "failed" for status in statuses):
                run_status = "failed"
                error = "One or more workflow nodes failed."
                for row in rows:
                    if row["status"] == "waiting":
                        con.execute("UPDATE workflow_node_runs SET status='skipped',error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", ("Workflow stopped after an upstream node failure.", now, now, run_id, row["node_id"]))
                        self._event(con, run_id, row["node_id"], "skipped", {"reason": "upstream-failure"})
                con.execute("UPDATE workflow_runs SET status=?,error_text=?,completed_at=?,updated_at=? WHERE id=?", (run_status, error, now, now, run_id))
                self._event(con, run_id, None, "run-failed", {"failedNodes": [row["node_id"] for row in rows if row["status"] == "failed"]})
            elif statuses and all(status == "completed" for status in statuses):
                con.execute("UPDATE workflow_runs SET status='completed',completed_at=?,updated_at=? WHERE id=?", (now, now, run_id))
                self._event(con, run_id, None, "run-completed", {"nodeCount": len(rows)})
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
            "createdAt": row["created_at"],
            "startedAt": row["started_at"],
            "completedAt": row["completed_at"],
            "updatedAt": row["updated_at"],
        } for row in rows]
        return {"ok": True, "count": len(items), "runs": items}

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
                con.execute("UPDATE workflow_node_runs SET status='cancelled',error_text=?,completed_at=?,updated_at=? WHERE run_id=? AND node_id=?", (reason, now, now, run["id"], row["node_id"]))
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
            nodes = con.execute("SELECT status,COUNT(*) n FROM workflow_node_runs GROUP BY status").fetchall()
            schema = con.execute("SELECT value FROM workflow_meta WHERE key='schema_version'").fetchone()
        counts = {state: 0 for state in NODE_STATES}
        counts.update({row["status"]: row["n"] for row in nodes})
        return {
            "ok": integrity == "ok",
            "status": "ready" if integrity == "ok" else "degraded",
            "version": VERSION,
            "architecture": "typed-scientific-workflow-dag-orchestrator",
            "storage": "sqlite-wal",
            "schemaVersion": int(schema["value"]) if schema else DB_SCHEMA_VERSION,
            "databasePath": self.db_path,
            "databaseBytes": path.stat().st_size if path.exists() else 0,
            "definitionCount": definitions,
            "runCount": runs,
            "activeRunCount": active,
            "nodeCounts": counts,
            "dagValidation": True,
            "dependencyAwareScheduling": True,
            "parallelReadyNodes": True,
            "resultBindings": True,
            "artifactHandoffs": True,
            "dispatcherBacked": True,
            "integrityCheck": integrity,
        }
