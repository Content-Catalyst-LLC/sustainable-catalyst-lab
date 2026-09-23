#!/usr/bin/env bash
set -euo pipefail
trap 'echo "ERROR: Lab v0.135.0 GitHub promotion stopped at line $LINENO (exit $?): $BASH_COMMAND" >&2' ERR
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v01350-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"
unzip -q "$source_zip" -d "$work/source"
# Defensive normalization: repository ZIPs must leave directories traversable on macOS/Linux.
find "$work/source" -type d -exec chmod u+rwx {} +
find "$work/source" -type f -exec chmod u+rw {} +
source_root="$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | sed -n '1p')"
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'__VERIFY135__'
import json,sys
m=json.load(open(sys.argv[1]))
assert m.get('releaseVersion')=='0.135.0'
assert m.get('competingModelHypothesisAnalysisVersion')=='0.135.0'
assert m.get('v01350RequiredRouteCount')==49
assert m.get('v01350ComparisonFamilyCount')==24
print('PASS: source ZIP identifies Lab v0.135.0 / Competing Model & Hypothesis Analysis')
__VERIFY135__
repo="${HOME}/Downloads/sc-lab-v01350-git"; rm -rf "$repo"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"
cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git status --short
git add -A
git commit -m "Release Lab v0.135.0 Competing Model and Hypothesis Analysis"
git push origin main
if git rev-parse v0.135.0 >/dev/null 2>&1; then git tag -d v0.135.0; git push origin :refs/tags/v0.135.0 || true; fi
git tag v0.135.0
git push origin v0.135.0
echo 'PASS - Lab v0.135.0 pushed to main and tagged v0.135.0.'
git log -1 --oneline --decorate
git tag --points-at HEAD
