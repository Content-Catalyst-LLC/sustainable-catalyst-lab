#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"


# SC_LAB_CURRENT_TOOLCHAIN_SELECTION
PYTHON_BIN="${PYTHON_BIN:-${SC_LAB_PYTHON_BIN:-$HOME/Downloads/.sc-lab-v0200-venv/bin/python}}"
SC_LAB_PYTHON_BIN="${SC_LAB_PYTHON_BIN:-$PYTHON_BIN}"
NODE_TOOLS_BIN="${SC_LAB_NODE_TOOLS_BIN:-$HOME/Downloads/.sc-lab-node-tools/node_modules/.bin}"

export PYTHON_BIN
export SC_LAB_PYTHON_BIN
export SC_LAB_NODE_TOOLS_BIN

if [[ -d "$NODE_TOOLS_BIN" ]]; then
  export PATH="$NODE_TOOLS_BIN:$PATH"
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "FAIL: Lab Python interpreter not found at $PYTHON_BIN" >&2
  exit 1
fi

if ! "$PYTHON_BIN" -m pytest --version >/dev/null 2>&1; then
  echo "FAIL: pytest is unavailable in $PYTHON_BIN" >&2
  exit 1
fi

if ! command -v tsc >/dev/null 2>&1; then
  echo "FAIL: TypeScript compiler not found at $NODE_TOOLS_BIN/tsc" >&2
  exit 1
fi

# SC_LAB_CURRENT_TYPESCRIPT_SELECTION
NODE_TOOLS_BIN="${SC_LAB_NODE_TOOLS_BIN:-$HOME/Downloads/.sc-lab-node-tools/node_modules/.bin}"

if [[ -d "$NODE_TOOLS_BIN" ]]; then
  export PATH="$NODE_TOOLS_BIN:$PATH"
fi

if ! command -v tsc >/dev/null 2>&1; then
  echo "FAIL: TypeScript compiler not found." >&2
  echo "Expected Lab toolchain:" >&2
  echo "  $NODE_TOOLS_BIN/tsc" >&2
  exit 1
fi

# SC_LAB_CURRENT_PYTHON_SELECTION
PYTHON_BIN="${SC_LAB_PYTHON_BIN:-}"

if [[ -z "$PYTHON_BIN" ]]; then
  for candidate in "$HOME/Downloads/.sc-lab-v0200-venv/bin/python" "$ROOT/.venv/bin/python" "$(command -v python3 2>/dev/null || true)"; do
    if [[ -n "$candidate" && -x "$candidate" ]]; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  echo "FAIL: No usable Python interpreter found." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -m pytest --version >/dev/null 2>&1; then
  echo "FAIL: pytest is unavailable in $PYTHON_BIN" >&2
  echo "Expected Lab environment: $HOME/Downloads/.sc-lab-v0200-venv/bin/python" >&2
  exit 1
fi

export SC_LAB_PYTHON_BIN="$PYTHON_BIN"
export PYTHON_BIN
PYTHON_SHIM_DIR="$(mktemp -d "${TMPDIR:-/tmp}/sc-lab-python-shims.XXXXXX")"

for name in python python3 python3.12 python3.13 python3.14; do
  ln -sf "$PYTHON_BIN" "$PYTHON_SHIM_DIR/$name"
done

cat > "$PYTHON_SHIM_DIR/pytest" <<'EOF'
#!/usr/bin/env bash
exec "$SC_LAB_PYTHON_BIN" -m pytest "$@"
EOF

cat > "$PYTHON_SHIM_DIR/py.test" <<'EOF'
#!/usr/bin/env bash
exec "$SC_LAB_PYTHON_BIN" -m pytest "$@"
EOF

chmod +x "$PYTHON_SHIM_DIR/pytest" "$PYTHON_SHIM_DIR/py.test"
export PATH="$PYTHON_SHIM_DIR:$PATH"

