#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.118.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.118.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
echo "=== LAB v0.118.0 — VISUAL RESEARCH NARRATIVE & FIGURE COMPOSER ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true
ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01180.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.118.0-$ts"; env_backup="/tmp/sc-lab-v0.118.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"; [[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/visual_research_narrative_figure_composer_v01180.py" ]] || { echo "ERROR: v0.118.0 module missing" >&2; exit 1; }
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/"
cp "$env_backup" "$BASE/.env.production"; chmod 600 "$BASE/.env.production"
cd "$BASE"; docker compose config --quiet; docker compose build lab; docker compose up -d --force-recreate lab
healthy=0
for _ in $(seq 1 60); do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null || true)"; case "$state" in healthy) healthy=1; break;; unhealthy|exited|dead) docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1;; esac; sleep 2; done
[[ "$healthy" == 1 ]] || { echo "ERROR: container did not become healthy" >&2; docker logs --tail=200 "$CONTAINER" >&2 || true; exit 1; }
health="$(curl -fsS "http://127.0.0.1:${PORT}/health")"; design="$(curl -fsS "http://127.0.0.1:${PORT}/v1/scientific-visualization-design-system/health")"; stats="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-statistical-uncertainty-graphics/health")"; dash="$(curl -fsS "http://127.0.0.1:${PORT}/v1/interactive-scientific-dashboards/health")"; advanced="$(curl -fsS "http://127.0.0.1:${PORT}/v1/advanced-3d-4d-scientific-visualization/health")"; narrative="$(curl -fsS "http://127.0.0.1:${PORT}/v1/visual-research-narrative-figure-composer/health")"; core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$design" "$stats" "$dash" "$advanced" "$narrative" "$core" <<'PYVERIFY'
import json,sys,re
h,d,s,db,a,n,c=[json.loads(x) for x in sys.argv[1:]]
assert h.get('ok') is True and h.get('version')=='1.0.0',h
assert d.get('ok') is True and d.get('version')=='0.114.0',d
assert s.get('ok') is True and s.get('version')=='0.115.0',s
assert db.get('ok') is True and db.get('version')=='0.116.0',db
assert a.get('ok') is True and a.get('version')=='0.117.0',a
assert n.get('ok') is True and n.get('version')=='0.118.0',n
assert n.get('figure_kind_count')==12 and n.get('automatic_core_submission') is False,n
assert c.get('ok') is True,c
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(c.get('version',''))); assert m,c; assert tuple(map(int,m.groups())) >= (3,0,0),c
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.114 publication design system healthy')
print('PASS: retained v0.115 statistical graphics healthy')
print('PASS: retained v0.116 dashboards healthy')
print('PASS: retained v0.117 3D/4D visualization healthy')
print('PASS: Lab v0.118.0 narrative composer health contract')
print(f"PASS: compatible Platform Core v{c.get('version')} detected (minimum 3.0.0)")
PYVERIFY
docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.visual_research_narrative_figure_composer_v01180 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/visual-research-narrative-figure-composer'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/schema',f'{base}/narrative/normalize',f'{base}/section/normalize',f'{base}/figure/normalize',f'{base}/figure-plate/build',f'{base}/caption/build',f'{base}/annotations/build',f'{base}/research-links/build',f'{base}/references/build',f'{base}/provenance/trace',f'{base}/layout/plan',f'{base}/export/plan',f'{base}/publication/package',f'{base}/revision/snapshot',f'{base}/core-visual/plan',f'{base}/accessibility/audit'}
assert not(required-paths), sorted(required-paths)
fig={'id':'f1','figure_ref':'lab:figure:f1','figure_kind':'statistical-figure','title':'Observed response','caption':'Declared response and uncertainty.','alt_text':'A response curve with a shaded uncertainty band.','source_refs':['lab:dataset:d1'],'method_refs':['lab:method:m1'],'finding_refs':['lab:finding:f1']}
narr={'id':'deploy-narrative','title':'Deployment narrative','format':'research-report','figures':[fig],'sections':[{'id':'results','type':'results','title':'Results','blocks':[{'type':'paragraph','text':'Declared result.'},{'type':'figure','figure_refs':['lab:figure:f1']}]}],'source_refs':['lab:dataset:d1']}
n=normalize_narrative(narr); assert n['automatic_scientific_conclusion_generation'] is False and n['automatic_figure_mutation'] is False
assert build_figure_plate({'figures':[fig],'caption':'Declared plate caption.'})['automatic_figure_reordering'] is False
assert build_caption_package({'figure':fig})['automatic_caption_inference'] is False
assert build_annotation_layer({'figure_ref':'lab:figure:f1','annotations':[{'text':'Declared annotation.','evidence_refs':['lab:evidence:e1']}]})['automatic_evidence_weighting'] is False
assert trace_provenance({'narrative':narr})['provenance_trace']['source_refs']==['lab:dataset:d1']
assert build_export_plan({'narrative':narr,'formats':['pdf','html','json']})['automatic_publication'] is False
assert build_publication_package({'narrative':narr})['automatic_scientific_validity_certification'] is False
assert build_revision_snapshot({'narrative':narr})['automatic_persistence'] is False
core=build_core_visual_plan({'narrative':narr,'session_id':'deployment-session'}); assert core['automatic_core_submission'] is False and core['core_renders_narrative'] is False
assert accessibility_audit({'narrative':narr})['accessible'] is True
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: v0.118 required narrative composer routes loaded')
print('PASS: narrative, figure plate, caption, provenance, publication, revision, accessibility, and Core fixtures')
print('PASS: no automatic conclusion/caption/relationship/evidence-weight/scientific-validity inference')
PYFIXTURE
echo "PASS - Sustainable Catalyst Lab v0.118.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
