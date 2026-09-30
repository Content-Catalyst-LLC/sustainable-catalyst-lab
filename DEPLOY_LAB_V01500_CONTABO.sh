#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.150.0.zip}"
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH="https://core.sustainablecatalyst.com/health"
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP"; exit 1; }
ts="$(date +%Y%m%d-%H%M%S)"; backup="$BASE/backups/backend-v0.150.0-$ts"; mkdir -p "$backup"
[ -d "$LIVE_BACKEND" ] && cp -a "$LIVE_BACKEND" "$backup/backend" || true
[ -f "$BASE/.env.production" ] && cp -a "$BASE/.env.production" "$backup/.env.production" || true
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
unzip -q "$ZIP" -d "$tmp"; src="$tmp/sustainable-catalyst-lab-backend-v0.150.0/backend"
[ -f "$src/app/integrated_computational_research_laboratory_v01500.py" ] || { echo 'ERROR: v0.150.0 module missing'; exit 1; }
[ -f "$src/app/scientific_model_validation_benchmark_laboratory_v01490.py" ] || { echo 'ERROR: v0.149.0 predecessor missing'; exit 1; }
mkdir -p "$LIVE_BACKEND"; rsync -a --delete --exclude='data/' "$src/" "$LIVE_BACKEND/"
cd "$BASE"
if [ -f docker-compose.yml ]; then COMPOSE=(docker compose -f docker-compose.yml); elif [ -f compose.yml ]; then COMPOSE=(docker compose -f compose.yml); else echo 'ERROR: compose file not found'; exit 1; fi
"${COMPOSE[@]}" config >/dev/null; "${COMPOSE[@]}" build "$CONTAINER" 2>/dev/null || "${COMPOSE[@]}" build; "${COMPOSE[@]}" up -d "$CONTAINER" 2>/dev/null || "${COMPOSE[@]}" up -d
for i in $(seq 1 60); do if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then break; fi; sleep 2; done
curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null
python3 - <<'PY2'
import json,urllib.request
base='http://127.0.0.1:8092'
def get(path): return json.load(urllib.request.urlopen(base+path,timeout=10))
h=get('/v1/integrated-computational-research-laboratory/v01500/health'); assert h['version']=='0.150.0' and h['integratedComputationalResearchLaboratory'] is True and h['api_route_count']==86 and h['workspaceCount']==8 and h['labExecutesHeavyCompute'] is False and h['automaticScientificValidity'] is False
p=get('/v1/scientific-model-validation-benchmark-laboratory/v01490/health'); assert p['version']=='0.149.0'
q=get('/v1/multimodal-scientific-experiment-workspace/v01480/health'); assert q['version']=='0.148.0'
print('PASS: v0.150.0, v0.149.0, and v0.148.0 backend endpoints healthy')
PY2
curl -fsS "$CORE_HEALTH" >/dev/null && echo 'PASS: Platform Core health reachable' || echo 'WARN: Platform Core health check unavailable'
echo 'PASS - Sustainable Catalyst Lab v0.150.0 backend deployment complete.'
