#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }
echo "==> v0.71.0 Advanced Scientific Visualization Front Door & 4D Projection regression gate"
node --check assets/js/modules/advanced-visualization-front-door-v0710.js
node --check assets/js/sc-lab-production-stability-v0266.js
node tests/test-v0710.js
php tests/test-v0710.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-advanced-visualization-front-door-v0710.php >/dev/null
php -l includes/class-sc-lab-production-stability-v0266.php >/dev/null
php -l templates/lab-app.php >/dev/null
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_preregistration_v0700.py \
  backend/tests/test_scientific_theory_v0690.py \
  backend/tests/test_hierarchical_modeling_v0680.py \
  backend/tests/test_causal_inference_v0670.py \
  backend/tests/test_graph_studio_v0470.py
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.71.0'
assert m['featureVersion']=='0.71.0'
assert m['platformVersion']=='1.0.0'
assert m['moduleCount']==148
assert m['routeAssertions']==393
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
    for rel,expected in m[section].items():
        p=Path(rel)
        if not p.is_file(): raise SystemExit(f'FAIL - missing manifest file {rel}')
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=expected: raise SystemExit(f'FAIL - manifest hash mismatch {rel}')
print('PASS - v0.71.0 release manifest integrity')
PY
echo "PASS - Lab v0.71.0 Advanced Scientific Visualization Front Door & 4D Projection release gate"
