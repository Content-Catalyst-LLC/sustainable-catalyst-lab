#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.163.0.zip}";ROOT="/opt/sustainable-catalyst/lab";COMPOSE="$ROOT/compose.yml";STAMP="$(date -u +%Y%m%dT%H%M%SZ)";BACKUP="$ROOT.backup-v0.163.0-$STAMP";TMP="$(mktemp -d)";trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ]||{ echo "ERROR: missing $ZIP" >&2;exit 1;};[ -d "$ROOT/backend" ]||{ echo "ERROR: missing $ROOT/backend" >&2;exit 1;};[ -f "$COMPOSE" ]||{ echo "ERROR: missing $COMPOSE" >&2;exit 1;};echo '=== LAB v0.163.0 BACKEND DEPLOY ===';cp -a "$ROOT" "$BACKUP";unzip -q "$ZIP" -d "$TMP";SRC="$TMP/sustainable-catalyst-lab-backend-v0.163.0/backend";[ -d "$SRC" ]||{ echo 'ERROR: backend payload not found' >&2;exit 1;};rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
if ! grep -q 'SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH' "$COMPOSE";then python3 - "$COMPOSE" <<'PY2'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();needle='      SC_LAB_CROSS_PROJECT_RESOURCE_DB_PATH: "/app/data/sc-lab-cross-project-resource-v01620.sqlite3"\n'
if needle not in s: raise SystemExit('ERROR: could not locate v0.162.0 compose environment anchor')
add='      SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH: "/app/data/sc-lab-institutional-governance-v01630.sqlite3"\n      SC_LAB_INSTITUTIONAL_GOVERNANCE_PERSISTENT_DISK_MOUNTED: "1"\n';p.write_text(s.replace(needle,needle+add,1))
PY2
fi
cd "$ROOT";docker compose -f "$COMPOSE" build lab;docker compose -f "$COMPOSE" up -d lab;HEALTH=/tmp/sc-lab-v01630-health.json;rm -f "$HEALTH";for i in $(seq 1 90);do if curl -fsS http://127.0.0.1:8092/health>"$HEALTH";then break;fi;sleep 2;done;[ -s "$HEALTH" ]||{ echo 'ERROR: Lab backend health did not become available.' >&2;exit 1;}
python3 - "$HEALTH" <<'PY2'
import json,sys
h=json.load(open(sys.argv[1]));assert h.get('ok') is True;assert h.get('status')=='ready';x=h.get('institutionalResearchGovernanceReviewFederation') or {};assert x.get('version')=='0.163.0';assert x.get('institutionRegistry') is True;assert x.get('governanceBodyRegistry') is True;assert x.get('federatedReviewRelationships') is True;assert x.get('externalReviewerAssignments') is True;assert x.get('explicitIndependenceDeclarations') is True;assert x.get('humanRecordedDecisions') is True;assert x.get('dissentPreservation') is True;assert x.get('automaticReviewerSelection') is False;assert x.get('automaticEthicsApproval') is False;assert x.get('automaticScientificValidity') is False;assert x.get('automaticCaseApproval') is False;assert x.get('automaticPublication') is False
for key,ver in [('crossProjectDependencyResearchResourcePlanning','0.162.0'),('researchProgramPortfolioOrchestration','0.161.0'),('computationalResearchOperatingSystemII','0.160.0'),('integratedScientificReviewValidationPublicationGate','0.159.0'),('scientificReproductionIndependentReplicationNetwork','0.158.0'),('crossStudyReplicationMetaExperiment','0.157.0'),('distributedHpcAcceleratedCoordination','0.156.0'),('batchExperimentSweepEnsemble','0.155.0'),('reproducibleProtocolNotebookWorkspace','0.154.0'),('fourDComputationalResearchWorkspace','0.153.0')]: assert (h.get(key) or {}).get('version')==ver,(key,h.get(key))
print('PASS - Compute Core health exposes v0.163.0 and retains v0.162.0/v0.161.0/v0.160.0/v0.159.0/v0.158.0/v0.157.0/v0.156.0/v0.155.0/v0.154.0/v0.153.0 capabilities')
PY2
echo 'NOTE - authenticated v0.163.0 governance routes should be verified through the WordPress HMAC proxy.';echo 'PASS - Lab backend synchronized for v0.163.0';echo "Backup: $BACKUP"
