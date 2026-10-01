#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-/mnt/data/sc-lab-v0.154.0-artifacts}"
cd "$ROOT"
python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT"
python3 - <<'PY'
from pathlib import Path
import json, hashlib, datetime
root=Path('.')
p=root/'build/sc-lab-release-manifest.json'
m=json.loads(p.read_text())
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
m['wordpressCriticalFiles']=wp;m['backendCriticalFiles']=backend;m['criticalFiles']={};m['generatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();seed='\n'.join(f'{k}:{v}' for k,v in wp.items()).encode();m['buildFingerprint']=hashlib.sha256(seed).hexdigest();p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print(f'Generated WordPress runtime manifest with {len(wp)} immutable files; backend manifest with {len(backend)} files')
PY
"$ROOT/VALIDATE_LAB_V01540.sh" "$ROOT"
rm -rf "$OUT"; mkdir -p "$OUT"
repo_stage="$(mktemp -d)"; plugin_stage="$(mktemp -d)"; backend_stage="$(mktemp -d)"; trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.154.0/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.154.0/' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete --exclude='.git/' --exclude='/backend/' --exclude='/tests/' --exclude='/scripts/' --exclude='/sdk/' --exclude='/examples/' --exclude='/docs/' --exclude='/data/' --exclude='dist-v0.154.0/' --exclude='*.zip' "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.154.0/backend/"
( cd "$repo_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.154.0-repository.zip" sustainable-catalyst-lab-main )
( cd "$plugin_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.154.0-wordpress.zip" sustainable-catalyst-lab )
( cd "$backend_stage" && zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.154.0.zip" sustainable-catalyst-lab-backend-v0.154.0 )
python3 - "$OUT/sustainable-catalyst-lab-v0.154.0-wordpress.zip" "$OUT/sustainable-catalyst-lab-backend-v0.154.0.zip" <<'PY'
import zipfile,json,hashlib,sys
wp=zipfile.ZipFile(sys.argv[1]); root=wp.namelist()[0].split('/')[0]; m=json.loads(wp.read(root+'/build/sc-lab-release-manifest.json')); assert m['releaseVersion']=='0.154.0'; assert m['featureVersion']=='0.154.0'; names=set(wp.namelist()); missing=[]; mismatch=[]
for rel,expected in m.get('wordpressCriticalFiles',{}).items():
    n=root+'/'+rel
    if n not in names: missing.append(rel); continue
    if hashlib.sha256(wp.read(n)).hexdigest()!=expected: mismatch.append(rel)
assert not missing,(len(missing),missing[:10]); assert not mismatch,(len(mismatch),mismatch[:10])
php_issues=[]
for n in names:
    if n.endswith('.php') and not n.endswith('/'):
        data=wp.read(n)
        if data.startswith(b'\xef\xbb\xbf') or not data.startswith(b'<?php'): php_issues.append(n)
assert not php_issues,php_issues[:20]
be=zipfile.ZipFile(sys.argv[2]); broot=be.namelist()[0].split('/')[0]; bnames=set(be.namelist())
for rel,expected in m.get('backendCriticalFiles',{}).items():
    short=rel[len('backend/'):] if rel.startswith('backend/') else rel; n=broot+'/backend/'+short; assert n in bnames,rel; assert hashlib.sha256(be.read(n)).hexdigest()==expected,rel
for n in [broot+'/backend/app/reproducible_protocol_notebook_v01540.py',broot+'/backend/tests/test_reproducible_protocol_notebook_v01540.py',broot+'/backend/app/computational_research_workspace_v01530.py']:
    assert n in bnames,n
for rel in ['assets/js/sc-lab-safe-bootstrap-v01540.js','assets/js/sc-lab-linked-scientific-views-v01540.js','assets/js/sc-lab-scene-persistence-provenance-handoff-v01540.js','assets/js/sc-lab-4d-computational-research-workspace-v01540.js','assets/js/sc-lab-reproducible-protocol-notebook-v01540.js','assets/css/sc-lab-reproducible-protocol-notebook-v01540.css','includes/class-sc-lab-reproducible-protocol-notebook-v01540.php','contracts/lab-reproducible-protocol-v01540.schema.json','contracts/lab-computational-notebook-v01540.schema.json','contracts/lab-notebook-reproduction-manifest-v01540.schema.json']:
    assert root+'/'+rel in names,rel
print(f"PASS: packaged WordPress manifest verifies {len(m['wordpressCriticalFiles'])} immutable runtime files; backend verifies {len(m['backendCriticalFiles'])} files")
print(f"PASS: packaged WordPress PHP output-safety verifies {sum(1 for n in names if n.endswith('.php'))} PHP files")
print('releaseVersion='+m['releaseVersion']);print('featureVersion='+m['featureVersion']);print('buildFingerprint='+m['buildFingerprint'])
PY
cp "$ROOT/PUSH_LAB_V01540_FINAL.sh" "$ROOT/DEPLOY_LAB_V01540_CONTABO.sh" "$ROOT/DEPLOY_LAB_WORDPRESS_V01540_BLUEHOST.sh" "$ROOT/VALIDATE_LAB_V01540.sh" "$ROOT/PACKAGE_LAB_V01540.sh" "$ROOT/CHECK_LAB_PHP_OUTPUT_SAFETY.py" "$ROOT/BUILD_LAB_V01540.md" "$ROOT/LAB_REPRODUCIBLE_PROTOCOL_COMPUTATIONAL_NOTEBOOK_WORKSPACE_0.154.0.md" "$ROOT/RELEASE_NOTES_0.154.0_REPRODUCIBLE_PROTOCOL_COMPUTATIONAL_NOTEBOOK_WORKSPACE.md" "$ROOT/DEPLOY_LAB_BACKEND_v0.154.0.md" "$OUT/"
( cd "$OUT" && sha256sum sustainable-catalyst-lab-v0.154.0-repository.zip sustainable-catalyst-lab-v0.154.0-wordpress.zip sustainable-catalyst-lab-backend-v0.154.0.zip > SHA256SUMS.txt )
release_stage="$(mktemp -d)"; cp -a "$OUT/." "$release_stage/"; ( cd "$release_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.154.0-release-bundle.zip" . ); rm -rf "$release_stage"; ( cd "$OUT" && sha256sum sustainable-catalyst-lab-v0.154.0-release-bundle.zip >> SHA256SUMS.txt )
echo "PASS - Lab v0.154.0 packages written to $OUT"
