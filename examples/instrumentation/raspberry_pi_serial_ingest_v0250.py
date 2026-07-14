from __future__ import annotations

import json
import sys


def normalize_line(line: str) -> dict:
    record = json.loads(line)
    record.setdefault("qualityFlags", [])
    record.setdefault("instrumentId", "RPI-SERIAL-1")
    return record


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        print(json.dumps(normalize_line(line), sort_keys=True))
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
