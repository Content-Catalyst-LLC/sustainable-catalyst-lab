#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.109.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab"; LIVE_BACKEND="$BASE/backend"; ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.109.0.zip}"; CONTAINER="sc-lab"; PORT="8092"; CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]] || { echo "ERROR: backend ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$BASE" && -f "$BASE/.env.production" && -f "$BASE/compose.yml" && -d "$LIVE_BACKEND" ]] || { echo "ERROR: live Lab deployment prerequisites missing" >&2; exit 1; }
for cmd in docker unzip rsync curl python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

echo "=== LAB v0.109.0 — VISUAL REASONING & SCIENTIFIC SCENE BRIDGE ==="
echo "=== COMPOSE VOLUME DECLARATIONS (PRESERVED) ==="
docker compose -f "$BASE/compose.yml" config 2>/dev/null | sed -n '/volumes:/,$p' | head -80 || true

ts="$(date +%Y%m%d-%H%M%S)"; tmp="$(mktemp -d /tmp/sc-lab-v01090.XXXXXX)"; trap 'rm -rf "$tmp"' EXIT
backup="$BASE/backend.before-v0.109.0-$ts"; env_backup="/tmp/sc-lab-v0.109.0.env.production.$ts"
cp -a "$LIVE_BACKEND" "$backup"; cp "$BASE/.env.production" "$env_backup"; chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp"
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile' | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: backend/Dockerfile not found" >&2; exit 1; }
source_backend="$(dirname "$source_file")"
[[ -f "$source_backend/app/platform_core_v3_visual_scene_v01090.py" ]] || { echo "ERROR: v0.109.0 visual-scene module missing" >&2; exit 1; }
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
visual="$(curl -fsS "http://127.0.0.1:${PORT}/v1/platform-core-v3-visual-scene/health")"
core_health="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$health" "$adapter" "$objects" "$context" "$execution" "$research" "$visual" "$core_health" <<'PYVERIFY'
import json,sys,re
health,adapter,objects,context,execution,research,visual,core=[json.loads(x) for x in sys.argv[1:]]
assert health.get('ok') is True and health.get('version')=='1.0.0',health
assert adapter.get('ok') is True and adapter.get('lab_release_version')=='0.104.0',adapter
assert objects.get('ok') is True and objects.get('lab_release_version')=='0.105.0' and objects.get('mapping_count')==20,objects
assert context.get('ok') is True and context.get('lab_release_version')=='0.106.0',context
assert execution.get('ok') is True and execution.get('lab_release_version')=='0.107.0',execution
assert research.get('ok') is True and research.get('lab_release_version')=='0.108.0',research
assert visual.get('ok') is True and visual.get('lab_release_version')=='0.109.0',visual
assert visual.get('minimum_core_release')=='3.0.0',visual
for k in ('automatic_core_submission','automatic_core_mutation','automatic_rendering_by_core','automatic_visual_truth_inference'):
 assert visual.get(k) is False,(k,visual)
assert core.get('ok') is True,core
m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',str(core.get('version',''))); assert m,core
assert tuple(map(int,m.groups())) >= (3,0,0),core
print('PASS: Lab Compute Core 1.0.0 healthy')
print('PASS: retained v0.104-v0.108 Platform Core integration surfaces healthy')
print('PASS: Lab v0.109.0 visual reasoning/scientific scene health contract')
print(f"PASS: compatible Platform Core v{core.get('version')} detected (minimum 3.0.0)")
PYVERIFY

