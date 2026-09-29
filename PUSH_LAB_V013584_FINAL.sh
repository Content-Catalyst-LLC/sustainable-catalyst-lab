#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v013584-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"; unzip -q "$source_zip" -d "$work/source"
source_root=$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY2'
import json,sys
m=json.load(open(sys.argv[1])); assert m.get('releaseVersion')=='0.135.8.4'; print('PASS: source ZIP identifies Lab v0.135.8.4')
PY2
repo="${HOME}/Downloads/sc-lab-v013584-git"; rm -rf "$repo"; git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"; cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"; git add -A; git commit -m "Release Lab v0.135.8.4 Live Scientific Object Binding Project State Persistence and Advanced Provenance Exploration"; git push origin main
git tag -a v0.135.8.4 -m "Lab v0.135.8.4"; git push origin v0.135.8.4
echo 'PASS - Lab v0.135.8.4 pushed and tagged.'
