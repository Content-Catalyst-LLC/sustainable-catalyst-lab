#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/Downloads/sc-lab-v0.163.1-artifacts/sustainable-catalyst-lab-v0.163.1-repository.zip}"; REPO="${2:-$HOME/Downloads/sustainable-catalyst-lab}"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
[ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }; [ -d "$REPO/.git" ] || { echo "ERROR: Git repository not found: $REPO" >&2; exit 1; }
unzip -q "$ZIP" -d "$TMP"; SRC="$TMP/sustainable-catalyst-lab-main"; [ -d "$SRC" ] || { echo 'ERROR: repository payload not found' >&2; exit 1; }
rsync -a --delete --exclude='.git/' "$SRC/" "$REPO/"
cd "$REPO"; git add -A
if ! git diff --cached --quiet; then git commit -m 'Release Lab v0.163.1 — Unified Workspace Shell & Progressive Module Navigation'; fi
git push origin HEAD:main
if git ls-remote --exit-code --tags origin refs/tags/v0.163.1 >/dev/null 2>&1; then echo 'ERROR: remote tag v0.163.1 already exists; refusing to rewrite it.' >&2; exit 1; fi
git tag -a v0.163.1 -m 'Lab v0.163.1 — Unified Workspace Shell & Progressive Module Navigation'
git push origin v0.163.1
echo 'PASS - pushed Lab v0.163.1 and tag v0.163.1'
