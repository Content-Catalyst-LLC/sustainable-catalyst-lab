#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
node "$ROOT/tests/export-code-samples.js" "$TMP"
for f in kinetic.py kinetic.R kinetic.jl kinetic.js kinetic.ts kinetic.sql kinetic.c kinetic.cpp kinetic.f90 kinetic.rs kinetic.go kinetic.hs kinetic.ipynb; do test -s "$TMP/$f"; done
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
if [[ -z "$PYTHON_BIN" ]]; then echo "Python 3 is required for generated-code tests." >&2; exit 1; fi
"$PYTHON_BIN" "$TMP/kinetic.py" | grep -q "125"
node --check "$TMP/kinetic.js"
tsc --noEmit --target ES2020 --module commonjs "$TMP/kinetic.ts"
gcc -std=c11 "$TMP/kinetic.c" -lm -o "$TMP/kinetic-c" && "$TMP/kinetic-c" | grep -q "125"
g++ -std=c++20 "$TMP/kinetic.cpp" -o "$TMP/kinetic-cpp" && "$TMP/kinetic-cpp" | grep -q "125"
gfortran "$TMP/kinetic.f90" -o "$TMP/kinetic-fortran" && "$TMP/kinetic-fortran" | grep -q "125"
mkdir "$TMP/go-run"; cp "$TMP/kinetic.go" "$TMP/go-run/main.go"; (cd "$TMP/go-run" && go mod init example.com/sc-lab-test >/dev/null 2>&1 && go run .) | grep -q "125"
grep -q "fn main()" "$TMP/kinetic.rs"
grep -q "calculate <- function" "$TMP/kinetic.R"
grep -q "function calculate" "$TMP/kinetic.jl"
grep -q "module Main" "$TMP/kinetic.hs"
grep -q "WITH inputs AS" "$TMP/kinetic.sql"
echo "Generated-code tests passed."
