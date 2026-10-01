from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.153.0"
ASSET_SCHEMA = "sc-lab-4d-computational-workspace-asset/0.153.0"
REVISION_SCHEMA = "sc-lab-4d-computational-workspace-revision/0.153.0"
LINEAGE_SCHEMA = "sc-lab-4d-computational-workspace-lineage/0.153.0"
COMPARE_SCHEMA = "sc-lab-4d-computational-workspace-comparison/0.153.0"
BOUNDARY = (
    "Workspace persistence preserves computational scene state, compute references, selections, provenance, "
    "and explicit lineage. It does not establish evidence, causality, significance, calibration, or scientific validity."
)


class ComputationalResearchWorkspaceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip()
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise ComputationalResearchWorkspaceError(f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 240, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ComputationalResearchWorkspaceError(f"{label} is required.")
    if len(text) > maximum:
        raise ComputationalResearchWorkspaceError(f"{label} exceeds {maximum} characters.")
    return text


def _bounded_json(value: Any, label: str, maximum_bytes: int = 1_500_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise ComputationalResearchWorkspaceError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise ComputationalResearchWorkspaceError(f"{label} exceeds the workspace payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


def _normalize_refs(value: Any, maximum: int = 200) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value[:maximum]:
        if isinstance(item, str):
            ref = item.strip()
            if ref:
                out.append({"ref": ref[:300]})
        elif isinstance(item, dict):
            ref = str(item.get("ref") or item.get("id") or item.get("runId") or item.get("resultId") or "").strip()
            if ref:
                row = {"ref": ref[:300]}
                for key in ("kind", "method", "createdAt", "digest"):
                    if item.get(key) is not None:
                        row[key] = str(item.get(key))[:300]
                out.append(row)
    return out


class ComputationalResearchWorkspaceManager:
    def __init__(self, db_path: str, persistent_disk_mounted: bool = False, max_assets_per_project: int = 500, history_limit: int = 100000) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_assets_per_project = max(1, int(max_assets_per_project))
        self.history_limit = max(100, int(history_limit))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS crw_assets(
                  id TEXT PRIMARY KEY,
                  project_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  status TEXT NOT NULL,
                  parent_asset_id TEXT,
                  source_scene_id TEXT,
                  latest_revision_id TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  actor TEXT NOT NULL,
                  metadata_json TEXT NOT NULL,
                  asset_hash TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS crw_assets_project_idx ON crw_assets(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS crw_revisions(
                  id TEXT PRIMARY KEY,
                  asset_id TEXT NOT NULL,
                  revision_no INTEGER NOT NULL,
                  scene_digest TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  actor TEXT NOT NULL,
                  scene_json TEXT NOT NULL,
                  provenance_json TEXT NOT NULL,
                  compute_refs_json TEXT NOT NULL,
                  research_object_json TEXT NOT NULL,
                  revision_hash TEXT NOT NULL,
                  UNIQUE(asset_id, revision_no),
                  FOREIGN KEY(asset_id) REFERENCES crw_assets(id)
                );
                CREATE INDEX IF NOT EXISTS crw_revisions_asset_idx ON crw_revisions(asset_id, revision_no DESC);
                CREATE TABLE IF NOT EXISTS crw_events(
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  asset_id TEXT NOT NULL,
                  project_id TEXT NOT NULL,
                  event_type TEXT NOT NULL,
                  occurred_at TEXT NOT NULL,
                  actor TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  previous_hash TEXT NOT NULL,
                  event_hash TEXT NOT NULL
                );
                """
            )

    def _event(self, db: sqlite3.Connection, asset_id: str, project_id: str, event_type: str, actor: str, payload: Any) -> None:
        row = db.execute("SELECT event_hash FROM crw_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = str(row["event_hash"]) if row else ""
        occurred = _now()
        envelope = {"assetId": asset_id, "projectId": project_id, "eventType": event_type, "occurredAt": occurred, "actor": actor, "payload": payload, "previousHash": previous}
        event_hash = _sha(envelope)
        db.execute(
            "INSERT INTO crw_events(asset_id,project_id,event_type,occurred_at,actor,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (asset_id, project_id, event_type, occurred, actor, json.dumps(payload, sort_keys=True), previous, event_hash),
        )
        db.execute("DELETE FROM crw_events WHERE seq NOT IN (SELECT seq FROM crw_events ORDER BY seq DESC LIMIT ?)", (self.history_limit,))

    @staticmethod
    def _asset_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": ASSET_SCHEMA,
            "id": row["id"],
            "projectId": row["project_id"],
            "title": row["title"],
            "status": row["status"],
            "parentAssetId": row["parent_asset_id"],
            "sourceSceneId": row["source_scene_id"],
            "latestRevisionId": row["latest_revision_id"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
            "metadata": json.loads(row["metadata_json"] or "{}"),
            "assetHash": row["asset_hash"],
        }

    @staticmethod
    def _revision_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": REVISION_SCHEMA,
            "id": row["id"],
            "assetId": row["asset_id"],
            "revision": int(row["revision_no"]),
            "sceneDigest": row["scene_digest"],
            "createdAt": row["created_at"],
            "actor": row["actor"],
            "scene": json.loads(row["scene_json"] or "{}"),
            "provenance": json.loads(row["provenance_json"] or "{}"),
            "computeRefs": json.loads(row["compute_refs_json"] or "[]"),
            "researchObject": json.loads(row["research_object_json"] or "{}"),
            "revisionHash": row["revision_hash"],
        }

    def health(self) -> dict[str, Any]:
        with self._connect() as db:
            assets = int(db.execute("SELECT COUNT(*) AS n FROM crw_assets").fetchone()["n"])
            revisions = int(db.execute("SELECT COUNT(*) AS n FROM crw_revisions").fetchone()["n"])
        return {
            "ok": True,
            "status": "ready",
            "version": VERSION,
            "assetSchema": ASSET_SCHEMA,
            "revisionSchema": REVISION_SCHEMA,
            "lineageSchema": LINEAGE_SCHEMA,
            "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local-volume",
            "serverBackedProjectAssets": True,
            "immutableRevisions": True,
            "forkLineage": True,
            "comparison": True,
            "automaticCompute": False,
            "automaticScientificValidity": False,
            "counts": {"assets": assets, "revisions": revisions},
            "boundary": BOUNDARY,
        }

    def policies(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "maxAssetsPerProject": self.max_assets_per_project,
            "maxSceneBytes": 1_500_000,
            "maxComputeRefs": 200,
            "revisionsImmutable": True,
            "archiveInsteadOfDelete": True,
            "forkRequiresExplicitAction": True,
            "compareIsDescriptiveOnly": True,
            "automaticCompute": False,
            "automaticCoreSubmission": False,
            "boundary": BOUNDARY,
        }

    def create_asset(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project ID")
        title = _clean_text(payload.get("title") or "4D computational scene", "title", 160)
        scene = _bounded_json(payload.get("scene") or {}, "scene")
        provenance = _bounded_json(payload.get("provenance") or {}, "provenance", 300_000)
        research_object = _bounded_json(payload.get("researchObject") or {}, "researchObject", 500_000)
        compute_refs = _normalize_refs(payload.get("computeRefs"))
        metadata = _bounded_json(payload.get("metadata") or {}, "metadata", 100_000)
        parent_asset_id = str(payload.get("parentAssetId") or "").strip() or None
        if parent_asset_id:
            parent_asset_id = _clean_id(parent_asset_id, "parent asset ID")
        source_scene_id = str(payload.get("sourceSceneId") or scene.get("id") or "").strip()[:180] or None
        asset_id = _clean_id(payload.get("assetId") or f"4dws:{uuid.uuid4().hex}", "asset ID")
        stamp = _now()
        with self._lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) AS n FROM crw_assets WHERE project_id=? AND status!='archived'", (project_id,)).fetchone()["n"])
            if count >= self.max_assets_per_project:
                raise ComputationalResearchWorkspaceError("Project workspace asset limit reached.", 409)
            if db.execute("SELECT 1 FROM crw_assets WHERE id=?", (asset_id,)).fetchone():
                raise ComputationalResearchWorkspaceError("Workspace asset already exists.", 409)
            if parent_asset_id and not db.execute("SELECT 1 FROM crw_assets WHERE id=?", (parent_asset_id,)).fetchone():
                raise ComputationalResearchWorkspaceError("Parent workspace asset does not exist.", 404)
            revision_id = f"4drev:{uuid.uuid4().hex}"
            scene_digest = str((provenance.get("integrity") or {}).get("sceneStateDigest") or _sha(scene))
            revision_payload = {"scene": scene, "provenance": provenance, "computeRefs": compute_refs, "researchObject": research_object}
            revision_hash = _sha({"assetId": asset_id, "revision": 1, **revision_payload})
            asset_hash = _sha({"id": asset_id, "projectId": project_id, "title": title, "parentAssetId": parent_asset_id, "sourceSceneId": source_scene_id, "createdAt": stamp})
            db.execute(
                "INSERT INTO crw_assets(id,project_id,title,status,parent_asset_id,source_scene_id,latest_revision_id,created_at,updated_at,actor,metadata_json,asset_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (asset_id, project_id, title, "active", parent_asset_id, source_scene_id, revision_id, stamp, stamp, actor, json.dumps(metadata, sort_keys=True), asset_hash),
            )
            db.execute(
                "INSERT INTO crw_revisions(id,asset_id,revision_no,scene_digest,created_at,actor,scene_json,provenance_json,compute_refs_json,research_object_json,revision_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (revision_id, asset_id, 1, scene_digest, stamp, actor, json.dumps(scene, sort_keys=True), json.dumps(provenance, sort_keys=True), json.dumps(compute_refs, sort_keys=True), json.dumps(research_object, sort_keys=True), revision_hash),
            )
            self._event(db, asset_id, project_id, "asset-created", actor, {"revisionId": revision_id, "parentAssetId": parent_asset_id})
            db.commit()
        return self.get_asset(asset_id)

    def list_assets(self, project_id: str, limit: int = 100, include_archived: bool = False) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project ID")
        limit = max(1, min(500, int(limit)))
        with self._connect() as db:
            if include_archived:
                rows = db.execute("SELECT * FROM crw_assets WHERE project_id=? ORDER BY updated_at DESC LIMIT ?", (project_id, limit)).fetchall()
            else:
                rows = db.execute("SELECT * FROM crw_assets WHERE project_id=? AND status!='archived' ORDER BY updated_at DESC LIMIT ?", (project_id, limit)).fetchall()
        return {"ok": True, "version": VERSION, "projectId": project_id, "assets": [self._asset_row(r) for r in rows], "count": len(rows), "boundary": BOUNDARY}

    def get_asset(self, asset_id: str) -> dict[str, Any]:
        asset_id = _clean_id(asset_id, "asset ID")
        with self._connect() as db:
            row = db.execute("SELECT * FROM crw_assets WHERE id=?", (asset_id,)).fetchone()
            if not row:
                raise ComputationalResearchWorkspaceError("Workspace asset not found.", 404)
            revisions = db.execute("SELECT * FROM crw_revisions WHERE asset_id=? ORDER BY revision_no DESC", (asset_id,)).fetchall()
        return {"ok": True, "version": VERSION, "asset": self._asset_row(row), "revisions": [self._revision_row(r) for r in revisions], "boundary": BOUNDARY}

    def add_revision(self, asset_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        asset_id = _clean_id(asset_id, "asset ID")
        scene = _bounded_json(payload.get("scene") or {}, "scene")
        provenance = _bounded_json(payload.get("provenance") or {}, "provenance", 300_000)
        research_object = _bounded_json(payload.get("researchObject") or {}, "researchObject", 500_000)
        compute_refs = _normalize_refs(payload.get("computeRefs"))
        with self._lock, self._connect() as db:
            asset = db.execute("SELECT * FROM crw_assets WHERE id=?", (asset_id,)).fetchone()
            if not asset:
                raise ComputationalResearchWorkspaceError("Workspace asset not found.", 404)
            if asset["status"] == "archived":
                raise ComputationalResearchWorkspaceError("Archived workspace assets cannot receive new revisions.", 409)
            rev_no = int(db.execute("SELECT COALESCE(MAX(revision_no),0)+1 AS n FROM crw_revisions WHERE asset_id=?", (asset_id,)).fetchone()["n"])
            revision_id = f"4drev:{uuid.uuid4().hex}"
            stamp = _now()
            scene_digest = str((provenance.get("integrity") or {}).get("sceneStateDigest") or _sha(scene))
            revision_hash = _sha({"assetId": asset_id, "revision": rev_no, "scene": scene, "provenance": provenance, "computeRefs": compute_refs, "researchObject": research_object})
            db.execute(
                "INSERT INTO crw_revisions(id,asset_id,revision_no,scene_digest,created_at,actor,scene_json,provenance_json,compute_refs_json,research_object_json,revision_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (revision_id, asset_id, rev_no, scene_digest, stamp, actor, json.dumps(scene, sort_keys=True), json.dumps(provenance, sort_keys=True), json.dumps(compute_refs, sort_keys=True), json.dumps(research_object, sort_keys=True), revision_hash),
            )
            db.execute("UPDATE crw_assets SET latest_revision_id=?,updated_at=?,actor=? WHERE id=?", (revision_id, stamp, actor, asset_id))
            self._event(db, asset_id, asset["project_id"], "revision-created", actor, {"revisionId": revision_id, "revision": rev_no})
            db.commit()
        return self.get_asset(asset_id)

    def fork_asset(self, asset_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        source = self.get_asset(asset_id)
        latest = source["revisions"][0]
        body = {
            "title": payload.get("title") or f"{source['asset']['title']} — fork",
            "scene": latest["scene"],
            "provenance": latest["provenance"],
            "researchObject": latest["researchObject"],
            "computeRefs": latest["computeRefs"],
            "metadata": {"forkedFromAssetId": asset_id, "forkedFromRevisionId": latest["id"], **(payload.get("metadata") or {})},
            "parentAssetId": asset_id,
            "sourceSceneId": source["asset"].get("sourceSceneId"),
        }
        return self.create_asset(source["asset"]["projectId"], body, actor)

    def compare(self, left_asset_id: str, right_asset_id: str) -> dict[str, Any]:
        left = self.get_asset(left_asset_id)
        right = self.get_asset(right_asset_id)
        lrev, rrev = left["revisions"][0], right["revisions"][0]
        def snapshot(rev: dict[str, Any]) -> dict[str, Any]:
            st = ((rev.get("scene") or {}).get("sceneState") or {})
            linked = st.get("linked") or {}
            return {
                "sceneDigest": rev.get("sceneDigest"),
                "model": st.get("model") or st.get("demo"),
                "w": st.get("w"),
                "surface": bool(st.get("surface")),
                "selectionHistoryCount": len(linked.get("history") or []),
                "pinnedSelectionCount": len(linked.get("pins") or []),
                "computeRefCount": len(rev.get("computeRefs") or []),
            }
        ls, rs = snapshot(lrev), snapshot(rrev)
        changes = {key: {"left": ls.get(key), "right": rs.get(key)} for key in sorted(set(ls) | set(rs)) if ls.get(key) != rs.get(key)}
        return {
            "ok": True,
            "version": VERSION,
            "schema": COMPARE_SCHEMA,
            "leftAssetId": left_asset_id,
            "rightAssetId": right_asset_id,
            "sameSceneState": lrev.get("sceneDigest") == rrev.get("sceneDigest"),
            "changes": changes,
            "descriptiveOnly": True,
            "automaticScientificConclusion": False,
            "boundary": BOUNDARY,
        }

    def lineage(self, asset_id: str) -> dict[str, Any]:
        asset_id = _clean_id(asset_id, "asset ID")
        chain: list[dict[str, Any]] = []
        visited: set[str] = set()
        current = asset_id
        with self._connect() as db:
            while current and current not in visited and len(chain) < 100:
                visited.add(current)
                row = db.execute("SELECT * FROM crw_assets WHERE id=?", (current,)).fetchone()
                if not row:
                    break
                item = self._asset_row(row)
                chain.append(item)
                current = item.get("parentAssetId") or ""
            revisions = db.execute("SELECT id,revision_no,scene_digest,created_at,actor,revision_hash FROM crw_revisions WHERE asset_id=? ORDER BY revision_no ASC", (asset_id,)).fetchall()
        return {
            "ok": True,
            "version": VERSION,
            "schema": LINEAGE_SCHEMA,
            "assetId": asset_id,
            "ancestorChain": chain,
            "revisions": [{"id": r["id"], "revision": int(r["revision_no"]), "sceneDigest": r["scene_digest"], "createdAt": r["created_at"], "actor": r["actor"], "revisionHash": r["revision_hash"]} for r in revisions],
            "boundary": BOUNDARY,
        }

    def archive(self, asset_id: str, actor: str) -> dict[str, Any]:
        asset_id = _clean_id(asset_id, "asset ID")
        stamp = _now()
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM crw_assets WHERE id=?", (asset_id,)).fetchone()
            if not row:
                raise ComputationalResearchWorkspaceError("Workspace asset not found.", 404)
            db.execute("UPDATE crw_assets SET status='archived',updated_at=?,actor=? WHERE id=?", (stamp, actor, asset_id))
            self._event(db, asset_id, row["project_id"], "asset-archived", actor, {})
            db.commit()
        return self.get_asset(asset_id)
