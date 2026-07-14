from __future__ import annotations

from pathlib import Path
from typing import Any

from .laboratory_data_instrumentation import VERSION as ENGINE_VERSION, catalog

VERSION = "0.25.1"


def instrumentation_production_health() -> dict[str, Any]:
    contract = catalog()
    counts = {
        "methodCount": len(contract.get("methods", [])),
        "benchmarkCount": len(contract.get("benchmarks", [])),
        "categoryCount": len(contract.get("categories", [])),
        "recordTypeCount": len(contract.get("recordTypes", [])),
        "connectionProfileCount": len(contract.get("connectionProfiles", [])),
        "qualityFlagCount": len(contract.get("qualityFlags", [])),
    }
    ready = (
        contract.get("version") == ENGINE_VERSION
        and counts["methodCount"] == 48
        and counts["benchmarkCount"] == 48
        and counts["categoryCount"] == 8
        and counts["recordTypeCount"] == 9
        and counts["connectionProfileCount"] == 8
        and counts["qualityFlagCount"] == 8
    )
    root = Path(__file__).resolve().parents[2]
    app = Path(__file__).resolve().parent

    return {
        "ok": ready,
        "status": "ready" if ready else "contract-incomplete",
        "release": VERSION,
        "engineRelease": ENGINE_VERSION,
        **counts,
        "assets": {
            "contract": (root / "contracts" / "laboratory-data-instrumentation-v0250.json").is_file(),
            "engine": (app / "laboratory_data_instrumentation.py").is_file(),
            "engineRoutes": (app / "laboratory_data_instrumentation_routes.py").is_file(),
            "productionHealth": (app / "instrumentation_production_health.py").is_file(),
            "productionRoutes": (app / "instrumentation_production_routes.py").is_file(),
        },
        "boundaries": {
            "automaticLocalDeviceAccess": False,
            "clinicalInstrumentation": False,
            "regulatedReleaseAuthority": False,
            "localFirstManualOperation": True,
        },
    }
