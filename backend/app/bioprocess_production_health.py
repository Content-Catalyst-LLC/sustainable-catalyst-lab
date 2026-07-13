from __future__ import annotations

from pathlib import Path
from typing import Any

from .biotechnology_bioprocess_engineering import (
    VERSION as ENGINE_VERSION,
    catalog,
)

VERSION = "0.22.1"


def production_health() -> dict[str, Any]:
    contract = catalog()
    method_count = len(contract.get("methods", []))
    benchmark_count = len(contract.get("benchmarks", []))
    category_count = len(contract.get("categories", []))
    ready = (
        method_count == 48
        and benchmark_count == 48
        and category_count == 8
    )

    root = Path(__file__).resolve().parents[2]

    return {
        "ok": ready,
        "status": "ready" if ready else "catalog-incomplete",
        "release": VERSION,
        "engineRelease": ENGINE_VERSION,
        "methodCount": method_count,
        "benchmarkCount": benchmark_count,
        "categoryCount": category_count,
        "assets": {
            "contract": (
                root
                / "contracts"
                / "biotechnology-bioprocess-methods-v0220.json"
            ).is_file(),
            "engine": (
                Path(__file__).resolve().parent
                / "biotechnology_bioprocess_engineering.py"
            ).is_file(),
            "routes": (
                Path(__file__).resolve().parent
                / "biotechnology_bioprocess_routes.py"
            ).is_file(),
        },
    }
