#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.135.19.0 deployment stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
BASE="/opt/sustainable-catalyst/lab";LIVE_BACKEND="$BASE/backend";ZIP="${1:-/tmp/sustainable-catalyst-lab-backend-v0.135.19.0.zip}";CONTAINER="sc-lab";PORT="8092";CORE_HEALTH_URL="${SC_PLATFORM_CORE_HEALTH_URL:-https://core.sustainablecatalyst.com/health}"
[[ -f "$ZIP" ]]||{ echo "ERROR: backend ZIP not found: $ZIP" >&2;exit 1;};for cmd in docker unzip rsync curl python3 find sed dirname;do command -v "$cmd" >/dev/null||{ echo "ERROR: required command missing: $cmd" >&2;exit 1;};done
echo "=== LAB v0.135.19.0 — CROSS-REVIEW SYNTHESIS / RESOLUTION MATRIX ==="
ts="$(date +%Y%m%d-%H%M%S)";tmp="$(mktemp -d /tmp/sc-lab-v0135190.XXXXXX)";cleanup(){ chmod -R u+rwX "$tmp" 2>/dev/null||true;rm -rf "$tmp" 2>/dev/null||true;};trap cleanup EXIT
backup="$BASE/backend.before-v0.135.19.0-$ts";env_backup="/tmp/sc-lab-v0.135.19.0.env.production.$ts";cp -a "$LIVE_BACKEND" "$backup";cp "$BASE/.env.production" "$env_backup";chmod 600 "$env_backup"
unzip -q "$ZIP" -d "$tmp";find "$tmp" -type d -exec chmod u+rwx {} +;find "$tmp" -type f -exec chmod u+rw {} +
source_file="$(find "$tmp" -type f -path '*/backend/Dockerfile'|sed -n '1p')";[[ -n "$source_file" ]]||{ echo "ERROR: backend/Dockerfile not found" >&2;exit 1;};source_backend="$(dirname "$source_file")"
for f in graph_studio_review_audit_v0135140.py graph_studio_multi_reviewer_panels_v0135180.py graph_studio_cross_review_synthesis_v0135190.py;do [[ -f "$source_backend/app/$f" ]]||{ echo "ERROR: required module missing: $f" >&2;exit 1;};done
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$source_backend/" "$LIVE_BACKEND/";cp "$env_backup" "$BASE/.env.production";chmod 600 "$BASE/.env.production";cd "$BASE";docker compose config --quiet;docker compose build lab;docker compose up -d --force-recreate lab
healthy=0;for _ in $(seq 1 60);do state="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER" 2>/dev/null||true)";[[ "$state" == healthy ]]&&{ healthy=1;break;};[[ "$state" =~ unhealthy|exited|dead ]]&&exit 1;sleep 2;done;[[ "$healthy" == 1 ]]||{ echo "ERROR: Lab container did not become healthy" >&2;exit 1;}
patch="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-cross-review-synthesis/v0135190/health")";accept="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-cross-review-synthesis/v0135190/acceptance")";prior="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-multi-reviewer-panels/v0135180/health")";audit="$(curl -fsS "http://127.0.0.1:${PORT}/v1/graph-studio-review-audit/v0135140/health")";core="$(curl -fsS "$CORE_HEALTH_URL")"
python3 - "$patch" "$accept" "$prior" "$audit" "$core" <<'PY2'
import json,sys,re
patch,accept,prior,audit,core=[json.loads(z) for z in sys.argv[1:]]
assert patch.get('ok') is True and patch.get('version')=='0.135.19.0' and patch.get('api_route_count')==21
assert patch.get('cross_review_synthesis') and patch.get('resolution_matrix') and patch.get('dissent_preserved')
assert accept.get('ok') and accept.get('majority_voting') is False and accept.get('consensus_scoring') is False and accept.get('reviewer_ranking') is False and accept.get('automatic_resolution') is False
assert prior.get('ok') is True and prior.get('version')=='0.135.18.0';assert audit.get('ok') is True and audit.get('version')=='0.135.14.0'
parts=[int(x) for x in re.findall(r'\d+',str(core.get('version','')))];assert core.get('ok') is True and len(parts)>=3 and tuple(parts[:3])>=(3,0,0)
print('PASS: v0.135.19.0 cross-review backend healthy');print('PASS: retained v0.135.18.0 multi-reviewer panels');print('PASS: retained v0.135.14.0 review audit');print(f"PASS: compatible Platform Core v{core.get('version')} detected")
PY2
docker exec -i "$CONTAINER" python - <<'PY2'
from app.main import app
from app import graph_studio_cross_review_synthesis_v0135190 as m
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)};req={x for x in paths if x.startswith('/v1/graph-studio-cross-review-synthesis/v0135190')};assert len(req)==21,len(req)
a=m.acceptance_report();assert a['cross_review_synthesis'] and a['project_resolution_matrix'] and a['dissent_register'] and not a['majority_voting'] and not a['reviewer_ranking'] and not a['automatic_resolution']
print(f'INFO: {len(paths)} FastAPI path routes registered');print('PASS: v0.135.19.0 backend acceptance contracts')
PY2
echo "PASS - Sustainable Catalyst Lab v0.135.19.0 backend deployment complete.";echo "Backend backup: $backup";echo "Environment backup: $env_backup"
