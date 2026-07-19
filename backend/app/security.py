from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import re
import sqlite3
import time
from fastapi import Header, HTTPException, Request, status

from .config import settings

NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


def body_sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def canonical_message(timestamp: str, method: str, path: str, body: bytes) -> bytes:
    return f"{timestamp}\n{method.upper()}\n{path}\n{body_sha256(body)}".encode("utf-8")


def make_signature(secret: str, timestamp: str, method: str, path: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), canonical_message(timestamp, method, path, body), hashlib.sha256).hexdigest()


def verify_signature(secret: str, timestamp: str, method: str, path: str, body: bytes, signature: str) -> bool:
    expected = make_signature(secret, timestamp, method, path, body)
    return hmac.compare_digest(expected, signature)


class ReplayNonceStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS request_nonces(nonce_hash TEXT PRIMARY KEY, expires_at INTEGER NOT NULL)")

    def _db(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10)

    def claim(self, timestamp: str, nonce: str, signature: str, ttl_seconds: int) -> bool:
        now = int(time.time())
        digest = hashlib.sha256(f"{timestamp}:{nonce}:{signature}".encode()).hexdigest()
        with self._db() as db:
            db.execute("DELETE FROM request_nonces WHERE expires_at < ?", (now,))
            try:
                db.execute("INSERT INTO request_nonces(nonce_hash, expires_at) VALUES(?,?)", (digest, now + ttl_seconds))
            except sqlite3.IntegrityError:
                return False
        return True


_replay_store: ReplayNonceStore | None = None
_replay_store_path = ""


def _replay() -> ReplayNonceStore:
    global _replay_store, _replay_store_path
    if _replay_store is None or _replay_store_path != settings.security_replay_db_path:
        _replay_store = ReplayNonceStore(settings.security_replay_db_path)
        _replay_store_path = settings.security_replay_db_path
    return _replay_store


async def require_compute_auth(
    request: Request,
    x_sc_lab_key: str | None = Header(default=None),
    x_sc_lab_timestamp: str | None = Header(default=None),
    x_sc_lab_signature: str | None = Header(default=None),
    x_sc_lab_nonce: str | None = Header(default=None),
    x_sc_lab_client: str | None = Header(default=None),
    x_sc_lab_actor: str | None = Header(default=None),
    x_sc_lab_actor_name: str | None = Header(default=None),
) -> dict[str, str]:
    if settings.auth_mode == "open-development":
        return {"mode": settings.auth_mode, "client": x_sc_lab_client or "local-development", "actor": x_sc_lab_actor or x_sc_lab_client or "local-development", "actorName": x_sc_lab_actor_name or "Local development"}

    if settings.signing_secret:
        if not x_sc_lab_timestamp or not x_sc_lab_signature:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signed compute request required.")
        try:
            sent = int(x_sc_lab_timestamp)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid compute timestamp.") from exc
        if abs(int(time.time()) - sent) > settings.signature_tolerance_seconds:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired compute signature.")
        body = await request.body()
        if not verify_signature(settings.signing_secret, x_sc_lab_timestamp, request.method, request.url.path, body, x_sc_lab_signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid compute signature.")
        if settings.security_require_request_nonce:
            if not x_sc_lab_nonce or not NONCE_RE.fullmatch(x_sc_lab_nonce):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="A valid unique request nonce is required.")
            if not _replay().claim(x_sc_lab_timestamp, x_sc_lab_nonce, x_sc_lab_signature, settings.signature_tolerance_seconds * 2):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Replayed compute request rejected.")
        return {"mode": "hmac-sha256", "client": x_sc_lab_client or "wordpress", "actor": x_sc_lab_actor or x_sc_lab_client or "wordpress", "actorName": x_sc_lab_actor_name or "WordPress user"}

    if not x_sc_lab_key or not hmac.compare_digest(x_sc_lab_key, settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid compute API key.")
    return {"mode": "api-key", "client": x_sc_lab_client or "wordpress", "actor": x_sc_lab_actor or x_sc_lab_client or "wordpress", "actorName": x_sc_lab_actor_name or "WordPress user"}
