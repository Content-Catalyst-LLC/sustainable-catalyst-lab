#!/usr/bin/env python3
"""Normalize newline-delimited instrument JSON for v0.25.2 adapters."""

from __future__ import annotations

import json
import sys
import time
from typing import Any


def normalize(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": float(record.get("timestamp") or time.time()),
        "channel": str(record.get("channel") or "custom"),
        "value": float(record["value"]),
        "unit": str(record.get("unit") or ""),
        "qualityFlags": list(record.get("qualityFlags") or []),
        "instrumentId": record.get("instrumentId"),
        "sensorId": record.get("sensorId"),
        "sampleId": record.get("sampleId"),
    }


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue

        try:
            record = normalize(json.loads(line))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": str(error),
                    }
                ),
                file=sys.stderr,
            )
            continue

        print(json.dumps(record, separators=(",", ":")))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
