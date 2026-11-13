#!/usr/bin/env python3
"""SC-FIG-04: package the pinned MapLibre GL JS CSP build into assets/lib (reproducible).

    python3 scripts/package_maplibre_vendor.py <dir with maplibre-gl-5.24.0.tgz>

Fetch the tarball with `npm pack maplibre-gl@5.24.0`; it must match the registry integrity pinned below.
The CSP build is used because it never creates a worker from a blob of its own code: the worker is a separate
file, which Lab fetches, verifies against its pinned hash and only then starts. The three files are copied
unchanged. Re-running produces byte-identical output.
"""
import base64
import hashlib
import io
import json
import pathlib
import sys
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME, VERSION = "maplibre-gl", "5.24.0"
INTEGRITY = "sha512-ALyFxgtd5R+65UqZ/++lOqwWcC0SNho9c27fYSyLmG7AfnAul2o46F05aDJGPbFU57wos9dgcIySHs0Xe6ia3A=="
FILES = ("dist/maplibre-gl-csp.js", "dist/maplibre-gl-csp-worker.js", "dist/maplibre-gl.css")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    tgz = (pathlib.Path(sys.argv[1]) / f"{NAME}-{VERSION}.tgz").read_bytes()
    if "sha512-" + base64.b64encode(hashlib.sha512(tgz).digest()).decode() != INTEGRITY:
        raise SystemExit("tarball does not match the registry integrity")
    out = ROOT / "assets" / "lib" / f"{NAME}-{VERSION}"
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(tgz)) as tar:
        pkg = json.loads(tar.extractfile("package/package.json").read())
        if pkg["version"] != VERSION or pkg["license"] != "BSD-3-Clause":
            raise SystemExit("unexpected version or licence")
        for name in FILES:
            data = tar.extractfile("package/" + name).read()
            (out / pathlib.Path(name).name).write_bytes(data)
            files[pathlib.Path(name).name] = {"sha256": sha256(data), "bytes": len(data)}
        (out / "LICENSE.txt").write_bytes(tar.extractfile("package/LICENSE.txt").read())
    (out / "SOURCE.json").write_text(json.dumps({
        "library": NAME, "version": VERSION, "files": files, "origin": f"npm {NAME}@{VERSION} dist/ (unchanged)",
        "npmTarballIntegrity": INTEGRITY, "licence": "BSD-3-Clause (see LICENSE.txt)",
        "network": "Served from the plugin directory only; no CDN. The worker is started only after its bytes match the pinned hash.",
        "reason": "SC-FIG-04 geospatial figures in Graph Studio (inline GeoJSON only; no basemap, tiles, glyphs or sprites).",
    }, indent=2) + "\n")
    for k, v in files.items():
        print(k, v["sha256"], v["bytes"])


if __name__ == "__main__":
    main()
