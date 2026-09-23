#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.134.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.134.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.134.0 — EVIDENCE SYNTHESIS INTELLIGENCE II ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01340.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.134.0-$ts"; env_backup="/tmp/sc-lab-v0.134.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/evidence_synthesis_intelligence_ii_v01340.py" ]] || { echo "ERROR: v0.134 evidence-synthesis-intelligence module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/statistical-assumption-diagnostic-intelligence/health")"; current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/evidence-synthesis-intelligence-ii/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$current" "$core" <<'PYDEPLOY'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert p.get('ok') is True and p.get('version')=='0.133.0'; assert r.get('ok') is True and r.get('version')=='0.134.0'; assert r.get('synthesis_family_count')==20 and r.get('automatic_study_quality_scoring') is False and r.get('automatic_consensus_certification') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.133 Statistical Assumption & Diagnostic Intelligence healthy'); print('PASS: Lab v0.134.0 Evidence Synthesis Intelligence II health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYDEPLOY
docker exec -i "$CONTAINER" python - <<'PYDEPLOY'
from app.main import app
from app.evidence_synthesis_intelligence_ii_v01340 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/evidence-synthesis-intelligence-ii'; required={x for x in paths if x.startswith(base)}; assert len(required)>=44
assert contradiction_report({'evidence':[{'evidence_ref':'a','claim_refs':['c'],'state':'supports'},{'evidence_ref':'b','claim_refs':['c'],'state':'challenges'}]})['contradiction_count']==1
assert quantitative_synthesis({'effects':[{'effect':.1,'standard_error':.1},{'effect':.2,'standard_error':.1}]})['automatic_truth_inference'] is False
assert replication_synthesis({'evidence':[{'evidence_ref':'o','state':'supports'},{'evidence_ref':'r','replication_of_ref':'o','state':'challenges'}]})['automatic_replication_certification'] is False
assert core_object_plan({'project_ref':'deployment-project','claim_refs':['c'],'evidence_refs':['e']})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['determine_truth'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.134 required Evidence Synthesis Intelligence II routes loaded'); print('PASS: contradiction, meta-analysis, replication, and Core fixtures'); print('PASS: no automatic quality scoring, consensus certification, truth inference, scientific validity, or Core submission')
PYDEPLOY
echo "PASS - Sustainable Catalyst Lab v0.134.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
