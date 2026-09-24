#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }

echo "==> v0.48.2 UI runtime responsiveness + event loop repair regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_probabilistic_analysis_v0480.py \
  backend/tests/test_graph_studio_v0470.py \
  backend/tests/test_response_surfaces_v0460.py \
  backend/tests/test_model_studio_v0460.py \
  backend/tests/test_dynamic_systems_v0450.py \
  backend/tests/test_model_studio_v0450.py \
  backend/tests/test_model_studio_v0440.py \
  backend/tests/test_model_diagnostics_v0430.py \
  backend/tests/test_model_studio_v0430.py \
  backend/tests/test_model_studio_v0420.py \
  backend/tests/test_equation_builder_v0420.py \
  backend/tests/test_model_studio_v0410.py \
  backend/tests/test_model_calibration_v0302.py \
  backend/tests/test_scientific_visualization_v0274.py \
  backend/tests/test_design_studies_v0301.py \
  backend/tests/test_model_registry_v0340.py \
  backend/tests/test_ensemble_uncertainty_v0341.py \
  backend/tests/test_surrogate_reduced_order_v0342.py

node tests/test-v0482.js
php tests/test-v0482.php
php tests/test-v0482-integrity-runtime.php
node --check assets/js/modules/presentation-runtime-v0482.js
node --check assets/js/modules/interface-reorganization-v0470.js
node --check assets/js/modules/graph-studio-v0470.js
node --check assets/js/modules/probabilistic-analysis-v0480.js
node --check assets/js/sc-lab-app.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-presentation-repair-v0481.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/probabilistic_analysis.py backend/app/graph_studio.py backend/app/response_surfaces.py backend/app/dynamic_systems.py backend/app/model_diagnostics.py backend/app/equation_builder.py backend/app/model_studio.py backend/app/main.py

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib, json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.48.2'
assert m['featureVersion']=='0.48.2'
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
print(f"PASS - release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY

echo "PASS - Lab v0.48.2 UI Runtime Responsiveness & Event Loop Repair release gate"
