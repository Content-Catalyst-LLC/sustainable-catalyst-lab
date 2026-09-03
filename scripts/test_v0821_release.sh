#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"; [[ -n "$PYTHON_BIN" ]] || { echo "FAIL - Python 3 required" >&2; exit 1; }
command -v node >/dev/null || { echo "FAIL - Node required" >&2; exit 1; }; command -v php >/dev/null || { echo "FAIL - PHP required" >&2; exit 1; }
echo "==> v0.82.1 Canonical Release Identity & Release Console Repair"
node --check assets/js/modules/release-console-v0821.js
node tests/test-v0821.js
php tests/test-v0821.php
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/sc-lab-release-bootstrap.php >/dev/null
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-runtime-repair-v0263.php >/dev/null
php -l includes/class-sc-lab-feeds.php >/dev/null
php -l templates/lab-app.php >/dev/null
bash -n scripts/test_release_current.sh
[[ $(wc -l < scripts/test_release_current.sh) -eq 410 ]] || { echo "FAIL - established 410-line current-release harness changed" >&2; exit 1; }
echo "==> governed visualization/backend compatibility (unchanged v0.82 engine line)"
PYTHONPATH="$ROOT/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py backend/tests/test_annotation_measurement_markup_v0810.py backend/tests/test_spatial_geospatial_raster_v0800.py backend/tests/test_linked_views_v0790.py backend/tests/test_time_parameter_space_v0780.py backend/tests/test_scientific_scene_v0770.py backend/tests/test_large_data_visualization_v0760.py backend/tests/test_scientific_data_binding_v0750.py backend/tests/test_visualization_engine_v0740.py backend/tests/test_visualization_engine_v0730.py backend/tests/test_data_transformations_v0550.py backend/tests/test_graph_studio_v0470.py backend/tests/test_reproducible_model_package_v0500.py backend/tests/test_scientific_workflow_composer_v0570.py backend/tests/test_model_studio_v0460.py backend/tests/test_preregistration_v0700.py
echo "==> release manifest integrity"
"$PYTHON_BIN" - <<'PY2'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.82.1' and m['featureVersion']=='0.82.1' and m['platformVersion']=='1.0.0'
assert m['repairRelease']=='0.82.1' and m['repairLine']=='canonical-release-identity-release-console'
pat=re.compile(r'(^|/)(?:\.pytest_cache|__pycache__|\.venv[^/]*)($|/)|^backend/data/|^data/')
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  if pat.search(rel): raise SystemExit('FAIL - mutable runtime/cache path in manifest: '+rel)
  p=Path(rel)
  if not p.is_file(): raise SystemExit('FAIL - missing manifest file '+rel)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise SystemExit('FAIL - manifest hash mismatch '+rel)
print(f"PASS - v0.82.1 release manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress/source + {len(m['backendCriticalFiles'])} backend files)")
PY2
echo "==> canonical release identity source contract"
"$PYTHON_BIN" - <<'PY2'
from pathlib import Path
import json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
main=Path('sustainable-catalyst-lab.php').read_text()
tpl=Path('templates/lab-app.php').read_text()
js=Path('assets/js/modules/release-console-v0821.js').read_text()
header=re.search(r'^ \* Version: ([0-9.]+)$',main,re.M).group(1)
if not (m['releaseVersion']==header=='0.82.1'): raise SystemExit('FAIL - manifest/plugin header release mismatch')
if 'runtime?.releaseVersion' not in js: raise SystemExit('FAIL - Release Console is not runtime-release driven')
if "SC_LAB_RELEASE_VERSION" not in tpl or 'data-sc-lab-release-console' not in tpl: raise SystemExit('FAIL - server Release Console identity missing')
if 'SC_LAB_VERSION' in re.search(r'<section class="sc-lab-release-console-v0821".*?</section>',tpl,re.S).group(0): raise SystemExit('FAIL - Release Console references legacy SC_LAB_VERSION')
print('PASS - manifest = plugin header = runtime release = Release Console source contract')
PY2
echo "PASS - Lab v0.82.1 Canonical Release Identity & Release Console Repair release gate"
