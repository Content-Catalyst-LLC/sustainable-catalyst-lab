#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.157.0.1.zip}"
ROOT="/opt/sustainable-catalyst/lab"; COMPOSE="$ROOT/compose.yml"; STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; BACKUP="$ROOT.backup-v0.157.0.1-$STAMP"; TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
[ -d "$ROOT/backend" ] || { echo "ERROR: missing $ROOT/backend" >&2; exit 1; }
echo '=== LAB v0.157.0.1 BACKEND SYNCHRONIZATION DEPLOY ==='
echo 'Scientific backend behavior remains v0.157.0; this repair release keeps backend artifacts synchronized.'
cp -a "$ROOT" "$BACKUP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.157.0.1/backend"; [ -d "$SRC" ] || { echo 'ERROR: backend payload not found' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
if ! grep -q 'SC_LAB_CROSS_STUDY_REPLICATION_DB_PATH' "$COMPOSE"; then
python3 - "$COMPOSE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();needle='      SC_LAB_DISTRIBUTED_COORDINATION_DB_PATH: "/app/data/sc-lab-distributed-coordination-v01560.sqlite3"\n'
if needle not in s: raise SystemExit('ERROR: could not locate v0.156.0 distributed coordination compose environment anchor')
addition='      SC_LAB_CROSS_STUDY_REPLICATION_DB_PATH: "/app/data/sc-lab-cross-study-replication-v01570.sqlite3"\n      SC_LAB_CROSS_STUDY_REPLICATION_PERSISTENT_DISK_MOUNTED: "1"\n'
s=s.replace(needle,needle+addition,1);p.write_text(s)
PY
fi
cd "$ROOT"; docker compose -f "$COMPOSE" build lab; docker compose -f "$COMPOSE" up -d lab
HEALTH=/tmp/sc-lab-v015701-health.json; rm -f "$HEALTH"
for i in $(seq 1 75); do if curl -fsS http://127.0.0.1:8092/health >"$HEALTH"; then break; fi; sleep 2; done
python3 - "$HEALTH" <<'PY'
import json,sys
h=json.load(open(sys.argv[1])); assert h.get('ok') is True; assert h.get('status')=='ready'
c=h.get('crossStudyReplicationMetaExperiment') or {}; assert c.get('version')=='0.157.0'; assert c.get('immutableStudyRevisions') is True; assert c.get('automaticReplicationJudgment') is False; assert c.get('humanScientificReviewRequired') is True
d=h.get('distributedHpcAcceleratedCoordination') or {}; assert d.get('version')=='0.156.0'; assert d.get('automaticDispatch') is False
b=h.get('batchExperimentSweepEnsemble') or {}; assert b.get('version')=='0.155.0'; assert b.get('automaticDispatch') is False
r=h.get('reproducibleProtocolNotebookWorkspace') or {}; assert r.get('version')=='0.154.0'
w=h.get('fourDComputationalResearchWorkspace') or {}; assert w.get('version')=='0.153.0'
print('PASS - Compute Core retains v0.157.0 scientific capability under v0.157.0.1 repair release')
PY
echo 'NOTE - v0.157.0.1 authorization presentation repair is implemented in WordPress; backend HMAC protections remain unchanged.'
echo 'PASS - Lab backend synchronized for v0.157.0.1'
echo "Backup: $BACKUP"
