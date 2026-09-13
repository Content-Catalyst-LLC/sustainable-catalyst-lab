#!/usr/bin/env python3
"""Validate the repaired Lab v0.103.0 WordPress ZIP against its own manifest."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile

ROOT = "sustainable-catalyst-lab/"
MANIFEST = ROOT + "build/sc-lab-release-manifest.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_path")
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip_path) as z:
        bad = z.testzip()
        if bad:
            raise SystemExit(f"ERROR: corrupt ZIP member: {bad}")
        names = [n for n in z.namelist() if not n.endswith("/")]
        if not names or any(not n.startswith(ROOT) for n in names):
            raise SystemExit("ERROR: ZIP must contain one canonical sustainable-catalyst-lab/ root")
        manifest = json.loads(z.read(MANIFEST))
        if manifest.get("releaseVersion") != "0.103.0":
            raise SystemExit("ERROR: releaseVersion is not 0.103.0")
        if "Energy Systems Intelligence v1.6.0" not in str(manifest.get("releaseLine", "")):
            raise SystemExit("ERROR: stale Energy Systems release identity")
        critical = manifest.get("wordpressCriticalFiles") or {}
        missing = []
        mismatched = []
        for rel, expected in sorted(critical.items()):
            member = ROOT + rel
            if member not in z.namelist():
                missing.append(rel)
                continue
            actual = digest(z.read(member))
            if actual != expected:
                mismatched.append((rel, expected, actual))
        if missing or mismatched:
            if missing:
                print(f"ERROR: missing {len(missing)} manifest-critical files")
                for rel in missing[:30]: print(f"  MISSING {rel}")
            if mismatched:
                print(f"ERROR: {len(mismatched)} manifest hash mismatches")
                for rel, exp, act in mismatched[:30]: print(f"  HASH {rel}: {exp} != {act}")
            raise SystemExit(1)
        expected_count = len(critical) + 1
        if len(names) != expected_count:
            raise SystemExit(f"ERROR: file count {len(names)} != expected {expected_count}")
        print("PASS: ZIP integrity")
        print("PASS: canonical sustainable-catalyst-lab/ root")
        print(f"PASS: releaseVersion={manifest['releaseVersion']}")
        print(f"PASS: releaseLine={manifest['releaseLine']}")
        print(f"PASS: verifiedFileCount={len(critical)}")
        print(f"PASS: archiveFileCount={len(names)}")


if __name__ == "__main__":
    main()
