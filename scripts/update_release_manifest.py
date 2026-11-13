#!/usr/bin/env python3
"""Refresh build/sc-lab-release-manifest.json for a WordPress plugin release.

    python3 scripts/update_release_manifest.py <release-version>

Hashes git-tracked files only (never untracked working-tree files), using the inclusion rule of
the v0.163.x PACKAGE scripts: the main plugin file plus assets/, includes/, templates/, contracts/
and build/ (minus the manifest itself). The Lab integrity runtime (v0.26.3.2) compares these hashes,
the plugin header and releaseVersion; any edit to a listed file without a refresh reports
"partial-or-mismatched" on the live site. backendCriticalFiles is left unchanged: the backend is
not shipped in the WordPress plugin.
"""
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "build/sc-lab-release-manifest.json"
MAIN = ROOT / "sustainable-catalyst-lab.php"
INCLUDE_ROOTS = ("assets/", "includes/", "templates/", "contracts/", "build/")


def main(release):
    manifest = json.loads(MANIFEST.read_text())
    feature = manifest["featureVersion"]
    if not re.fullmatch(re.escape(feature) + r"(\.\d+)?", release):
        sys.exit(f"FAIL - {release} is not on feature line {feature}")
    header = re.search(r"^[ \t*#@]*Version:\s*(\S+)", MAIN.read_text(), re.M).group(1)
    if header != release:
        sys.exit(f"FAIL - plugin header Version is {header}, expected {release}")

    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], check=True, capture_output=True).stdout.decode().split("\0")
    files = {}
    for rel in sorted(f for f in tracked if f):
        if rel == "build/sc-lab-release-manifest.json":
            continue
        if rel == "sustainable-catalyst-lab.php" or rel.startswith(INCLUDE_ROOTS):
            files[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

    manifest["releaseVersion"] = release
    manifest["wordpressCriticalFiles"] = files
    manifest["criticalFiles"] = {}
    manifest["buildFingerprint"] = hashlib.sha256("\n".join(f"{k}:{v}" for k, v in sorted(files.items())).encode()).hexdigest()
    manifest["generatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"releaseVersion": release, "featureVersion": feature, "wordpressCriticalFiles": len(files),
                      "buildFingerprint": manifest["buildFingerprint"]}))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
