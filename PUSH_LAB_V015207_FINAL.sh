#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sustainable-catalyst-lab-v0.152.0.7-repository.zip}"
TARGET="${2:-$HOME/Downloads/sustainable-catalyst-lab}"
rm -rf "$TARGET.__v015207_stage"
mkdir -p "$TARGET.__v015207_stage"
unzip -q "$ZIP" -d "$TARGET.__v015207_stage"
SRC="$TARGET.__v015207_stage/sustainable-catalyst-lab-main"
if [ ! -d "$TARGET/.git" ]; then
  git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$TARGET"
fi
rsync -a --delete --exclude='.git/' "$SRC/" "$TARGET/"
cd "$TARGET"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Release Lab v0.152.0.7 — Interactive 4D Scientific Front Door & Compute Runtime Reconnection"
fi
git push origin main
if git rev-parse -q --verify refs/tags/v0.152.0.7 >/dev/null; then git tag -d v0.152.0.7; fi
git tag -a v0.152.0.7 -m "Lab v0.152.0.7"
git push origin refs/tags/v0.152.0.7 --force
rm -rf "$TARGET.__v015207_stage"
echo 'PASS - pushed Lab v0.152.0.7 and tag v0.152.0.7'
