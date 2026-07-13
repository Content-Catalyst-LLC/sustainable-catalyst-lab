#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Testing Sustainable Catalyst Lab v0.13.0"
find "$ROOT" -name '*.php' -print0 | xargs -0 -n1 php -l >/dev/null
find "$ROOT/assets/js" -name '*.js' -print0 | xargs -0 -n1 node --check
php "$ROOT/tests/test-php.php"
php "$ROOT/tests/test-render.php"
node "$ROOT/tests/test-js.js"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
if [[ -z "$PYTHON_BIN" ]]; then echo "Python 3 is required for backend tests." >&2; exit 1; fi
PYTHONPATH="$ROOT/backend" "$PYTHON_BIN" -m pytest "$ROOT/backend/tests" -q
if grep -q "preexec_fn=" "$ROOT/backend/app/executor.py"; then echo "Thread-unsafe preexec_fn must not be used." >&2; exit 1; fi
"$ROOT/tests/test-generated-code.sh"
grep -q 'Version: 0.13.0' "$ROOT/sustainable-catalyst-lab.php"
grep -q "define('SC_LAB_VERSION', '0.13.0')" "$ROOT/sustainable-catalyst-lab.php"
grep -q 'type: worker' "$ROOT/render.yaml"
grep -q 'type: keyvalue' "$ROOT/render.yaml"

echo "Running Lab v0.13.0 civil and infrastructure validation..."
node tests/test-v0120.js
php tests/test-v0120.php
PYTHONPATH="$PWD/backend${PYTHONPATH:+:$PYTHONPATH}" "${PYTHON_BIN:-python3}" -m pytest backend/tests/test_civil_infrastructure.py -q


echo "Running Lab v0.13.0 architecture and building-performance validation..."
node tests/test-v0130.js
php tests/test-v0130.php
PYTHONPATH="$PWD/backend${PYTHONPATH:+:$PYTHONPATH}" "${PYTHON_BIN:-python3}" -m pytest backend/tests/test_architecture_building.py -q

echo "Release tests passed."

# Lab v0.13.0 report-composer, accessibility, migration, and restore checks.
REPO_ROOT_V095="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
node "$REPO_ROOT_V095/tests/test-v095.js"

# Lab v0.13.0 electrical, electronics, embedded, interface, and hardware validation checks.
REPO_ROOT_V0100="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
node "$REPO_ROOT_V0100/tests/test-v0100.js"

# Lab v0.13.0 mechanical and thermal engineering validation checks.
REPO_ROOT_V0110="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
node "$REPO_ROOT_V0110/tests/test-v0110.js"
php "$REPO_ROOT_V0110/tests/test-v0110.php"
PYTHONPATH="$REPO_ROOT_V0110/backend${PYTHONPATH:+:$PYTHONPATH}" "${PYTHON_BIN:-python3}" -m pytest "$REPO_ROOT_V0110/backend/tests/test_mechanical_thermal.py" -q

