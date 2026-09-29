#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.141.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"
LIVE_BACKEND="$BASE/backend"
ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.141.0.zip}"
CONTAINER="sc-lab"
PORT="8092"
CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: required command missing: $cmd" >&2; exit 1; }; done

echo "=== LAB v0.141.0 — MACHINE LEARNING EXPERIMENT WORKSPACE ==="
ts="$(date +%Y%m%d-%H%M%S)"
tmp="$(mktemp -d /tmp/sc-lab-v01410.XXXXXX)"
cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null || true; }
trap cleanup EXIT
backup="$BASE/backend.before-v0.141.0-$ts"
env_backup="/tmp/sc-lab-v0.141.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"
cp "$BASE/.env.production" "$env_backup"
chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
find "$tmp" -type d -exec chmod u+rwx {} +
find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
for f in machine_learning_experiment_workspace_v01410.py scientific_research_operating_system_v01400.py release_integrity_scope_repair_v013901.py scholarly_study_original_research_package_v01390.py research_program_intelligence_v01380.py research_change_impact_living_analysis_v01370.py; do
  [[ -f "$source_backend/app/$f" ]] || { echo "ERROR: required module missing: $f" >&2; exit 1; }
done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"
chmod 600 "$BASE/.env.production"
cd "$BASE"
docker compose config --quiet
docker compose build lab
docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do
  state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"
  [[ "$state" == healthy ]] && { healthy=1; break; }
  [[ "$state" =~ unhealthy|exited|dead ]] && exit 1
  sleep 2
done
[[ "$healthy" == 1 ]] || { echo "ERROR: Lab container did not become healthy" >&2; exit 1; }
current="$(curl -fsS "http://127.0.0.1:${PORT}/v1/machine-learning-experiment-workspace/v01410/health")"
acceptance="$(curl -fsS "http://127.0.0.1:${PORT}/v1/machine-learning-experiment-workspace/v01410/acceptance")"
researchos="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-research-operating-system/v01400/health")"
repair="$(curl -fsS "http://127.0.0.1:${PORT}/v1/release-integrity-scope-repair/v013901/health")"
prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scholarly-study-original-research-package/v01390/health")"
core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$current" "$acceptance" "$researchos" "$repair" "$prior" "$core" <<'PY2'
import json,re,sys
current,acceptance,researchos,repair,prior,core=[json.loads(x) for x in sys.argv[1:]]
assert current.get('ok') is True and current.get('version')=='0.141.0' and current.get('routeCount')==27
assert current.get('workspaceExecutionRequired') is True
assert acceptance.get('ok') is True and acceptance.get('machineLearningExperimentWorkspace') is True
assert acceptance.get('workspaceExecutionHandoff') is True and acceptance.get('researchOSBridge') is True
assert acceptance.get('labExecutesTraining') is False and acceptance.get('predictionIsEvidence') is False
assert acceptance.get('automaticBestModelSelection') is False and acceptance.get('automaticScientificValidity') is False
assert researchos.get('ok') is True and researchos.get('version')=='0.140.0'
assert repair.get('ok') is True and repair.get('version')=='0.139.0.1'
assert prior.get('ok') is True and prior.get('version')=='0.139.0'
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))]
assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3]) >= (3,57,0)
print('PASS: Lab v0.141.0 ML Experiment Workspace healthy')
print('PASS: retained v0.140.0 Scientific Research OS')
print('PASS: retained v0.139.0.1 release-integrity repair')
print(f"PASS: neural-capable Platform Core v{core.get('version')} detected")
PY2
docker exec -i "$CONTAINER" python - <<'PY2'
from app.main import app
from app import machine_learning_experiment_workspace_v01410 as m
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}
req={x for x in paths if x.startswith('/v1/machine-learning-experiment-workspace/v01410')}
assert len(req)==27, len(req)
a=m.acceptance_report()
assert a['machineLearningExperimentWorkspace'] and a['workspaceExecutionHandoff'] and a['workspaceResultIngest']
assert a['backwardCompatibleV01400'] and a['manifestScopeRepairRetainedV013901']
assert not a['labExecutesTraining'] and not a['predictionIsEvidence'] and not a['automaticBestModelSelection']
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.141.0 backend acceptance contracts')
PY2
echo "PASS - Sustainable Catalyst Lab v0.141.0 backend deployment complete."
echo "Backend backup: $backup"
echo "Environment backup: $env_backup"
