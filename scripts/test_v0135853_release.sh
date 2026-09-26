#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
node --check assets/js/modules/graph-studio-native-provenance-v013585.js
node tests/test-v0135853.js
node tests/test-v0135852.js
php tests/test-v0135853.php
php tests/test-v0135852.php
php tests/test-v0135851.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-graph-studio-context-relationships-v0135853.php >/dev/null
python3 -m pytest -q backend/tests/test_graph_studio_context_relationships_v0135853.py backend/tests/test_graph_studio_incremental_interaction_v0135852.py tests/test_graph_studio_native_provenance_v013585.py tests/test_graph_studio_provenance_authority_v0135851.py
python3 - <<'PY2'
import json,hashlib
from pathlib import Path
from backend.app.main import app
root=Path('.')
m=json.load(open(root/'build/sc-lab-release-manifest.json'))
assert m['releaseVersion']=='0.135.8.5.3'
assert m['graphStudioContextRelationshipsVersion']=='0.135.8.5.3'
for sec in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,exp in m[sec].items():
  p=root/rel; assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==exp,rel
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
patch={p for p in paths if p.startswith('/v1/graph-studio-context-relationships/v0135853')}
assert len(patch)==8,len(patch)
print(f'PASS - manifest integrity ({len(m["wordpressCriticalFiles"])} WordPress/runtime + {len(m["backendCriticalFiles"])} backend files)')
print(f'PASS - FastAPI routes {len(paths)} total / {len(patch)} v0.135.8.5.3')
PY2
echo 'PASS - Lab v0.135.8.5.3 release gate'
