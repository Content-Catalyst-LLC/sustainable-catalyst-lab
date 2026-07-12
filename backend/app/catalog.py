from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[1] / "catalog" / "methods.json"


class CatalogError(ValueError):
    """Raised when a method contract cannot be resolved."""


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    methods = catalog.get("methods")
    if not isinstance(methods, list):
        raise RuntimeError("The execution catalog does not contain a methods list.")
    catalog["by_id"] = {method["id"]: method for method in methods}
    return catalog


def get_method(method_id: str) -> dict[str, Any]:
    method = load_catalog()["by_id"].get(method_id)
    if method is None:
        raise CatalogError(f"Unknown curated method: {method_id}")
    return method


def public_catalog() -> dict[str, Any]:
    catalog = load_catalog()
    return {
        "schema": catalog.get("schema"),
        "version": catalog.get("version"),
        "languages": catalog.get("languages", {}),
        "methods": [
            {
                "id": method["id"],
                "name": method.get("name"),
                "domain": method.get("domain"),
                "version": method.get("version"),
                "equation": method.get("equation"),
                "inputs": method.get("inputs", []),
                "outputs": [
                    {key: value for key, value in output.items() if key != "expression"}
                    for output in method.get("outputs", [])
                ],
                "languages": method.get("languages", []),
                "assumptions": method.get("assumptions", []),
            }
            for method in catalog["methods"]
        ],
    }
