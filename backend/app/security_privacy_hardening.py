from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VERSION = "0.39.1"
SECRET_SCHEMA = "sc-lab-secret-record/0.39.1"
CREDENTIAL_SCHEMA = "sc-lab-service-credential/0.39.1"
AUDIT_SCHEMA = "sc-lab-security-audit-event/0.39.1"
PRIVACY_REQUEST_SCHEMA = "sc-lab-privacy-request/0.39.1"

SENSITIVE_KEYS = {
    "password", "passwd", "secret", "token", "api_key", "apikey", "credential",
    "private_key", "access_token", "refresh_token", "authorization", "cookie",
    "ssn", "social_security_number", "medical_record", "biometric", "raw_restricted_data",
}
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,127}$")


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    data = value if isinstance(value, bytes) else _canonical(value)
    return hashlib.sha256(data).hexdigest()


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if not IDENTIFIER_RE.fullmatch(text):
        raise SecurityHardeningError(422, f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 500) -> str:
    text = str(value or "").strip()
    if not text or len(text) > maximum:
        raise SecurityHardeningError(422, f"Invalid {label}.")
    return text


def _decode_key(value: str) -> bytes | None:
    value = (value or "").strip()
    if not value:
        return None
    if re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raw = bytes.fromhex(value)
    else:
        padding = "=" * (-len(value) % 4)
        try:
            raw = base64.urlsafe_b64decode(value + padding)
        except Exception as exc:
            raise ValueError("Secret master key must be 32-byte hex or URL-safe base64.") from exc
    if len(raw) != 32:
        raise ValueError("Secret master key must decode to exactly 32 bytes.")
    return raw


