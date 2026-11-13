#!/usr/bin/env bash
# SC-FIG-01 / FIG-02A Graph Studio Plotly preview: Node, PHP and (when Chrome is present) Chromium contracts.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> FIG-02A preview: hashing and content policy (Node)"
node tests/test-fig02a-plotly-preview.js

echo "==> FIG-02A preview: WordPress loader (PHP)"
php -l includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php >/dev/null
php tests/test-fig02a-plotly-preview.php
tampered="$(mktemp -d)"
trap 'rm -rf "$tampered"' EXIT
mkdir -p "$tampered/assets/lib/plotly-3.3.1"
{ cat assets/lib/plotly-3.3.1/plotly.min.js; echo "/* modified */"; } > "$tampered/assets/lib/plotly-3.3.1/plotly.min.js"
FIG02A_TAMPERED_DIR="$tampered" php tests/test-fig02a-plotly-preview.php

echo "==> FIG-02A preview: Chromium harness"
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
  --dump-dom "file://$PWD/tests/chromium-fig02a-plotly-preview.html" 2>/dev/null)"
printf '%s' "$dom" | python3 -c 'import html,re,sys; s=sys.stdin.read(); m=re.search(r"<pre id=\"cert-log\">(.*?)</pre>", s, re.S); print(html.unescape(m.group(1)) if m else "no harness log")'
# Here-string, not a pipe: grep -q exits early and SIGPIPE would fail the pipeline under pipefail.
grep -q 'data-cert="pass"' <<<"$dom" || { echo "FAIL - Chromium harness"; exit 1; }
echo "PASS - FIG-02A Graph Studio Plotly preview Chromium harness"
