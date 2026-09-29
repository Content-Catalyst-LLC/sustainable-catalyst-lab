#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.146.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.146.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done
echo '=== LAB v0.146.0 — GRAPH & NETWORK SCIENCE RESEARCH WORKSPACE ==='
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01460.XXXXXX)"; cleanup(){ rm -rf "$tmp" 2>/dev/null || true; }; trap cleanup EXIT
backup="$BASE/backend.before-v0.146.0-$ts"; env_backup="/tmp/sc-lab-v0.146.0.env.production.$ts"; cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"; source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo 'ERROR: backend/Dockerfile not found' >&2; exit 1; }; source_backend="$(dirname "$source_file")"
for f in graph_network_science_research_workspace_v01460.py simulation_computational_experiment_workspace_v01450.py statistical_econometric_research_workspace_v01440.py computational_linguistics_research_workspace_v01430.py integrated_neural_research_workspace_v01420.py scientific_research_operating_system_v01400.py; do [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }; done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"; cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0; for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; [[ "$state" == healthy ]] && { healthy=1; break; }; [[ "$state" =~ unhealthy|exited|dead ]] && exit 1; sleep 2; done; [[ "$healthy" == 1 ]] || { echo 'ERROR: Lab container did not become healthy' >&2; exit 1; }
new="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-network-science-research-workspace/v01460/health")"; sim="$(curl -fsS "http://127.0.0.1:${PORT}/v1/simulation-computational-experiment-workspace/v01450/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/statistical-econometric-research-workspace/v01440/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$new" "$sim" "$stats" "$core" <<'PY2'
import json,re,sys
new,sim,stats,core=[json.loads(x) for x in sys.argv[1:]]
assert new.get('ok') is True and new.get('version')=='0.146.0' and new.get('api_route_count')==61
assert new.get('graphNetworkScienceResearchWorkspace') is True and new.get('explicitEdgeSemantics') is True
assert new.get('workspaceExecutionAuthority') is True and new.get('workbenchPrototypeExecutionAuthority') is True and new.get('platformCoreCanonicalAuthority') is True
assert new.get('labExecutesLargeGraphAlgorithms') is False and new.get('automaticRelationshipInference') is False and new.get('automaticCausalInference') is False and new.get('automaticScientificValidity') is False and new.get('graphMetricIsEvidence') is False
assert sim.get('ok') is True and sim.get('version')=='0.145.0'; assert stats.get('ok') is True and stats.get('version')=='0.144.0'
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]; assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,0,0)
print('PASS: Lab v0.146.0 backend healthy with v0.145.0/v0.144.0 predecessors retained'); print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PY2
echo 'PASS - Sustainable Catalyst Lab v0.146.0 backend deployment complete.'; echo "Backend backup: $backup"; echo "Environment backup: $env_backup"
