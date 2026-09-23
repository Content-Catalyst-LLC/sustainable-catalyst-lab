#!/usr/bin/env python3
"""Build the slim Sustainable Catalyst Lab v0.95.0 WordPress runtime package.

This package contains only the WordPress runtime: plugin bootstrap, PHP includes,
templates, browser assets, governed contracts, static scientific data, and the
canonical release manifest. Repository tests, docs, SDKs, and Python backend
source are intentionally excluded; the backend is deployed separately.
"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT_NAME = "sustainable-catalyst-lab"
RUNTIME_TREES = ("assets", "includes", "templates", "contracts")


def eligible(rel: Path) -> bool:
    parts = set(rel.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return False
    if rel.suffix == ".pyc":
        return False
    # Preserve static assets/data; exclude only repository/runtime state paths.
    text = rel.as_posix()
    return not text.startswith("data/") and not text.startswith("backend/data/")


def collect_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for rel in ("sustainable-catalyst-lab.php", "LICENSE", "build/sc-lab-release-manifest.json"):
        p = root / rel
        if p.is_file():
            files.add(p)
    for tree in RUNTIME_TREES:
        base = root / tree
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and eligible(p.relative_to(root)):
                files.add(p)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = Path(args.output).resolve()
    files = collect_files(root)
    rels = {p.relative_to(root).as_posix() for p in files}
    required = {
        "sustainable-catalyst-lab.php",
        "build/sc-lab-release-manifest.json",
        "assets/data/elements.json",
        "assets/js/modules/carbon-mrv-registry-v0950.js",
        "assets/css/sc-lab-carbon-mrv-registry-v0950.css",
        "includes/class-sc-lab-carbon-mrv-registry-v0950.php",
        "contracts/carbon-mrv-method-v1200.schema.json",
        "contracts/carbon-mrv-readiness-v1200.schema.json",
        "contracts/carbon-mrv-registry-policy-v1200.json",
    }
    missing = sorted(required - rels)
    if missing:
        raise SystemExit("ERROR: required WordPress runtime files missing: " + ", ".join(missing))
    forbidden = [r for r in rels if r.startswith(("backend/", "tests/", "scripts/", "docs/", "sdk/", "examples/"))]
    if forbidden:
        raise SystemExit("ERROR: repository-only files leaked into WordPress runtime package")

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    total = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files:
            rel = p.relative_to(root).as_posix()
            total += p.stat().st_size
            zf.write(p, f"{ROOT_NAME}/{rel}")
    print(f"WORDPRESS_RUNTIME_FILE_COUNT={len(files)}")
    print(f"WORDPRESS_RUNTIME_UNCOMPRESSED_BYTES={total}")
    print(f"WORDPRESS_RUNTIME_ZIP_BYTES={out.stat().st_size}")
    print(f"WORDPRESS_RUNTIME_ZIP={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
