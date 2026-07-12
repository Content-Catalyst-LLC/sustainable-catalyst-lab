from __future__ import annotations

from typing import Any

from .executor import compare_languages, execute_method


def perform(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    if operation == "execute":
        return execute_method(
            payload["methodId"],
            payload["language"],
            payload.get("inputs", {}),
            payload.get("timeoutSeconds", 8),
            payload.get("includeSource", False),
        )
    if operation == "compare":
        return compare_languages(
            payload["methodId"],
            payload["languages"],
            payload.get("inputs", {}),
            payload.get("timeoutSeconds", 8),
            payload.get("includeSource", False),
            payload.get("absoluteTolerance", 1e-10),
            payload.get("relativeTolerance", 1e-9),
        )
    raise ValueError(f"Unsupported job operation: {operation}")
