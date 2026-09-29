#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v0135210-promote-$$";rm -rf "$work";mkdir -p "$work/source";unzip -q "$source_zip" -d "$work/source"
source_root=$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY2'
import json,sys
m=json.load(open(sys.argv[1]));assert m.get('releaseVersion')=='0.135.21.0';assert m.get('graphStudioReviewWorkspaceConsolidationVersion')=='0.135.21.0';assert m.get('v0135210RequiredRouteCount')==18;assert m.get('v0135210ReviewWorkspaceConsolidation') is True;assert m.get('v0135210DeterministicHydration') is True;assert m.get('v0135210RuntimeCertification') is True;assert m.get('v0135210AutomaticScientificValidity') is False;assert m.get('v0135210FullGraphRedraw') is False;print('PASS: source ZIP identifies Lab v0.135.21.0')
PY2
repo="${HOME}/Downloads/sc-lab-v0135210-git";rm -rf "$repo";git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo";cd "$repo";git checkout main;git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git add -A;git commit -m "Release Lab v0.135.21.0 Graph Studio review workspace consolidation and runtime certification";git push origin main;git tag -a v0.135.21.0 -m "Lab v0.135.21.0";git push origin v0.135.21.0
echo 'PASS - Lab v0.135.21.0 pushed and tagged.'
