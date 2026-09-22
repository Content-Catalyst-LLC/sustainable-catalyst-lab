#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.108.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.108.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.108.0 — FINDINGS, CLAIMS, EVIDENCE & VALIDATION BRIDGE ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01080.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.108.0-$ts"; env_backup="/tmp/sc-lab-v0.108.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_findings_validation_v01080.py" ]] || { echo "ERROR: v0.108.0 findings/validation module missing" >&2; exit 1; }
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
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$research" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,research,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert adapter.get('ok') is True and adapter.get('lab_release_version')=='0.104.0',adapter
assert objects.get('ok') is True and objects.get('lab_release_version')=='0.105.0' and objects.get('mapping_count')==20,objects
assert context.get('ok') is True and context.get('lab_release_version')=='0.106.0',context
assert execution.get('ok') is True and execution.get('lab_release_version')=='0.107.0',execution
assert research.get('ok') is True and research.get('lab_release_version')=='0.108.0',research
assert research.get('minimum_core_release')=='3.0.0',research
for k in ('automatic_core_submission','automatic_claim_inference','automatic_finding_generation','automatic_evidence_judgment','automatic_contradiction_resolution','automatic_replication_certification','scientific_validity_certified','truth_determined'):
 assert research.get(k) is False,(k,research)
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104-v0.107 Platform Core integration surfaces healthy')
print('PASS: Lab v0.108.0 findings/claims/evidence/validation health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_findings_validation_v01080 import (
 build_core_claim_binding,build_core_contradiction_binding,build_core_evidence_link_binding,build_core_finding_binding,
 build_core_replication_binding,build_core_validation_challenge_binding,map_legacy_scientific_claim,normalize_claim,normalize_finding
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-research-intelligence/manifest','/v1/platform-core-v3-research-intelligence/schema',
'/v1/platform-core-v3-research-intelligence/findings/normalize','/v1/platform-core-v3-research-intelligence/findings/bind',
'/v1/platform-core-v3-research-intelligence/claims/normalize','/v1/platform-core-v3-research-intelligence/claims/bind',
'/v1/platform-core-v3-research-intelligence/evidence-links/bind','/v1/platform-core-v3-research-intelligence/contradictions/bind',
'/v1/platform-core-v3-research-intelligence/validation/bind','/v1/platform-core-v3-research-intelligence/replications/bind',
'/v1/platform-core-v3-research-intelligence/legacy-claim/map'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'8','session_key':'deploy-session','title':'Deployment Fixture','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy','researcher_ref':'researcher:deploy'}
finding={'id':'f1','title':'Finding','statement':'Declared deployment result.','finding_type':'result','status':'recorded','execution_ref':'lab:execution:r1','source_refs':['lab:artifact:a1']}
claim={'id':'c1','studyId':'s1','statement':'A declared association is present in the modeled scenario.','claimType':'associational','status':'active','evidenceLinks':[{'id':'e1','role':'supports','sourceType':'analysis','ref':'lab:artifact:a1'}]}
nf=normalize_finding({'context':ctx,'finding':finding}); bf=build_core_finding_binding({'context':ctx,'finding':finding})
nc=normalize_claim({'context':ctx,'claim':claim}); bc=build_core_claim_binding({'context':ctx,'claim':claim})
ev=build_core_evidence_link_binding({'context':ctx,'evidence_link':{'id':'e1','evidence_ref':'lab:artifact:a1','target_type':'claim','target_id':'core-claim-1','relation':'supports','declared_strength':'moderate'}})
co=build_core_contradiction_binding({'context':ctx,'contradiction':{'id':'co1','claim_a_id':'a','claim_b_id':'b','status':'unresolved'}})
va=build_core_validation_challenge_binding({'context':ctx,'validation':{'id':'v1','challenge_type':'uncertainty_challenge','title':'Uncertainty challenge'}})
rp=build_core_replication_binding({'context':ctx,'replication':{'id':'rp1','challenge_id':'core-challenge-1','target_ref':'lab:claim:c1','execution_ref':'lab:execution:rep1'}})
legacy=map_legacy_scientific_claim({'context':ctx,'claim':claim})
assert nf['finding']['finding_key']=='f1' and len(nf['finding']['finding_hash'])==64
assert bf['automatic_submission'] is False and bf['data']['metadata']['underlying_finding_remains_authoritative_in_lab'] is True
assert nc['claim']['claim_type']=='interpretive' and nc['claim']['status']=='proposed'
assert bc['automatic_submission'] is False and bc['data']['status']=='proposed'
assert ev['data']['declared_strength']=='moderate' and ev['data']['metadata']['evidence_strength_is_declared_not_core_judged'] is True
assert co['data']['status']=='unresolved' and co['automatic_core_mutation'] is False
assert va['scientific_validity_certified'] is False
assert rp['data']['provenance']['replication_result_is_declared_not_core_certified'] is True
assert len(legacy['core_evidence_bindings'])==1 and legacy['automatic_scientific_certification'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: twelve v0.108 findings/claims/evidence/validation routes loaded')
print('PASS: Lab v0.62 claim semantics bridge to Core without inferring supported status')
print('PASS: evidence strength, contradictions, challenges, and replication remain declared/non-determinative')
print('PASS: no automatic Core submission, mutation, scientific certification, or truth determination')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.108.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
