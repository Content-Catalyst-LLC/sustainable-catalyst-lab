#!/usr/bin/env bash
# SC-FIG-04 MapLibre geospatial views: Node, PHP and (when Chrome and the websockets package are present) Chromium.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> MapLibre view contract 1.0 and 1.1 (Node)"
node tests/test-maplibre-fig03a.js
node tests/test-maplibre-fig04.js

echo "==> Vendored MapLibre is the pinned npm release, unchanged"
python3 - <<'PY'
import hashlib, json, pathlib
d = pathlib.Path("assets/lib/maplibre-gl-5.24.0")
meta = json.loads((d / "SOURCE.json").read_text())
for name, f in meta["files"].items():
    b = (d / name).read_bytes()
    assert hashlib.sha256(b).hexdigest() == f["sha256"] and len(b) == f["bytes"], name
print("PASS - maplibre-gl 5.24.0 files match SOURCE.json")
PY

echo "==> MapLibre WordPress loader (PHP)"
php -l includes/class-sc-lab-graph-studio-figure-bundle-renderer.php >/dev/null
php tests/test-maplibre-fig04.php
tampered="$(mktemp -d)"
trap 'rm -rf "$tampered"' EXIT
cp -R assets includes "$tampered/"
echo "/* modified */" >> "$tampered/assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js"
FIG04_TAMPERED_DIR="$tampered" php tests/test-maplibre-fig04.php

echo "==> MapLibre Chromium harness (strict CSP, SwiftShader WebGL)"
if ! python3 -c 'import websockets' 2>/dev/null; then
  echo "SKIP - Chromium harness NOT_PERFORMED (python websockets package missing)"; exit 0
fi
if [ -z "${CHROME_BIN:-}" ] && [ ! -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && ! command -v google-chrome >/dev/null 2>&1; then
  echo "SKIP - Chromium harness NOT_PERFORMED (no Chrome; set CHROME_BIN)"; exit 0
fi
python3 scripts/run_chromium_fig04.py "$tampered/chromium"
echo "PASS - SC-FIG-04 MapLibre Chromium harness"