CURRENT_VERSION="$(
  "$PYTHON_BIN" - sustainable-catalyst-lab.php <<'PY'
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(
    r"^\s*\*\s*Version:\s*([0-9]+\.[0-9]+\.[0-9]+)",
    text,
    re.M,
)
if not match:
    raise SystemExit("Plugin version marker missing.")
print(match.group(1))
PY
)"

TMP_SUITE="$ROOT/scripts/.test_release_current_compat.sh"
TMP_PHP="$ROOT/tests/.test-php-current-compat.php"
TMP_RENDER="$ROOT/tests/.test-render-current-compat.php"
TMP_MICRO="$ROOT/tests/.test-v0200-current-compat.php"
TMP_ENGINEERING="$ROOT/tests/.test-engineering-current-compat.php"

cleanup() {
  rm -f \
    "$TMP_SUITE" \
    "$TMP_PHP" \
    "$TMP_RENDER" \
    "$TMP_MICRO" \
    "$TMP_ENGINEERING"

  rm -rf "${PYTHON_SHIM_DIR:-}"
}
trap cleanup EXIT

"$PYTHON_BIN" - \
  "$CURRENT_VERSION" \
  "$ROOT/scripts/test_release.sh" \
  "$TMP_SUITE" \
  "$ROOT/tests/test-php.php" \
  "$TMP_PHP" \
  "$ROOT/tests/test-render.php" \
  "$TMP_RENDER" \
  "$ROOT/tests/test-v0200.php" \
  "$TMP_MICRO" \
  "$ROOT/tests/test-engineering-interface-v0200.php" \
  "$TMP_ENGINEERING" <<'PY'
from pathlib import Path
import re
import sys

(
    version,
    suite_source,
    suite_target,
    php_source,
    php_target,
    render_source,
    render_target,
    micro_source,
    micro_target,
    engineering_source,
    engineering_target,
) = sys.argv[1:]

suite_source = Path(suite_source)
suite_target = Path(suite_target)
php_source = Path(php_source)
php_target = Path(php_target)
render_source = Path(render_source)
render_target = Path(render_target)
micro_source = Path(micro_source)
micro_target = Path(micro_target)
engineering_source = Path(engineering_source)
engineering_target = Path(engineering_target)

suite = suite_source.read_text(encoding="utf-8")
suite = re.sub(
    r'echo "Testing Sustainable Catalyst Lab v[^"]+"',
    f'echo "Testing Sustainable Catalyst Lab v{version}"',
    suite,
    count=1,
)
suite = re.sub(
    r"grep -q 'Version: [0-9.]+'",
    f"grep -q 'Version: {version}'",
    suite,
    count=1,
)
suite = re.sub(
    r"grep -q \"define\('SC_LAB_VERSION', '[0-9.]+'\)\"",
    (
        "grep -q \"define('SC_LAB_VERSION', "
        f"'{version}')\""
    ),
    suite,
    count=1,
)
suite = suite.replace(
    'php "$ROOT/tests/test-php.php"',
    'php "$ROOT/tests/.test-php-current-compat.php"',
    1,
)
suite = suite.replace(
    'php "$ROOT/tests/test-render.php"',
    'php "$ROOT/tests/.test-render-current-compat.php"',
    1,
)
suite = suite.replace(
    'php tests/test-v0200.php',
    'php tests/.test-v0200-current-compat.php',
    1,
)
suite = suite.replace(
    'php tests/test-engineering-interface-v0200.php',
    'php tests/.test-engineering-current-compat.php',
    1,
)
suite_target.write_text(suite, encoding="utf-8")
suite_target.chmod(0o755)

php_test = php_source.read_text(encoding="utf-8")
php_test = php_test.replace(
    "'Version: 0.20.0'",
    f"'Version: {version}'",
    1,
)
php_test = php_test.replace(
    "\"define('SC_LAB_VERSION', '0.20.0')\"",
    f"\"define('SC_LAB_VERSION', '{version}')\"",
    1,
)
php_target.write_text(php_test, encoding="utf-8")

