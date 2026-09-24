#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
echo '=== Lab v0.135.8.4.1 release validation ==='
node --check assets/js/modules/graph-studio-live-binding-v013584.js
node --check assets/js/modules/graph-studio-provenance-interaction-recovery-v0135841.js
node tests/test-v0135841.js
php tests/test-v0135841.php
php tests/test-v013584.php
php -l includes/class-sc-lab-graph-studio-provenance-interaction-recovery-v0135841.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l sustainable-catalyst-lab.php >/dev/null
python3 -m pytest -q \
 backend/tests/test_scientific_visualization_experience_v01351.py \
 backend/tests/test_model_architecture_computational_provenance_graphs_v01352.py \
 backend/tests/test_multi_view_scientific_analysis_canvas_v01353.py \
 backend/tests/test_interactive_scientific_scene_drilldown_v01354.py \
 backend/tests/test_scientific_scene_linking_comparative_context_v01355.py \
 backend/tests/test_reproducible_visual_analysis_sessions_v01356.py \
 backend/tests/test_visual_research_narrative_findings_v01357.py \
 backend/tests/test_research_review_critique_revision_v01358.py \
 backend/tests/test_graph_studio_canonical_runtime_v013581.py \
 backend/tests/test_graph_studio_renderer_replacement_v013582.py \
 backend/tests/test_graph_studio_recovery_v013583.py \
 backend/tests/test_graph_studio_bootstrap_finalization_v0135831.py \
 backend/tests/test_graph_studio_live_binding_v013584.py \
 backend/tests/test_graph_studio_provenance_interaction_recovery_v0135841.py
python3 - <<'PY2'
import json,hashlib,pathlib
root=pathlib.Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.135.8.4.1'; assert m['v0135841RequiredRouteCount']==8; assert m['v0135841ProgrammaticLayoutClick'] is False
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
for sec in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[sec].items(): assert (root/rel).is_file(),rel; assert sha(root/rel)==expected,rel
print(f"PASS: manifest integrity {len(m['wordpressCriticalFiles'])} WordPress/runtime + {len(m['backendCriticalFiles'])} backend files")
PY2
(cd backend && python3 - <<'PY3'
from app.main import app
paths=[r.path for r in app.routes if isinstance(getattr(r,'path',None),str)]
req=[p for p in paths if p.startswith('/v1/graph-studio-provenance-interaction/v0135841')]
assert len(req)==8,len(req)
print(f'PASS: FastAPI paths={len(paths)} patch routes={len(req)}')
PY3
)
echo 'PASS - Lab v0.135.8.4.1 release validation complete.'
