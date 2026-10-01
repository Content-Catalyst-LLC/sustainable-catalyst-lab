#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.154.0.zip}"
ROOT="/opt/sustainable-catalyst/lab"; COMPOSE="$ROOT/compose.yml"; STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; BACKUP="$ROOT.backup-v0.154.0-$STAMP"; TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
[ -d "$ROOT/backend" ] || { echo "ERROR: missing $ROOT/backend" >&2; exit 1; }
cp -a "$ROOT" "$BACKUP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.154.0/backend"; [ -d "$SRC" ] || { echo 'ERROR: backend payload not found' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
if ! grep -q 'SC_LAB_PROTOCOL_NOTEBOOK_DB_PATH' "$COMPOSE"; then
  python3 - "$COMPOSE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text(); needle='      SC_LAB_4D_WORKSPACE_DB_PATH: "/app/data/sc-lab-4d-computational-workspaces.sqlite3"\n'
if needle not in s:
    needle='      SC_LAB_JOB_DB_PATH: "/app/data/sc-lab-compute-jobs.sqlite3"\n'
    if needle not in s: raise SystemExit('ERROR: could not locate Lab compose environment block')
addition='      SC_LAB_PROTOCOL_NOTEBOOK_DB_PATH: "/app/data/sc-lab-protocol-notebook-v01540.sqlite3"\n      SC_LAB_PROTOCOL_NOTEBOOK_PERSISTENT_DISK_MOUNTED: "1"\n'
s=s.replace(needle,needle+addition,1); p.write_text(s)
PY
fi
cd "$ROOT"; docker compose -f "$COMPOSE" build lab; docker compose -f "$COMPOSE" up -d lab
HEALTH=/tmp/sc-lab-v01540-health.json; rm -f "$HEALTH"
for i in $(seq 1 60); do if curl -fsS http://127.0.0.1:8092/health >"$HEALTH"; then break; fi; sleep 2; done
python3 - "$HEALTH" <<'PY'
import json,sys
h=json.load(open(sys.argv[1])); assert h.get('ok') is True; assert h.get('status')=='ready'; assert int(h.get('methodCount',0))>=23; assert int(h.get('benchmarkCount',0))>=14
r=h.get('reproducibleProtocolNotebookWorkspace') or {}; assert r.get('version')=='0.154.0'; assert r.get('serverBackedProtocols') is True; assert r.get('serverBackedNotebooks') is True; assert r.get('arbitraryCodeExecution') is False
w=h.get('fourDComputationalResearchWorkspace') or {}; assert w.get('version')=='0.153.0'; assert w.get('serverBackedProjectAssets') is True
print('PASS - Compute Core health with v0.154.0 protocol/notebook capability and v0.153.0 4D workspace retained')
PY
curl -fsS http://127.0.0.1:8092/v1/cross-workspace-research-dependency-graph/v01520/health -o /tmp/sc-lab-v01540-dependency-health.json
python3 - /tmp/sc-lab-v01540-dependency-health.json <<'PY'
import json,sys
h=json.load(open(sys.argv[1])); assert h.get('ok') is True; assert int(h.get('api_route_count',0))==120
print('PASS - v0.152 dependency graph health')
PY
echo 'NOTE - authenticated v0.154.0 protocol/notebook routes should be verified through the WordPress HMAC proxy.'
echo 'PASS - Lab backend synchronized for v0.154.0'
echo "Backup: $BACKUP"
