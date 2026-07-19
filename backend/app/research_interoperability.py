from __future__ import annotations

import copy
import hmac
import json
import re
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.38.0"
PROFILE_SCHEMA = "sc-research-interoperability-profile/0.38.0"
ENVELOPE_SCHEMA = "sc-research-handoff-envelope/0.38.0"
NEGOTIATION_SCHEMA = "sc-research-compatibility-negotiation/0.38.0"
RECEIPT_SCHEMA = "sc-research-handoff-receipt/0.38.0"
EVENT_SCHEMA = "sc-research-interoperability-event/0.38.0"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
PRODUCT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")
CONTRACT_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{1,150}/[0-9]+\.[0-9]+$")
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
ROLE_RANK = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
HANDOFF_STATUSES = {"draft", "sealed", "delivered", "received", "accepted", "rejected", "withdrawn"}
DIRECTIONS = {"export", "import"}
DECISIONS = {"accepted", "rejected", "needs-changes"}
ENTITY_TYPES = {
    "dataset", "observation-set", "workflow", "workflow-run", "experiment", "campaign", "model",
    "surrogate-model", "artifact", "evidence-record", "citation-set", "publication", "reproducibility-package",
    "manuscript", "decision-packet", "scenario", "indicator-set", "research-brief", "workspace-snapshot",
}
DEFAULT_PRODUCTS = {
    "sustainable-catalyst-lab", "decision-studio", "knowledge-library", "research-librarian",
    "sustainable-catalyst-workbench", "site-intelligence", "catalyst-data", "catalyst-canvas",
    "catalyst-finance", "catalyst-grit", "catalyst-narrative-risk", "global-impact-catalyst", "catalyst-analytics-r",
}
FORBIDDEN_KEYS = {
    "code", "sourcecode", "shell", "command", "callback", "callbackurl", "webhook", "executable", "script",
    "token", "secret", "password", "privatekey", "credential", "apikey", "accesskey", "authorization",
    "bytes", "binary", "rawdata", "datasetbytes", "filecontents", "payloadbytes",
}


class InteroperabilityError(ValueError):
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
        raise InteroperabilityError(f"A valid {label} is required.")
    return clean


def _product(value: Any, label: str = "product identifier") -> str:
    clean = _text(value, 80).lower()
    if not PRODUCT_RE.match(clean):
        raise InteroperabilityError(f"A valid {label} is required.")
    return clean


def _contract(value: Any) -> str:
    clean = _text(value, 180).lower()
    if not CONTRACT_RE.match(clean):
        raise InteroperabilityError("A typed contract identifier ending in /major.minor is required.")
    return clean


def _sha(value: Any, label: str = "SHA-256") -> str:
    clean = _text(value, 64).lower()
    if not SHA_RE.match(clean):
        raise InteroperabilityError(f"A valid {label} is required.")
    return clean


def _safe(value: Any, depth: int = 0) -> Any:
    if depth > 14:
        raise InteroperabilityError("Interoperability payload exceeds the nesting limit.", 413)
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in value.items():
            skey = _text(key, 120)
            normalized = skey.lower().replace("_", "").replace("-", "")
            if normalized in FORBIDDEN_KEYS:
                raise InteroperabilityError(f"Executable, secret, credential, callback, or embedded-byte field '{skey}' is not permitted.", 422)
            output[skey] = _safe(item, depth + 1)
        return output
    if isinstance(value, list):
        if len(value) > 10000:
            raise InteroperabilityError("Interoperability lists may contain at most 10,000 entries.", 413)
        return [_safe(item, depth + 1) for item in value]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _text(value, 100000)


def _obj(value: Any, limit: int = 4 * 1024 * 1024) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise InteroperabilityError("A JSON object is required.")
    clean = _safe(copy.deepcopy(value))
    if len(_stable(clean).encode("utf-8")) > limit:
        raise InteroperabilityError("Interoperability payload exceeds the configured limit.", 413)
    return clean


