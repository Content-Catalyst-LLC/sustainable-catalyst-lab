#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.152.0.10.zip}"
ROOT="/opt/sustainable-catalyst/lab"
COMPOSE="$ROOT/compose.yml"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$ROOT.backup-v0.152.0.10-$STAMP"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
[ -d "$ROOT/backend" ] || { echo "ERROR: missing $ROOT/backend" >&2; exit 1; }
cp -a "$ROOT" "$BACKUP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.152.0.10/backend"
[ -d "$SRC" ] || { echo 'ERROR: backend payload not found' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
cd "$ROOT"
docker compose -f "$COMPOSE" build lab
docker compose -f "$COMPOSE" up -d lab
HEALTH=/tmp/sc-lab-v015210-health.json
rm -f "$HEALTH"
for i in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8092/health >"$HEALTH"; then break; fi
  sleep 2
done
[ -s "$HEALTH" ] || { echo 'ERROR: Lab backend health did not become ready' >&2; exit 1; }
python3 -m json.tool "$HEALTH"
python3 - "$HEALTH" <<'PY'
import json,sys
h=json.load(open(sys.argv[1]))
assert h.get('ok') is True, h
assert h.get('status') == 'ready', h
assert int(h.get('methodCount',0)) >= 23, h
assert int(h.get('benchmarkCount',0)) >= 14, h
print('PASS - Compute Core health')
PY
curl -fsS http://127.0.0.1:8092/v1/cross-workspace-research-dependency-graph/v01520/health \
  -o /tmp/sc-lab-v015210-dependency-health.json
python3 -m json.tool /tmp/sc-lab-v015210-dependency-health.json
python3 - /tmp/sc-lab-v015210-dependency-health.json <<'PY'
import json,sys
h=json.load(open(sys.argv[1]))
assert h.get('ok') is True, h
assert int(h.get('api_route_count',0)) == 120, h
print('PASS - v0.152 dependency graph health')
PY
echo 'NOTE - /v1/capabilities is HMAC-protected; verify capabilities through the WordPress compute proxy.'
echo 'PASS - Lab backend synchronized for v0.152.0.10'
echo "Backup: $BACKUP"
