#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v013583-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"; unzip -q "$source_zip" -d "$work/source"
source_root=$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY2'
import json,sys
m=json.load(open(sys.argv[1])); assert m.get('releaseVersion')=='0.135.8.3'; assert m.get('graphStudioRecoveryVersion')=='0.135.8.3'; print('PASS: source ZIP identifies Lab v0.135.8.3')
PY2
repo="${HOME}/Downloads/sc-lab-v013583-git"; rm -rf "$repo"; git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"; cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"; git add -A; git commit -m "Release Lab v0.135.8.3 Renderer Mount Lifecycle Scientific State Hydration and Visual Workspace Recovery"; git push origin main
if git rev-parse v0.135.8.3 >/dev/null 2>&1; then git tag -d v0.135.8.3; git push origin :refs/tags/v0.135.8.3 || true; fi
git tag v0.135.8.3; git push origin v0.135.8.3; echo 'PASS - Lab v0.135.8.3 pushed and tagged.'
