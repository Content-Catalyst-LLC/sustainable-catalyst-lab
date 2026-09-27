#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
node --check assets/js/modules/graph-studio-review-workspace-consolidation-v0135210.js
node --check assets/js/modules/project-workspace-review-workspace-v0135210.js
node tests/test-v0135210.js
node tests/test-v0135210-runtime.js
php tests/test-v0135210.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-graph-studio-review-workspace-consolidation-v0135210.php >/dev/null
PYTHONPATH=backend python3 -m pytest -q \
 backend/tests/test_graph_studio_review_workspace_consolidation_v0135210.py \
 backend/tests/test_graph_studio_review_closure_v0135200.py \
 backend/tests/test_graph_studio_cross_review_synthesis_v0135190.py \
 backend/tests/test_graph_studio_multi_reviewer_panels_v0135180.py \
 backend/tests/test_graph_studio_review_reproduction_v0135170.py \
 backend/tests/test_research_reproduction_replication_studio_v01290.py \
 backend/tests/test_graph_studio_revision_impact_v0135160.py \
 backend/tests/test_graph_studio_verification_artifacts_v0135150.py \
 backend/tests/test_graph_studio_review_audit_v0135140.py \
 backend/tests/test_graph_studio_review_resolution_v0135130.py \
 backend/tests/test_graph_studio_review_threads_v0135120.py \
 backend/tests/test_graph_studio_competing_paths_v0135110.py \
 backend/tests/test_graph_studio_provenance_path_analysis_v0135100.py \
 backend/tests/test_graph_studio_object_explorer_v013590.py \
 backend/tests/test_graph_studio_context_relationships_v0135853.py \
 backend/tests/test_graph_studio_incremental_interaction_v0135852.py
PYTHONPATH=backend python3 - <<'PY2'
import json,hashlib
from pathlib import Path
from app.main import app
root=Path('.');m=json.load(open(root/'build/sc-lab-release-manifest.json'))
assert m['releaseVersion']=='0.135.21.0';assert m['featureVersion']=='0.135.21.0';assert m['graphStudioReviewWorkspaceConsolidationVersion']=='0.135.21.0';assert m['v0135210RequiredRouteCount']==18
for sec in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,exp in m[sec].items():
  p=root/rel;assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==exp,rel
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)};patch={p for p in paths if p.startswith('/v1/graph-studio-review-workspace/v0135210')};assert len(patch)==18,len(patch)
print(f'PASS - manifest integrity ({len(m["wordpressCriticalFiles"])} WordPress/runtime + {len(m["backendCriticalFiles"])} backend files)')
print(f'PASS - FastAPI routes {len(paths)} total / {len(patch)} v0.135.21.0')
PY2
set +e
bash scripts/test_chromium_v0135210.sh
browser_rc=$?
set -e
if [[ $browser_rc -eq 77 ]]; then echo 'INFO: Chromium browser certification unavailable in this build environment; executable DOM/runtime certification remains passed.'; elif [[ $browser_rc -ne 0 ]]; then exit $browser_rc; fi
echo 'PASS - Lab v0.135.21.0 release gate'
