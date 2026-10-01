#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.163.1.1.zip}"
ROOT=/opt/sustainable-catalyst/lab
COMPOSE="$ROOT/compose.yml"
SERVICE=lab
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/opt/sustainable-catalyst/lab.backup-v0.163.1.1-$STAMP"
[ -f "$ZIP" ] || { echo "ERROR: backend zip not found: $ZIP" >&2; exit 1; }
[ -d "$ROOT" ] || { echo "ERROR: Lab root missing: $ROOT" >&2; exit 1; }
cp -a "$ROOT" "$BACKUP"
rollback(){
  echo 'ERROR: v0.163.1.1 deployment failed; restoring pre-deploy backend and compose configuration.' >&2
  rsync -a --delete --exclude='data/' "$BACKUP/backend/" "$ROOT/backend/" || true
  cp "$BACKUP/compose.yml" "$COMPOSE" || true
  cd "$ROOT" && docker compose -f "$COMPOSE" build "$SERVICE" >/dev/null 2>&1 || true
  cd "$ROOT" && docker compose -f "$COMPOSE" up -d "$SERVICE" >/dev/null 2>&1 || true
}
trap rollback ERR
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.163.1.1/backend"
[ -d "$SRC" ] || { echo 'ERROR: packaged backend root missing' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
cd "$ROOT"
docker compose -f "$COMPOSE" build "$SERVICE"
docker compose -f "$COMPOSE" up -d "$SERVICE"
for i in $(seq 1 90); do
  if curl -fsS http://127.0.0.1:8092/health >/tmp/sc-lab-v016311-health.json 2>/dev/null; then break; fi
  sleep 2
done
[ -s /tmp/sc-lab-v016311-health.json ] || { echo 'ERROR: Lab backend health did not become available.' >&2; exit 1; }
python3 - <<'PY2'
import json
p='/tmp/sc-lab-v016311-health.json'; h=json.load(open(p)); raw=json.dumps(h,separators=(',',':'))
assert '0.163.1.1' in raw, 'v0.163.1.1 repair marker absent from health'
assert 'unifiedWorkspaceShellLiveDomRepair' in raw, 'live DOM repair health object absent'
assert 'unifiedWorkspaceShell' in raw and '0.163.1' in raw, 'v0.163.1 feature marker not retained'
assert 'institutionalGovernanceConfigStartupRepair' in raw, 'v0.163.0.1 startup repair not retained'
print('PASS - Compute Core health exposes v0.163.1.1 page-length repair and retained prior capabilities')
PY2
trap - ERR
echo 'NOTE - v0.163.1.1 changes shell delivery and live DOM binding; scientific backend semantics remain unchanged.'
echo 'PASS - Lab backend synchronized for v0.163.1.1'
echo "Backup: $BACKUP"
