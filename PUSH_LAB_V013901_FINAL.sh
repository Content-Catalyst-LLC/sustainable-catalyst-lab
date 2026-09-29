#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:?Usage: $0 /path/to/sustainable-catalyst-lab-v0.139.0.1-repository.zip}"
REMOTE="${SC_LAB_GIT_REMOTE:-https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP/src"
git clone "$REMOTE" "$TMP/repo"
rsync -a --delete --exclude='.git' "$TMP/src/sustainable-catalyst-lab-main/" "$TMP/repo/"
cd "$TMP/repo"
grep -q 'Version: 0.139.0.1' sustainable-catalyst-lab.php
git add -A
if git diff --cached --quiet; then echo 'No changes to commit.'; else git commit -m 'Release Lab v0.139.0.1 — WordPress Release Manifest Scope & Integrity Repair'; git push origin main; fi
if git rev-parse 'v0.139.0.1' >/dev/null 2>&1; then echo 'Tag v0.139.0.1 already exists locally.'; else git tag -a v0.139.0.1 -m 'Lab v0.139.0.1 — WordPress Release Manifest Scope & Integrity Repair'; fi
git push origin v0.139.0.1
echo 'PASS - Lab v0.139.0.1 pushed and tagged.'
