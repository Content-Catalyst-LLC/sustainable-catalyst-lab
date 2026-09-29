#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; OUT="${2:-$ROOT/dist-v0.141.4}"; cd "$ROOT"
python3 - <<'PY2'
from pathlib import Path
import json,hashlib,datetime
root=Path('.'); m=json.loads((root/'build/sc-lab-release-manifest.json').read_text()); include_roots=('assets/','includes/','templates/','contracts/','build/'); files={}
for p in sorted(root.rglob('*')):
    if not p.is_file(): continue
    rel=p.as_posix().lstrip('./')
    if rel=='build/sc-lab-release-manifest.json': continue
    if rel=='sustainable-catalyst-lab.php' or rel.startswith(include_roots):
        if rel.startswith('data/'): continue
        files[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
m['wordpressCriticalFiles']=files; m['criticalFiles']={}; m['generatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat(); seed='\n'.join(f'{k}:{v}' for k,v in files.items()).encode(); m['buildFingerprint']=hashlib.sha256(seed).hexdigest(); (root/'build/sc-lab-release-manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n'); print(f'Generated WordPress runtime manifest with {len(files)} immutable files')
PY2
"$ROOT/VALIDATE_LAB_V01414.sh" "$ROOT"
rm -rf "$OUT"; mkdir -p "$OUT"; repo_stage="$(mktemp -d)"; plugin_stage="$(mktemp -d)"; backend_stage="$(mktemp -d)"; trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.141.4/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.141.4/' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete --exclude='.git/' --exclude='/backend/' --exclude='/tests/' --exclude='/scripts/' --exclude='/sdk/' --exclude='/examples/' --exclude='/docs/' --exclude='/data/' --exclude='dist-v0.141.4/' --exclude='*.zip' "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.141.4/backend/"
( cd "$repo_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.141.4-repository.zip" sustainable-catalyst-lab-main; cd "$plugin_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.141.4-wordpress.zip" sustainable-catalyst-lab; cd "$backend_stage" && zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.141.4.zip" sustainable-catalyst-lab-backend-v0.141.4 )
python3 - "$OUT/sustainable-catalyst-lab-v0.141.4-wordpress.zip" <<'PY2'
import zipfile,json,hashlib,sys
z=zipfile.ZipFile(sys.argv[1]); root=z.namelist()[0].split('/')[0]; m=json.loads(z.read(root+'/build/sc-lab-release-manifest.json')); names=set(z.namelist()); missing=[]; mismatch=[]
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    name=root+'/'+rel
    if name not in names: missing.append(rel); continue
    if hashlib.sha256(z.read(name)).hexdigest()!=expected: mismatch.append(rel)
assert not missing,(len(missing),missing[:10]); assert not mismatch,(len(mismatch),mismatch[:10]); assert all(not p.startswith(('backend/','data/','tests/','scripts/','sdk/','examples/','docs/')) for p in m['wordpressCriticalFiles']); print(f"PASS: packaged WordPress manifest verifies {len(m['wordpressCriticalFiles'])} files; 0 missing; 0 mismatches")
PY2
for f in DEPLOY_LAB_V01414_CONTABO.sh PUSH_LAB_V01414_FINAL.sh VALIDATE_LAB_V01414.sh HYPERPARAMETER_STUDY_SEARCH_RESULTS_0.141.4.md RELEASE_NOTES_0.141.4_HYPERPARAMETER_STUDY_SEARCH_RESULTS.md; do cp "$ROOT/$f" "$OUT/"; done
(cd "$OUT" && shasum -a 256 sustainable-catalyst-lab-v0.141.4-repository.zip sustainable-catalyst-lab-v0.141.4-wordpress.zip sustainable-catalyst-lab-backend-v0.141.4.zip > SHA256SUMS.txt && zip -qr sustainable-catalyst-lab-v0.141.4-release-bundle.zip sustainable-catalyst-lab-v0.141.4-repository.zip sustainable-catalyst-lab-v0.141.4-wordpress.zip sustainable-catalyst-lab-backend-v0.141.4.zip DEPLOY_LAB_V01414_CONTABO.sh PUSH_LAB_V01414_FINAL.sh VALIDATE_LAB_V01414.sh HYPERPARAMETER_STUDY_SEARCH_RESULTS_0.141.4.md RELEASE_NOTES_0.141.4_HYPERPARAMETER_STUDY_SEARCH_RESULTS.md SHA256SUMS.txt)
echo "PASS - Lab v0.141.4 artifacts packaged in $OUT"
