#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
[[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }
command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }
echo "==> v0.62.0 Scientific Claims, Evidence Matrix & Conclusion Traceability regression gate"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_scientific_claims_traceability_v0620.py backend/tests/test_scientific_study_lifecycle_v0610.py backend/tests/test_beta_field_diagnostics_v0601.py backend/tests/test_integrated_research_beta_v0600.py backend/tests/test_scientific_audit_v0590.py backend/tests/test_scientific_compute_hardening_v0580.py backend/tests/test_scientific_workflow_composer_v0570.py backend/tests/test_advanced_experimental_design_v0560.py backend/tests/test_data_transformations_v0550.py backend/tests/test_dynamic_systems_v0540.py backend/tests/test_correlated_uncertainty_v0530.py backend/tests/test_bayesian_inference_v0520.py backend/tests/test_advanced_statistical_modeling_v0510.py backend/tests/test_reproducible_model_package_v0500.py backend/tests/test_shared_model_handoff_v0490.py \
  backend/tests/test_probabilistic_analysis_v0480.py backend/tests/test_graph_studio_v0470.py backend/tests/test_response_surfaces_v0460.py \
  backend/tests/test_model_studio_v0460.py backend/tests/test_dynamic_systems_v0450.py backend/tests/test_model_studio_v0450.py \
  backend/tests/test_model_studio_v0440.py backend/tests/test_model_diagnostics_v0430.py backend/tests/test_model_studio_v0430.py \
  backend/tests/test_model_studio_v0420.py backend/tests/test_equation_builder_v0420.py backend/tests/test_model_studio_v0410.py \
  backend/tests/test_model_calibration_v0302.py backend/tests/test_scientific_visualization_v0274.py backend/tests/test_design_studies_v0301.py \
  backend/tests/test_model_registry_v0340.py backend/tests/test_ensemble_uncertainty_v0341.py backend/tests/test_surrogate_reduced_order_v0342.py backend/tests/test_scientific_audit_validation_dependency_v0590_r1.py backend/tests/test_security_privacy_hardening_v0391.py
node tests/test-v0480.js
node tests/test-v0550.js
node tests/test-v0560.js
node tests/test-v0570.js
node tests/test-v0580.js
node tests/test-v0590.js
node tests/test-v0600.js
node tests/test-v0601.js
node tests/test-v0610.js
node tests/test-v0620.js
php tests/test-v0620.php
php tests/test-v0620-integrity-runtime.php
node --check assets/js/modules/scientific-claims-v0620.js
node --check assets/js/modules/scientific-study-lifecycle-v0610.js
node --check assets/js/modules/contextual-navigation-v0483.js
node --check assets/js/modules/presentation-runtime-v0482.js
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-python-compute-core-v0261.php >/dev/null
php -l includes/class-sc-lab-scientific-claims-v0620.php >/dev/null
php -l includes/class-sc-lab-scientific-study-lifecycle-v0610.php >/dev/null
php -l templates/lab-app.php >/dev/null
"$PYTHON_BIN" -m py_compile backend/app/scientific_claims_traceability_v0620.py backend/app/scientific_study_lifecycle_v0610.py backend/app/beta_field_diagnostics_v0601.py backend/app/integrated_research_beta_v0600.py backend/app/scientific_audit_v0590.py backend/app/scientific_compute_hardening.py backend/app/scientific_workflow_composer.py backend/app/config.py backend/app/main.py
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
text=Path('backend/app/main.py').read_text()
for route in (
 '/v1/scientific-claims/v0620/health','/v1/scientific-claims/v0620/policies','/v1/scientific-claims/v0620/normalize-claim','/v1/scientific-claims/v0620/review-claim',
 '/v1/scientific-claims/v0620/normalize-conclusion','/v1/scientific-claims/v0620/review-conclusion','/v1/scientific-claims/v0620/evaluate','/v1/scientific-claims/v0620/packet','/v1/scientific-claims/v0620/verify',
 '/v1/scientific-studies/v0610/health','/v1/scientific-studies/v0610/evaluate','/v1/beta-diagnostics/v0601/health','/v1/integrated-research/v0600/health'):
    assert route in text, f'missing FastAPI route: {route}'
print('PASS - v0.62.0 scientific claims + inherited study/beta routes wired')
PY
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib,json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.62.0';assert m['featureVersion']=='0.62.0';assert m['platformVersion']=='1.0.0'
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
echo "PASS - Lab v0.62.0 Scientific Claims, Evidence Matrix & Conclusion Traceability release gate"
