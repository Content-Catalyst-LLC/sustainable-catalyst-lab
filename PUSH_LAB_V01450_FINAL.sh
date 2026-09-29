#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sustainable-catalyst-lab-v0.145.0-repository.zip}"; REPO="${2:-$HOME/Downloads/sustainable-catalyst-lab}"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
[[ -f "$ZIP" ]] || { echo "ERROR: repository ZIP not found: $ZIP" >&2; exit 1; }
if [[ ! -d "$REPO/.git" ]]; then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$REPO"; fi
unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab-main"; [[ -d "$SRC" ]] || { echo 'ERROR: repository root missing' >&2; exit 1; }
cd "$REPO"; git checkout main; git pull --ff-only origin main; rsync -a --delete --exclude='.git/' "$SRC/" "$REPO/"; git add -A
if ! git diff --cached --quiet; then git commit -m 'Release Lab v0.145.0 — Simulation & Computational Experiment Workspace'; fi
git push origin main
if git rev-parse 'v0.145.0' >/dev/null 2>&1; then git tag -d 'v0.145.0'; fi
git tag -a 'v0.145.0' -m 'Lab v0.145.0 — Simulation & Computational Experiment Workspace'; git push origin ':refs/tags/v0.145.0' 2>/dev/null || true; git push origin 'v0.145.0'
echo 'PASS - Lab v0.145.0 pushed and tagged.'
