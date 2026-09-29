#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.110.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.110.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.110.0 — REPRODUCIBILITY & SCHOLARLY PACKAGE BRIDGE ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01100.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.110.0-$ts"; env_backup="/tmp/sc-lab-v0.110.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_scholarly_package_v01100.py" ]] || { echo "ERROR: v0.110.0 scholarly-package module missing" >&2; exit 1; }
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
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$research" "$visual" "$packages" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,research,visual,packages,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert adapter.get('ok') is True and adapter.get('lab_release_version')=='0.104.0',adapter
assert objects.get('ok') is True and objects.get('lab_release_version')=='0.105.0' and objects.get('mapping_count')==20,objects
assert context.get('ok') is True and context.get('lab_release_version')=='0.106.0',context
assert execution.get('ok') is True and execution.get('lab_release_version')=='0.107.0',execution
assert research.get('ok') is True and research.get('lab_release_version')=='0.108.0',research
assert visual.get('ok') is True and visual.get('lab_release_version')=='0.109.0',visual
assert packages.get('ok') is True and packages.get('lab_release_version')=='0.110.0',packages
assert packages.get('minimum_core_release')=='3.0.0',packages
for k in ('automatic_core_submission','automatic_publication','automatic_reproducibility_certification'): assert packages.get(k) is False,(k,packages)
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104-v0.109 Platform Core integration surfaces healthy')
print('PASS: Lab v0.110.0 reproducibility/scholarly package health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_scholarly_package_v01100 import build_core_package_binding,build_scholarly_interoperability_plan,bridge_citations,bridge_datasets_notebooks,build_provenance_manifest,map_legacy_package,manifest,normalize_package
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={'/v1/platform-core-v3-scholarly-packages/health','/v1/platform-core-v3-scholarly-packages/manifest','/v1/platform-core-v3-scholarly-packages/schema','/v1/platform-core-v3-scholarly-packages/packages/normalize','/v1/platform-core-v3-scholarly-packages/packages/bind','/v1/platform-core-v3-scholarly-packages/scholarly/package','/v1/platform-core-v3-scholarly-packages/scholarly/plan','/v1/platform-core-v3-scholarly-packages/citations/bridge','/v1/platform-core-v3-scholarly-packages/descriptors/bridge','/v1/platform-core-v3-scholarly-packages/provenance/manifest','/v1/platform-core-v3-scholarly-packages/publications/bind','/v1/platform-core-v3-scholarly-packages/validations/record','/v1/platform-core-v3-scholarly-packages/legacy-package/map'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'9','session_key':'deploy-session','title':'Deployment Fixture','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy','researcher_ref':'researcher:deploy'}
pkg={'schema':'sc-lab-reproducibility-package/0.37.0','id':'pkg-deploy','title':'Deploy replication package','packageVersion':'1.0.0','packageHash':'a'*64,'resources':[{'object_ref':'lab:dataset:d1'}],'citations':[{'cited_object_ref':'library:source:s1','citation_format':'plain-text','citation_text':'Source'}],'datasets':[{'dataset_ref':'lab:dataset:d1','content_hash':'b'*64}],'notebooks':[{'notebook_ref':'lab:notebook:n1','execution_ref':'lab:execution:r1'}]}
n=normalize_package({'context':ctx,'package':pkg}); b=build_core_package_binding({'context':ctx,'package':pkg}); plan=build_scholarly_interoperability_plan({'context':ctx,'package':pkg}); cit=bridge_citations({'context':ctx,'package':pkg}); desc=bridge_datasets_notebooks({'context':ctx,'package':pkg}); prov=build_provenance_manifest({'context':ctx,'package':pkg}); legacy=map_legacy_package({'context':ctx,'package':pkg})
assert n['package']['package_type']=='replication_package' and b['automatic_submission'] is False
assert plan['requires_core_package_id_after_create'] is True and plan['automatic_reproducibility_certification'] is False
assert cit['requires_core_package_id'] is True and desc['requires_core_package_id'] is True and prov['lineage_is_declared_not_inferred'] is True
assert legacy['automatic_publication'] is False and legacy['automatic_certification'] is False
assert manifest()['boundaries']['core_certifies_reproducibility'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: thirteen v0.110 reproducibility/scholarly package routes loaded')
print('PASS: Lab packages map to Core unified-runtime package bindings and scholarly plans')
print('PASS: follow-up scholarly operations explicitly wait for Core package identity')
print('PASS: Lab retains package/science authority; Core does not publish or certify reproducibility')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.110.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
