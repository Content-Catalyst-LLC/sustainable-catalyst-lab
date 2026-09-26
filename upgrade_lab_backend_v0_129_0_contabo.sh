#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.129.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.129.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.129.0 — RESEARCH REPRODUCTION & REPLICATION STUDIO ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01290.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.129.0-$ts"; env_backup="/tmp/sc-lab-v0.129.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/research_reproduction_replication_studio_v01290.py" ]] || { echo "ERROR: v0.129 reproduction/replication module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/experimental-design-power-analysis/health")"; rr="$(curl -fsS "http://127.0.0.1:${PORT}/v1/research-reproduction-replication-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$rr" "$core" <<'PYDEPLOY'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert p.get('ok') is True and p.get('version')=='0.128.0'; assert r.get('ok') is True and r.get('version')=='0.129.0'; assert r.get('method_family_count')==15 and r.get('automatic_claim_confirmation') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.128 Experimental Design & Power Analysis healthy'); print('PASS: Lab v0.129.0 Research Reproduction & Replication Studio health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYDEPLOY
docker exec -i "$CONTAINER" python - <<'PYDEPLOY'
from app.main import app
from app.research_reproduction_replication_studio_v01290 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/research-reproduction-replication-studio'; required={x for x in paths if x.startswith(base)}; assert len(required)>=30
assert artifact_inventory({'artifacts':[{'ref':'d:1','required':True,'available':True,'sha256':'a'*64}]})['hash_coverage_fraction']==1
assert result_comparison({'expected':[1,2],'observed':[1.001,1.999],'absolute_tolerance':.01})['all_within_tolerance'] is True
assert replication_protocol({'claim_refs':['c:1']})['automatic_success_criteria_selection'] is False
assert reproducibility_matrix({'dimensions':{'inputs':'available'}})['automatic_grade'] is False
assert build_core_object_plan({'session_id':'deployment-session','analysis_id':'rr-deploy'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.129 required reproduction/replication routes loaded'); print('PASS: artifact integrity, tolerance comparison, replication, matrix, and Core fixtures'); print('PASS: no automatic execution, claim confirmation, replication success, scientific validity, or Core submission')
PYDEPLOY
echo "PASS - Sustainable Catalyst Lab v0.129.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
