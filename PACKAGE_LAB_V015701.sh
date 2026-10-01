#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-$HOME/Downloads/sc-lab-v0.157.0.1-artifacts}"
cd "$ROOT"
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ]; then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"; fi
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
m['wordpressCriticalFiles']=wp; m['backendCriticalFiles']=backend; m['criticalFiles']={}; m['generatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat(); seed='\n'.join(f'{k}:{v}' for k,v in wp.items()).encode(); m['buildFingerprint']=hashlib.sha256(seed).hexdigest(); p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print(f'Generated WordPress manifest with {len(wp)} files; backend manifest with {len(backend)} files')
PY
"$ROOT/VALIDATE_LAB_V015701.sh" "$ROOT"
rm -rf "$OUT"; mkdir -p "$OUT"
repo_stage="$(mktemp -d)"; plugin_stage="$(mktemp -d)"; backend_stage="$(mktemp -d)"; trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.157.0.1/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.157.0.1/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete --exclude='.git/' --exclude='/backend/' --exclude='/tests/' --exclude='/scripts/' --exclude='/sdk/' --exclude='/examples/' --exclude='/docs/' --exclude='/data/' --exclude='dist-v0.157.0.1/' --exclude='*.zip' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.157.0.1/backend/"
( cd "$repo_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.157.0.1-repository.zip" sustainable-catalyst-lab-main )
( cd "$plugin_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.157.0.1-wordpress.zip" sustainable-catalyst-lab )
( cd "$backend_stage" && zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.157.0.1.zip" sustainable-catalyst-lab-backend-v0.157.0.1 )
python3 - "$OUT/sustainable-catalyst-lab-v0.157.0.1-wordpress.zip" "$OUT/sustainable-catalyst-lab-backend-v0.157.0.1.zip" <<'PY'
import zipfile,json,hashlib,sys
wp=zipfile.ZipFile(sys.argv[1]); root=wp.namelist()[0].split('/')[0]; m=json.loads(wp.read(root+'/build/sc-lab-release-manifest.json')); assert m['releaseVersion']=='0.157.0.1'; assert m['featureVersion']=='0.157.0'; names=set(wp.namelist())
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    n=root+'/'+rel; assert n in names,rel; assert hashlib.sha256(wp.read(n)).hexdigest()==expected,rel
be=zipfile.ZipFile(sys.argv[2]); broot=be.namelist()[0].split('/')[0]; bnames=set(be.namelist())
for rel,expected in m.get('backendCriticalFiles',{}).items():
    short=rel[len('backend/'):] if rel.startswith('backend/') else rel; n=broot+'/backend/'+short; assert n in bnames,rel; assert hashlib.sha256(be.read(n)).hexdigest()==expected,rel
for rel in ['includes/class-sc-lab-canonical-release-front-door-auth-repair-v015701.php','assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js','assets/css/sc-lab-canonical-release-front-door-auth-repair-v015701.css']:
    assert root+'/'+rel in names,rel
for n in [broot+'/backend/app/cross_study_replication_meta_experiment_v01570.py',broot+'/backend/tests/test_cross_study_replication_meta_experiment_v01570.py']:
    assert n in bnames,n
print('PASS - packaged v0.157.0.1 manifest and required files verify')
PY
for f in PUSH_LAB_V015701_FINAL.sh DEPLOY_LAB_V015701_CONTABO.sh DEPLOY_LAB_WORDPRESS_V015701_BLUEHOST.sh VALIDATE_LAB_V015701.sh PACKAGE_LAB_V015701.sh BUILD_LAB_V015701.md LAB_CANONICAL_RELEASE_FRONT_DOOR_AUTHORIZATION_REPAIR_0.157.0.1.md RELEASE_NOTES_0.157.0.1_CANONICAL_RELEASE_FRONT_DOOR_AUTHORIZATION_REPAIR.md DEPLOY_LAB_BACKEND_v0.157.0.1.md; do [ -f "$ROOT/$f" ] && cp "$ROOT/$f" "$OUT/"; done
( cd "$OUT" && sha256sum sustainable-catalyst-lab-v0.157.0.1-repository.zip sustainable-catalyst-lab-v0.157.0.1-wordpress.zip sustainable-catalyst-lab-backend-v0.157.0.1.zip > SHA256SUMS.txt )
release_stage="$(mktemp -d)"; cp -a "$OUT/." "$release_stage/"; ( cd "$release_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.157.0.1-release-bundle.zip" . ); rm -rf "$release_stage"; ( cd "$OUT" && sha256sum sustainable-catalyst-lab-v0.157.0.1-release-bundle.zip >> SHA256SUMS.txt )
echo "PASS - Lab v0.157.0.1 packages written to $OUT"
