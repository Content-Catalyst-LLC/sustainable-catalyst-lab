#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> v0.72.0 Homepage 4D Biodiversity Modeling Preview regression gate"
node --check assets/js/modules/advanced-visualization-front-door-v0710.js
node tests/test-v0710.js
node tests/test-v0720.js
php tests/test-v0720.php
php tests/test-v0720-render.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-homepage-biodiversity-v0720.php >/dev/null
php -l includes/class-sc-lab-advanced-visualization-front-door-v0710.php >/dev/null

echo "==> focused backend compatibility"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_graph_studio_v0470.py \
  backend/tests/test_preregistration_v0700.py

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.72.0'
assert m['featureVersion']=='0.72.0'
assert m['platformVersion']=='1.0.0'
assert m['moduleCount']==149
assert m['routeAssertions']==394
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
    for rel,expected in m[section].items():
        p=Path(rel)
        if not p.is_file(): raise SystemExit(f'FAIL - missing manifest file {rel}')
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=expected: raise SystemExit(f'FAIL - manifest hash mismatch {rel}')
print('PASS - v0.72.0 release manifest integrity')
PY

echo "PASS - Lab v0.72.0 Homepage 4D Biodiversity Modeling Preview release gate"
