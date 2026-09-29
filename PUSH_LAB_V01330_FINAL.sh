#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "ERROR: Lab v0.133.0 GitHub promotion stopped at line $LINENO (exit $rc): $BASH_COMMAND" >&2; exit $rc' ERR
ZIP="${1:-${PWD}/sustainable-catalyst-lab-v0.133.0-repository.zip}"
[[ -f "$ZIP" ]] || { echo "ERROR: source ZIP not found: $ZIP" >&2; exit 1; }
TMPROOT="$(mktemp -d /tmp/sc-lab-v01330-source.XXXXXX)"; trap 'rm -rf "$TMPROOT"' EXIT
unzip -q "$ZIP" -d "$TMPROOT"
source_manifest="$(find "$TMPROOT" -type f -path '*/build/sc-lab-release-manifest.json' | sed -n '1p')"; source_root="$(dirname "$(dirname "$source_manifest")")"
python3 - "$source_manifest" <<'PYVERIFY'
import json,sys
m=json.load(open(sys.argv[1])); assert m.get('releaseVersion')=='0.133.0'; assert m.get('statisticalAssumptionDiagnosticIntelligenceVersion')=='0.133.0'; assert m.get('v01330RequiredRouteCount')==45; assert m.get('v01330AssumptionFamilyCount')==23
print('PASS: source ZIP identifies Lab v0.133.0 / Statistical Assumption & Diagnostic Intelligence')
PYVERIFY
GITDIR="${HOME}/Downloads/sc-lab-v01330-git"; rm -rf "$GITDIR"
git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-lab.git "$GITDIR"
cd "$GITDIR"; git checkout main; git pull --ff-only origin main
rsync -a --delete --exclude='.git/' "$source_root/" "$GITDIR/"
git status --short
git add -A
git commit -m "Release Lab v0.133.0 Statistical Assumption and Diagnostic Intelligence"
git push origin main
if git rev-parse v0.133.0 >/dev/null 2>&1; then echo 'ERROR: tag v0.133.0 already exists locally' >&2; exit 1; fi
git tag -a v0.133.0 -m "Sustainable Catalyst Lab v0.133.0 — Statistical Assumption & Diagnostic Intelligence"
git push origin v0.133.0
echo 'PASS - Lab v0.133.0 pushed to main and tagged v0.133.0.'
git log -1 --oneline --decorate; git describe --tags --exact-match