def _contracts(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise InteroperabilityError("At least one supported contract is required.")
    return sorted(set(_contract(item) for item in value[:500]))


def policies(max_profiles: int = 5000, max_handoffs: int = 250000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-research-interoperability-policy/0.38.0",
        "schemas": {"profile": PROFILE_SCHEMA, "envelope": ENVELOPE_SCHEMA, "negotiation": NEGOTIATION_SCHEMA, "receipt": RECEIPT_SCHEMA, "event": EVENT_SCHEMA},
        "limits": {"profiles": max_profiles, "handoffs": max_handoffs, "maxPayloadBytes": 4 * 1024 * 1024},
        "entityTypes": sorted(ENTITY_TYPES),
        "knownProducts": sorted(DEFAULT_PRODUCTS),
        "capabilities": {
            "typedCrossProductHandoffs": True,
            "canonicalExchangeEnvelopes": True,
            "contractVersionNegotiation": True,
            "capabilityNegotiation": True,
            "idempotentImports": True,
            "signedReceipts": True,
            "workspaceGovernance": True,
            "directRemoteCallbacks": False,
            "arbitraryCode": False,
            "embeddedRestrictedData": False,
            "hardDelete": False,
        },
    }


class ResearchInteroperabilityLayer:
    def __init__(self, db_path: str, workspaces: Any, receipt_secret: str = "", max_profiles: int = 5000, max_handoffs: int = 250000, history_limit: int = 250000):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.receipt_secret = str(receipt_secret or "")
        self.max_profiles = max(1, int(max_profiles))
        self.max_handoffs = max(1, int(max_handoffs))
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
                CREATE TABLE IF NOT EXISTS interoperability_profiles(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,product_id TEXT NOT NULL,display_name TEXT NOT NULL,
                  status TEXT NOT NULL,contracts_json TEXT NOT NULL,capabilities_json TEXT NOT NULL,metadata_json TEXT NOT NULL,
                  profile_hash TEXT NOT NULL,created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_by TEXT NOT NULL,updated_at TEXT NOT NULL,
                  UNIQUE(workspace_id,product_id,id)
                );
                CREATE TABLE IF NOT EXISTS interoperability_handoffs(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,direction TEXT NOT NULL,source_product TEXT NOT NULL,target_product TEXT NOT NULL,
                  entity_type TEXT NOT NULL,contract_version TEXT NOT NULL,status TEXT NOT NULL,external_id TEXT,
                  envelope_json TEXT NOT NULL,envelope_hash TEXT NOT NULL,compatibility_json TEXT NOT NULL,
                  created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_by TEXT NOT NULL,updated_at TEXT NOT NULL,
                  sealed_at TEXT,delivered_at TEXT,withdrawn_at TEXT,withdrawal_reason TEXT
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_interop_import_dedupe ON interoperability_handoffs(workspace_id,direction,envelope_hash);
                CREATE INDEX IF NOT EXISTS idx_interop_handoffs_workspace ON interoperability_handoffs(workspace_id,status,updated_at);
                CREATE TABLE IF NOT EXISTS interoperability_receipts(
                  id TEXT PRIMARY KEY,handoff_id TEXT NOT NULL,workspace_id TEXT NOT NULL,decision TEXT NOT NULL,status TEXT NOT NULL,
                  details_json TEXT NOT NULL,receipt_json TEXT NOT NULL,receipt_hash TEXT NOT NULL,signature TEXT,
                  actor_id TEXT NOT NULL,created_at TEXT NOT NULL,
                  FOREIGN KEY(handoff_id) REFERENCES interoperability_handoffs(id)
                );
                CREATE TABLE IF NOT EXISTS interoperability_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,workspace_id TEXT NOT NULL,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,
                  event_type TEXT NOT NULL,actor_id TEXT NOT NULL,details_json TEXT NOT NULL,event_hash TEXT NOT NULL,created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_interop_events_workspace ON interoperability_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT INTO meta(key,value) VALUES('schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")

    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True):
        try:
            workspace = self.workspaces.get(workspace_id, actor_id, False, False)["workspace"]
        except Exception as exc:
            raise InteroperabilityError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 403)) from exc
        if not allow_archived and workspace.get("status") == "archived":
            raise InteroperabilityError("The workspace is archived and read-only.", 409)
        role = ((workspace.get("currentMembership") or {}).get("role") or "viewer")
        if ROLE_RANK.get(role, 0) < ROLE_RANK[minimum]:
            raise InteroperabilityError(f"The {minimum} role or higher is required.", 403)
        return workspace

    def _event(self, con: sqlite3.Connection, workspace_id: str, entity_type: str, entity_id: str, event_type: str, actor_id: str, details: dict[str, Any]):
        created = _now()
        payload = {"schema": EVENT_SCHEMA, "version": VERSION, "workspaceId": workspace_id, "entityType": entity_type, "entityId": entity_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created}
        event_hash = _hash(payload)
        cur = con.execute(
            "INSERT INTO interoperability_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (workspace_id, entity_type, entity_id, event_type, actor_id, _stable(details), event_hash, created),
        )
        payload.update({"sequence": cur.lastrowid, "eventHash": event_hash})
        return payload

    @staticmethod
    def _profile(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": PROFILE_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"],
            "productId": row["product_id"], "displayName": row["display_name"], "status": row["status"],
            "supportedContracts": json.loads(row["contracts_json"]), "capabilities": json.loads(row["capabilities_json"]),
            "metadata": json.loads(row["metadata_json"]), "profileHash": row["profile_hash"],
            "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedBy": row["updated_by"], "updatedAt": row["updated_at"],
        }

    @staticmethod
    def _handoff(row: sqlite3.Row) -> dict[str, Any]:
        result = json.loads(row["envelope_json"])
        result.update({
            "status": row["status"], "direction": row["direction"], "envelopeHash": row["envelope_hash"],
            "compatibility": json.loads(row["compatibility_json"]), "externalId": row["external_id"],
            "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedBy": row["updated_by"], "updatedAt": row["updated_at"],
            "sealedAt": row["sealed_at"], "deliveredAt": row["delivered_at"], "withdrawnAt": row["withdrawn_at"], "withdrawalReason": row["withdrawal_reason"],
        })
        return result

    def register_profile(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "editor", False)
        body = _obj(payload)
        pid = _id(body.get("id") or body.get("productId"), "profile identifier")
        product_id = _product(body.get("productId"))
        contracts = _contracts(body.get("supportedContracts"))
        capabilities = sorted(set(_text(v, 120) for v in (body.get("capabilities") or []) if _text(v, 120)))
        metadata = _obj(body.get("metadata") or {}, 262144)
        display = _text(body.get("displayName") or product_id, 200)
        status = _text(body.get("status") or "active", 20).lower()
        if status not in {"active", "suspended", "deprecated"}:
            raise InteroperabilityError("Profile status must be active, suspended, or deprecated.")
        now = _now()
        profile_core = {"schema": PROFILE_SCHEMA, "version": VERSION, "id": pid, "workspaceId": workspace_id, "productId": product_id, "displayName": display, "status": status, "supportedContracts": contracts, "capabilities": capabilities, "metadata": metadata}
        profile_hash = _hash(profile_core)
        with self._connect() as con:
            count = con.execute("SELECT COUNT(*) FROM interoperability_profiles").fetchone()[0]
            existing_row = con.execute("SELECT workspace_id FROM interoperability_profiles WHERE id=?", (pid,)).fetchone()
            exists = existing_row is not None
            if existing_row and existing_row["workspace_id"] != workspace_id:
                raise InteroperabilityError("This interoperability profile identifier belongs to another workspace.", 409)
            if count >= self.max_profiles and not exists:
                raise InteroperabilityError("The interoperability profile limit has been reached.", 409)
            con.execute(
                "INSERT INTO interoperability_profiles(id,workspace_id,product_id,display_name,status,contracts_json,capabilities_json,metadata_json,profile_hash,created_by,created_at,updated_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET product_id=excluded.product_id,display_name=excluded.display_name,status=excluded.status,contracts_json=excluded.contracts_json,capabilities_json=excluded.capabilities_json,metadata_json=excluded.metadata_json,profile_hash=excluded.profile_hash,updated_by=excluded.updated_by,updated_at=excluded.updated_at",
                (pid, workspace_id, product_id, display, status, _stable(contracts), _stable(capabilities), _stable(metadata), profile_hash, actor_id, now, actor_id, now),
            )
            self._event(con, workspace_id, "profile", pid, "profile-registered" if not exists else "profile-updated", actor_id, {"productId": product_id, "profileHash": profile_hash})
            row = con.execute("SELECT * FROM interoperability_profiles WHERE id=?", (pid,)).fetchone()
        return {"ok": True, "profile": self._profile(row)}

    def list_profiles(self, workspace_id: str, actor_id: str, status: str = "", limit: int = 200) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id)
        args: list[Any] = [workspace_id]
        where = "workspace_id=?"
        if status:
            where += " AND status=?"; args.append(status)
        args.append(max(1, min(2000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM interoperability_profiles WHERE {where} ORDER BY updated_at DESC LIMIT ?", args).fetchall()
        return {"ok": True, "profiles": [self._profile(r) for r in rows], "count": len(rows)}

    def _get_profile(self, con: sqlite3.Connection, workspace_id: str, profile_id: str) -> dict[str, Any]:
        row = con.execute("SELECT * FROM interoperability_profiles WHERE id=? AND workspace_id=?", (_id(profile_id, "profile identifier"), workspace_id)).fetchone()
        if not row:
            raise InteroperabilityError("Interoperability profile was not found.", 404)
        return self._profile(row)

    def negotiate(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id)
        body = _obj(payload, 262144)
        with self._connect() as con:
            source = self._get_profile(con, workspace_id, body.get("sourceProfileId"))
            target = self._get_profile(con, workspace_id, body.get("targetProfileId"))
        requested = sorted(set(_contract(v) for v in (body.get("requestedContracts") or source["supportedContracts"])))
        compatible = sorted(set(requested) & set(source["supportedContracts"]) & set(target["supportedContracts"]))
        requested_caps = sorted(set(_text(v, 120) for v in (body.get("requiredCapabilities") or []) if _text(v, 120)))
        shared_caps = sorted(set(source["capabilities"]) & set(target["capabilities"]))
        missing_caps = sorted(set(requested_caps) - set(shared_caps))
        result = {
            "schema": NEGOTIATION_SCHEMA, "version": VERSION, "workspaceId": workspace_id,
            "sourceProfile": {"id": source["id"], "productId": source["productId"], "profileHash": source["profileHash"]},
            "targetProfile": {"id": target["id"], "productId": target["productId"], "profileHash": target["profileHash"]},
            "requestedContracts": requested, "compatibleContracts": compatible, "selectedContract": compatible[-1] if compatible else None,
            "requiredCapabilities": requested_caps, "sharedCapabilities": shared_caps, "missingCapabilities": missing_caps,
            "compatible": bool(compatible) and not missing_caps and source["status"] == "active" and target["status"] == "active",
            "negotiatedAt": _now(),
        }
        result["negotiationHash"] = _hash(result)
        return {"ok": True, "negotiation": result}

    def create_handoff(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "contributor", False)
        body = _obj(payload)
        hid = _id(body.get("id"), "handoff identifier")
        source = _product(body.get("sourceProduct") or "sustainable-catalyst-lab", "source product")
        target = _product(body.get("targetProduct"), "target product")
        entity_type = _text(body.get("entityType"), 80).lower()
        if entity_type not in ENTITY_TYPES:
            raise InteroperabilityError("The handoff entity type is not supported.")
        contract_version = _contract(body.get("contractVersion"))
        resource = _obj(body.get("resource") or {}, 2 * 1024 * 1024)
        resource_id = _id(resource.get("id"), "resource identifier")
        resource_sha = _sha(resource.get("sha256"), "resource SHA-256")
        provenance = _obj(body.get("provenance") or {}, 512000)
        requirements = sorted(set(_text(v, 120) for v in (body.get("requiredCapabilities") or []) if _text(v, 120)))
        external_id = _text(body.get("externalId"), 180) or None
        now = _now()
        core = {
            "schema": ENVELOPE_SCHEMA, "version": VERSION, "id": hid, "workspaceId": workspace_id,
            "sourceProduct": source, "targetProduct": target, "entityType": entity_type, "contractVersion": contract_version,
            "resource": {**resource, "id": resource_id, "sha256": resource_sha}, "provenance": provenance,
            "requiredCapabilities": requirements, "createdAt": now,
            "safety": {"arbitraryCode": False, "embeddedRestrictedData": False, "directRemoteCallbacks": False},
        }
        envelope_hash = _hash(core)
        compatibility = {"checked": False, "compatible": None, "requiredCapabilities": requirements}
        with self._connect() as con:
            count = con.execute("SELECT COUNT(*) FROM interoperability_handoffs").fetchone()[0]
            if count >= self.max_handoffs:
                raise InteroperabilityError("The interoperability handoff limit has been reached.", 409)
            try:
                con.execute(
                    "INSERT INTO interoperability_handoffs(id,workspace_id,direction,source_product,target_product,entity_type,contract_version,status,external_id,envelope_json,envelope_hash,compatibility_json,created_by,created_at,updated_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (hid, workspace_id, "export", source, target, entity_type, contract_version, "draft", external_id, _stable(core), envelope_hash, _stable(compatibility), actor_id, now, actor_id, now),
                )
            except sqlite3.IntegrityError as exc:
                raise InteroperabilityError("A handoff with this identifier or envelope hash already exists.", 409) from exc
            self._event(con, workspace_id, "handoff", hid, "handoff-created", actor_id, {"sourceProduct": source, "targetProduct": target, "entityType": entity_type, "contractVersion": contract_version, "envelopeHash": envelope_hash})
            row = con.execute("SELECT * FROM interoperability_handoffs WHERE id=?", (hid,)).fetchone()
        return {"ok": True, "handoff": self._handoff(row)}

    def _get_handoff_row(self, con: sqlite3.Connection, workspace_id: str, handoff_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM interoperability_handoffs WHERE id=? AND workspace_id=?", (_id(handoff_id, "handoff identifier"), workspace_id)).fetchone()
        if not row:
            raise InteroperabilityError("Interoperability handoff was not found.", 404)
        return row

    def seal_handoff(self, workspace_id: str, handoff_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "editor", False)
        body = _obj(payload or {}, 262144)
        with self._connect() as con:
            row = self._get_handoff_row(con, workspace_id, handoff_id)
            if row["direction"] != "export" or row["status"] != "draft":
                raise InteroperabilityError("Only draft export handoffs can be sealed.", 409)
            envelope = json.loads(row["envelope_json"])
            if _hash(envelope) != row["envelope_hash"]:
                raise InteroperabilityError("The handoff envelope failed integrity verification.", 409)
            compatibility = {"checked": False, "compatible": None, "requiredCapabilities": envelope.get("requiredCapabilities", [])}
            source_profile_id = body.get("sourceProfileId")
            target_profile_id = body.get("targetProfileId")
            if source_profile_id and target_profile_id:
                negotiation = self.negotiate(workspace_id, {"sourceProfileId": source_profile_id, "targetProfileId": target_profile_id, "requestedContracts": [envelope["contractVersion"]], "requiredCapabilities": envelope.get("requiredCapabilities", [])}, actor_id)["negotiation"]
                compatibility = negotiation
                if negotiation["sourceProfile"]["productId"] != envelope["sourceProduct"]:
                    raise InteroperabilityError("The source profile product does not match the handoff source product.", 409)
                if negotiation["targetProfile"]["productId"] != envelope["targetProduct"]:
                    raise InteroperabilityError("The target profile product does not match the handoff target product.", 409)
                if not negotiation["compatible"]:
                    raise InteroperabilityError("The source and target profiles are not compatible with this handoff.", 409)
            sealed = _now()
            con.execute("UPDATE interoperability_handoffs SET status='sealed',compatibility_json=?,updated_by=?,updated_at=?,sealed_at=? WHERE id=?", (_stable(compatibility), actor_id, sealed, sealed, row["id"]))
            self._event(con, workspace_id, "handoff", row["id"], "handoff-sealed", actor_id, {"envelopeHash": row["envelope_hash"], "compatibility": compatibility})
            updated = con.execute("SELECT * FROM interoperability_handoffs WHERE id=?", (row["id"],)).fetchone()
        return {"ok": True, "handoff": self._handoff(updated)}

    def export_bundle(self, workspace_id: str, handoff_id: str, actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            row = self._get_handoff_row(con, workspace_id, handoff_id)
            if row["status"] not in {"sealed", "delivered", "accepted", "rejected"}:
                raise InteroperabilityError("The handoff must be sealed before export.", 409)
            envelope = json.loads(row["envelope_json"])
            if _hash(envelope) != row["envelope_hash"]:
                raise InteroperabilityError("The handoff envelope failed integrity verification.", 409)
            bundle = {"schema": "sc-research-handoff-bundle/0.38.0", "version": VERSION, "envelope": envelope, "envelopeHash": row["envelope_hash"], "compatibility": json.loads(row["compatibility_json"]), "exportedAt": _now()}
            bundle["bundleHash"] = _hash(bundle)
            if row["status"] == "sealed":
                delivered = _now()
                con.execute("UPDATE interoperability_handoffs SET status='delivered',delivered_at=?,updated_at=?,updated_by=? WHERE id=?", (delivered, delivered, actor_id, row["id"]))
                self._event(con, workspace_id, "handoff", row["id"], "handoff-exported", actor_id, {"bundleHash": bundle["bundleHash"]})
        return {"ok": True, "bundle": bundle, "canonicalJson": _stable(bundle)}

    def import_envelope(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "contributor", False)
        body = _obj(payload)
        envelope = body.get("envelope") if isinstance(body.get("envelope"), dict) else body
        envelope = _obj(envelope)
        if envelope.get("schema") != ENVELOPE_SCHEMA or envelope.get("version") != VERSION:
            raise InteroperabilityError("The handoff envelope schema or version is not supported.", 422)
        claimed_hash = _sha(body.get("envelopeHash") or envelope.get("envelopeHash"), "envelope SHA-256")
        clean_envelope = copy.deepcopy(envelope)
        clean_envelope.pop("envelopeHash", None)
        actual_hash = _hash(clean_envelope)
        if actual_hash != claimed_hash:
            raise InteroperabilityError("The imported envelope hash does not match its canonical content.", 409)
        source = _product(clean_envelope.get("sourceProduct"), "source product")
        target = _product(clean_envelope.get("targetProduct"), "target product")
        entity_type = _text(clean_envelope.get("entityType"), 80).lower()
        if entity_type not in ENTITY_TYPES:
            raise InteroperabilityError("The imported entity type is not supported.")
        contract_version = _contract(clean_envelope.get("contractVersion"))
        _sha((clean_envelope.get("resource") or {}).get("sha256"), "resource SHA-256")
        hid = _id(body.get("importId") or f"import-{claimed_hash[:24]}", "import identifier")
        now = _now()
        with self._connect() as con:
            existing = con.execute("SELECT * FROM interoperability_handoffs WHERE workspace_id=? AND direction='import' AND envelope_hash=?", (workspace_id, claimed_hash)).fetchone()
            if existing:
                return {"ok": True, "idempotent": True, "handoff": self._handoff(existing)}
            con.execute(
                "INSERT INTO interoperability_handoffs(id,workspace_id,direction,source_product,target_product,entity_type,contract_version,status,external_id,envelope_json,envelope_hash,compatibility_json,created_by,created_at,updated_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (hid, workspace_id, "import", source, target, entity_type, contract_version, "received", clean_envelope.get("id"), _stable(clean_envelope), claimed_hash, _stable({"checked": True, "compatible": True, "imported": True}), actor_id, now, actor_id, now),
            )
            self._event(con, workspace_id, "handoff", hid, "handoff-imported", actor_id, {"sourceProduct": source, "targetProduct": target, "entityType": entity_type, "contractVersion": contract_version, "envelopeHash": claimed_hash})
            row = con.execute("SELECT * FROM interoperability_handoffs WHERE id=?", (hid,)).fetchone()
        return {"ok": True, "idempotent": False, "handoff": self._handoff(row)}

    def record_receipt(self, workspace_id: str, handoff_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "reviewer", False)
        body = _obj(payload, 512000)
        decision = _text(body.get("decision"), 30).lower()
        if decision not in DECISIONS:
            raise InteroperabilityError("Decision must be accepted, rejected, or needs-changes.")
        details = _obj(body.get("details") or {}, 262144)
        with self._connect() as con:
            row = self._get_handoff_row(con, workspace_id, handoff_id)
            if row["status"] == "withdrawn":
                raise InteroperabilityError("A withdrawn handoff cannot receive a receipt.", 409)
            if row["status"] == "draft":
                raise InteroperabilityError("The handoff must be sealed or received before a receipt can be recorded.", 409)
            created = _now()
            receipt_id = _id(body.get("id") or f"receipt-{row['id']}-{created.replace(':','').replace('-','')}", "receipt identifier")
            receipt_core = {"schema": RECEIPT_SCHEMA, "version": VERSION, "id": receipt_id, "handoffId": row["id"], "workspaceId": workspace_id, "envelopeHash": row["envelope_hash"], "decision": decision, "details": details, "actorId": actor_id, "createdAt": created}
            receipt_hash = _hash(receipt_core)
            signature = hmac.new(self.receipt_secret.encode("utf-8"), receipt_hash.encode("ascii"), sha256).hexdigest() if self.receipt_secret else None
            receipt = {**receipt_core, "receiptHash": receipt_hash, "signature": signature, "signatureMethod": "hmac-sha256" if signature else "sha256-receipt-hash"}
            new_status = "accepted" if decision == "accepted" else "rejected" if decision == "rejected" else row["status"]
            con.execute("INSERT INTO interoperability_receipts(id,handoff_id,workspace_id,decision,status,details_json,receipt_json,receipt_hash,signature,actor_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (receipt_id, row["id"], workspace_id, decision, "final" if decision in {"accepted", "rejected"} else "advisory", _stable(details), _stable(receipt), receipt_hash, signature, actor_id, created))
            con.execute("UPDATE interoperability_handoffs SET status=?,updated_by=?,updated_at=? WHERE id=?", (new_status, actor_id, created, row["id"]))
            self._event(con, workspace_id, "receipt", receipt_id, "handoff-receipt-recorded", actor_id, {"handoffId": row["id"], "decision": decision, "receiptHash": receipt_hash})
        return {"ok": True, "receipt": receipt}

    def verify_receipt(self, workspace_id: str, receipt_hash: str, actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id)
        digest = _sha(receipt_hash, "receipt SHA-256")
        with self._connect() as con:
            row = con.execute("SELECT * FROM interoperability_receipts WHERE workspace_id=? AND receipt_hash=?", (workspace_id, digest)).fetchone()
        if not row:
            raise InteroperabilityError("Interoperability receipt was not found.", 404)
        receipt = json.loads(row["receipt_json"])
        core = {k: receipt[k] for k in ["schema", "version", "id", "handoffId", "workspaceId", "envelopeHash", "decision", "details", "actorId", "createdAt"]}
        hash_valid = _hash(core) == row["receipt_hash"] == receipt.get("receiptHash")
        signature_valid = None
        if row["signature"]:
            expected = hmac.new(self.receipt_secret.encode("utf-8"), row["receipt_hash"].encode("ascii"), sha256).hexdigest()
            signature_valid = hmac.compare_digest(expected, row["signature"]) if self.receipt_secret else False
        return {"ok": bool(hash_valid and signature_valid is not False), "receipt": receipt, "integrity": {"hashValid": hash_valid, "signatureValid": signature_valid}}

    def withdraw(self, workspace_id: str, handoff_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id, "editor", False)
        reason = _text((_obj(payload or {}, 262144)).get("reason"), 1000)
        if not reason:
            raise InteroperabilityError("A withdrawal reason is required.")
        with self._connect() as con:
            row = self._get_handoff_row(con, workspace_id, handoff_id)
            if row["status"] == "withdrawn":
                return {"ok": True, "handoff": self._handoff(row)}
            if row["status"] == "accepted":
                raise InteroperabilityError("Accepted handoffs cannot be withdrawn; issue a superseding handoff instead.", 409)
            now = _now()
            con.execute("UPDATE interoperability_handoffs SET status='withdrawn',withdrawn_at=?,withdrawal_reason=?,updated_by=?,updated_at=? WHERE id=?", (now, reason, actor_id, now, row["id"]))
            self._event(con, workspace_id, "handoff", row["id"], "handoff-withdrawn", actor_id, {"reason": reason})
            updated = con.execute("SELECT * FROM interoperability_handoffs WHERE id=?", (row["id"],)).fetchone()
        return {"ok": True, "handoff": self._handoff(updated)}

    def get_handoff(self, workspace_id: str, handoff_id: str, actor_id: str) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id)
        with self._connect() as con:
            row = self._get_handoff_row(con, workspace_id, handoff_id)
            receipts = con.execute("SELECT receipt_json FROM interoperability_receipts WHERE handoff_id=? ORDER BY created_at", (row["id"],)).fetchall()
        return {"ok": True, "handoff": self._handoff(row), "receipts": [json.loads(r[0]) for r in receipts]}

    def list_handoffs(self, workspace_id: str, actor_id: str, status: str = "", direction: str = "", limit: int = 200) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id)
        where = ["workspace_id=?"]; args: list[Any] = [workspace_id]
        if status:
            if status not in HANDOFF_STATUSES: raise InteroperabilityError("Unknown handoff status.")
            where.append("status=?"); args.append(status)
        if direction:
            if direction not in DIRECTIONS: raise InteroperabilityError("Direction must be export or import.")
            where.append("direction=?"); args.append(direction)
        args.append(max(1, min(2000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM interoperability_handoffs WHERE {' AND '.join(where)} ORDER BY updated_at DESC LIMIT ?", args).fetchall()
        return {"ok": True, "handoffs": [self._handoff(r) for r in rows], "count": len(rows)}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        self._workspace(workspace_id, actor_id)
        with self._connect() as con:
            rows = con.execute("SELECT * FROM interoperability_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(5000, int(limit))))).fetchall()
        events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": r["sequence"], "workspaceId": r["workspace_id"], "entityType": r["entity_type"], "entityId": r["entity_id"], "eventType": r["event_type"], "actorId": r["actor_id"], "details": json.loads(r["details_json"]), "eventHash": r["event_hash"], "createdAt": r["created_at"]} for r in rows]
        return {"ok": True, "events": events, "count": len(events)}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema = con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]
            counts = {
                "profiles": con.execute("SELECT COUNT(*) FROM interoperability_profiles").fetchone()[0],
                "handoffs": con.execute("SELECT COUNT(*) FROM interoperability_handoffs").fetchone()[0],
                "receipts": con.execute("SELECT COUNT(*) FROM interoperability_receipts").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM interoperability_events").fetchone()[0],
            }
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schema": "sc-research-interoperability-health/0.38.0", "database": {"path": self.db_path, "schemaVersion": schema, "integrity": integrity}, "counts": counts, "receiptSigning": "hmac-sha256" if self.receipt_secret else "sha256-receipt-hash", "capabilities": policies(self.max_profiles, self.max_handoffs)["capabilities"], "time": _now()}
