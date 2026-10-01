#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.163.0.1.zip}"; ROOT="/opt/sustainable-catalyst/lab"; COMPOSE="$ROOT/compose.yml"; STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; BACKUP="$ROOT.backup-v0.163.0.1-$STAMP"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }; [ -d "$ROOT/backend" ] || { echo "ERROR: missing $ROOT/backend" >&2; exit 1; }; [ -f "$COMPOSE" ] || { echo "ERROR: missing $COMPOSE" >&2; exit 1; }
echo '=== LAB v0.163.0.1 BACKEND STARTUP REPAIR DEPLOY ==='; cp -a "$ROOT" "$BACKUP"; unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab-backend-v0.163.0.1/backend"; [ -d "$SRC" ] || { echo 'ERROR: backend payload not found' >&2; exit 1; }
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
python3 - "$ROOT/backend/app/config.py" "$ROOT/backend/app/main.py" <<'PY2'
from pathlib import Path
import sys,re
c=Path(sys.argv[1]).read_text(); m=Path(sys.argv[2]).read_text()
assert 'SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_DB_PATH' in c
assert 'institutional_review_federation_max_bodies' in c
start=m.index('institutional_governance_v01630 = InstitutionalResearchGovernanceReviewFederationManager('); line=m[start:m.index('\n',start)]
assert 'settings.institutional_review_federation_db_path' in line
assert 'settings.institutional_governance_max_bodies' not in line
print('PASS - v0.163.0.1 backend startup binding preflight')
PY2
if ! grep -q 'SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_DB_PATH' "$COMPOSE"; then python3 - "$COMPOSE" <<'PY2'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text(); needle='      SC_LAB_CROSS_PROJECT_RESOURCE_DB_PATH: "/app/data/sc-lab-cross-project-resource-v01620.sqlite3"\n'
if needle not in s: raise SystemExit('ERROR: could not locate v0.162.0 compose environment anchor')
add='      SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_DB_PATH: "/app/data/sc-lab-institutional-review-federation-v01630.sqlite3"\n      SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_PERSISTENT_DISK_MOUNTED: "1"\n'
p.write_text(s.replace(needle,needle+add,1))
PY2
fi
rollback(){
  echo 'ERROR: v0.163.0.1 health failed; restoring pre-deploy backend and compose.' >&2
  rsync -a --delete --exclude='data/' "$BACKUP/backend/" "$ROOT/backend/"
  cp "$BACKUP/compose.yml" "$COMPOSE"
  cd "$ROOT"; docker compose -f "$COMPOSE" build lab >/dev/null; docker compose -f "$COMPOSE" up -d lab >/dev/null
  for i in $(seq 1 60); do if curl -fsS http://127.0.0.1:8092/health >/tmp/sc-lab-v016301-rollback-health.json 2>/dev/null; then echo 'PASS - previous Lab backend restored after failed v0.163.0.1 deployment.' >&2; return 0; fi; sleep 2; done
  echo 'ERROR: automatic rollback also failed health verification; inspect docker logs.' >&2
  return 1
}
cd "$ROOT"; docker compose -f "$COMPOSE" build lab; docker compose -f "$COMPOSE" up -d lab
HEALTH=/tmp/sc-lab-v016301-health.json; rm -f "$HEALTH"
for i in $(seq 1 90); do if curl -fsS http://127.0.0.1:8092/health >"$HEALTH" 2>/dev/null; then break; fi; sleep 2; done
if [ ! -s "$HEALTH" ]; then docker logs --tail 120 sc-lab >&2 || true; rollback || true; exit 1; fi
if ! python3 - "$HEALTH" <<'PY2'
import json,sys
h=json.load(open(sys.argv[1])); assert h.get('ok') is True; assert h.get('status')=='ready'
x=h.get('institutionalResearchGovernanceReviewFederation') or {}; assert x.get('version')=='0.163.0'; assert x.get('institutionRegistry') is True; assert x.get('governanceBodyRegistry') is True; assert x.get('federatedReviewRelationships') is True; assert x.get('automaticReviewerSelection') is False; assert x.get('automaticEthicsApproval') is False; assert x.get('automaticScientificValidity') is False; assert x.get('automaticPublication') is False
r=h.get('institutionalGovernanceConfigStartupRepair') or {}; assert r.get('version')=='0.163.0.1'; assert r.get('legacyInstitutionalGovernanceNamespacePreserved') is True; assert r.get('backendStartupBindingValidated') is True
for key,ver in [('crossProjectDependencyResearchResourcePlanning','0.162.0'),('researchProgramPortfolioOrchestration','0.161.0'),('computationalResearchOperatingSystemII','0.160.0'),('integratedScientificReviewValidationPublicationGate','0.159.0'),('scientificReproductionIndependentReplicationNetwork','0.158.0'),('crossStudyReplicationMetaExperiment','0.157.0'),('distributedHpcAcceleratedCoordination','0.156.0'),('batchExperimentSweepEnsemble','0.155.0'),('reproducibleProtocolNotebookWorkspace','0.154.0'),('fourDComputationalResearchWorkspace','0.153.0')]: assert (h.get(key) or {}).get('version')==ver,(key,h.get(key))
print('PASS - Compute Core health exposes v0.163.0.1 startup repair, v0.163.0 federation, and retained prior capabilities')
PY2
then docker logs --tail 120 sc-lab >&2 || true; rollback || true; exit 1; fi
echo 'NOTE - authenticated v0.163.0 governance routes should be verified through the WordPress HMAC proxy.'; echo 'PASS - Lab backend synchronized for v0.163.0.1'; echo "Backup: $BACKUP"
