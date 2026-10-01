#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.158.0.zip}";ROOT="/opt/sustainable-catalyst/lab";COMPOSE="$ROOT/compose.yml";STAMP="$(date -u +%Y%m%dT%H%M%SZ)";BACKUP="$ROOT.backup-v0.158.0-$STAMP";TMP="$(mktemp -d)";trap 'rm -rf "$TMP"' EXIT;[ -f "$ZIP" ]||{ echo "ERROR: missing $ZIP" >&2;exit 1;};[ -d "$ROOT/backend" ]||{ echo "ERROR: missing $ROOT/backend" >&2;exit 1;};echo '=== LAB v0.158.0 BACKEND DEPLOY ===';cp -a "$ROOT" "$BACKUP";unzip -q "$ZIP" -d "$TMP";SRC="$TMP/sustainable-catalyst-lab-backend-v0.158.0/backend";[ -d "$SRC" ]||{ echo 'ERROR: backend payload not found' >&2;exit 1;};rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
if ! grep -q 'SC_LAB_REPLICATION_NETWORK_DB_PATH' "$COMPOSE";then python3 - "$COMPOSE" <<'PY2'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();needle='      SC_LAB_CROSS_STUDY_REPLICATION_DB_PATH: "/app/data/sc-lab-cross-study-replication-v01570.sqlite3"\n';
if needle not in s: raise SystemExit('ERROR: could not locate v0.157.0 cross-study compose environment anchor')
add='      SC_LAB_REPLICATION_NETWORK_DB_PATH: "/app/data/sc-lab-replication-network-v01580.sqlite3"\n      SC_LAB_REPLICATION_NETWORK_PERSISTENT_DISK_MOUNTED: "1"\n';p.write_text(s.replace(needle,needle+add,1))
PY2
fi
cd "$ROOT";docker compose -f "$COMPOSE" build lab;docker compose -f "$COMPOSE" up -d lab;HEALTH=/tmp/sc-lab-v01580-health.json;rm -f "$HEALTH";for i in $(seq 1 75);do if curl -fsS http://127.0.0.1:8092/health>"$HEALTH";then break;fi;sleep 2;done
python3 - "$HEALTH" <<'PY2'
import json,sys
h=json.load(open(sys.argv[1]));assert h.get('ok') is True;assert h.get('status')=='ready';n=h.get('scientificReproductionIndependentReplicationNetwork') or {};assert n.get('version')=='0.158.0';assert n.get('replicationNodeRegistry') is True;assert n.get('independenceInferred') is False;assert n.get('automaticExecution') is False;assert n.get('automaticReplicationJudgment') is False;assert n.get('credentialsStored') is False;c=h.get('crossStudyReplicationMetaExperiment') or {};assert c.get('version')=='0.157.0';d=h.get('distributedHpcAcceleratedCoordination') or {};assert d.get('version')=='0.156.0';b=h.get('batchExperimentSweepEnsemble') or {};assert b.get('version')=='0.155.0';r=h.get('reproducibleProtocolNotebookWorkspace') or {};assert r.get('version')=='0.154.0';w=h.get('fourDComputationalResearchWorkspace') or {};assert w.get('version')=='0.153.0';print('PASS - Compute Core health exposes v0.158.0 and retains v0.157.0/v0.156.0/v0.155.0/v0.154.0/v0.153.0 capabilities')
PY2
echo 'NOTE - authenticated v0.158.0 replication-network routes should be verified through the WordPress HMAC proxy.';echo 'PASS - Lab backend synchronized for v0.158.0';echo "Backup: $BACKUP"
