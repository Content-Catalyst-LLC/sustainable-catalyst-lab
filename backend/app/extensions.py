from __future__ import annotations

import importlib
import pkgutil
from typing import Any
from fastapi import FastAPI


def load_legacy_extensions(app: FastAPI) -> dict[str, Any]:
    loaded: list[str] = []
    failed: dict[str, str] = {}
    package = importlib.import_module("app")
    for module in pkgutil.iter_modules(package.__path__):
        name = module.name
        if not name.endswith("_routes") or name in {"extensions"}:
            continue
        try:
            imported = importlib.import_module(f"app.{name}")
            router = getattr(imported, "router", None)
            if router is not None:
                app.include_router(router)
                loaded.append(name)
        except Exception as exc:
            failed[name] = f"{type(exc).__name__}: {exc}"
    return {"loaded": sorted(loaded), "failed": failed}
