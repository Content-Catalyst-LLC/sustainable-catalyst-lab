#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "==> v0.70.0 R1 Repository Runtime-Health Scope, Plugin Identity & Route-Alias Repair regression gate"
./scripts/test_v0700_release.sh
php tests/test-v0700-r1.php
php tests/test-v0700-r1-repository-integrity.php
php tests/test-v0700-r1-wordpress-integrity.php
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php -l tests/test-v0700-r1.php >/dev/null
php -l tests/test-v0700-r1-repository-integrity.php >/dev/null
php -l tests/test-v0700-r1-wordpress-integrity.php >/dev/null
"${PYTHON_BIN:-python3}" - <<'PY'
from pathlib import Path
import json
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.70.0'
assert m['featureVersion']=='0.70.0'
assert m['platformVersion']=='1.0.0'
assert m['repairLine']=='R1'
assert m['repairRelease']=='0.70.0-r1'
assert m['moduleCount']==147
assert m['routeAssertions']==393
print('PASS - v0.70.0 R1 release identity and inherited scientific assertion line')
PY
echo "PASS - Lab v0.70.0 R1 Repository Runtime-Health Scope, Plugin Identity & Route-Alias Repair release gate"
