#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }
echo "==> v0.51.0 Advanced Statistical Modeling & Generalized Regression regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_advanced_statistical_modeling_v0510.py backend/tests/test_reproducible_model_package_v0500.py backend/tests/test_shared_model_handoff_v0490.py \
  backend/tests/test_probabilistic_analysis_v0480.py backend/tests/test_graph_studio_v0470.py backend/tests/test_response_surfaces_v0460.py \
  backend/tests/test_model_studio_v0460.py backend/tests/test_dynamic_systems_v0450.py backend/tests/test_model_studio_v0450.py \
  backend/tests/test_model_studio_v0440.py backend/tests/test_model_diagnostics_v0430.py backend/tests/test_model_studio_v0430.py \
  backend/tests/test_model_studio_v0420.py backend/tests/test_equation_builder_v0420.py backend/tests/test_model_studio_v0410.py \
  backend/tests/test_model_calibration_v0302.py backend/tests/test_scientific_visualization_v0274.py backend/tests/test_design_studies_v0301.py \
  backend/tests/test_model_registry_v0340.py backend/tests/test_ensemble_uncertainty_v0341.py backend/tests/test_surrogate_reduced_order_v0342.py
node tests/test-v0510.js
php tests/test-v0510.php
php tests/test-v0510-integrity-runtime.php
node --check assets/js/modules/advanced-statistical-modeling-v0510.js
node --check assets/js/modules/reproducible-model-package-v0500.js
node --check assets/js/modules/shared-model-handoff-v0490.js
node --check assets/js/modules/contextual-navigation-v0483.js
node --check assets/js/modules/presentation-runtime-v0482.js
node --check assets/js/sc-lab-app.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-python-compute-core-v0261.php >/dev/null
php -l includes/class-sc-lab-advanced-statistical-modeling-v0510.php >/dev/null
php -l includes/class-sc-lab-reproducible-model-package-v0500.php >/dev/null
php -l includes/class-sc-lab-shared-model-handoff-v0490.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/advanced_statistical_modeling.py backend/app/reproducible_model_package.py backend/app/shared_model_handoff.py backend/app/probabilistic_analysis.py backend/app/graph_studio.py backend/app/model_studio.py backend/app/main.py
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
text=Path('backend/app/main.py').read_text()
for route in ('/v1/model-studio/statistics/health','/v1/model-studio/statistics/policies','/v1/model-studio/statistics/normalize','/v1/model-studio/statistics/fit','/v1/model-studio/statistics/predict','/v1/model-studio/statistics/cross-validate','/v1/model-studio/statistics/compare'):
    assert route in text, f'missing FastAPI route: {route}'
print('PASS - v0.51.0 FastAPI statistical-modeling routes wired')
PY
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.51.0';assert m['featureVersion']=='0.51.0';assert m['platformVersion']=='1.0.0'
errors=[]
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m.get(section,{}).items():
  p=Path(rel)
  if not p.is_file(): errors.append(f'missing {rel}');continue
  actual=hashlib.sha256(p.read_bytes()).hexdigest()
  if actual!=expected: errors.append(f'hash mismatch {rel}')
if errors: raise SystemExit('FAIL - release manifest integrity\n'+'\n'.join(errors[:40]))
print(f"PASS - release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY
echo "PASS - Lab v0.51.0 Advanced Statistical Modeling & Generalized Regression release gate"
