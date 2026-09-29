#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-$ROOT/dist-v0.140.0}"
rm -rf "$OUT"; mkdir -p "$OUT"
"$ROOT/VALIDATE_LAB_V01400.sh" "$ROOT"
repo_stage="$(mktemp -d)"; plugin_stage="$(mktemp -d)"; backend_stage="$(mktemp -d)"
trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.140.0/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.140.0/' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete \
  --exclude='.git/' --exclude='backend/' --exclude='tests/' --exclude='scripts/' --exclude='sdk/' --exclude='examples/' --exclude='docs/' \
  --exclude='dist-v0.140.0/' --exclude='*.zip' \
  "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.140.0/backend/"
(
  cd "$repo_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.140.0-repository.zip" sustainable-catalyst-lab-main
  cd "$plugin_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.140.0-wordpress.zip" sustainable-catalyst-lab
  cd "$backend_stage" && zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.140.0.zip" sustainable-catalyst-lab-backend-v0.140.0
)
cp "$ROOT/DEPLOY_LAB_V01400_CONTABO.sh" "$OUT/"
cp "$ROOT/PUSH_LAB_V01400_FINAL.sh" "$OUT/"
cp "$ROOT/VALIDATE_LAB_V01400.sh" "$OUT/"
cp "$ROOT/DEPLOY_LAB_BACKEND_v0.140.0.md" "$OUT/"
cp "$ROOT/RELEASE_NOTES_0.140.0_SCIENTIFIC_RESEARCH_OPERATING_SYSTEM.md" "$OUT/"
(
  cd "$OUT"
  shasum -a 256 sustainable-catalyst-lab-v0.140.0-repository.zip sustainable-catalyst-lab-v0.140.0-wordpress.zip sustainable-catalyst-lab-backend-v0.140.0.zip > SHA256SUMS.txt
  zip -qr sustainable-catalyst-lab-v0.140.0-release-bundle.zip \
    sustainable-catalyst-lab-v0.140.0-repository.zip \
    sustainable-catalyst-lab-v0.140.0-wordpress.zip \
    sustainable-catalyst-lab-backend-v0.140.0.zip \
    DEPLOY_LAB_V01400_CONTABO.sh PUSH_LAB_V01400_FINAL.sh VALIDATE_LAB_V01400.sh \
    DEPLOY_LAB_BACKEND_v0.140.0.md RELEASE_NOTES_0.140.0_SCIENTIFIC_RESEARCH_OPERATING_SYSTEM.md SHA256SUMS.txt
)
echo "PASS - Lab v0.140.0 artifacts packaged in $OUT"
