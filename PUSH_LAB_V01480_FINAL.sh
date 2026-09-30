#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sustainable-catalyst-lab-v0.148.0-repository.zip}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
unzip -q "$ZIP" -d "$WORK"
SRC="$WORK/sustainable-catalyst-lab-main"
TARGET="${SC_LAB_REPO_DIR:-$HOME/Downloads/sustainable-catalyst-lab}"
if [ ! -d "$TARGET/.git" ]; then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$TARGET"; fi
cd "$TARGET"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$SRC/" "$TARGET/"
git add -A
if ! git diff --cached --quiet; then git commit -m 'Release Lab v0.148.0 — Multimodal Scientific Experiment Workspace'; fi
git push origin main
if git rev-parse v0.148.0 >/dev/null 2>&1; then git tag -d v0.148.0; git push origin :refs/tags/v0.148.0 || true; fi
git tag -a v0.148.0 -m 'Lab v0.148.0 — Multimodal Scientific Experiment Workspace'
git push origin v0.148.0
echo 'PASS - GitHub main and v0.148.0 tag pushed.'
