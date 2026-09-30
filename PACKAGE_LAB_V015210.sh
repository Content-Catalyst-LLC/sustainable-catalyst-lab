#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-/mnt/data/sc-lab-v0.152.0.10-artifacts}"
cd "$ROOT"

python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"
python3 - <<'PY'
from pathlib import Path
import json,hashlib,datetime
root=Path('.'); p=root/'build/sc-lab-release-manifest.json'; m=json.loads(p.read_text())
include_roots=('assets/','includes/','templates/','contracts/','build/')
wp={}
for f in sorted(root.rglob('*')):
    if not f.is_file(): continue
    rel=f.as_posix().lstrip('./')
    if rel=='build/sc-lab-release-manifest.json': continue
    if rel=='sustainable-catalyst-lab.php' or rel.startswith(include_roots):
        if rel.startswith('data/'): continue
        wp[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
backend={}
for f in sorted((root/'backend').rglob('*')):
    if not f.is_file(): continue
    rel=f.as_posix()
    if '/data/' in '/'+rel or '__pycache__' in rel or '.pytest_cache' in rel or rel.endswith('.pyc'): continue
    backend[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
m['wordpressCriticalFiles']=wp; m['backendCriticalFiles']=backend; m['criticalFiles']={}
m['generatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
seed='\n'.join(f'{k}:{v}' for k,v in wp.items()).encode(); m['buildFingerprint']=hashlib.sha256(seed).hexdigest()
p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print(f'Generated WordPress runtime manifest with {len(wp)} immutable files; backend manifest with {len(backend)} files')
PY

"$ROOT/VALIDATE_LAB_V015210.sh" "$ROOT"
rm -rf "$OUT"; mkdir -p "$OUT"
repo_stage="$(mktemp -d)"; plugin_stage="$(mktemp -d)"; backend_stage="$(mktemp -d)"
trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.152.0.10/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.152.0.10/' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete --exclude='.git/' --exclude='/backend/' --exclude='/tests/' --exclude='/scripts/' --exclude='/sdk/' --exclude='/examples/' --exclude='/docs/' --exclude='/data/' --exclude='dist-v0.152.0.10/' --exclude='*.zip' "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.152.0.10/backend/"
( cd "$repo_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.152.0.10-repository.zip" sustainable-catalyst-lab-main )
( cd "$plugin_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.152.0.10-wordpress.zip" sustainable-catalyst-lab )
( cd "$backend_stage" && zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.152.0.10.zip" sustainable-catalyst-lab-backend-v0.152.0.10 )

python3 - "$OUT/sustainable-catalyst-lab-v0.152.0.10-wordpress.zip" "$OUT/sustainable-catalyst-lab-backend-v0.152.0.10.zip" <<'PY'
import zipfile,json,hashlib,sys
wp=zipfile.ZipFile(sys.argv[1]); root=wp.namelist()[0].split('/')[0]
m=json.loads(wp.read(root+'/build/sc-lab-release-manifest.json')); names=set(wp.namelist()); missing=[]; mismatch=[]
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    name=root+'/'+rel
    if name not in names: missing.append(rel); continue
    if hashlib.sha256(wp.read(name)).hexdigest()!=expected: mismatch.append(rel)
assert not missing,(len(missing),missing[:10]); assert not mismatch,(len(mismatch),mismatch[:10])
# PHP output safety inside the packaged WordPress artifact.
php_issues=[]
for name in names:
    if not name.endswith('.php') or name.endswith('/'):
        continue
    data=wp.read(name)
    if data.startswith(b'\xef\xbb\xbf') or not data.startswith(b'<?php'):
        php_issues.append(name)
assert not php_issues,php_issues[:20]
be=zipfile.ZipFile(sys.argv[2]); broot=be.namelist()[0].split('/')[0]; bnames=set(be.namelist()); bmissing=[]; bmismatch=[]
for rel,expected in m.get('backendCriticalFiles',{}).items():
    short=rel[len('backend/'):] if rel.startswith('backend/') else rel; name=broot+'/backend/'+short
    if name not in bnames: bmissing.append(rel); continue
    if hashlib.sha256(be.read(name)).hexdigest()!=expected: bmismatch.append(rel)
assert not bmissing,(len(bmissing),bmissing[:10]); assert not bmismatch,(len(bmismatch),bmismatch[:10])
print(f"PASS: packaged WordPress manifest verifies {len(m['wordpressCriticalFiles'])} immutable runtime files; backend verifies {len(m['backendCriticalFiles'])} files")
print(f"PASS: packaged WordPress PHP output-safety verifies {sum(1 for n in names if n.endswith('.php'))} PHP files")
print('releaseVersion='+m['releaseVersion']); print('buildFingerprint='+m['buildFingerprint'])
PY

cp "$ROOT/PUSH_LAB_V015210_FINAL.sh" \
   "$ROOT/DEPLOY_LAB_V015210_CONTABO.sh" \
   "$ROOT/DEPLOY_LAB_WORDPRESS_V015210_BLUEHOST.sh" \
   "$ROOT/VALIDATE_LAB_V015210.sh" \
   "$ROOT/PACKAGE_LAB_V015210.sh" \
   "$ROOT/CHECK_LAB_PHP_OUTPUT_SAFETY.py" \
   "$ROOT/BUILD_LAB_V015210.md" \
   "$ROOT/LAB_4D_UNCERTAINTY_SENSITIVITY_ENSEMBLE_EXPLORER_0.152.0.10.md" \
   "$ROOT/RELEASE_NOTES_0.152.0.10_4D_UNCERTAINTY_SENSITIVITY_ENSEMBLE_EXPLORER.md" \
   "$ROOT/DEPLOY_LAB_BACKEND_v0.152.0.10.md" \
   "$OUT/"

( cd "$OUT" && sha256sum sustainable-catalyst-lab-v0.152.0.10-repository.zip sustainable-catalyst-lab-v0.152.0.10-wordpress.zip sustainable-catalyst-lab-backend-v0.152.0.10.zip > SHA256SUMS.txt )
release_stage="$(mktemp -d)"; cp -a "$OUT/." "$release_stage/"; ( cd "$release_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.152.0.10-release-bundle.zip" . ); rm -rf "$release_stage"
( cd "$OUT" && sha256sum sustainable-catalyst-lab-v0.152.0.10-release-bundle.zip >> SHA256SUMS.txt )
echo "PASS - Lab v0.152.0.10 packages written to $OUT"
