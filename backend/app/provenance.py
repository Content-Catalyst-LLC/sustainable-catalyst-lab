from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

from .config import settings
from .schemas import ProvenanceRecord


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def package_versions(names: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in sorted(set(names + ["fastapi", "pydantic"])):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "unavailable"
    return versions


def build_provenance(*, method: str, method_version: str, inputs: dict[str, Any], result: dict[str, Any], duration_ms: float, packages: list[str], random_seed: int | None, auth: dict[str, str]) -> ProvenanceRecord:
    return ProvenanceRecord(
        run_id=str(uuid.uuid4()),
        method=method,
        method_version=method_version,
        service_version=settings.version,
        executed_at=datetime.now(timezone.utc).isoformat(),
        duration_ms=round(duration_ms, 3),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        packages=package_versions(packages),
        input_sha256=digest(inputs),
        result_sha256=digest(result),
        random_seed=random_seed,
        authentication_mode=auth.get("mode", "unknown"),
        client_id=auth.get("client", "unknown"),
    )
