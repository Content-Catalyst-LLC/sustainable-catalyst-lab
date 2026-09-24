#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.112.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.112.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"; CORE_CERT_READINESS_URL="${SC_PLATFORM_CORE_CERT_READINESS_URL:-}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.112.0 — PLATFORM CORE INTEGRATION CERTIFICATION ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01120.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.112.0-$ts"; env_backup="/tmp/sc-lab-v0.112.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_integration_certification_v01120.py" ]] || { echo "ERROR: v0.112.0 integration-certification module missing" >&2; exit 1; }
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
cert="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-integration-certification/health")"
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$research" "$visual" "$packages" "$investigation" "$cert" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,research,visual,packages,investigation,cert,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
checks=[(adapter,'0.104.0'),(objects,'0.105.0'),(context,'0.106.0'),(execution,'0.107.0'),(research,'0.108.0'),(visual,'0.109.0'),(packages,'0.110.0'),(investigation,'0.111.0'),(cert,'0.112.0')]
for obj,v in checks: assert obj.get('ok') is True and obj.get('lab_release_version')==v,(v,obj)
assert cert.get('certified_layer_count')==8 and cert.get('conformance_case_count')==18,cert
for k in ('automatic_core_submission','automatic_product_invocation','automatic_case_execution','automatic_scientific_certification','automatic_truth_determination'): assert cert.get(k) is False,(k,cert)
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104-v0.111 Platform Core integration surfaces healthy')
print('PASS: Lab v0.112.0 Platform Core integration certification health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

if [[ -n "$CORE_CERT_READINESS_URL" ]]; then
  readiness="$(curl -fsS "$CORE_CERT_READINESS_URL")"
  docker exec -i "$CONTAINER" python - "$readiness" <<'PYREADY'
import json,sys
from app.platform_core_v3_integration_certification_v01120 import compatibility_report
r=compatibility_report(json.loads(sys.argv[1])); assert r['compatible'] is True,r
print('PASS: live Core integration-certification readiness is compatible')
PYREADY
else
  echo "INFO: SC_PLATFORM_CORE_CERT_READINESS_URL not set; live protected Core certification-readiness check skipped"
fi

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_integration_certification_v01120 import CASE_CATALOG,assess_roundtrip,build_case_plans,build_full_submission_plan,build_product_plan,build_run_plan,build_suite_plan,catalog,manifest
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}; base='/v1/platform-core-v3-integration-certification'
required={f'{base}/health',f'{base}/manifest',f'{base}/schema',f'{base}/catalog',f'{base}/suites/plan',f'{base}/products/plan',f'{base}/cases/plan',f'{base}/runs/plan',f'{base}/case-results/plan',f'{base}/exchange-checks/plan',f'{base}/trace-checks/plan',f'{base}/reproduction-checks/plan',f'{base}/evidence/plan',f'{base}/findings/plan',f'{base}/roundtrip/assess',f'{base}/compatibility/check',f'{base}/full-plan'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'12','session_key':'deploy-session','title':'Deployment Certification','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy','researcher_ref':'researcher:deploy'}
s=build_suite_plan({'context':ctx}); p=build_product_plan({'suite_id':'suite:deploy'}); cases=build_case_plans({'suite_id':'suite:deploy'}); run=build_run_plan({'suite_id':'suite:deploy','product_id':'product-row:deploy'}); full=build_full_submission_plan({'context':ctx})
assert s['automatic_submission'] is False and p['automatic_submission'] is False and cases['count']==18 and run['automatic_product_invocation'] is False and full['automatic_case_execution'] is False
results=[{'case_key':x[0],'status':'pass'} for x in CASE_CATALOG]; a=assess_roundtrip({'results':results}); assert a['declared_conformance'] is True and a['scientific_validity_certified'] is False and a['product_quality_certified'] is False and a['truth_determined'] is False
assert catalog()['layer_count']==8 and manifest()['boundaries']['core_determines_truth'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: seventeen v0.112 integration-certification routes loaded')
print('PASS: eight-layer / eighteen-case certification catalog')
print('PASS: full Core certification submission plan is explicit and non-submitting')
print('PASS: declared roundtrip conformance does not certify science, product quality, or truth')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.112.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