render_test = render_source.read_text(encoding="utf-8")
render_test = render_test.replace(
    "define('SC_LAB_VERSION', '0.20.0');",
    f"define('SC_LAB_VERSION', '{version}');",
    1,
)
render_test = render_test.replace(
    "strpos($html, 'v0.20.0')",
    f"strpos($html, 'v{version}')",
    1,
)
render_target.write_text(render_test, encoding="utf-8")

micro_test = micro_source.read_text(encoding="utf-8")
micro_test = micro_test.replace(
    "preg_match('/Version:\\s*0\\.20\\.0/', $main)",
    (
        "preg_match('/Version:\\s*"
        + version.replace(".", "\\.")
        + "/', $main)"
    ),
    1,
)
micro_target.write_text(micro_test, encoding="utf-8")

engineering_test = engineering_source.read_text(
    encoding="utf-8"
)

repair_block = (
    "$repair_js = file_get_contents(\n"
    "    $root\n"
    "    . '/assets/js/modules/'\n"
    "    . 'engineering-interface-repair-v0200.js'\n"
    ");\n"
)

runtime_block = repair_block + (
    "$civil_runtime = file_get_contents(\n"
    "    $root\n"
    "    . '/assets/js/modules/'\n"
    "    . 'civil-infrastructure-runtime-v0200.js'\n"
    ");\n"
)

if repair_block not in engineering_test:
    raise SystemExit(
        "Could not locate the engineering repair source block."
    )

engineering_test = engineering_test.replace(
    repair_block,
    runtime_block,
    1,
)

civil_initializer = (
    "engineering_repair_assert(\n"
    "    strpos($repair_js, "
    "'Lab.CivilInfrastructureLab') !== false,\n"
    "    'Civil initializer'\n"
    ");"
)

civil_initializer_replacement = (
    "engineering_repair_assert(\n"
    "    strpos($repair_js, "
    "'Lab.CivilInfrastructureLab') === false,\n"
    "    'Civil delegated from engineering repair'\n"
    ");\n"
    "engineering_repair_assert(\n"
    "    strpos($civil_runtime, "
    "'Lab.CivilInfrastructureLab') !== false,\n"
    "    'Authoritative Civil initializer'\n"
    ");"
)

if civil_initializer not in engineering_test:
    raise SystemExit(
        "Could not locate the stale Civil initializer assertion."
    )

engineering_test = engineering_test.replace(
    civil_initializer,
    civil_initializer_replacement,
    1,
)

civil_guard = (
    "engineering_repair_assert(\n"
    "    strpos($repair_js, "
    "\"minimumVersion: '0.15.0'\") !== false,\n"
    "    'Civil repaired-interface version guard'\n"
    ");"
)

civil_guard_replacement = (
    "engineering_repair_assert(\n"
    "    strpos($civil_runtime, "
    "\"MINIMUM_MODULE_VERSION = '0.15.0'\") "
    "!== false,\n"
    "    'Authoritative Civil version guard'\n"
    ");"
)

if civil_guard not in engineering_test:
    raise SystemExit(
        "Could not locate the stale Civil version guard."
    )

engineering_test = engineering_test.replace(
    civil_guard,
    civil_guard_replacement,
    1,
)

engineering_target.write_text(
    engineering_test,
    encoding="utf-8",
)
PY

bash "$TMP_SUITE"

node tests/test-v0210.js
php tests/test-v0210.php
node tests/test-v0211.js
php tests/test-v0211.php


node tests/test-v0212.js
php tests/test-v0212.php


node tests/test-v0213.js
php tests/test-v0213.php


node tests/test-v0220.js
php tests/test-v0220.php


node tests/test-v0221.js
php tests/test-v0221.php

node tests/test-v0222.js
php tests/test-v0222.php

node tests/test-v0223.js
php tests/test-v0223.php

echo "Current release validation passed for v$CURRENT_VERSION."
