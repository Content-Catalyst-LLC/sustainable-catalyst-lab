#!/usr/bin/env python3
"""Build the integrity-complete Lab v0.103.0 WordPress package.

This repair builder is intentionally manifest-driven.  Every file listed in
`wordpressCriticalFiles` is required, hash-verified, and included in the ZIP,
plus the canonical release manifest itself. Lab's repository root is the
WordPress plugin source tree; this prevents the v0.103.0 slim packaging defect
where contract/runtime files were omitted from the archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import zipfile

PLUGIN_DIR = pathlib.Path(".")
MANIFEST_REL = pathlib.Path("build/sc-lab-release-manifest.json")
ROOT_NAME = "sustainable-catalyst-lab"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(repo: pathlib.Path) -> dict:
    path = repo / PLUGIN_DIR / MANIFEST_REL
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("releaseVersion") != "0.103.0":
        raise SystemExit(f"ERROR: expected releaseVersion 0.103.0, got {data.get('releaseVersion')!r}")
    if "Energy Systems Intelligence v1.6.0" not in str(data.get("releaseLine", "")):
        raise SystemExit(f"ERROR: stale releaseLine: {data.get('releaseLine')!r}")
    critical = data.get("wordpressCriticalFiles")
    if not isinstance(critical, dict) or not critical:
        raise SystemExit("ERROR: wordpressCriticalFiles is empty or missing")
    return data


def verify_sources(repo: pathlib.Path, manifest: dict) -> list[pathlib.Path]:
    plugin = repo / PLUGIN_DIR
    critical = manifest["wordpressCriticalFiles"]
    files: list[pathlib.Path] = []
    errors: list[str] = []
    for rel, expected in sorted(critical.items()):
        path = plugin / rel
        if not path.is_file():
            errors.append(f"MISSING {rel}")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(f"HASH {rel}: expected {expected}, got {actual}")
            continue
        files.append(path)
    if errors:
        print("ERROR: source does not match the canonical v0.103.0 WordPress manifest:", file=sys.stderr)
        for e in errors[:50]:
            print(f"  {e}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... {len(errors)-50} more", file=sys.stderr)
        raise SystemExit(1)
    return files


def build(repo: pathlib.Path, output: pathlib.Path) -> None:
    manifest = load_manifest(repo)
    source_files = verify_sources(repo, manifest)
    manifest_path = repo / PLUGIN_DIR / MANIFEST_REL

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    # Canonical archive = release manifest + every integrity-critical WP file.
    members = [manifest_path] + source_files
    seen: set[str] = set()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in members:
            rel = path.relative_to(repo / PLUGIN_DIR).as_posix()
            arc = f"{ROOT_NAME}/{rel}"
            if arc in seen:
                continue
            seen.add(arc)
            z.write(path, arc)

    expected_count = len(manifest["wordpressCriticalFiles"]) + 1
    if len(seen) != expected_count:
        raise SystemExit(f"ERROR: archive member count {len(seen)} != expected {expected_count}")

    print(f"PASS: built {output}")
    print(f"PASS: packaged {len(manifest['wordpressCriticalFiles'])} manifest-critical WordPress files")
    print(f"PASS: archive members={len(seen)} (critical files + canonical manifest)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    build(pathlib.Path(args.repo).resolve(), pathlib.Path(args.output).resolve())


if __name__ == "__main__":
    main()
