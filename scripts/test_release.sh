#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Testing Sustainable Catalyst Lab v0.3.0"
find "$ROOT" -name '*.php' -print0 | xargs -0 -n1 php -l >/dev/null
find "$ROOT/assets/js" -name '*.js' -print0 | xargs -0 -n1 node --check
php "$ROOT/tests/test-php.php"
php "$ROOT/tests/test-render.php"
node "$ROOT/tests/test-js.js"
grep -q 'Version: 0.3.0' "$ROOT/sustainable-catalyst-lab.php"
grep -q "define('SC_LAB_VERSION', '0.3.0')" "$ROOT/sustainable-catalyst-lab.php"
echo "Release tests passed."
