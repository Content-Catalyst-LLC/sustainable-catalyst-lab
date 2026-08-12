#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> Scientific Equation Builder + modeling regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_equation_builder_v0420.py \
  backend/tests/test_model_studio_v0420.py \
  backend/tests/test_model_studio_v0410.py \
  backend/tests/test_model_calibration_v0302.py \
  backend/tests/test_scientific_visualization_v0274.py \
  backend/tests/test_design_studies_v0301.py \
  backend/tests/test_model_registry_v0340.py \
  backend/tests/test_ensemble_uncertainty_v0341.py \
  backend/tests/test_surrogate_reduced_order_v0342.py

node tests/test-v0420.js
php tests/test-v0420.php
php tests/test-v0420-integrity-runtime.php
node --check assets/js/modules/scientific-visualization-engine-v0410.js
node --check assets/js/modules/model-studio-v0420.js
node --check assets/js/modules/numerical-visualization-studio.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-model-studio-v0420.php >/dev/null
php -l includes/class-sc-lab-python-compute-core-v0261.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/equation_builder.py backend/app/model_studio.py backend/app/main.py

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib, json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.42.0'
assert m['featureVersion']=='0.42.0'
assert m['platformVersion']=='1.0.0'
errors=[]
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
    for rel, expected in m.get(section,{}).items():
        p=Path(rel)
        if not p.is_file(): errors.append(f'missing {rel}'); continue
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected: errors.append(f'hash mismatch {rel}')
if errors:
    raise SystemExit('FAIL - release manifest integrity\n'+'\n'.join(errors[:40]))
print(f"PASS - release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress + {len(m['backendCriticalFiles'])} backend files)")
PY

echo "PASS - Lab v0.42.0 Scientific Equation Builder & Model Definition release gate"
