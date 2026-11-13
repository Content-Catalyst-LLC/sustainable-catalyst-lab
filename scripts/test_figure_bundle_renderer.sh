#!/usr/bin/env bash
# SC-FIG-01 generic sc.figure-bundle.v1 renderer: Node, PHP and (when Chrome is present) Chromium contracts.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Figure bundle renderer: package verification (Node)"
node tests/test-figure-bundle-renderer.js

echo "==> Figure bundle renderer: WordPress loader (PHP)"
php -l includes/class-sc-lab-graph-studio-figure-bundle-renderer.php >/dev/null
php tests/test-figure-bundle-renderer.php
tampered="$(mktemp -d)"
trap 'rm -rf "$tampered"' EXIT
mkdir -p "$tampered/assets/lib/plotly-3.3.1"
{ cat assets/lib/plotly-3.3.1/plotly.min.js; echo "/* modified */"; } > "$tampered/assets/lib/plotly-3.3.1/plotly.min.js"
FIG02A_TAMPERED_DIR="$tampered" php tests/test-figure-bundle-renderer.php

echo "==> Figure bundle renderer: Chromium harness"
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
dom="$("$chrome" --headless=new --disable-gpu --no-first-run --user-data-dir="$tampered/profile" \
  --allow-file-access-from-files --virtual-time-budget=20000 \
  --dump-dom "file://$PWD/tests/chromium-figure-bundle-renderer.html" 2>/dev/null)"
printf '%s' "$dom" | python3 -c 'import html,re,sys; s=sys.stdin.read(); m=re.search(r"<pre id=\"cert-log\">(.*?)</pre>", s, re.S); print(html.unescape(m.group(1)) if m else "no harness log")'
grep -q 'data-cert="pass"' <<<"$dom" || { echo "FAIL - Chromium harness"; exit 1; }
echo "PASS - SC-FIG-01 figure bundle renderer Chromium harness"
