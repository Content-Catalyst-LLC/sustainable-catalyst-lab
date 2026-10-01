#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.156.0.zip}"
ROOT="/opt/sustainable-catalyst/lab"; COMPOSE="$ROOT/compose.yml"; STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; BACKUP="$ROOT.backup-v0.156.0-$STAMP"; TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
[ -d "$ROOT/backend" ] || { echo "ERROR: missing $ROOT/backend" >&2; exit 1; }
cp -a "$ROOT" "$BACKUP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.156.0/backend"; [ -d "$SRC" ] || { echo 'ERROR: backend payload not found' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
if ! grep -q 'SC_LAB_DISTRIBUTED_COORDINATION_DB_PATH' "$COMPOSE"; then
python3 - "$COMPOSE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text(); needle='      SC_LAB_BATCH_EXPERIMENT_CAMPAIGN_DB_PATH: "/app/data/sc-lab-batch-experiment-campaign-v01550.sqlite3"\n'
if needle not in s: raise SystemExit('ERROR: could not locate v0.155.0 batch campaign compose environment anchor')
addition='      SC_LAB_DISTRIBUTED_COORDINATION_DB_PATH: "/app/data/sc-lab-distributed-coordination-v01560.sqlite3"\n      SC_LAB_DISTRIBUTED_COORDINATION_PERSISTENT_DISK_MOUNTED: "1"\n'
s=s.replace(needle,needle+addition,1); p.write_text(s)
PY
fi
cd "$ROOT"; docker compose -f "$COMPOSE" build lab; docker compose -f "$COMPOSE" up -d lab
HEALTH=/tmp/sc-lab-v01560-health.json; rm -f "$HEALTH"
for i in $(seq 1 60); do if curl -fsS http://127.0.0.1:8092/health >"$HEALTH"; then break; fi; sleep 2; done
python3 - "$HEALTH" <<'PY'
import json,sys
h=json.load(open(sys.argv[1])); assert h.get('ok') is True; assert h.get('status')=='ready'
d=h.get('distributedHpcAcceleratedCoordination') or {}; assert d.get('version')=='0.156.0'; assert d.get('computeTargetRegistry') is True; assert d.get('acceleratorAwarePlacement') is True; assert d.get('hpcJobArrayPlanning') is True; assert d.get('automaticDispatch') is False; assert d.get('automaticFailover') is False; assert d.get('credentialsStored') is False; assert d.get('arbitraryCodeExecution') is False
b=h.get('batchExperimentSweepEnsemble') or {}; assert b.get('version')=='0.155.0'; assert b.get('automaticDispatch') is False
r=h.get('reproducibleProtocolNotebookWorkspace') or {}; assert r.get('version')=='0.154.0'
w=h.get('fourDComputationalResearchWorkspace') or {}; assert w.get('version')=='0.153.0'
print('PASS - Compute Core health exposes v0.156.0 and retains v0.155.0/v0.154.0/v0.153.0 capabilities')
PY
echo 'NOTE - authenticated v0.156.0 coordination routes should be verified through the WordPress HMAC proxy.'
echo 'PASS - Lab backend synchronized for v0.156.0'
echo "Backup: $BACKUP"