docker exec -i "$CONTAINER" python - <<'PYFIXTURE'
from app.main import app
from app.platform_core_v3_visual_scene_v01090 import (
 build_core_scene_contract,build_core_visual_binding,bridge_linked_views,bridge_uncertainty_visual,
 map_legacy_scene,manifest,negotiate_renderer,normalize_scene,normalize_visual,renderer_catalog
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-visual-scene/health','/v1/platform-core-v3-visual-scene/manifest','/v1/platform-core-v3-visual-scene/schema',
'/v1/platform-core-v3-visual-scene/visuals/normalize','/v1/platform-core-v3-visual-scene/visuals/bind',
'/v1/platform-core-v3-visual-scene/scenes/normalize','/v1/platform-core-v3-visual-scene/scenes/bridge',
'/v1/platform-core-v3-visual-scene/linked-views/bridge','/v1/platform-core-v3-visual-scene/uncertainty/bridge',
'/v1/platform-core-v3-visual-scene/renderers/catalog','/v1/platform-core-v3-visual-scene/renderers/negotiate',
'/v1/platform-core-v3-visual-scene/legacy-scene/map'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:deploy','session_id':'9','session_key':'deploy-session','title':'Deployment Fixture','workflow_ref':'lab:workflow:deploy','project_state_ref':'core:state:deploy','researcher_ref':'researcher:deploy'}
scene={'id':'scene-deploy','title':'Deploy scene','rendererPreference':'native-webgpu','cameras':[{'id':'cam-1','type':'perspective'}],'nodes':[{'id':'points','type':'point-cloud','sourceObjectId':'lab:dataset:d1','vertexCount':3,'children':[]}]}
nv=normalize_visual({'context':ctx,'visual':{'id':'v1','visual_type':'scientific-figure','title':'Figure','source_refs':['lab:dataset:d1'],'renderer':'svg2d'}})
bv=build_core_visual_binding({'context':ctx,'visual':nv['visual']})
ns=normalize_scene({'context':ctx,'scene':scene}); cs=build_core_scene_contract({'context':ctx,'scene':scene}); legacy=map_legacy_scene({'context':ctx,'scene':scene})
linked=bridge_linked_views({'context':ctx,'composition':{'title':'Linked','views':[{'id':'a','renderer':'svg2d','datasetId':'d1'},{'id':'b','renderer':'canvas3d','datasetId':'d1'}],'links':[{'sourceViewId':'a','targetViewIds':['b'],'channel':'selection','key':'id'}]},'source_refs':['lab:dataset:d1']})
unc=bridge_uncertainty_visual({'context':ctx,'layer':{'id':'u1','uncertaintySeries':[{'id':'s1','type':'interval','semantics':'custom','records':[{'x':0,'center':2,'lower':1.5,'upper':2.5}]}]},'source_refs':['lab:result:r1']})
cat=renderer_catalog(); neg=negotiate_renderer({'browserCapabilities':{'detected':{'svg':True,'canvas2d':True,'webgl2':True,'webgpu':False}},'requiredFeatures':['3d'],'preferredRenderers':['webgpu','webgl2','canvas3d'],'allowFallback':True})
assert bv['automatic_submission'] is False and bv['data']['visual_ref']=='lab:visual:v1'
assert ns['scene']['scene_kind']=='advanced-scene' and cs['core_scene']['contract']=='sc.visual-runtime.scene.v1'
assert cs['automatic_rendering'] is False and legacy['automatic_rendering'] is False
assert linked['automatic_link_inference'] is False and unc['automatic_uncertainty_inference'] is False
assert len(cat['registry']['renderers'])>=4 and neg['core_renderer_selection'] is False
assert manifest()['boundaries']['core_renders_visuals'] is False
print(f'INFO: {len(path_routes)} FastAPI path routes registered')
print('PASS: twelve v0.109 visual reasoning/scientific scene routes loaded')
print('PASS: Lab scientific scenes map to renderer-neutral Core scene contracts')
print('PASS: linked-view and uncertainty semantics remain declared, not inferred')
print('PASS: Lab retains renderer/GPU authority; Core remains reference-first and renderer-neutral')
PYFIXTURE

echo "PASS - Sustainable Catalyst Lab v0.109.0 backend deployment complete."
echo "Backend backup: $backup"; echo "Environment backup: $env_backup"; echo "Compose file and compose-managed volumes were left unchanged."
