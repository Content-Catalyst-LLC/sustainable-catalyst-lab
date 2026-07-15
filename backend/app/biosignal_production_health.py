from __future__ import annotations

from pathlib import Path
from typing import Any

from .biomedical_engineering_biosignals import (
    VERSION as ENGINE_VERSION,
    catalog,
)

VERSION = "0.23.1"


def biosignal_production_health() -> dict[str, Any]:
    contract = catalog()
    method_count = len(contract.get("methods", []))
    benchmark_count = len(contract.get("benchmarks", []))
    category_count = len(contract.get("categories", []))
    ready = (
        contract.get("version") == ENGINE_VERSION
        and method_count == 48
        and benchmark_count == 48
        and category_count == 8
    )

    root = Path(__file__).resolve().parents[1]
    app = Path(__file__).resolve().parent

    return {
        "ok": ready,
        "status": "ready" if ready else "contract-incomplete",
        "release": VERSION,
        "engineRelease": ENGINE_VERSION,
        "methodCount": method_count,
        "benchmarkCount": benchmark_count,
        "categoryCount": category_count,
        "assets": {
            "contract": (
                root
                / "contracts"
                / "biomedical-engineering-biosignals-v0230.json"
            ).is_file(),
            "engine": (
                app
                / "biomedical_engineering_biosignals.py"
            ).is_file(),
            "engineRoutes": (
                app
                / "biomedical_engineering_biosignals_routes.py"
            ).is_file(),
            "productionHealth": (
                app
                / "biosignal_production_health.py"
            ).is_file(),
            "productionRoutes": (
                app
                / "biosignal_production_routes.py"
            ).is_file(),
        },
        "responsibleUse": {
            "clinicalUse": False,
            "diagnosticUse": False,
            "patientMonitoring": False,
        },
    }
