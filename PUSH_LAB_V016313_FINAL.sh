#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$(pwd)/sustainable-catalyst-lab-v0.163.1.3-repository.zip}"
REPO="${2:-$HOME/Downloads/sustainable-catalyst-lab}"
[ -f "$ZIP" ] || { echo "ERROR: repository zip not found: $ZIP" >&2; exit 1; }
[ -d "$REPO/.git" ] || { echo "ERROR: Git repo not found: $REPO" >&2; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab-main"
cd "$REPO"; git fetch origin --tags; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$SRC/" "$REPO/"
git add -A
if ! git diff --cached --quiet; then git commit -m 'Release Lab v0.163.1.3 — 4D Front-Door Visual Polish & Compact Control Layout'; fi
git push origin main
if git ls-remote --exit-code --tags origin refs/tags/v0.163.1.3 >/dev/null 2>&1; then echo 'ERROR: remote tag v0.163.1.3 already exists; refusing to rewrite it.' >&2; exit 1; fi
git tag -a v0.163.1.3 -m 'Lab v0.163.1.3 — 4D Front-Door Visual Polish & Compact Control Layout'
git push origin v0.163.1.3
echo 'PASS - pushed Lab v0.163.1.3 and tag v0.163.1.3'
