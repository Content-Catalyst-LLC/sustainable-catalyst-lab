#!/usr/bin/env bash
set -euo pipefail
trap 'echo "ERROR: Lab v0.135.4 GitHub promotion stopped at line $LINENO (exit $?): $BASH_COMMAND" >&2' ERR
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v01354-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"
unzip -q "$source_zip" -d "$work/source"
find "$work/source" -type d -exec chmod u+rwx {} +
find "$work/source" -type f -exec chmod u+rw {} +
source_root="$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | sed -n '1p')"
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PYVERIFY'
import json,sys
m=json.load(open(sys.argv[1]))
assert m.get('releaseVersion')=='0.135.4'
assert m.get('interactiveScientificSceneDrillDownVersion')=='0.135.4'
assert m.get('v01354RequiredRouteCount')==45
assert m.get('v01354LayerTypeCount')==12
assert m.get('v01354DrillTargetTypeCount')==8
assert m.get('v01354ViewModeCount')==6
assert m.get('v01354NavigationModeCount')==5
assert m.get('v01354LodModeCount')==4
print('PASS: source ZIP identifies Lab v0.135.4 / Interactive Scientific Scene & Visual Drill-Down')
PYVERIFY
repo="${HOME}/Downloads/sc-lab-v01354-git"; rm -rf "$repo"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"
cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git status --short
git add -A
git commit -m "Release Lab v0.135.4 Interactive Scientific Scene and Visual Drill-Down"
git push origin main
if git rev-parse v0.135.4 >/dev/null 2>&1; then git tag -d v0.135.4; git push origin :refs/tags/v0.135.4 || true; fi
git tag v0.135.4
git push origin v0.135.4
echo 'PASS - Lab v0.135.4 pushed to main and tagged v0.135.4.'
git log -1 --oneline --decorate
git tag --points-at HEAD
