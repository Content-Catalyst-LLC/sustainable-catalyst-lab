#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.115.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.115.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.115.0 — ADVANCED STATISTICAL & UNCERTAINTY GRAPHICS ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01150.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.115.0-$ts"; env_backup="/tmp/sc-lab-v0.115.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/advanced_statistical_uncertainty_graphics_v01150.py" ]] || { echo "ERROR: v0.115.0 statistical-graphics module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }

health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-statistical-uncertainty-graphics/health")"; production="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-production-runtime/health")"; core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$stats" "$production" "$core_health" <<'PYVERIFY'
import json,sys,re
health,design,stats,production,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert design.get('ok') is True and design.get('version')=='0.114.0',design
assert stats.get('ok') is True and stats.get('version')=='0.115.0',stats
assert stats.get('graphic_type_count')==16 and stats.get('boundaries',{}).get('automatic_kde_bandwidth') is False,stats
assert production.get('ok') is True and production.get('lab_release_version')=='0.113.0',production
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core; assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.114 publication-grade visualization design system healthy')
print('PASS: Lab v0.115.0 advanced statistical & uncertainty graphics health contract')
print('PASS: retained v0.113 production runtime healthy')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.advanced_statistical_uncertainty_graphics_v01150 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/advanced-statistical-uncertainty-graphics'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/distributions/normalize',f'{base}/distributions/kde',f'{base}/distributions/figure',f'{base}/intervals/figure',f'{base}/fan-chart/figure',f'{base}/posterior/figure',f'{base}/coefficients/forest',f'{base}/calibration/reliability',f'{base}/diagnostics/residuals',f'{base}/qq/figure',f'{base}/sensitivity/figure',f'{base}/uncertainty/decomposition',f'{base}/coverage/figure',f'{base}/small-multiples/compose',f'{base}/publication/build'}
assert not(required-paths),sorted(required-paths)
pub={'caption':'Deployment fixture.','source':'Deployment fixture.','method':'Declared deployment method.'}
h=build_distribution_figure({'mode':'histogram','samples':[1,2,2,3,4,5],'bins':4,'publication':pub}); assert h['graphic_type']=='histogram'
k=explicit_kde({'samples':[1,2,3,4],'bandwidth':.5}); assert k['automatic_bandwidth_selection'] is False and len(k['density'])>=32
fan=build_fan_chart({'quantile_levels':[.1,.25,.5,.75,.9],'records':[{'x':0,'values':[1,2,3,4,5]},{'x':1,'values':[2,3,4,5,6]}],'publication':pub}); assert len(fan['statistical_metadata']['bands'])==2
cal=build_calibration_figure({'bins':[{'predicted':.2,'observed':.1,'count':10},{'predicted':.8,'observed':.9,'count':10}],'publication':pub}); assert round(cal['statistical_metadata']['expected_calibration_error'],6)==.1
qq=build_qq_figure({'samples':[1,2,3,4],'reference_distribution':'normal','publication':pub}); assert qq['statistical_metadata']['automatic_distribution_selection'] is False
sens=build_sensitivity_figure({'method':'sobol','indices':[{'parameter':'x1','st':.7,'s1':.5},{'parameter':'x2','st':.2,'s1':.1}],'publication':pub}); assert sens['statistical_metadata']['automatic_significance_inference'] is False
publication=build_publication_figure({'advanced_figure':cal,'profile':'journal-double','alt_text':'Calibration reliability diagram.'}); assert publication['publication_ready'] is True and publication['scientific_validity_certified'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: eighteen v0.115 statistical graphics routes loaded')
print('PASS: empirical distributions, explicit KDE, fan chart, calibration, Q-Q, sensitivity, and publication bridge fixtures')
print('PASS: rendering remains separate from statistical/scientific validity and truth judgments')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.115.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
