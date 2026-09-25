#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.130.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.130.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || exit 1; done
echo "=== LAB v0.130.0 — SCIENTIFIC RESEARCH PROJECT STUDIO ==="
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01300.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.130.0-$ts"; env_backup="/tmp/sc-lab-v0.130.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/scientific_research_project_studio_v01300.py" ]] || { echo "ERROR: v0.130 project studio module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"; cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || exit 1
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/research-reproduction-replication-studio/health")"; project="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-research-project-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$prior" "$project" "$core" <<'PYDEPLOY'
import json,sys,re
h,p,r,core=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0'; assert p.get('ok') is True and p.get('version')=='0.129.0'; assert r.get('ok') is True and r.get('version')=='0.130.0'; assert r.get('method_family_count')==18 and r.get('automatic_domain_object_mutation') is False
mm=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert core.get('ok') is True and mm and tuple(map(int,mm.groups())) >= (3,0,0)
print('PASS: Lab Compute Core 1.0.0 healthy'); print('PASS: retained v0.129 Research Reproduction & Replication Studio healthy'); print('PASS: Lab v0.130.0 Scientific Research Project Studio health contract'); print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYDEPLOY
docker exec -i "$CONTAINER" python - <<'PYDEPLOY'
from app.main import app
from app.scientific_research_project_studio_v01300 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/scientific-research-project-studio'; required={x for x in paths if x.startswith(base)}; assert len(required)>=32
assert component_registry({'components':[{'ref':'d:1','type':'dataset'}]})['project_registry_is_not_domain_authority'] is True
assert relationship_graph({'node_refs':['d:1','m:1'],'relationships':[{'from_ref':'d:1','to_ref':'m:1','relation':'input-to'}]})['automatic_relationship_inference'] is False
assert readiness_report({'checks':{'project':1,'components':1,'provenance':1,'methods':1,'outputs':1}})['ready_for_scientific_acceptance'] is False
assert core_project_plan({'project_ref':'deployment-project','session_id':'deployment-session'})['automatic_core_submission'] is False
assert interpretation_boundaries_report()['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered'); print('PASS: v0.130 required Scientific Research Project Studio routes loaded'); print('PASS: project registry, graph, readiness, snapshot/Core boundaries'); print('PASS: no automatic source-object mutation, scientific inference, validity certification, or Core submission')
PYDEPLOY
echo "PASS - Sustainable Catalyst Lab v0.130.0 backend deployment complete."; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