def _safe_detail(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in SENSITIVE_KEYS or any(part in normalized for part in ("secret", "password", "credential", "token", "private_key")):
                out[str(key)] = "[REDACTED]"
            else:
                out[str(key)] = _safe_detail(item)
        return out
    if isinstance(value, list):
        return [_safe_detail(item) for item in value]
    if isinstance(value, str):
        text = EMAIL_RE.sub("[EMAIL]", value)
        return PHONE_RE.sub("[PHONE]", text)
    return value


def privacy_scan(value: Any) -> dict[str, Any]:
    findings: list[dict[str, str]] = []

    def walk(item: Any, path: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                child_path = f"{path}.{key}" if path else str(key)
                normalized = str(key).lower().replace("-", "_")
                if normalized in SENSITIVE_KEYS or any(part in normalized for part in ("secret", "password", "credential", "token", "private_key")):
                    findings.append({"path": child_path, "category": "secret-or-credential"})
                walk(child, child_path)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{path}[{index}]")
        elif isinstance(item, str):
            if EMAIL_RE.search(item):
                findings.append({"path": path or "$", "category": "email"})
            if PHONE_RE.search(item):
                findings.append({"path": path or "$", "category": "phone"})

    walk(value, "")
    unique = {(entry["path"], entry["category"]): entry for entry in findings}
    ordered = [unique[key] for key in sorted(unique)]
    return {"ok": True, "version": VERSION, "findingCount": len(ordered), "findings": ordered, "containsSensitiveData": bool(ordered)}


def privacy_redact(value: Any) -> Any:
    return _safe_detail(value)


class SecurityHardeningError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def policies(persistent_disk_mounted: bool = False, vault_locked: bool = True) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-security-privacy-policy/0.39.1",
        "capabilities": {
            "aes256GcmSecretVault": True,
            "versionedSecretRotation": True,
            "oneTimeCredentialDisclosure": True,
            "scryptCredentialHashes": True,
            "nonceReplayProtection": True,
            "tamperEvidentAuditChain": True,
            "optionalAuditHmac": True,
            "recursivePrivacyScanning": True,
            "deterministicRedaction": True,
            "privacyRequestWorkflow": True,
            "singleSignOn": False,
            "externalKeyManagement": False,
        },
        "defaults": {
            "secretValuesReturnedByList": False,
            "credentialPlaintextRetention": False,
            "auditDetailRedaction": True,
            "vaultLocked": vault_locked,
            "storageDurability": "persistent-disk" if persistent_disk_mounted else "instance-local",
        },
    }


class SecurityPrivacyManager:
    def __init__(
        self,
        db_path: str,
        master_key: str = "",
        previous_keys_json: str = "",
        audit_secret: str = "",
        persistent_disk_mounted: bool = False,
        max_secrets: int = 100000,
        max_credentials: int = 250000,
        history_limit: int = 500000,
        credential_ttl_days: int = 90,
    ):
        self.db_path = db_path
        self.persistent_disk_mounted = persistent_disk_mounted
        self.max_secrets = max_secrets
        self.max_credentials = max_credentials
        self.history_limit = history_limit
        self.credential_ttl_days = credential_ttl_days
        self.audit_secret = (audit_secret or "").encode("utf-8")
        self.keys: dict[str, bytes] = {}
        active = _decode_key(master_key)
        self.active_key_id = ""
        if active:
            self.active_key_id = hashlib.sha256(active).hexdigest()[:16]
            self.keys[self.active_key_id] = active
        if previous_keys_json.strip():
            try:
                previous = json.loads(previous_keys_json)
                if not isinstance(previous, dict):
                    raise ValueError
                for key_id, encoded in previous.items():
                    raw = _decode_key(str(encoded))
                    if raw:
                        calculated = hashlib.sha256(raw).hexdigest()[:16]
                        if str(key_id) not in {calculated, "auto"}:
                            raise ValueError(f"Previous key ID {key_id} does not match key material.")
                        self.keys[calculated] = raw
            except Exception as exc:
                raise ValueError("SC_LAB_SECRET_PREVIOUS_MASTER_KEYS must be a JSON object of key IDs to 32-byte keys.") from exc
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @property
    def vault_locked(self) -> bool:
        return not bool(self.active_key_id)

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS secret_versions (
                id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, name TEXT NOT NULL,
                version INTEGER NOT NULL, key_id TEXT NOT NULL, nonce BLOB NOT NULL,
                ciphertext BLOB NOT NULL, aad TEXT NOT NULL, value_digest TEXT NOT NULL,
                status TEXT NOT NULL, created_by TEXT NOT NULL, created_at TEXT NOT NULL,
                rotated_from TEXT, metadata_json TEXT NOT NULL DEFAULT '{}',
                UNIQUE(institution_id, name, version)
            );
            CREATE INDEX IF NOT EXISTS idx_secret_active ON secret_versions(institution_id, name, status);
            CREATE TABLE IF NOT EXISTS service_credentials (
                id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, principal_id TEXT NOT NULL,
                label TEXT NOT NULL, token_prefix TEXT NOT NULL, salt BLOB NOT NULL,
                token_hash BLOB NOT NULL, scopes_json TEXT NOT NULL, status TEXT NOT NULL,
                issued_by TEXT NOT NULL, issued_at TEXT NOT NULL, expires_at TEXT NOT NULL,
                revoked_at TEXT, last_verified_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_credentials_prefix ON service_credentials(token_prefix, status);
            CREATE TABLE IF NOT EXISTS privacy_requests (
                id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, request_type TEXT NOT NULL,
                subject_reference TEXT NOT NULL, status TEXT NOT NULL, requested_by TEXT NOT NULL,
                requested_at TEXT NOT NULL, due_at TEXT NOT NULL, resolved_by TEXT,
                resolved_at TEXT, resolution TEXT, metadata_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS security_audit_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL,
                institution_id TEXT NOT NULL, event_type TEXT NOT NULL, actor_id TEXT NOT NULL,
                subject_type TEXT NOT NULL, subject_id TEXT NOT NULL, detail_json TEXT NOT NULL,
                previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL, signature TEXT,
                created_at TEXT NOT NULL
            );
            """)

    def _require_vault(self) -> tuple[str, bytes]:
        if self.vault_locked:
            raise SecurityHardeningError(503, "Secret vault is locked. Configure SC_LAB_SECRET_MASTER_KEY with a 32-byte key.")
        return self.active_key_id, self.keys[self.active_key_id]

    def _event(self, institution_id: str, event_type: str, actor: str, subject_type: str, subject_id: str, detail: Any) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        safe = _safe_detail(detail)
        with self._db() as db:
            previous = db.execute("SELECT event_hash FROM security_audit_events WHERE institution_id=? ORDER BY sequence DESC LIMIT 1", (institution_id,)).fetchone()
            previous_hash = previous["event_hash"] if previous else "0" * 64
            created_at = _utc()
            event_id = "audit-" + secrets.token_hex(12)
            core = {
                "schema": AUDIT_SCHEMA, "id": event_id, "institutionId": institution_id,
                "eventType": event_type, "actorId": actor, "subjectType": subject_type,
                "subjectId": subject_id, "detail": safe, "previousHash": previous_hash,
                "createdAt": created_at,
            }
            event_hash = _sha(core)
            signature = hmac.new(self.audit_secret, event_hash.encode("ascii"), hashlib.sha256).hexdigest() if self.audit_secret else None
            db.execute(
                "INSERT INTO security_audit_events(id,institution_id,event_type,actor_id,subject_type,subject_id,detail_json,previous_hash,event_hash,signature,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (event_id, institution_id, event_type, actor, subject_type, subject_id, json.dumps(safe, separators=(",", ":")), previous_hash, event_hash, signature, created_at),
            )
            excess = db.execute("SELECT COUNT(*) AS n FROM security_audit_events").fetchone()["n"] - self.history_limit
            if excess > 0:
                db.execute("DELETE FROM security_audit_events WHERE sequence IN (SELECT sequence FROM security_audit_events ORDER BY sequence LIMIT ?)", (excess,))
        return {**core, "eventHash": event_hash, "signature": signature}

    @staticmethod
    def _secret_public(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": SECRET_SCHEMA, "id": row["id"], "institutionId": row["institution_id"],
            "name": row["name"], "version": row["version"], "keyId": row["key_id"],
            "status": row["status"], "valueDigest": row["value_digest"], "createdBy": row["created_by"],
            "createdAt": row["created_at"], "rotatedFrom": row["rotated_from"],
            "metadata": json.loads(row["metadata_json"] or "{}"), "valueStored": True,
        }

    def list_secrets(self, institution_id: str, actor: str, name: str = "") -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        query = "SELECT * FROM secret_versions WHERE institution_id=?"
        params: list[Any] = [institution_id]
        if name:
            query += " AND name=?"
            params.append(_clean_id(name, "secret name"))
        query += " ORDER BY name, version DESC"
        with self._db() as db:
            rows = db.execute(query, params).fetchall()
        self._event(institution_id, "secret.metadata.listed", actor, "institution", institution_id, {"nameFilter": name, "count": len(rows)})
        return {"ok": True, "secrets": [self._secret_public(row) for row in rows], "valuesDisclosed": False}

    def put_secret(self, institution_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        key_id, key = self._require_vault()
        institution_id = _clean_id(institution_id, "institution ID")
        name = _clean_id(payload.get("name"), "secret name")
        value = _clean_text(payload.get("value"), "secret value", 65536)
        metadata = _safe_detail(payload.get("metadata") or {})
        with self._db() as db:
            total = db.execute("SELECT COUNT(*) AS n FROM secret_versions").fetchone()["n"]
            if total >= self.max_secrets:
                raise SecurityHardeningError(429, "Secret vault capacity reached.")
            current = db.execute("SELECT * FROM secret_versions WHERE institution_id=? AND name=? AND status='active' ORDER BY version DESC LIMIT 1", (institution_id, name)).fetchone()
            version = (current["version"] + 1) if current else 1
            secret_id = f"secret-{secrets.token_hex(12)}"
            aad_obj = {"schema": SECRET_SCHEMA, "institutionId": institution_id, "name": name, "version": version, "keyId": key_id}
            aad = _canonical(aad_obj)
            nonce = os.urandom(12)
            ciphertext = AESGCM(key).encrypt(nonce, value.encode("utf-8"), aad)
            if current:
                db.execute("UPDATE secret_versions SET status='superseded' WHERE id=?", (current["id"],))
            db.execute(
                "INSERT INTO secret_versions(id,institution_id,name,version,key_id,nonce,ciphertext,aad,value_digest,status,created_by,created_at,rotated_from,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (secret_id, institution_id, name, version, key_id, nonce, ciphertext, aad.decode("utf-8"), hashlib.sha256(value.encode("utf-8")).hexdigest(), "active", actor, _utc(), current["id"] if current else None, json.dumps(metadata, separators=(",", ":"))),
            )
            row = db.execute("SELECT * FROM secret_versions WHERE id=?", (secret_id,)).fetchone()
        self._event(institution_id, "secret.created" if version == 1 else "secret.rotated", actor, "secret", secret_id, {"name": name, "version": version, "keyId": key_id, "rotatedFrom": current["id"] if current else None})
        return {"ok": True, "secret": self._secret_public(row), "valueDisclosed": False}

    def resolve_secret(self, institution_id: str, name: str) -> str:
        institution_id = _clean_id(institution_id, "institution ID")
        name = _clean_id(name, "secret name")
        with self._db() as db:
            row = db.execute("SELECT * FROM secret_versions WHERE institution_id=? AND name=? AND status='active' ORDER BY version DESC LIMIT 1", (institution_id, name)).fetchone()
        if not row:
            raise SecurityHardeningError(404, "Secret not found.")
        key = self.keys.get(row["key_id"])
        if not key:
            raise SecurityHardeningError(503, f"Secret key {row['key_id']} is not available in the configured keyring.")
        try:
            plaintext = AESGCM(key).decrypt(row["nonce"], row["ciphertext"], row["aad"].encode("utf-8"))
        except Exception as exc:
            raise SecurityHardeningError(409, "Secret integrity verification failed.") from exc
        return plaintext.decode("utf-8")

    def verify_secret(self, institution_id: str, name: str, candidate: str, actor: str) -> dict[str, Any]:
        actual = self.resolve_secret(institution_id, name)
        valid = hmac.compare_digest(actual.encode("utf-8"), str(candidate or "").encode("utf-8"))
        self._event(institution_id, "secret.verified", actor, "secret", name, {"valid": valid})
        return {"ok": True, "name": name, "valid": valid, "valueDisclosed": False}

    @staticmethod
    def _hash_token(token: str, salt: bytes) -> bytes:
        return hashlib.scrypt(token.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)

    def issue_credential(self, institution_id: str, principal_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        principal_id = _clean_id(principal_id, "principal ID")
        label = _clean_text(payload.get("label") or "Service credential", "credential label", 200)
        scopes = sorted({_clean_id(scope, "scope") for scope in (payload.get("scopes") or ["research:read"])})
        ttl_days = int(payload.get("ttlDays") or self.credential_ttl_days)
        ttl_days = max(1, min(ttl_days, 365))
        with self._db() as db:
            total = db.execute("SELECT COUNT(*) AS n FROM service_credentials").fetchone()["n"]
            if total >= self.max_credentials:
                raise SecurityHardeningError(429, "Credential capacity reached.")
        credential_id = "credential-" + secrets.token_hex(12)
        prefix = secrets.token_hex(4)
        token = f"sclab_{prefix}_{secrets.token_urlsafe(32)}"
        salt = os.urandom(16)
        token_hash = self._hash_token(token, salt)
        issued_at = _utc()
        expires_at = (datetime.now(timezone.utc) + timedelta(days=ttl_days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        with self._db() as db:
            db.execute(
                "INSERT INTO service_credentials(id,institution_id,principal_id,label,token_prefix,salt,token_hash,scopes_json,status,issued_by,issued_at,expires_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (credential_id, institution_id, principal_id, label, prefix, salt, token_hash, json.dumps(scopes), "active", actor, issued_at, expires_at),
            )
        self._event(institution_id, "credential.issued", actor, "service-credential", credential_id, {"principalId": principal_id, "label": label, "scopes": scopes, "expiresAt": expires_at})
        public = {"schema": CREDENTIAL_SCHEMA, "id": credential_id, "institutionId": institution_id, "principalId": principal_id, "label": label, "tokenPrefix": prefix, "scopes": scopes, "status": "active", "issuedBy": actor, "issuedAt": issued_at, "expiresAt": expires_at}
        return {"ok": True, "credential": public, "token": token, "tokenDisclosure": "one-time"}

    def list_credentials(self, institution_id: str, actor: str, principal_id: str = "") -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        query = "SELECT * FROM service_credentials WHERE institution_id=?"
        params: list[Any] = [institution_id]
        if principal_id:
            query += " AND principal_id=?"
            params.append(_clean_id(principal_id, "principal ID"))
        query += " ORDER BY issued_at DESC"
        with self._db() as db:
            rows = db.execute(query, params).fetchall()
        credentials = [{"schema": CREDENTIAL_SCHEMA, "id": row["id"], "institutionId": row["institution_id"], "principalId": row["principal_id"], "label": row["label"], "tokenPrefix": row["token_prefix"], "scopes": json.loads(row["scopes_json"]), "status": row["status"], "issuedBy": row["issued_by"], "issuedAt": row["issued_at"], "expiresAt": row["expires_at"], "revokedAt": row["revoked_at"], "lastVerifiedAt": row["last_verified_at"]} for row in rows]
        self._event(institution_id, "credential.metadata.listed", actor, "institution", institution_id, {"principalId": principal_id, "count": len(credentials)})
        return {"ok": True, "credentials": credentials, "tokensDisclosed": False}

    def verify_credential(self, token: str, required_scope: str = "") -> dict[str, Any]:
        parts = str(token or "").split("_", 2)
        if len(parts) != 3 or parts[0] != "sclab":
            return {"ok": True, "valid": False, "reason": "invalid-format"}
        prefix = parts[1]
        now = datetime.now(timezone.utc)
        with self._db() as db:
            rows = db.execute("SELECT * FROM service_credentials WHERE token_prefix=? AND status='active'", (prefix,)).fetchall()
            for row in rows:
                if datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) <= now:
                    continue
                candidate = self._hash_token(token, row["salt"])
                if hmac.compare_digest(candidate, row["token_hash"]):
                    scopes = json.loads(row["scopes_json"])
                    if required_scope and required_scope not in scopes and "*" not in scopes:
                        return {"ok": True, "valid": False, "reason": "insufficient-scope", "credentialId": row["id"]}
                    verified = _utc()
                    db.execute("UPDATE service_credentials SET last_verified_at=? WHERE id=?", (verified, row["id"]))
                    return {"ok": True, "valid": True, "credentialId": row["id"], "institutionId": row["institution_id"], "principalId": row["principal_id"], "scopes": scopes, "verifiedAt": verified}
        return {"ok": True, "valid": False, "reason": "not-found-or-expired"}

    def revoke_credential(self, institution_id: str, credential_id: str, actor: str) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        credential_id = _clean_id(credential_id, "credential ID")
        revoked_at = _utc()
        with self._db() as db:
            row = db.execute("SELECT * FROM service_credentials WHERE id=? AND institution_id=?", (credential_id, institution_id)).fetchone()
            if not row:
                raise SecurityHardeningError(404, "Credential not found.")
            if row["status"] != "revoked":
                db.execute("UPDATE service_credentials SET status='revoked', revoked_at=? WHERE id=?", (revoked_at, credential_id))
        self._event(institution_id, "credential.revoked", actor, "service-credential", credential_id, {"principalId": row["principal_id"]})
        return {"ok": True, "credentialId": credential_id, "status": "revoked", "revokedAt": revoked_at}

    def create_privacy_request(self, institution_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        request_type = str(payload.get("requestType") or "access").strip().lower()
        if request_type not in {"access", "correction", "deletion", "restriction", "portability", "objection"}:
            raise SecurityHardeningError(422, "Unsupported privacy request type.")
        subject_reference = _clean_text(payload.get("subjectReference"), "subject reference", 300)
        request_id = _clean_id(payload.get("id") or f"privacy-{secrets.token_hex(12)}", "privacy request ID")
        requested_at = _utc()
        due_at = (datetime.now(timezone.utc) + timedelta(days=max(1, min(int(payload.get("dueDays") or 30), 90)))).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        metadata = _safe_detail(payload.get("metadata") or {})
        with self._db() as db:
            try:
                db.execute("INSERT INTO privacy_requests(id,institution_id,request_type,subject_reference,status,requested_by,requested_at,due_at,metadata_json) VALUES(?,?,?,?,?,?,?,?,?)", (request_id, institution_id, request_type, subject_reference, "open", actor, requested_at, due_at, json.dumps(metadata, separators=(",", ":"))))
            except sqlite3.IntegrityError as exc:
                raise SecurityHardeningError(409, "Privacy request already exists.") from exc
        self._event(institution_id, "privacy.request.created", actor, "privacy-request", request_id, {"requestType": request_type, "subjectReferenceHash": hashlib.sha256(subject_reference.encode()).hexdigest(), "dueAt": due_at})
        return {"ok": True, "privacyRequest": {"schema": PRIVACY_REQUEST_SCHEMA, "id": request_id, "institutionId": institution_id, "requestType": request_type, "subjectReference": subject_reference, "status": "open", "requestedBy": actor, "requestedAt": requested_at, "dueAt": due_at, "metadata": metadata}}

    def list_privacy_requests(self, institution_id: str, actor: str, status: str = "") -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        query = "SELECT * FROM privacy_requests WHERE institution_id=?"
        params: list[Any] = [institution_id]
        if status:
            query += " AND status=?"; params.append(status)
        query += " ORDER BY requested_at DESC"
        with self._db() as db:
            rows = db.execute(query, params).fetchall()
        requests = [{"schema": PRIVACY_REQUEST_SCHEMA, "id": row["id"], "institutionId": row["institution_id"], "requestType": row["request_type"], "subjectReference": row["subject_reference"], "status": row["status"], "requestedBy": row["requested_by"], "requestedAt": row["requested_at"], "dueAt": row["due_at"], "resolvedBy": row["resolved_by"], "resolvedAt": row["resolved_at"], "resolution": row["resolution"], "metadata": json.loads(row["metadata_json"] or "{}")} for row in rows]
        self._event(institution_id, "privacy.request.listed", actor, "institution", institution_id, {"status": status, "count": len(requests)})
        return {"ok": True, "privacyRequests": requests}

    def resolve_privacy_request(self, institution_id: str, request_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        request_id = _clean_id(request_id, "privacy request ID")
        status = str(payload.get("status") or "completed").strip().lower()
        if status not in {"completed", "denied", "cancelled"}:
            raise SecurityHardeningError(422, "Invalid privacy request resolution status.")
        resolution = _clean_text(payload.get("resolution"), "resolution", 2000)
        resolved_at = _utc()
        with self._db() as db:
            row = db.execute("SELECT * FROM privacy_requests WHERE id=? AND institution_id=?", (request_id, institution_id)).fetchone()
            if not row:
                raise SecurityHardeningError(404, "Privacy request not found.")
            if row["status"] != "open":
                raise SecurityHardeningError(409, "Privacy request is already closed.")
            db.execute("UPDATE privacy_requests SET status=?, resolved_by=?, resolved_at=?, resolution=? WHERE id=?", (status, actor, resolved_at, resolution, request_id))
        self._event(institution_id, "privacy.request.resolved", actor, "privacy-request", request_id, {"status": status, "resolution": resolution})
        return {"ok": True, "privacyRequestId": request_id, "status": status, "resolvedBy": actor, "resolvedAt": resolved_at}

    def audit_timeline(self, institution_id: str, actor: str, limit: int = 500) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        limit = max(1, min(int(limit), 5000))
        with self._db() as db:
            rows = db.execute("SELECT * FROM security_audit_events WHERE institution_id=? ORDER BY sequence DESC LIMIT ?", (institution_id, limit)).fetchall()
        events = [{"schema": AUDIT_SCHEMA, "id": row["id"], "institutionId": row["institution_id"], "eventType": row["event_type"], "actorId": row["actor_id"], "subjectType": row["subject_type"], "subjectId": row["subject_id"], "detail": json.loads(row["detail_json"]), "previousHash": row["previous_hash"], "eventHash": row["event_hash"], "signature": row["signature"], "createdAt": row["created_at"]} for row in rows]
        return {"ok": True, "events": events, "requestedBy": actor}

    def verify_audit_chain(self, institution_id: str, actor: str) -> dict[str, Any]:
        institution_id = _clean_id(institution_id, "institution ID")
        with self._db() as db:
            rows = db.execute("SELECT * FROM security_audit_events WHERE institution_id=? ORDER BY sequence", (institution_id,)).fetchall()
        previous_hash = "0" * 64
        for row in rows:
            detail = json.loads(row["detail_json"])
            core = {"schema": AUDIT_SCHEMA, "id": row["id"], "institutionId": row["institution_id"], "eventType": row["event_type"], "actorId": row["actor_id"], "subjectType": row["subject_type"], "subjectId": row["subject_id"], "detail": detail, "previousHash": row["previous_hash"], "createdAt": row["created_at"]}
            calculated = _sha(core)
            if row["previous_hash"] != previous_hash or row["event_hash"] != calculated:
                return {"ok": True, "valid": False, "failedEventId": row["id"], "verifiedBy": actor}
            if self.audit_secret:
                expected = hmac.new(self.audit_secret, row["event_hash"].encode("ascii"), hashlib.sha256).hexdigest()
                if not row["signature"] or not hmac.compare_digest(expected, row["signature"]):
                    return {"ok": True, "valid": False, "failedEventId": row["id"], "reason": "signature", "verifiedBy": actor}
            previous_hash = row["event_hash"]
        return {"ok": True, "valid": True, "eventCount": len(rows), "headHash": previous_hash, "signed": bool(self.audit_secret), "verifiedBy": actor}

    def health(self) -> dict[str, Any]:
        with self._db() as db:
            counts = {
                "secretVersions": db.execute("SELECT COUNT(*) AS n FROM secret_versions").fetchone()["n"],
                "activeSecrets": db.execute("SELECT COUNT(*) AS n FROM secret_versions WHERE status='active'").fetchone()["n"],
                "credentials": db.execute("SELECT COUNT(*) AS n FROM service_credentials").fetchone()["n"],
                "activeCredentials": db.execute("SELECT COUNT(*) AS n FROM service_credentials WHERE status='active'").fetchone()["n"],
                "privacyRequests": db.execute("SELECT COUNT(*) AS n FROM privacy_requests").fetchone()["n"],
                "openPrivacyRequests": db.execute("SELECT COUNT(*) AS n FROM privacy_requests WHERE status='open'").fetchone()["n"],
                "auditEvents": db.execute("SELECT COUNT(*) AS n FROM security_audit_events").fetchone()["n"],
            }
        return {"ok": True, "status": "ready" if not self.vault_locked else "vault-locked", "version": VERSION, "schema": "sc-lab-security-privacy-health/0.39.1", "vaultLocked": self.vault_locked, "activeKeyId": self.active_key_id or None, "availableKeyIds": sorted(self.keys), "auditSigning": bool(self.audit_secret), "persistentDiskMounted": self.persistent_disk_mounted, "counts": counts}
