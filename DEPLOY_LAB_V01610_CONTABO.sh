#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.161.0.zip}"
ROOT="/opt/sustainable-catalyst/lab";COMPOSE="$ROOT/compose.yml";STAMP="$(date -u +%Y%m%dT%H%M%SZ)";BACKUP="$ROOT.backup-v0.161.0-$STAMP";TMP="$(mktemp -d)";trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ]||{ echo "ERROR: missing $ZIP" >&2;exit 1;};[ -d "$ROOT/backend" ]||{ echo "ERROR: missing $ROOT/backend" >&2;exit 1;};[ -f "$COMPOSE" ]||{ echo "ERROR: missing $COMPOSE" >&2;exit 1;}
echo '=== LAB v0.161.0 BACKEND DEPLOY ==='
cp -a "$ROOT" "$BACKUP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-backend-v0.161.0/backend";[ -d "$SRC" ]||{ echo 'ERROR: backend payload not found' >&2;exit 1;}
rsync -a --delete --exclude='data/' "$SRC/" "$ROOT/backend/"
if ! grep -q 'SC_LAB_PROGRAM_PORTFOLIO_DB_PATH' "$COMPOSE";then python3 - "$COMPOSE" <<'PY2'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();needle='      SC_LAB_RESEARCH_OS_DB_PATH: "/app/data/sc-lab-research-os-v01600.sqlite3"\n'
if needle not in s: raise SystemExit('ERROR: could not locate v0.160.0 Research OS compose environment anchor')
add='      SC_LAB_PROGRAM_PORTFOLIO_DB_PATH: "/app/data/sc-lab-program-portfolio-v01610.sqlite3"\n      SC_LAB_PROGRAM_PORTFOLIO_PERSISTENT_DISK_MOUNTED: "1"\n'
p.write_text(s.replace(needle,needle+add,1))
PY2
fi
cd "$ROOT";docker compose -f "$COMPOSE" build lab;docker compose -f "$COMPOSE" up -d lab
HEALTH=/tmp/sc-lab-v01610-health.json;rm -f "$HEALTH"
for i in $(seq 1 90);do if curl -fsS http://127.0.0.1:8092/health>"$HEALTH";then break;fi;sleep 2;done
[ -s "$HEALTH" ]||{ echo 'ERROR: Lab backend health did not become available.' >&2;exit 1;}
python3 - "$HEALTH" <<'PY2'
import json,sys
h=json.load(open(sys.argv[1]));assert h.get('ok') is True;assert h.get('status')=='ready'
p=h.get('researchProgramPortfolioOrchestration') or {};assert p.get('version')=='0.161.0';assert p.get('programRegistry') is True;assert p.get('portfolioRegistry') is True;assert p.get('researchOSProjectMembership') is True;assert p.get('programCommandCenter') is True;assert p.get('portfolioCommandCenter') is True;assert p.get('descriptiveAggregationOnly') is True;assert p.get('automaticProjectRanking') is False;assert p.get('automaticFundingAllocation') is False;assert p.get('automaticResourceAllocation') is False;assert p.get('automaticScientificValidity') is False;assert p.get('automaticPublication') is False
os=h.get('computationalResearchOperatingSystemII') or {};assert os.get('version')=='0.160.0'
g=h.get('integratedScientificReviewValidationPublicationGate') or {};assert g.get('version')=='0.159.0'
n=h.get('scientificReproductionIndependentReplicationNetwork') or {};assert n.get('version')=='0.158.0'
c=h.get('crossStudyReplicationMetaExperiment') or {};assert c.get('version')=='0.157.0'
d=h.get('distributedHpcAcceleratedCoordination') or {};assert d.get('version')=='0.156.0'
b=h.get('batchExperimentSweepEnsemble') or {};assert b.get('version')=='0.155.0'
r=h.get('reproducibleProtocolNotebookWorkspace') or {};assert r.get('version')=='0.154.0'
w=h.get('fourDComputationalResearchWorkspace') or {};assert w.get('version')=='0.153.0'
print('PASS - Compute Core health exposes v0.161.0 and retains v0.160.0/v0.159.0/v0.158.0/v0.157.0/v0.156.0/v0.155.0/v0.154.0/v0.153.0 capabilities')
PY2
echo 'NOTE - authenticated v0.161.0 program/portfolio routes should be verified through the WordPress HMAC proxy.'
echo 'PASS - Lab backend synchronized for v0.161.0'
echo "Backup: $BACKUP"
