#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sc-lab-v0.161.0-artifacts/sustainable-catalyst-lab-v0.161.0-repository.zip}"
TARGET="${2:-$HOME/Downloads/sustainable-catalyst-lab}"
STAGE="$TARGET.__v01610_stage"
rm -rf "$STAGE";mkdir -p "$STAGE"
[ -f "$ZIP" ]||{ echo "ERROR: missing $ZIP" >&2;exit 1;}
unzip -q "$ZIP" -d "$STAGE"
SRC="$STAGE/sustainable-catalyst-lab-main";[ -d "$SRC" ]||{ echo 'ERROR: repository payload not found' >&2;exit 1;}
if [ ! -d "$TARGET/.git" ];then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$TARGET";fi
rsync -a --delete --exclude='.git/' "$SRC/" "$TARGET/"
cd "$TARGET";git add -A
if ! git diff --cached --quiet;then git commit -m "Release Lab v0.161.0 — Research Program & Portfolio Orchestration";fi
git push origin main
if git rev-parse -q --verify refs/tags/v0.161.0 >/dev/null;then git tag -d v0.161.0;fi
git tag -a v0.161.0 -m "Lab v0.161.0 — Research Program & Portfolio Orchestration"
if git ls-remote --exit-code --tags origin refs/tags/v0.161.0 >/dev/null 2>&1;then echo 'ERROR: remote tag v0.161.0 already exists; refusing to rewrite a published release tag.' >&2;exit 1;fi
git push origin refs/tags/v0.161.0
rm -rf "$STAGE"
echo 'PASS - pushed Lab v0.161.0 and tag v0.161.0'
