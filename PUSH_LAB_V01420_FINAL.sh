#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v01420-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"
unzip -q "$source_zip" -d "$work/source"; source_root="$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)"
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY2'
import json,sys
m=json.load(open(sys.argv[1])); assert m.get('releaseVersion')=='0.142.0'; assert m.get('integratedNeuralResearchWorkspaceVersion')=='0.142.0'; assert m.get('reproducibleNeuralResearchPackageVersion')=='0.141.8'; assert m.get('v014001WordPressInstalledRuntimeScope') is True
print('PASS: source ZIP identifies Lab v0.142.0')
PY2
repo="${HOME}/Downloads/sc-lab-v01420-git"; rm -rf "$repo"; git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"; cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git add -A
git commit -m 'Release Lab v0.142.0 — Integrated Neural Research Workspace'
git push origin main
git tag -a v0.142.0 -m 'Lab v0.142.0 — Integrated Neural Research Workspace'
git push origin v0.142.0
echo 'PASS - Lab v0.142.0 pushed and tagged.'
