#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.143.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.143.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo '=== LAB v0.143.0 — COMPUTATIONAL LINGUISTICS RESEARCH WORKSPACE ==='
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01430.XXXXXX)"; cleanup(){ rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.143.0-$ts"; env_backup="/tmp/sc-lab-v0.143.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo 'ERROR: backend/Dockerfile not found' >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in computational_linguistics_research_workspace_v01430.py integrated_neural_research_workspace_v01420.py reproducible_neural_research_package_v01418.py embedding_explorer_v01417.py neural_explainability_workspace_v01416.py scientific_research_operating_system_v01400.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo 'ERROR: Lab container did not become healthy' >&2; exit 1; }
new="$(curl -fsS "http://127.0.0.1:${PORT}/v1/computational-linguistics-research-workspace/v01430/health")"; neural="$(curl -fsS "http://127.0.0.1:${PORT}/v1/integrated-neural-research-workspace/v01420/health")"; pkg="$(curl -fsS "http://127.0.0.1:${PORT}/v1/reproducible-neural-research-package/v01418/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$new" "$neural" "$pkg" "$core" <<'PY2'
import json,re,sys
new,neural,pkg,core=[json.loads(x) for x in sys.argv[1:]]
assert new.get('ok') is True and new.get('version')=='0.143.0' and new.get('api_route_count')==48
assert new.get('computationalLinguisticsResearchWorkspace') is True and new.get('originalLanguageFirst') is True and new.get('translationAsDerivedRepresentation') is True
assert new.get('workspaceExecutionAuthority') is True and new.get('librarySourceAuthority') is True and new.get('platformCoreCanonicalAuthority') is True
assert new.get('labExecutesHeavyLinguisticCompute') is False and new.get('automaticSemanticEquivalence') is False and new.get('automaticScientificValidity') is False and new.get('crossLingualSimilarityIsEvidence') is False
assert neural.get('ok') is True and neural.get('version')=='0.142.0'; assert pkg.get('ok') is True and pkg.get('version')=='0.141.8'
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]; assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,0,0)
print('PASS: Lab v0.143.0 backend healthy with v0.142.0/v0.141.8 predecessors retained'); print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PY2
echo 'PASS - Sustainable Catalyst Lab v0.143.0 backend deployment complete.'; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
