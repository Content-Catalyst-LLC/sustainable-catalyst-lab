#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.120.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.120.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.120.0 — EXPLORATORY DATA ANALYSIS STUDIO ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01200.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.120.0-$ts"; env_backup="/tmp/sc-lab-v0.120.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/exploratory_data_analysis_studio_v01200.py" ]] || { echo "ERROR: v0.120.0 EDA module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-statistical-uncertainty-graphics/health")"; dash="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-dashboards/health")"; advanced="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-3d-4d-scientific-visualization/health")"; narrative="$(curl -fsS "http://127.0.0.1:${PORT}/v1/visual-research-narrative-figure-composer/health")"; intelligence="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-figure-intelligence-automatic-layout/health")"; eda="$(curl -fsS "http://127.0.0.1:${PORT}/v1/exploratory-data-analysis-studio/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$stats" "$dash" "$advanced" "$narrative" "$intelligence" "$eda" "$core" <<'PYVERIFY'
import json,sys,re
h,d,s,db,a,n,i,e,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert d.get('ok') is True and d.get('version')=='0.114.0',d
assert s.get('ok') is True and s.get('version')=='0.115.0',s
assert db.get('ok') is True and db.get('version')=='0.116.0',db
assert a.get('ok') is True and a.get('version')=='0.117.0',a
assert n.get('ok') is True and n.get('version')=='0.118.0',n
assert i.get('ok') is True and i.get('version')=='0.119.0',i
assert e.get('ok') is True and e.get('version')=='0.120.0',e
assert e.get('analysis_family_count')==9 and e.get('automatic_source_mutation') is False,e
assert c.get('ok') is True,c
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert m,c; assert tuple(map(int,m.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.114–v0.119 visualization stack healthy')
print('PASS: Lab v0.120.0 Exploratory Data Analysis Studio health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.exploratory_data_analysis_studio_v01200 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/exploratory-data-analysis-studio'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/dataset/normalize',f'{base}/profile/build',f'{base}/missingness/analyze',f'{base}/distributions/analyze',f'{base}/correlations/analyze',f'{base}/groups/compare',f'{base}/outliers/analyze',f'{base}/relationship/analyze',f'{base}/transformations/plan',f'{base}/transformations/preview',f'{base}/dimensions/pca',f'{base}/visualization/plan',f'{base}/studio/build',f'{base}/snapshot/build',f'{base}/export/plan',f'{base}/core-object/plan'}
assert not(required-paths),sorted(required-paths)
rows=[{'group':'A','x':1.0,'y':2.0,'z':10.0},{'group':'A','x':2.0,'y':4.1,'z':11.0},{'group':'A','x':3.0,'y':6.2,'z':None},{'group':'B','x':4.0,'y':8.0,'z':13.0},{'group':'B','x':5.0,'y':10.2,'z':14.0},{'group':'B','x':40.0,'y':12.0,'z':15.0}]
p={'id':'deploy-eda','rows':rows}
assert normalize_dataset(p)['source_rows_immutable'] is True
assert profile_dataset(p)['exploratory_not_confirmatory'] is True
assert analyze_missingness(p)['mcar_mar_mnar_not_determined'] is True
assert analyze_correlations({**p,'columns':['x','y','z'],'method':'spearman'})['p_values_computed'] is False
assert compare_groups({**p,'group_by':'group','value_columns':['x','y']})['hypothesis_test_performed'] is False
assert analyze_outliers({**p,'columns':['x'],'method':'iqr'})['rows_removed'] is False
assert analyze_relationship({**p,'x':'x','y':'y'})['causality_inferred'] is False
plan=plan_transformations({**p,'operations':[{'column':'x','operation':'standardize'}]}); assert plan['automatic_application'] is False
assert preview_transformations({**p,'operations':plan['operations']})['source_dataset_mutated'] is False
assert analyze_pca({**p,'columns':['x','y','z'],'components':2})['cluster_structure_inferred'] is False
assert build_visualization_plan(p)['automatic_render'] is False
assert build_snapshot(p)['automatic_persistence'] is False
assert build_export_plan({**p,'formats':['json','pdf']})['automatic_file_write'] is False
assert build_core_object_plan({**p,'session_id':'deployment-session','analysis_id':'eda-deploy'})['automatic_core_submission'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.120 required EDA routes loaded')
print('PASS: descriptive EDA, transformations, PCA, visual planning, snapshot, export, and Core fixtures')
print('PASS: no automatic source mutation, significance claims, causality, scientific validity, or Core submission')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.120.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
