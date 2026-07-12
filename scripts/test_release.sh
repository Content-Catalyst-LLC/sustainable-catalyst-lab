#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Testing Sustainable Catalyst Lab v0.9.4"
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
grep -q 'Version: 0.9.4' "$ROOT/sustainable-catalyst-lab.php"
grep -q "define('SC_LAB_VERSION', '0.9.4')" "$ROOT/sustainable-catalyst-lab.php"
grep -q 'type: worker' "$ROOT/render.yaml"
grep -q 'type: keyvalue' "$ROOT/render.yaml"
echo "Release tests passed."
