#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v01400-promote-$$"
rm -rf "$work"; mkdir -p "$work/source"
unzip -q "$source_zip" -d "$work/source"
source_root="$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)"
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY2'
import json,sys
m=json.load(open(sys.argv[1]))
assert m.get('releaseVersion')=='0.140.0'
assert m.get('scientificResearchOperatingSystemVersion')=='0.140.0'
assert m.get('v01400RequiredRouteCount')==25
assert m.get('v01400LifecycleOrchestration') is True
assert m.get('v01400CapabilityMatrix') is True
assert m.get('v01400BackwardCompatibleV01390') is True
assert m.get('v01400AutomaticPhaseAdvance') is False
assert m.get('v01400AutomaticScientificValidity') is False
assert m.get('v01400AutomaticPublicationAcceptance') is False
print('PASS: source ZIP identifies Lab v0.140.0')
PY2
repo="${HOME}/Downloads/sc-lab-v01400-git"
rm -rf "$repo"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"
cd "$repo"
git checkout main
git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git add -A
git commit -m "Release Lab v0.140.0 Scientific Research Operating System Milestone"
git push origin main
git tag -a v0.140.0 -m "Lab v0.140.0"
git push origin v0.140.0
echo 'PASS - Lab v0.140.0 pushed and tagged.'
