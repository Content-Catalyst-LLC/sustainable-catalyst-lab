from __future__ import annotations

import hashlib
import hmac
import time
from fastapi import Header, HTTPException, Request, status

from .config import settings


def body_sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def canonical_message(timestamp: str, method: str, path: str, body: bytes) -> bytes:
    return f"{timestamp}\n{method.upper()}\n{path}\n{body_sha256(body)}".encode("utf-8")


def make_signature(secret: str, timestamp: str, method: str, path: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), canonical_message(timestamp, method, path, body), hashlib.sha256).hexdigest()


def verify_signature(secret: str, timestamp: str, method: str, path: str, body: bytes, signature: str) -> bool:
    expected = make_signature(secret, timestamp, method, path, body)
    return hmac.compare_digest(expected, signature)


async def require_compute_auth(
    request: Request,
    x_sc_lab_key: str | None = Header(default=None),
    x_sc_lab_timestamp: str | None = Header(default=None),
    x_sc_lab_signature: str | None = Header(default=None),
    x_sc_lab_client: str | None = Header(default=None),
) -> dict[str, str]:
    if settings.auth_mode == "open-development":
        return {"mode": settings.auth_mode, "client": x_sc_lab_client or "local-development"}

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
        return {"mode": "hmac-sha256", "client": x_sc_lab_client or "wordpress"}

    if not x_sc_lab_key or not hmac.compare_digest(x_sc_lab_key, settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid compute API key.")
    return {"mode": "api-key", "client": x_sc_lab_client or "wordpress"}
