from __future__ import annotations

import copy
import hmac
import json
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.37.2"
RECORD_SCHEMA = "sc-lab-public-reproduction-record/0.37.2"
CHALLENGE_SCHEMA = "sc-lab-reproduction-challenge/0.37.2"
RECEIPT_SCHEMA = "sc-lab-reproduction-verification-receipt/0.37.2"
EVENT_SCHEMA = "sc-lab-public-reproduction-event/0.37.2"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,118}[a-z0-9]$")
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
ROLE_RANK = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
RECORD_STATUSES = {"draft", "published", "withdrawn"}
VISIBILITIES = {"public", "unlisted"}
CHALLENGE_STATUSES = {"issued", "verified", "failed", "expired"}
FORBIDDEN_KEYS = {
    "code", "sourcecode", "shell", "command", "callback", "callbackurl", "executable", "script",
    "token", "secret", "password", "privatekey", "bytes", "binary", "rawdata", "datasetbytes",
    "credential", "apikey", "accesskey", "authorization",
}


class PublicReproductionError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, label: str = "identifier") -> str:
    clean = _text(value, 180)
    if not ID_RE.match(clean):
        raise PublicReproductionError(f"A valid {label} is required.")
    return clean


def _slug(value: Any) -> str:
    clean = _text(value, 120).lower()
    if not SLUG_RE.match(clean):
        raise PublicReproductionError("A public slug of 3-120 lowercase letters, numbers, and hyphens is required.")
    return clean


def _sha(value: Any, label: str) -> str:
    clean = _text(value, 64).lower()
    if not SHA_RE.match(clean):
        raise PublicReproductionError(f"A valid SHA-256 {label} is required.")
    return clean


def _safe(value: Any, depth: int = 0) -> Any:
    if depth > 12:
        raise PublicReproductionError("Nested public reproduction data exceeds the depth limit.", 413)
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            skey = _text(key, 120)
            normalized = skey.lower().replace("_", "").replace("-", "")
            if normalized in FORBIDDEN_KEYS:
                raise PublicReproductionError(f"Executable, secret, credential, or embedded byte field '{skey}' is not permitted.", 422)
            out[skey] = _safe(item, depth + 1)
        return out
    if isinstance(value, list):
        return [_safe(item, depth + 1) for item in value[:10000]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _text(value, 100000)


def _obj(value: Any, max_bytes: int = 4 * 1024 * 1024) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PublicReproductionError("A JSON object is required.")
    clean = _safe(copy.deepcopy(value))
    if len(_stable(clean).encode("utf-8")) > max_bytes:
        raise PublicReproductionError("Public reproduction payload exceeds the configured limit.", 413)
    return clean


def policies(max_records: int = 10000, max_challenges: int = 250000, challenge_ttl_seconds: int = 86400) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-public-reproduction-policy/0.37.2",
        "schemas": {"record": RECORD_SCHEMA, "challenge": CHALLENGE_SCHEMA, "receipt": RECEIPT_SCHEMA, "event": EVENT_SCHEMA},
        "limits": {"records": max_records, "challenges": max_challenges, "challengeTtlSeconds": challenge_ttl_seconds},
        "capabilities": {
            "publicVerificationRecords": True,
            "safeManifestViews": True,
            "nonceChallenges": True,
            "independentHashVerification": True,
            "signedReceipts": True,
            "tamperDetection": True,
            "publicCodeExecution": False,
            "embeddedRestrictedData": False,
            "unrestrictedCallbacks": False,
            "hardDelete": False,
        },
    }


