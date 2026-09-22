#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.114.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.114.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.114.0 — SCIENTIFIC VISUALIZATION DESIGN SYSTEM & PUBLICATION-GRADE RENDERING ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01140.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.114.0-$ts"; env_backup="/tmp/sc-lab-v0.114.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/scientific_visualization_design_system_v01140.py" ]] || { echo "ERROR: v0.114.0 design-system module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; visual="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-visual-scene/health")"; production="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-production-runtime/health")"; core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$visual" "$production" "$core_health" <<'PYVERIFY'
import json,sys,re
health,design,visual,production,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert design.get('ok') is True and design.get('version')=='0.114.0',design
assert design.get('publication_grade_rendering') is True and design.get('vector_first_exports') is True,design
assert visual.get('ok') is True and visual.get('lab_release_version')=='0.109.0',visual
assert production.get('ok') is True and production.get('lab_release_version')=='0.113.0',production
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core; assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: Lab v0.114.0 scientific visualization design-system health contract')
print('PASS: retained v0.109 visual bridge and v0.113 production runtime healthy')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.scientific_visualization_design_system_v01140 import build_publication_figure,compose_small_multiples,renderer_plan,manifest
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; base='/v1/scientific-visualization-design-system'; required={f'{base}/health',f'{base}/manifest',f'{base}/tokens',f'{base}/catalog',f'{base}/figures/normalize',f'{base}/figures/profile',f'{base}/annotations/plan',f'{base}/uncertainty/style',f'{base}/small-multiples/compose',f'{base}/accessibility/build',f'{base}/renderers/plan',f'{base}/exports/plan',f'{base}/audit',f'{base}/publication-figure/build',f'{base}/core-visual/plan'}; assert not(required-paths),sorted(required-paths)
spec={'kind':'line','title':'Deployment figure','axes':{'x':{'label':'Time','unit':'day'},'y':{'label':'Response','unit':'mg/L'}},'series':[{'id':'obs','semantic_role':'observed','points':[{'x':0,'y':1},{'x':1,'y':2}]},{'id':'model','semantic_role':'model','points':[{'x':0,'y':1.1},{'x':1,'y':1.9}]}],'publication':{'caption':'Deployment fixture.','source':'Deployment fixture.','method':'Deployment fixture.'},'provenance':{'source':'deployment'}}
r=build_publication_figure({'spec':spec,'profile':'journal-double','alt_text':'Observed and modeled response line figure.','annotations':[{'type':'finding','text':'Peak response','x':1,'y':2,'evidence_ref':'e:deploy'}],'uncertainty_layers':[{'kind':'confidence','level':.95}]}); f=r['figure']; assert r['audit']['publication_ready'] is True and r['audit']['scientific_validity_certified'] is False; assert f['rendering']['vector_first'] is True; assert r['export_plan']['automatic_file_write'] is False
assert renderer_plan({'figure':f,'publication':True})['preferred_renderer']=='svg2d'; assert compose_small_multiples({'panels':[{'id':'a'},{'id':'b'}],'columns':2})['responsive']['mobile_columns']==1; assert manifest()['boundaries']['automatic_truth_determination'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: fifteen v0.114 design-system routes loaded')
print('PASS: publication profile, semantic series, evidence-aware annotation, uncertainty, responsive composition, accessibility, vector-first renderer/export, and publication-audit fixtures')
print('PASS: visual publication readiness remains distinct from scientific validity and truth')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.114.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
