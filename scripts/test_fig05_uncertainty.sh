#!/usr/bin/env bash
# SC-FIG-05.3 runtime uncertainty encodings: Node, earlier figure contracts and (when Chrome and the websockets
# package are present) Chromium at 1280 px and 390 px.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Runtime bands, quantile fans and map uncertainty layers (Node)"
node tests/test-uncertainty-fig05.js

echo "==> Earlier figure contracts still hold"
node tests/test-figure-bundle-renderer.js
node tests/test-fig02a-plotly-preview.js
node tests/test-vega-lite-fig02b.js
node tests/test-maplibre-fig03a.js
node tests/test-maplibre-fig04.js
node tests/test-maplibre-fig041.js

echo "==> Uncertainty Chromium harness (same-origin, SwiftShader WebGL)"
if ! python3 -c 'import websockets' 2>/dev/null; then
  echo "SKIP - Chromium harness NOT_PERFORMED (python websockets package missing)"; exit 0
fi
if [ -z "${CHROME_BIN:-}" ] && [ ! -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && ! command -v google-chrome >/dev/null 2>&1; then
  echo "SKIP - Chromium harness NOT_PERFORMED (no Chrome; set CHROME_BIN)"; exit 0
fi
out="$(mktemp -d)"
python3 scripts/run_chromium_fig05.py "$out"
# The FIG-04 page shares the legend and PNG receipt code the uncertainty layer extends.
python3 scripts/run_chromium_fig04.py "$out/fig04"
echo "PASS - SC-FIG-05.3 uncertainty Chromium harness ($out)"
