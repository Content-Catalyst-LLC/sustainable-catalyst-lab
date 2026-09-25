#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v0135852-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"; unzip -q "$source_zip" -d "$work/source"
source_root=$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))
assert m.get('releaseVersion')=='0.135.8.5.2'
assert m.get('graphStudioNativeProvenanceVersion')=='0.135.8.5.2'
assert m.get('graphStudioIncrementalInteractionVersion')=='0.135.8.5.2'
assert m.get('v0135852RequiredRouteCount')==7
assert m.get('v0135852IncrementalRendering') is True
assert m.get('v0135852RelationshipSelectorStable') is True
assert m.get('v0135852FullRedrawForOrdinaryInteraction') is False
print('PASS: source ZIP identifies Lab v0.135.8.5.2')
PY
repo="${HOME}/Downloads/sc-lab-v0135852-git"; rm -rf "$repo"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"
cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git add -A
git commit -m "Release Lab v0.135.8.5.2 incremental provenance interaction hardening"
git push origin main
git tag -a v0.135.8.5.2 -m "Lab v0.135.8.5.2"; git push origin v0.135.8.5.2
echo 'PASS - Lab v0.135.8.5.2 pushed and tagged.'