class PublicReproductionPortal:
    def __init__(
        self,
        db_path: str,
        workspaces: Any,
        publication_studio: Any,
        manuscript_assembly: Any,
        receipt_secret: str = "",
        max_records: int = 10000,
        max_challenges: int = 250000,
        challenge_ttl_seconds: int = 86400,
        history_limit: int = 200000,
    ):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.publication_studio = publication_studio
        self.manuscript_assembly = manuscript_assembly
        self.receipt_secret = str(receipt_secret or "")
        self.max_records = max(1, int(max_records))
        self.max_challenges = max(1, int(max_challenges))
        self.challenge_ttl_seconds = max(300, min(604800, int(challenge_ttl_seconds)))
        self.history_limit = max(100, int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.db_path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _init_db(self):
        with self._connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS public_reproduction_records(
                  id TEXT PRIMARY KEY,slug TEXT NOT NULL UNIQUE,workspace_id TEXT NOT NULL,
                  publication_id TEXT NOT NULL,package_id TEXT NOT NULL,assembly_id TEXT,
                  title TEXT NOT NULL,summary TEXT NOT NULL,status TEXT NOT NULL,visibility TEXT NOT NULL,
                  snapshot_json TEXT NOT NULL,record_hash TEXT NOT NULL,canonical_uri TEXT NOT NULL,
                  created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_by TEXT NOT NULL,updated_at TEXT NOT NULL,
                  published_at TEXT,withdrawn_at TEXT,withdrawal_reason TEXT
                );
                CREATE TABLE IF NOT EXISTS reproduction_challenges(
                  id TEXT PRIMARY KEY,record_id TEXT NOT NULL,nonce TEXT NOT NULL UNIQUE,status TEXT NOT NULL,
                  expected_json TEXT NOT NULL,challenge_hash TEXT NOT NULL,evidence_json TEXT NOT NULL,
                  receipt_json TEXT NOT NULL,receipt_hash TEXT,submitter_label TEXT,created_at TEXT NOT NULL,
                  expires_at TEXT NOT NULL,verified_at TEXT,
                  FOREIGN KEY(record_id) REFERENCES public_reproduction_records(id)
                );
                CREATE TABLE IF NOT EXISTS public_reproduction_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,workspace_id TEXT,entity_type TEXT NOT NULL,
                  entity_id TEXT NOT NULL,event_type TEXT NOT NULL,actor_id TEXT NOT NULL,details_json TEXT NOT NULL,
                  event_hash TEXT NOT NULL,created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_public_repro_workspace ON public_reproduction_records(workspace_id,status,updated_at);
                CREATE INDEX IF NOT EXISTS idx_public_repro_slug ON public_reproduction_records(slug,status);
                CREATE INDEX IF NOT EXISTS idx_public_repro_challenges ON reproduction_challenges(record_id,status,created_at);
                CREATE INDEX IF NOT EXISTS idx_public_repro_events ON public_reproduction_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT INTO meta(key,value) VALUES('schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")

    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True):
        try:
            workspace = self.workspaces.get(workspace_id, actor_id, False, False)["workspace"]
        except Exception as exc:
            raise PublicReproductionError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 403)) from exc
        if not allow_archived and workspace.get("status") == "archived":
            raise PublicReproductionError("The workspace is archived and read-only.", 409)
        role = ((workspace.get("currentMembership") or {}).get("role") or "viewer")
        if ROLE_RANK.get(role, 0) < ROLE_RANK[minimum]:
            raise PublicReproductionError(f"The {minimum} role or higher is required.", 403)
        return workspace

    def _event(self, con: sqlite3.Connection, workspace_id: str | None, entity_type: str, entity_id: str, event_type: str, actor_id: str, details: dict[str, Any]):
        created = _now()
        payload = {"schema": EVENT_SCHEMA, "version": VERSION, "workspaceId": workspace_id, "entityType": entity_type, "entityId": entity_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created}
        event_hash = _hash(payload)
        cur = con.execute(
            "INSERT INTO public_reproduction_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (workspace_id, entity_type, entity_id, event_type, actor_id, _stable(details), event_hash, created),
        )
        payload.update({"sequence": cur.lastrowid, "eventHash": event_hash})
        return payload

    @staticmethod
    def _record(row: sqlite3.Row, include_snapshot: bool = True) -> dict[str, Any]:
        result = {
            "schema": RECORD_SCHEMA, "version": VERSION, "id": row["id"], "slug": row["slug"],
            "workspaceId": row["workspace_id"], "publicationId": row["publication_id"], "packageId": row["package_id"],
            "assemblyId": row["assembly_id"], "title": row["title"], "summary": row["summary"],
            "status": row["status"], "visibility": row["visibility"], "recordHash": row["record_hash"],
            "canonicalUri": row["canonical_uri"], "createdBy": row["created_by"], "createdAt": row["created_at"],
            "updatedBy": row["updated_by"], "updatedAt": row["updated_at"], "publishedAt": row["published_at"],
            "withdrawnAt": row["withdrawn_at"], "withdrawalReason": row["withdrawal_reason"],
        }
        if include_snapshot:
            result["snapshot"] = json.loads(row["snapshot_json"])
        return result

    @staticmethod
    def _challenge(row: sqlite3.Row, include_evidence: bool = True) -> dict[str, Any]:
        result = {
            "schema": CHALLENGE_SCHEMA, "version": VERSION, "id": row["id"], "recordId": row["record_id"],
            "nonce": row["nonce"], "status": row["status"], "expected": json.loads(row["expected_json"]),
            "challengeHash": row["challenge_hash"], "submitterLabel": row["submitter_label"],
            "createdAt": row["created_at"], "expiresAt": row["expires_at"], "verifiedAt": row["verified_at"],
            "receiptHash": row["receipt_hash"],
        }
        if include_evidence:
            result["evidence"] = json.loads(row["evidence_json"])
            result["receipt"] = json.loads(row["receipt_json"])
        return result

    def _published_publication(self, workspace_id: str, publication_id: str, actor_id: str) -> dict[str, Any]:
        try:
            publication = self.publication_studio.get_publication(workspace_id, publication_id, actor_id)["publication"]
        except Exception as exc:
            raise PublicReproductionError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 400)) from exc
        if publication.get("status") != "published":
            raise PublicReproductionError("The linked research publication must be published before a public reproduction record can be created.", 409)
        if not publication.get("publicationHash") or not publication.get("canonicalUri"):
            raise PublicReproductionError("The publication is missing immutable publication identity metadata.", 409)
        return publication

    def _sealed_assembly(self, workspace_id: str, assembly_id: str, actor_id: str) -> dict[str, Any] | None:
        if not assembly_id:
            return None
        try:
            assembly = self.manuscript_assembly.get_assembly(workspace_id, assembly_id, actor_id)["assembly"]
        except Exception as exc:
            raise PublicReproductionError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 400)) from exc
        if assembly.get("status") != "sealed" or not assembly.get("assemblyHash"):
            raise PublicReproductionError("The linked research assembly must be sealed.", 409)
        return assembly

    @staticmethod
    def _public_package(package: dict[str, Any]) -> dict[str, Any]:
        resources = []
        for item in package.get("resources") or []:
            if not isinstance(item, dict):
                continue
            resources.append({
                "id": _text(item.get("id"), 180), "type": _text(item.get("type"), 80),
                "title": _text(item.get("title"), 300), "version": _text(item.get("version"), 100),
                "sha256": _text(item.get("sha256"), 64).lower(), "mediaType": _text(item.get("mediaType"), 200),
                "role": _text(item.get("role"), 100), "uri": _text(item.get("uri"), 1000),
            })
        return {
            "id": package.get("id"), "title": package.get("title"), "description": package.get("description"),
            "packageVersion": package.get("packageVersion"), "license": package.get("license"),
            "resources": resources, "methods": _safe(package.get("methods") or {}),
            "environment": _safe(package.get("environment") or {}), "citations": _safe(package.get("citations") or []),
            "manifest": _safe(package.get("manifest") or {}), "packageHash": package.get("packageHash"),
            "sealedAt": package.get("sealedAt"),
        }

    def _snapshot(self, workspace_id: str, publication: dict[str, Any], package: dict[str, Any], assembly: dict[str, Any] | None, payload: dict[str, Any]) -> dict[str, Any]:
        outputs = publication.get("outputs") if isinstance(publication.get("outputs"), dict) else {}
        snapshot = {
            "schema": "sc-lab-public-reproduction-snapshot/0.37.2", "version": VERSION,
            "publication": {
                "id": publication.get("id"), "title": publication.get("title"), "subtitle": publication.get("subtitle"),
                "abstract": publication.get("abstract"), "authors": _safe(publication.get("authors") or []),
                "license": publication.get("license"), "publicationHash": publication.get("publicationHash"),
                "canonicalUri": publication.get("canonicalUri"), "publishedAt": publication.get("publishedAt"),
                "exportHash": outputs.get("exportHash"), "fileHashes": _safe(outputs.get("fileHashes") or {}),
            },
            "package": self._public_package(package),
            "assembly": None if not assembly else {
                "id": assembly.get("id"), "title": assembly.get("title"), "documentType": assembly.get("documentType"),
                "assemblyHash": assembly.get("assemblyHash"), "sealedAt": assembly.get("sealedAt"),
                "render": _safe(assembly.get("render") or {}),
            },
            "verificationInstructions": _safe(payload.get("verificationInstructions") or {
                "steps": [
                    "Download or independently reconstruct the sealed reproducibility package.",
                    "Compute SHA-256 hashes for the package manifest and declared resources.",
                    "Request a nonce challenge and submit only hashes and environment metadata.",
                    "Compare the resulting verification receipt with this public record.",
                ]
            }),
            "publicMetadata": _safe(payload.get("publicMetadata") or {}),
            "workspaceReference": _hash({"workspaceId": workspace_id}),
            "createdAt": _now(),
        }
        snapshot["snapshotHash"] = _hash(snapshot)
        return snapshot

    def create_record(self, workspace_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        payload = _obj(payload)
        record_id = _id(payload.get("id") or ("public-repro-" + secrets.token_hex(8)), "record ID")
        slug = _slug(payload.get("slug") or record_id.lower().replace("_", "-").replace(".", "-"))
        publication_id = _id(payload.get("publicationId"), "publication ID")
        assembly_id = _text(payload.get("assemblyId"), 180)
        publication = self._published_publication(workspace_id, publication_id, actor_id)
        try:
            package = self.publication_studio.get_package(workspace_id, publication["packageId"], actor_id)["package"]
        except Exception as exc:
            raise PublicReproductionError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 400)) from exc
        if package.get("status") not in {"sealed", "published"} or not package.get("packageHash"):
            raise PublicReproductionError("The linked reproducibility package must be sealed and hashed.", 409)
        assembly = self._sealed_assembly(workspace_id, assembly_id, actor_id)
        snapshot = self._snapshot(workspace_id, publication, package, assembly, payload)
        title = _text(payload.get("title"), 300) or publication.get("title") or record_id
        summary = _text(payload.get("summary"), 5000) or publication.get("abstract") or "Public reproduction and verification record."
        visibility = _text(payload.get("visibility"), 20) or "public"
        if visibility not in VISIBILITIES:
            raise PublicReproductionError("Visibility must be public or unlisted.")
        core = {"id": record_id, "slug": slug, "workspaceId": workspace_id, "publicationId": publication_id, "packageId": package["id"], "assemblyId": assembly_id or None, "title": title, "summary": summary, "visibility": visibility, "snapshotHash": snapshot["snapshotHash"]}
        record_hash = _hash(core)
        canonical_uri = _text(payload.get("canonicalUri"), 1000) or f"urn:sc-lab:public-reproduction:{slug}:{record_hash}"
        now = _now()
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM public_reproduction_records").fetchone()[0] >= self.max_records:
                raise PublicReproductionError("Public reproduction record capacity has been reached.", 409)
            if con.execute("SELECT 1 FROM public_reproduction_records WHERE id=? OR slug=?", (record_id, slug)).fetchone():
                raise PublicReproductionError("Record ID or public slug already exists.", 409)
            con.execute(
                "INSERT INTO public_reproduction_records VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (record_id, slug, workspace_id, publication_id, package["id"], assembly_id or None, title, summary, "draft", visibility, _stable(snapshot), record_hash, canonical_uri, actor_id, now, actor_id, now, None, None, None),
            )
            self._event(con, workspace_id, "record", record_id, "public-record-created", actor_id, {"slug": slug, "publicationId": publication_id, "packageHash": package["packageHash"], "recordHash": record_hash})
            row = con.execute("SELECT * FROM public_reproduction_records WHERE id=?", (record_id,)).fetchone()
            return {"ok": True, "record": self._record(row)}

    def list_records(self, workspace_id: str, actor_id: str, status: str = "", limit: int = 200):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        where = "workspace_id=?"
        args: list[Any] = [workspace_id]
        if status:
            if status not in RECORD_STATUSES:
                raise PublicReproductionError("Unsupported public record status.")
            where += " AND status=?"
            args.append(status)
        args.append(max(1, min(2000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM public_reproduction_records WHERE {where} ORDER BY updated_at DESC LIMIT ?", args).fetchall()
            return {"ok": True, "version": VERSION, "records": [self._record(row, False) for row in rows]}

    def get_record(self, workspace_id: str, record_id: str, actor_id: str):
        workspace_id, record_id, actor_id = _id(workspace_id, "workspace ID"), _id(record_id, "record ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        with self._connect() as con:
            row = con.execute("SELECT * FROM public_reproduction_records WHERE id=? AND workspace_id=?", (record_id, workspace_id)).fetchone()
            if not row:
                raise PublicReproductionError("Public reproduction record not found.", 404)
            return {"ok": True, "record": self._record(row)}

    def publish_record(self, workspace_id: str, record_id: str, actor_id: str):
        workspace_id, record_id, actor_id = _id(workspace_id, "workspace ID"), _id(record_id, "record ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "administrator", False)
        with self._connect() as con:
            row = con.execute("SELECT * FROM public_reproduction_records WHERE id=? AND workspace_id=?", (record_id, workspace_id)).fetchone()
            if not row:
                raise PublicReproductionError("Public reproduction record not found.", 404)
            if row["status"] == "published":
                return {"ok": True, "record": self._record(row)}
            if row["status"] != "draft":
                raise PublicReproductionError("Only draft public reproduction records can be published.", 409)
            snapshot = json.loads(row["snapshot_json"])
            if snapshot.get("snapshotHash") != _hash({k: v for k, v in snapshot.items() if k != "snapshotHash"}):
                raise PublicReproductionError("The public snapshot failed integrity verification.", 409)
            now = _now()
            con.execute("UPDATE public_reproduction_records SET status='published',published_at=?,updated_by=?,updated_at=? WHERE id=?", (now, actor_id, now, record_id))
            self._event(con, workspace_id, "record", record_id, "public-record-published", actor_id, {"slug": row["slug"], "recordHash": row["record_hash"], "snapshotHash": snapshot["snapshotHash"]})
            return {"ok": True, "record": self._record(con.execute("SELECT * FROM public_reproduction_records WHERE id=?", (record_id,)).fetchone())}

    def withdraw_record(self, workspace_id: str, record_id: str, payload: dict[str, Any], actor_id: str):
        workspace_id, record_id, actor_id = _id(workspace_id, "workspace ID"), _id(record_id, "record ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "administrator", False)
        reason = _text((_obj(payload).get("reason")), 2000)
        if not reason:
            raise PublicReproductionError("A withdrawal reason is required.")
        with self._connect() as con:
            row = con.execute("SELECT * FROM public_reproduction_records WHERE id=? AND workspace_id=?", (record_id, workspace_id)).fetchone()
            if not row:
                raise PublicReproductionError("Public reproduction record not found.", 404)
            if row["status"] == "withdrawn":
                return {"ok": True, "record": self._record(row)}
            if row["status"] != "published":
                raise PublicReproductionError("Only published records can be withdrawn.", 409)
            now = _now()
            con.execute("UPDATE public_reproduction_records SET status='withdrawn',withdrawn_at=?,withdrawal_reason=?,updated_by=?,updated_at=? WHERE id=?", (now, reason, actor_id, now, record_id))
            self._event(con, workspace_id, "record", record_id, "public-record-withdrawn", actor_id, {"reason": reason, "recordHash": row["record_hash"]})
            return {"ok": True, "record": self._record(con.execute("SELECT * FROM public_reproduction_records WHERE id=?", (record_id,)).fetchone())}

    def public_record(self, slug: str):
        slug = _slug(slug)
        with self._connect() as con:
            row = con.execute("SELECT * FROM public_reproduction_records WHERE slug=?", (slug,)).fetchone()
            if not row or row["status"] not in {"published", "withdrawn"}:
                raise PublicReproductionError("Public reproduction record not found.", 404)
            record = self._record(row)
            record.pop("workspaceId", None)
            record.pop("createdBy", None)
            record.pop("updatedBy", None)
            record["publicStatus"] = "withdrawn" if row["status"] == "withdrawn" else "verified-public-record"
            return {"ok": True, "record": record}

    def public_manifest(self, slug: str):
        record = self.public_record(slug)["record"]
        snapshot = record["snapshot"]
        manifest = {
            "schema": "sc-lab-public-reproduction-manifest/0.37.2", "version": VERSION,
            "recordId": record["id"], "slug": record["slug"], "recordHash": record["recordHash"],
            "canonicalUri": record["canonicalUri"], "status": record["status"],
            "snapshotHash": snapshot["snapshotHash"], "publication": snapshot["publication"],
            "package": snapshot["package"], "assembly": snapshot.get("assembly"),
        }
        manifest["manifestHash"] = _hash(manifest)
        return {"ok": True, "manifest": manifest}

    def issue_challenge(self, slug: str, payload: dict[str, Any] | None = None):
        payload = _obj(payload or {}, 262144)
        public = self.public_record(slug)["record"]
        if public["status"] != "published":
            raise PublicReproductionError("Withdrawn records cannot issue new verification challenges.", 409)
        manifest = self.public_manifest(slug)["manifest"]
        challenge_id = "challenge-" + secrets.token_hex(12)
        nonce = secrets.token_urlsafe(24)
        created = _now()
        expires = (datetime.now(timezone.utc) + timedelta(seconds=self.challenge_ttl_seconds)).isoformat().replace("+00:00", "Z")
        expected = {
            "recordHash": public["recordHash"], "snapshotHash": public["snapshot"]["snapshotHash"],
            "manifestHash": manifest["manifestHash"], "publicationHash": public["snapshot"]["publication"].get("publicationHash"),
            "packageHash": public["snapshot"]["package"].get("packageHash"),
            "assemblyHash": (public["snapshot"].get("assembly") or {}).get("assemblyHash"),
            "resourceHashes": {item["id"]: item.get("sha256") for item in public["snapshot"]["package"].get("resources", []) if item.get("id") and item.get("sha256")},
        }
        challenge_core = {"id": challenge_id, "recordId": public["id"], "nonce": nonce, "expected": expected, "createdAt": created, "expiresAt": expires}
        challenge_hash = _hash(challenge_core)
        label = _text(payload.get("submitterLabel"), 300)
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM reproduction_challenges").fetchone()[0] >= self.max_challenges:
                raise PublicReproductionError("Verification challenge capacity has been reached.", 409)
            con.execute("INSERT INTO reproduction_challenges VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (challenge_id, public["id"], nonce, "issued", _stable(expected), challenge_hash, "{}", "{}", None, label, created, expires, None))
            self._event(con, None, "challenge", challenge_id, "verification-challenge-issued", "public", {"recordId": public["id"], "challengeHash": challenge_hash, "expiresAt": expires})
            row = con.execute("SELECT * FROM reproduction_challenges WHERE id=?", (challenge_id,)).fetchone()
            return {"ok": True, "challenge": self._challenge(row, False)}

    def _receipt_signature(self, receipt_hash: str) -> str | None:
        if not self.receipt_secret:
            return None
        return hmac.new(self.receipt_secret.encode("utf-8"), receipt_hash.encode("utf-8"), sha256).hexdigest()

    def submit_challenge(self, challenge_id: str, payload: dict[str, Any]):
        challenge_id = _id(challenge_id, "challenge ID")
        payload = _obj(payload, 2 * 1024 * 1024)
        nonce = _text(payload.get("nonce"), 200)
        if not nonce:
            raise PublicReproductionError("The challenge nonce is required.")
        with self._connect() as con:
            row = con.execute("SELECT c.*,r.slug,r.record_hash,r.status AS record_status,r.workspace_id FROM reproduction_challenges c JOIN public_reproduction_records r ON r.id=c.record_id WHERE c.id=?", (challenge_id,)).fetchone()
            if not row:
                raise PublicReproductionError("Verification challenge not found.", 404)
            if not hmac.compare_digest(row["nonce"], nonce):
                raise PublicReproductionError("The challenge nonce is invalid.", 403)
            if row["status"] in {"verified", "failed"}:
                return {"ok": True, "challenge": self._challenge(row), "receipt": json.loads(row["receipt_json"])}
            if row["record_status"] != "published":
                raise PublicReproductionError("The linked public reproduction record is no longer active.", 409)
            if datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) < datetime.now(timezone.utc):
                con.execute("UPDATE reproduction_challenges SET status='expired' WHERE id=?", (challenge_id,))
                raise PublicReproductionError("The verification challenge has expired.", 410)
            expected = json.loads(row["expected_json"])
            evidence = {
                "recordHash": _sha(payload.get("recordHash"), "record hash"),
                "snapshotHash": _sha(payload.get("snapshotHash"), "snapshot hash"),
                "manifestHash": _sha(payload.get("manifestHash"), "manifest hash"),
                "publicationHash": _sha(payload.get("publicationHash"), "publication hash"),
                "packageHash": _sha(payload.get("packageHash"), "package hash"),
                "assemblyHash": _text(payload.get("assemblyHash"), 64).lower() or None,
                "resourceHashes": _safe(payload.get("resourceHashes") or {}),
                "environment": _safe(payload.get("environment") or {}),
                "resultHashes": _safe(payload.get("resultHashes") or {}),
                "notes": _text(payload.get("notes"), 5000),
            }
            if evidence["assemblyHash"] and not SHA_RE.match(evidence["assemblyHash"]):
                raise PublicReproductionError("A valid SHA-256 assembly hash is required when provided.")
            mismatches = []
            for key in ("recordHash", "snapshotHash", "manifestHash", "publicationHash", "packageHash", "assemblyHash"):
                if expected.get(key) != evidence.get(key):
                    if expected.get(key) or evidence.get(key):
                        mismatches.append({"field": key, "expected": expected.get(key), "observed": evidence.get(key)})
            expected_resources = expected.get("resourceHashes") or {}
            observed_resources = evidence.get("resourceHashes") if isinstance(evidence.get("resourceHashes"), dict) else {}
            for rid, digest in expected_resources.items():
                if observed_resources.get(rid) != digest:
                    mismatches.append({"field": f"resourceHashes.{rid}", "expected": digest, "observed": observed_resources.get(rid)})
            verified = not mismatches
            verified_at = _now()
            receipt_core = {
                "schema": RECEIPT_SCHEMA, "version": VERSION, "id": "receipt-" + secrets.token_hex(12),
                "challengeId": challenge_id, "recordId": row["record_id"], "recordSlug": row["slug"],
                "challengeHash": row["challenge_hash"], "verified": verified, "mismatches": mismatches,
                "evidenceHash": _hash(evidence), "expectedHash": _hash(expected), "verifiedAt": verified_at,
                "signatureAlgorithm": "hmac-sha256" if self.receipt_secret else "sha256-receipt-hash",
            }
            receipt_hash = _hash(receipt_core)
            receipt = {**receipt_core, "receiptHash": receipt_hash, "signature": self._receipt_signature(receipt_hash)}
            status = "verified" if verified else "failed"
            con.execute("UPDATE reproduction_challenges SET status=?,evidence_json=?,receipt_json=?,receipt_hash=?,verified_at=? WHERE id=?", (status, _stable(evidence), _stable(receipt), receipt_hash, verified_at, challenge_id))
            self._event(con, row["workspace_id"], "challenge", challenge_id, "verification-challenge-completed", "public", {"recordId": row["record_id"], "verified": verified, "receiptHash": receipt_hash, "mismatchCount": len(mismatches)})
            return {"ok": True, "verified": verified, "receipt": receipt}

    def public_receipt(self, receipt_hash: str):
        receipt_hash = _sha(receipt_hash, "receipt hash")
        with self._connect() as con:
            row = con.execute("SELECT receipt_json,status FROM reproduction_challenges WHERE receipt_hash=?", (receipt_hash,)).fetchone()
            if not row:
                raise PublicReproductionError("Verification receipt not found.", 404)
            receipt = json.loads(row["receipt_json"])
            valid_hash = receipt.get("receiptHash") == _hash({k: v for k, v in receipt.items() if k not in {"receiptHash", "signature"}})
            valid_signature = True
            if receipt.get("signature") and self.receipt_secret:
                valid_signature = hmac.compare_digest(receipt["signature"], self._receipt_signature(receipt_hash) or "")
            return {"ok": valid_hash and valid_signature, "status": row["status"], "receipt": receipt, "integrity": {"receiptHashValid": valid_hash, "signatureValid": valid_signature}}

    def list_challenges(self, workspace_id: str, record_id: str, actor_id: str, limit: int = 200):
        workspace_id, record_id, actor_id = _id(workspace_id, "workspace ID"), _id(record_id, "record ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "reviewer")
        with self._connect() as con:
            record = con.execute("SELECT id FROM public_reproduction_records WHERE id=? AND workspace_id=?", (record_id, workspace_id)).fetchone()
            if not record:
                raise PublicReproductionError("Public reproduction record not found.", 404)
            rows = con.execute("SELECT * FROM reproduction_challenges WHERE record_id=? ORDER BY created_at DESC LIMIT ?", (record_id, max(1, min(2000, int(limit))))).fetchall()
            return {"ok": True, "version": VERSION, "challenges": [self._challenge(row) for row in rows]}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500):
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id)
        with self._connect() as con:
            rows = con.execute("SELECT * FROM public_reproduction_events WHERE workspace_id=? OR workspace_id IS NULL ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(self.history_limit, int(limit))))).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "workspaceId": row["workspace_id"], "entityType": row["entity_type"], "entityId": row["entity_id"], "eventType": row["event_type"], "actorId": row["actor_id"], "details": json.loads(row["details_json"]), "eventHash": row["event_hash"], "createdAt": row["created_at"]} for row in rows]
            return {"ok": True, "version": VERSION, "events": events}

    def health(self):
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            counts = {
                "records": con.execute("SELECT COUNT(*) FROM public_reproduction_records").fetchone()[0],
                "published": con.execute("SELECT COUNT(*) FROM public_reproduction_records WHERE status='published'").fetchone()[0],
                "withdrawn": con.execute("SELECT COUNT(*) FROM public_reproduction_records WHERE status='withdrawn'").fetchone()[0],
                "challenges": con.execute("SELECT COUNT(*) FROM reproduction_challenges").fetchone()[0],
                "verifiedReceipts": con.execute("SELECT COUNT(*) FROM reproduction_challenges WHERE status='verified'").fetchone()[0],
                "failedReceipts": con.execute("SELECT COUNT(*) FROM reproduction_challenges WHERE status='failed'").fetchone()[0],
            }
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schema": "sc-lab-public-reproduction-health/0.37.2", "database": {"path": self.db_path, "schemaVersion": schema, "integrity": integrity}, "counts": counts, "receiptSigning": "hmac-sha256" if self.receipt_secret else "sha256-receipt-hash", "capabilities": policies(self.max_records, self.max_challenges, self.challenge_ttl_seconds)["capabilities"], "time": _now()}
