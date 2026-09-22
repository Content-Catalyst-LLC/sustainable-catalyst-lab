#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.104.0 GitHub promotion stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR

SOURCE_ZIP="${1:-$PWD/sustainable-catalyst-lab-v0.104.0-repository.zip}"
REPO_URL="${SC_LAB_REPO_URL:-https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git}"
WORK_ROOT="${SC_LAB_GIT_WORK_ROOT:-$HOME/Downloads/sc-lab-v01040-git}"
TAG="v0.104.0"

[[ -f "$SOURCE_ZIP" ]] || { echo "ERROR: repository ZIP not found: $SOURCE_ZIP" >&2; exit 1; }
for cmd in git unzip rsync python3; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done

if git ls-remote --exit-code --tags "$REPO_URL" "refs/tags/$TAG" >/dev/null 2>&1; then
  echo "ERROR: remote tag $TAG already exists. Historical release tags must not be moved." >&2
  exit 1
fi

rm -rf "$WORK_ROOT"
git clone "$REPO_URL" "$WORK_ROOT"
cd "$WORK_ROOT"
git checkout main
git pull --ff-only origin main

stage="$(mktemp -d /tmp/sc-lab-v01040-git.XXXXXX)"
trap 'rm -rf "$stage"' EXIT
unzip -q "$SOURCE_ZIP" -d "$stage"
source_root="$(find "$stage" -type f -name sustainable-catalyst-lab.php -printf '%h\n' | head -1)"
[[ -n "$source_root" ]] || { echo "ERROR: sustainable-catalyst-lab.php not found in source ZIP" >&2; exit 1; }

python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PYVERIFY'
import json,sys
m=json.load(open(sys.argv[1]))
assert m.get('releaseVersion')=='0.104.0',m.get('releaseVersion')
assert m.get('platformCoreRequiredVersion')=='3.0.0',m.get('platformCoreRequiredVersion')
assert m.get('routeAssertions')==1008,m.get('routeAssertions')
print('PASS: source ZIP identifies Lab v0.104.0 / Platform Core v3.0.0 integration')
PYVERIFY

rsync -a --delete --exclude='.git/' "$source_root/" "$WORK_ROOT/"

git add -A
if git diff --cached --quiet; then
  echo "ERROR: no v0.104.0 changes are staged" >&2
  exit 1
fi

git status --short
git commit -m "Release Lab v0.104.0 Platform Core v3 runtime adapter"
git push origin main
git tag -a "$TAG" -m "Sustainable Catalyst Lab v0.104.0 — Platform Core v3 Runtime Adapter & Capability Registration"
git push origin "$TAG"

echo "PASS - Lab v0.104.0 pushed to main and tagged $TAG."
git log -1 --oneline
git tag --points-at HEAD
