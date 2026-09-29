#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.140.0.1 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.140.0.1.zip}"
CONTAINER="sc-lab"; PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo '=== LAB v0.140.0.1 — SCIENTIFIC RESEARCH OS RELEASE INTEGRITY REPAIR ==='
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v014001.XXXXXX)"
cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.140.0.1-$ts"; env_backup="/tmp/sc-lab-v0.140.0.1.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; find "$tmp" -type d -exec chmod u+rwx {} +; find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo 'ERROR: backend/Dockerfile not found' >&2; exit 1; }
source_backend="$(dirname "$source_file")"
for f in scientific_research_operating_system_v01400.py scholarly_study_original_research_package_v01390.py research_program_intelligence_v01380.py research_change_impact_living_analysis_v01370.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done
[[ "$healthy" == 1 ]] || { echo 'ERROR: Lab container did not become healthy' >&2; exit 1; }
current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-research-operating-system/v01400/health")"
prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scholarly-study-original-research-package/v01390/health")"
core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$current" "$prior" "$core" <<'PY2'
import json,re,sys
current,prior,core=[json.loads(x) for x in sys.argv[1:]]
assert current.get('ok') is True and current.get('version')=='0.140.0' and current.get('api_route_count')==25
assert current.get('scientific_research_operating_system') is True
assert prior.get('ok') is True and prior.get('version')=='0.139.0'
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]
assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,0,0)
print('PASS: v0.140.0 Scientific Research OS backend semantics preserved under v0.140.0.1 repair package')
print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PY2
echo 'PASS - Sustainable Catalyst Lab v0.140.0.1 synchronized backend deployment complete.'
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
