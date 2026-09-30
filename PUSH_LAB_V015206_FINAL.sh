#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sustainable-catalyst-lab-v0.152.0.6-repository.zip}"
TARGET="${2:-$HOME/Downloads/sustainable-catalyst-lab}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-lab-main"
mkdir -p "$TARGET"
if [ ! -d "$TARGET/.git" ]; then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$TARGET"; fi
rsync -a --delete --exclude='.git/' "$SRC/" "$TARGET/"
cd "$TARGET"
git add -A
git commit -m "Release Lab v0.152.0.6 — Safe-Boot Stabilization & Canonical Release Presentation" || true
git push origin main
git tag -d v0.152.0.6 2>/dev/null || true
git tag -a v0.152.0.6 -m "Lab v0.152.0.6 — Safe-Boot Stabilization & Canonical Release Presentation"
git push origin v0.152.0.6
echo 'PASS - pushed Lab v0.152.0.6'
