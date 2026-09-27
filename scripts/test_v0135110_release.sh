#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
node --check assets/js/modules/graph-studio-competing-paths-v0135110.js
node --check assets/js/modules/project-workspace-path-comparison-v0135110.js
node tests/test-v0135110.js
php tests/test-v0135110.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-graph-studio-competing-paths-v0135110.php >/dev/null
PYTHONPATH=backend python3 -m pytest -q backend/tests/test_graph_studio_competing_paths_v0135110.py backend/tests/test_graph_studio_provenance_path_analysis_v0135100.py backend/tests/test_graph_studio_object_explorer_v013590.py backend/tests/test_graph_studio_context_relationships_v0135853.py backend/tests/test_graph_studio_incremental_interaction_v0135852.py
PYTHONPATH=backend python3 - <<'PY2'
import json,hashlib
from pathlib import Path
from app.main import app
root=Path('.'); m=json.load(open(root/'build/sc-lab-release-manifest.json'))
assert m['releaseVersion']=='0.135.11.0'; assert m['graphStudioCompetingPathsVersion']=='0.135.11.0'; assert m['v0135110RequiredRouteCount']==10
for sec in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,exp in m[sec].items():
  p=root/rel; assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==exp,rel
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}; patch={p for p in paths if p.startswith('/v1/graph-studio-competing-paths/v0135110')}
assert len(patch)==10,len(patch)
print(f'PASS - manifest integrity ({len(m["wordpressCriticalFiles"])} WordPress/runtime + {len(m["backendCriticalFiles"])} backend files)')
print(f'PASS - FastAPI routes {len(paths)} total / {len(patch)} v0.135.11.0')
PY2
echo 'PASS - Lab v0.135.11.0 release gate'
