#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.111.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.111.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.111.0 — SCIENTIFIC INVESTIGATION RUNTIME INTEGRATION ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01110.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.111.0-$ts"; env_backup="/tmp/sc-lab-v0.111.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_scientific_investigation_v01110.py" ]] || { echo "ERROR: v0.111.0 scientific-investigation module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do
 state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"
 case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac
 sleep 2
done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"
adapter="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-adapter/health")"
objects="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-objects/health")"
context="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-context/health")"
execution="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-executions/health")"
research="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-research-intelligence/health")"
visual="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-visual-scene/health")"
packages="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-scholarly-packages/health")"
investigation="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-scientific-investigations/health")"
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$research" "$visual" "$packages" "$investigation" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,research,visual,packages,investigation,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert adapter.get('ok') is True and adapter.get('lab_release_version')=='0.104.0',adapter
assert objects.get('ok') is True and objects.get('lab_release_version')=='0.105.0' and objects.get('mapping_count')==20,objects
assert context.get('ok') is True and context.get('lab_release_version')=='0.106.0',context
assert execution.get('ok') is True and execution.get('lab_release_version')=='0.107.0',execution
assert research.get('ok') is True and research.get('lab_release_version')=='0.108.0',research
assert visual.get('ok') is True and visual.get('lab_release_version')=='0.109.0',visual
assert packages.get('ok') is True and packages.get('lab_release_version')=='0.110.0',packages
assert investigation.get('ok') is True and investigation.get('lab_release_version')=='0.111.0',investigation
assert investigation.get('minimum_core_release')=='3.0.0',investigation
for k in ('automatic_core_submission','automatic_execution','automatic_scientific_certification','automatic_truth_determination'): assert investigation.get(k) is False,(k,investigation)
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104-v0.110 Platform Core integration surfaces healthy')
print('PASS: Lab v0.111.0 scientific investigation runtime integration health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_scientific_investigation_v01110 import build_core_investigation_binding,build_runtime_integration_plan,bridge_evidence_context,bridge_reasoning_context,bridge_scientific_assets,check_investigation_continuity,manifest,normalize_investigation
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={'/v1/platform-core-v3-scientific-investigations/health','/v1/platform-core-v3-scientific-investigations/manifest','/v1/platform-core-v3-scientific-investigations/schema','/v1/platform-core-v3-scientific-investigations/investigations/normalize','/v1/platform-core-v3-scientific-investigations/investigations/bind','/v1/platform-core-v3-scientific-investigations/investigations/runtime-plan','/v1/platform-core-v3-scientific-investigations/investigations/evidence-context','/v1/platform-core-v3-scientific-investigations/investigations/reasoning-context','/v1/platform-core-v3-scientific-investigations/investigations/scientific-assets','/v1/platform-core-v3-scientific-investigations/investigations/continuity/check','/v1/platform-core-v3-scientific-investigations/legacy-study/map','/v1/platform-core-v3-scientific-investigations/legacy-argumentation/map'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'9','session_key':'deploy-session','title':'Deployment Fixture','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy','researcher_ref':'researcher:deploy'}
inv={'id':'inv-deploy','investigation_type':'computational','title':'Deployment investigation','status':'active','dataset_refs':['lab:dataset:d1'],'model_refs':['lab:model:m1'],'execution_refs':['lab:execution:r1'],'evidence_refs':['lab:evidence:e1'],'claim_refs':['lab:claim:c1'],'hypothesis_refs':['lab:hypothesis:h1'],'visual_refs':['lab:visual:v1'],'validation_refs':['lab:validation:x1'],'package_refs':['lab:research-package:p1']}
n=normalize_investigation({'context':ctx,'investigation':inv}); b=build_core_investigation_binding({'context':ctx,'investigation':inv}); plan=build_runtime_integration_plan({'context':ctx,'investigation':inv}); e=bridge_evidence_context({'context':ctx,'investigation':inv}); r=bridge_reasoning_context({'context':ctx,'investigation':inv}); a=bridge_scientific_assets({'context':ctx,'investigation':inv}); c=check_investigation_continuity({'context':ctx,'investigation':inv,'expected_context':{'project_ref':'project:deploy','session_id':'9'}})
assert n['investigation']['investigation_type']=='computational' and b['automatic_submission'] is False and b['automatic_execution'] is False
assert plan['plan']['automatic_investigation_run'] is False and plan['plan']['automatic_truth_determination'] is False
assert e['automatic_evidence_ranking'] is False and r['automatic_hypothesis_ranking'] is False and a['automatic_binding_submission'] is False
assert c['reference_continuity_valid'] is True and c['scientific_validity_assessed'] is False
assert manifest()['boundaries']['core_determines_truth'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: twelve v0.111 scientific investigation runtime routes loaded')
print('PASS: Lab investigation maps to Core unified-runtime investigation binding')
print('PASS: linked scientific assets remain explicit specialist-layer references')
print('PASS: Lab retains scientific authority; Core does not run, rank, select, certify, infer causality, or determine truth')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.111.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
