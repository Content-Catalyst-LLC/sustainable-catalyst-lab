#!/usr/bin/env bash
set -euo pipefail
source_zip="${1:?repository ZIP required}"
work="${TMPDIR:-/tmp}/sc-lab-v0135851-promote-$$"; rm -rf "$work"; mkdir -p "$work/source"; unzip -q "$source_zip" -d "$work/source"
source_root=$(find "$work/source" -mindepth 1 -maxdepth 1 -type d | head -1)
python3 - "$source_root/build/sc-lab-release-manifest.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]));
assert m.get('releaseVersion')=='0.135.8.5.1'
assert m.get('graphStudioNativeProvenanceVersion')=='0.135.8.5'
assert m.get('graphStudioProvenanceAuthorityVersion')=='0.135.8.5.1'
assert m.get('v0135851RequiredRouteCount')==6
assert m.get('v0135851LegacyInteractionEnabled') is False
assert m.get('v0135851LegacyRecoveryEnqueued') is False
assert m.get('v0135851ChromiumCertification') is True
print('PASS: source ZIP identifies Lab v0.135.8.5.1')
PY
repo="${HOME}/Downloads/sc-lab-v0135851-git"; rm -rf "$repo"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$repo"
cd "$repo"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$repo/"
git add -A
git commit -m "Release Lab v0.135.8.5.1 Provenance Runtime Authority and Browser Certification"
git push origin main
git tag -a v0.135.8.5.1 -m "Lab v0.135.8.5.1"; git push origin v0.135.8.5.1
echo 'PASS - Lab v0.135.8.5.1 pushed and tagged.'
