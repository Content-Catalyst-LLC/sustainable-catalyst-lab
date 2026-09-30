#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.152.0.5.zip}"
ROOT="${SC_LAB_ROOT:-/opt/sustainable-catalyst/lab}"
BACKUP="${ROOT}.backup-v0.152.0.5-$(date -u +%Y%m%dT%H%M%SZ)"
echo '=== LAB v0.152.0.5 BACKEND COMPATIBILITY DEPLOY ==='
echo 'Backend behavior is unchanged from v0.152.0; deployment is optional for this WordPress recovery.'
test -f "$ZIP"; test -f "$ROOT/compose.yml"
cp -a "$ROOT" "$BACKUP"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.152.0.5/backend"; test -d "$SRC"
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
cd "$ROOT"
docker compose -f compose.yml build lab
docker compose -f compose.yml up -d lab
for i in $(seq 1 30); do curl -fsS http://127.0.0.1:8092/health >/tmp/sc-lab-v015205-health.json && break; sleep 2; done
python3 -m json.tool /tmp/sc-lab-v015205-health.json >/dev/null
curl -fsS http://127.0.0.1:8092/v1/cross-workspace-research-dependency-graph/v01520/health | python3 -m json.tool
printf '%s\n' 'PASS - Lab backend remains compatible with v0.152.0.5 recovery release.'
