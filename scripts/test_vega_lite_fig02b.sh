#!/usr/bin/env bash
# SC-FIG-02B Vega-Lite views and verified SVG export: Node, PHP (incl. modified vendor) and Chromium contracts.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> FIG-02B: grammar, scientific contract and dataset hash (Node)"
node tests/test-vega-lite-fig02b.js

echo "==> FIG-02B: WordPress loader (PHP)"
php -l includes/class-sc-lab-graph-studio-figure-bundle-renderer.php >/dev/null
php tests/test-vega-lite-fig02b.php
tampered="$(mktemp -d)"
trap 'rm -rf "$tampered"' EXIT
mkdir -p "$tampered/assets/lib"
cp -R assets/lib/plotly-3.3.1 assets/lib/vega-6.4.0 assets/lib/vega-lite-6.5.0 assets/lib/vega-interpreter-2.3.2 "$tampered/assets/lib/"
echo "/* modified */" >> "$tampered/assets/lib/vega-interpreter-2.3.2/vega-interpreter.classic.js"
FIG02B_TAMPERED_DIR="$tampered" php tests/test-vega-lite-fig02b.php

echo "==> FIG-02B: Chromium harness (eval blocked by CSP)"
chrome="${CHROME_BIN:-}"
for candidate in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome google-chrome-stable chromium chromium-browser; do
  [ -n "$chrome" ] && break
  if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then chrome="$candidate"; fi
done
if [ -z "$chrome" ]; then
  echo "SKIP - Chromium harness NOT_PERFORMED (no Chrome/Chromium; set CHROME_BIN)"
  exit 0
fi
"$chrome" --version
# A hard limit so a blocked page can never hang CI.
dom="$(perl -e 'alarm 120; exec @ARGV' "$chrome" --headless=new --disable-gpu --no-first-run --user-data-dir="$tampered/profile" \
  --allow-file-access-from-files --virtual-time-budget=30000 \
  --dump-dom "file://$PWD/tests/chromium-fig02b-vega-lite.html" 2>/dev/null || true)"
printf '%s' "$dom" | python3 -c 'import html,re,sys; s=sys.stdin.read(); m=re.search(r"<pre id=\"cert-log\">(.*?)</pre>", s, re.S); print(html.unescape(m.group(1)) if m else "no harness log")'
grep -q 'data-cert="pass"' <<<"$dom" || { echo "FAIL - FIG-02B Chromium harness"; exit 1; }
echo "PASS - SC-FIG-02B Vega-Lite and verified SVG Chromium harness"
