#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.116.0 GitHub promotion stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
SOURCE_ZIP="${1:-$PWD/sustainable-catalyst-lab-v0.116.0-repository.zip}"
REPO_URL="${SC_LAB_REPO_URL:-https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git}"
WORK_ROOT="${SC_LAB_GIT_WORK_ROOT:-$HOME/Downloads/sc-lab-v01160-git}"
TAG="v0.116.0"
[[ -f "$SOURCE_ZIP" ]] || { echo "ERROR: repository ZIP not found: $SOURCE_ZIP" >&2; exit 1; }
for cmd in git unzip rsync python3 find sed dirname; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is required" >&2; exit 1; }; done
if git ls-remote --exit-code --tags "$REPO_URL" "refs/tags/$TAG" >/dev/null 2>&1; then echo "ERROR: remote tag $TAG already exists." >&2; exit 1; fi
rm -rf "$WORK_ROOT"; git clone "$REPO_URL" "$WORK_ROOT"; cd "$WORK_ROOT"; git checkout main; git pull --ff-only origin main
stage="$(mktemp -d /tmp/sc-lab-v01160-git.XXXXXX)"; trap 'rm -rf "$stage"' EXIT
unzip -q "$SOURCE_ZIP" -d "$stage"
source_file="$(find "$stage" -type f -name sustainable-catalyst-lab.php | sed -n '1p')"
[[ -n "$source_file" ]] || { echo "ERROR: plugin file not found" >&2; exit 1; }
source_root="$(dirname "$source_file")"
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PYVERIFY'
import json,sys
m=json.load(open(sys.argv[1])); assert m.get('releaseVersion')=='0.116.0'; assert m.get('interactiveScientificDashboardsVersion')=='0.116.0'; assert m.get('v01160RequiredRouteCount')==18; assert m.get('v01160InteractionChannelCount')==7
print('PASS: source ZIP identifies Lab v0.116.0 / Interactive Scientific Dashboards & Small Multiples')
PYVERIFY
rsync -a --delete --exclude='.git/' "$source_root/" "$WORK_ROOT/"
git add -A
if git diff --cached --quiet; then echo "ERROR: no v0.116.0 changes are staged" >&2; exit 1; fi
git status --short
git commit -m "Release Lab v0.116.0 interactive scientific dashboards"
git push origin main
git tag -a "$TAG" -m "Sustainable Catalyst Lab v0.116.0 — Interactive Scientific Dashboards & Small Multiples"
git push origin "$TAG"
echo "PASS - Lab v0.116.0 pushed to main and tagged $TAG."
git log -1 --oneline
git tag --points-at HEAD
