#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sustainable-catalyst-lab-v0.151.0-repository.zip}"
REPO="${2:-$HOME/Downloads/sustainable-catalyst-lab}"
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP"; exit 1; }
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT; unzip -q "$ZIP" -d "$tmp"; src="$tmp/sustainable-catalyst-lab-main"
[ -d "$REPO/.git" ] || { echo "ERROR: Git repo not found at $REPO"; exit 1; }
cd "$REPO"; git fetch origin --tags; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$src/" "$REPO/"
git add -A
if ! git diff --cached --quiet; then git commit -m 'Release Lab v0.151.0 — Scientific Workflow & Experiment Orchestration'; fi
git push origin main
if git rev-parse v0.151.0 >/dev/null 2>&1; then git tag -d v0.151.0; git push origin :refs/tags/v0.151.0 || true; fi
git tag -a v0.151.0 -m 'Lab v0.151.0 — Scientific Workflow & Experiment Orchestration'
git push origin v0.151.0
echo 'PASS - GitHub main and v0.151.0 tag pushed.'
