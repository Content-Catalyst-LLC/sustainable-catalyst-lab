#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.152.0.1.zip}"
BASE="${SC_LAB_BASE:-/opt/sustainable-catalyst/lab}"
echo '=== LAB v0.152.0.1 BACKEND COMPATIBILITY DEPLOY ==='
echo 'Backend code is unchanged from v0.152.0; this script safely refreshes the identical backend package if desired.'
[ -f "$ZIP" ] || { echo "STOP: missing $ZIP"; exit 2; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.152.0.1/backend"
[ -d "$SRC" ] || { echo 'STOP: backend payload not found'; exit 3; }
if [ -d "$BASE/backend" ]; then
  cp -a "$BASE/backend" "$BASE/backend.backup-v0.152.0.1-$(date +%Y%m%d%H%M%S)"
fi
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$SRC/" "$BASE/backend/"
cd "$BASE"
docker compose build sc-lab
docker compose up -d sc-lab
for i in $(seq 1 45); do
  if curl -fsS http://127.0.0.1:8092/health >/tmp/sc-lab-health.json 2>/dev/null; then cat /tmp/sc-lab-health.json; echo; break; fi
  sleep 2
done
curl -fsS http://127.0.0.1:8092/v1/cross-workspace-research-dependency-graph/v01520/health | python3 -m json.tool
echo 'PASS - Lab backend remains compatible with v0.152.0.1 UI hotfix.'
