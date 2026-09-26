#!/usr/bin/env bash
set -euo pipefail
trap 'echo "ERROR: Lab v0.135.1 GitHub promotion stopped at line $LINENO (exit $?): $BASH_COMMAND" >&2' ERR
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v01351-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"
unzip -q "$source_zip" -d "$work/source"
# ZIPs are treated as transport, not authority for local permission semantics.
find "$work/source" -type d -exec chmod u+rwx {} +
find "$work/source" -type f -exec chmod u+rw {} +
source_root="$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | sed -n '1p')"
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'__VERIFY1351__'
import json,sys
m=json.load(open(sys.argv[1]))
assert m.get('releaseVersion')=='0.135.1'
assert m.get('scientificVisualizationExperienceVersion')=='0.135.1'
assert m.get('v01351RequiredRouteCount')==32
assert m.get('v01351PanelFamilyCount')==12
assert m.get('v01351CapabilityFamilyCount')==12
print('PASS: source ZIP identifies Lab v0.135.1 / Scientific Visualization Experience Overhaul')
__VERIFY1351__
repo="${HOME}/Downloads/sc-lab-v01351-git"; rm -rf "$repo"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"
cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git status --short
git add -A
git commit -m "Release Lab v0.135.1 Scientific Visualization Experience Overhaul"
git push origin main
if git rev-parse v0.135.1 >/dev/null 2>&1; then git tag -d v0.135.1; git push origin :refs/tags/v0.135.1 || true; fi
git tag v0.135.1
git push origin v0.135.1
echo 'PASS - Lab v0.135.1 pushed to main and tagged v0.135.1.'
git log -1 --oneline --decorate
git tag --points-at HEAD
