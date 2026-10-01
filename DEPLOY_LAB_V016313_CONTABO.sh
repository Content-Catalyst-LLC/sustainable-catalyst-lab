#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.163.1.3.zip}"
ROOT=/opt/sustainable-catalyst/lab; COMPOSE="$ROOT/compose.yml"; SERVICE=lab
STAMP="$(date +%Y%m%d-%H%M%S)"; BACKUP="/opt/sustainable-catalyst/lab.backup-v0.163.1.3-$STAMP"
[ -f "$ZIP" ] || { echo "ERROR: backend zip not found: $ZIP" >&2; exit 1; }
[ -d "$ROOT" ] || { echo "ERROR: Lab root missing: $ROOT" >&2; exit 1; }
cp -a "$ROOT" "$BACKUP"
rollback(){ echo 'ERROR: v0.163.1.3 deployment failed; restoring pre-deploy backend and compose configuration.' >&2; rsync -a --delete --exclude='data/' "$BACKUP/backend/" "$ROOT/backend/" || true; cp "$BACKUP/compose.yml" "$COMPOSE" || true; cd "$ROOT" && docker compose -f "$COMPOSE" build "$SERVICE" >/dev/null 2>&1 || true; cd "$ROOT" && docker compose -f "$COMPOSE" up -d "$SERVICE" >/dev/null 2>&1 || true; }
trap rollback ERR
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab-backend-v0.163.1.3/backend"
[ -d "$SRC" ] || { echo 'ERROR: packaged backend root missing' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
cd "$ROOT"; docker compose -f "$COMPOSE" build "$SERVICE"; docker compose -f "$COMPOSE" up -d "$SERVICE"
rm -f /tmp/sc-lab-v016313-health.json
for i in $(seq 1 90); do if curl -fsS http://127.0.0.1:8092/health >/tmp/sc-lab-v016313-health.json 2>/dev/null; then break; fi; sleep 2; done
[ -s /tmp/sc-lab-v016313-health.json ] || { echo 'ERROR: Lab backend health did not become available.' >&2; exit 1; }
python3 - <<'PY2'
import json
h=json.load(open('/tmp/sc-lab-v016313-health.json')); raw=json.dumps(h,separators=(',',':'))
assert '0.163.1.3' in raw, 'v0.163.1.3 repair marker absent'
assert 'frontDoorVisualPolishCompactLayout' in raw, 'v0.163.1.3 visual-polish health object absent'
assert 'frontDoorVisualizationSignalsRetentionRepair' in raw, 'v0.163.1.2 front-door retention health object absent'
assert 'unifiedWorkspaceShellLiveDomRepair' in raw, 'v0.163.1.1 page-length repair not retained'
assert 'institutionalGovernanceConfigStartupRepair' in raw, 'v0.163.0.1 startup repair not retained'
print('PASS - Compute Core health exposes v0.163.1.3 4D front-door visual polish and retained prior capabilities')
PY2
trap - ERR
echo 'NOTE - v0.163.1.3 changes 4D front-door visual presentation only; scientific backend semantics remain unchanged.'
echo 'PASS - Lab backend synchronized for v0.163.1.3'
echo "Backup: $BACKUP"
