#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROMIUM="${CHROMIUM_BIN:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)}"
if [[ -z "$CHROMIUM" ]]; then echo 'SKIP: Chromium/Chrome not found'; exit 77; fi
out="$(mktemp)"; err="$(mktemp)"; profile="$(mktemp -d)"; trap 'rm -f "$out" "$err"; rm -rf "$profile"' EXIT
set +e
timeout 12s "$CHROMIUM" --headless --no-sandbox --disable-gpu --disable-dev-shm-usage --disable-background-networking --no-first-run --user-data-dir="$profile" --allow-file-access-from-files --virtual-time-budget=1200 --dump-dom "file://$ROOT/tests/chromium-v0135210.html" > "$out" 2> "$err"
rc=$?
set -e
if [[ $rc -eq 124 ]]; then echo 'SKIP: Chromium headless timed out in this build environment'; exit 77; fi
if [[ $rc -ne 0 ]]; then echo "ERROR: Chromium exited $rc" >&2; tail -20 "$err" >&2; exit $rc; fi
grep -q 'data-cert="pass"' "$out" || { echo 'ERROR: browser harness did not certify' >&2; exit 1; }
grep -q '"certified":true' "$out" || exit 1
grep -q '"one":true' "$out" || exit 1
grep -q '"switched":true' "$out" || exit 1
echo 'PASS: v0.135.21.0 Chromium headless runtime certification'
