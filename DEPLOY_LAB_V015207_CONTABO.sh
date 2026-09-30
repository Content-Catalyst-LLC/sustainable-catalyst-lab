#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.152.0.7.zip}"
ROOT="/opt/sustainable-catalyst/lab"
COMPOSE="$ROOT/compose.yml"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$ROOT.backup-v0.152.0.7-$STAMP"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
cp -a "$ROOT" "$BACKUP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.152.0.7/backend"
[ -d "$SRC" ] || { echo 'ERROR: backend payload not found' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
cd "$ROOT"
docker compose -f "$COMPOSE" build lab
docker compose -f "$COMPOSE" up -d lab
for i in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8092/health >/tmp/sc-lab-v015207-health.json; then break; fi
  sleep 2
done
python3 -m json.tool /tmp/sc-lab-v015207-health.json >/dev/null
curl -fsS http://127.0.0.1:8092/v1/cross-workspace-research-dependency-graph/v01520/health | python3 -m json.tool >/dev/null
curl -fsS http://127.0.0.1:8092/v1/capabilities | python3 -m json.tool >/dev/null
echo "PASS - Lab backend synchronized for v0.152.0.7"
echo "Backup: $BACKUP"
