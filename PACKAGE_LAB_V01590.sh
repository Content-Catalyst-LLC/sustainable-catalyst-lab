#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")"&&pwd)}";OUT="${2:-$HOME/Downloads/sc-lab-v0.159.0-artifacts}";cd "$ROOT"
if [ -f CHECK_LAB_PHP_OUTPUT_SAFETY.py ];then python3 CHECK_LAB_PHP_OUTPUT_SAFETY.py "$ROOT";fi
python3 - <<'PY2'
from pathlib import Path
import json,hashlib,datetime
root=Path('.');p=root/'build/sc-lab-release-manifest.json';m=json.loads(p.read_text());include_roots=('assets/','includes/','templates/','contracts/','build/');wp={}
for f in sorted(root.rglob('*')):
 if not f.is_file():continue
 rel=f.as_posix().lstrip('./')
 if rel=='build/sc-lab-release-manifest.json':continue
 if rel=='sustainable-catalyst-lab.php' or rel.startswith(include_roots):
  if rel.startswith('data/'):continue
  wp[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
backend={}
for f in sorted((root/'backend').rglob('*')):
 if not f.is_file():continue
 rel=f.as_posix()
 if '/data/' in '/'+rel or '__pycache__' in rel or '.pytest_cache' in rel or rel.endswith('.pyc'):continue
 backend[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
m['wordpressCriticalFiles']=wp;m['backendCriticalFiles']=backend;m['criticalFiles']={};m['generatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();m['buildFingerprint']=hashlib.sha256('\n'.join(f'{k}:{v}' for k,v in wp.items()).encode()).hexdigest();p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');print(f'Generated WordPress manifest with {len(wp)} files; backend manifest with {len(backend)} files')
PY2
"$ROOT/VALIDATE_LAB_V01590.sh" "$ROOT"
rm -rf "$OUT";mkdir -p "$OUT";repo_stage="$(mktemp -d)";plugin_stage="$(mktemp -d)";backend_stage="$(mktemp -d)";trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.159.0/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.159.0/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete --exclude='.git/' --exclude='/backend/' --exclude='/tests/' --exclude='/scripts/' --exclude='/sdk/' --exclude='/examples/' --exclude='/docs/' --exclude='/data/' --exclude='dist-v0.159.0/' --exclude='*.zip' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='data/' --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.159.0/backend/"
(cd "$repo_stage"&&zip -qr "$OUT/sustainable-catalyst-lab-v0.159.0-repository.zip" sustainable-catalyst-lab-main)
(cd "$plugin_stage"&&zip -qr "$OUT/sustainable-catalyst-lab-v0.159.0-wordpress.zip" sustainable-catalyst-lab)
(cd "$backend_stage"&&zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.159.0.zip" sustainable-catalyst-lab-backend-v0.159.0)
python3 - "$OUT/sustainable-catalyst-lab-v0.159.0-wordpress.zip" "$OUT/sustainable-catalyst-lab-backend-v0.159.0.zip" <<'PY2'
import zipfile,json,hashlib,sys
wp=zipfile.ZipFile(sys.argv[1]);root=wp.namelist()[0].split('/')[0];m=json.loads(wp.read(root+'/build/sc-lab-release-manifest.json'));assert m['releaseVersion']=='0.159.0';names=set(wp.namelist())
for rel,exp in m['wordpressCriticalFiles'].items():n=root+'/'+rel;assert n in names,rel;assert hashlib.sha256(wp.read(n)).hexdigest()==exp,rel
be=zipfile.ZipFile(sys.argv[2]);br=be.namelist()[0].split('/')[0];bn=set(be.namelist())
for rel,exp in m['backendCriticalFiles'].items():short=rel[len('backend/'):] if rel.startswith('backend/') else rel;n=br+'/backend/'+short;assert n in bn,rel;assert hashlib.sha256(be.read(n)).hexdigest()==exp,rel
for rel in ['includes/class-sc-lab-integrated-scientific-review-validation-publication-gate-v01590.php','assets/js/sc-lab-integrated-scientific-review-publication-gate-v01590.js','assets/css/sc-lab-integrated-scientific-review-publication-gate-v01590.css','contracts/lab-review-publication-manifest-v01590.schema.json']:assert root+'/'+rel in names,rel
assert br+'/backend/app/integrated_scientific_review_validation_publication_gate_v01590.py' in bn
print('PASS - packaged v0.159.0 manifest and required files verify')
PY2
for f in PUSH_LAB_V01590_FINAL.sh DEPLOY_LAB_V01590_CONTABO.sh DEPLOY_LAB_WORDPRESS_V01590_BLUEHOST.sh VALIDATE_LAB_V01590.sh PACKAGE_LAB_V01590.sh BUILD_LAB_V01590.md LAB_INTEGRATED_SCIENTIFIC_REVIEW_VALIDATION_PUBLICATION_GATE_0.159.0.md RELEASE_NOTES_0.159.0_INTEGRATED_SCIENTIFIC_REVIEW_VALIDATION_PUBLICATION_GATE.md DEPLOY_LAB_BACKEND_v0.159.0.md;do [ -f "$ROOT/$f" ]&&cp "$ROOT/$f" "$OUT/";done
(cd "$OUT"&&sha256sum sustainable-catalyst-lab-v0.159.0-repository.zip sustainable-catalyst-lab-v0.159.0-wordpress.zip sustainable-catalyst-lab-backend-v0.159.0.zip>SHA256SUMS.txt)
release_stage="$(mktemp -d)";cp -a "$OUT/." "$release_stage/";(cd "$release_stage"&&zip -qr "$OUT/sustainable-catalyst-lab-v0.159.0-release-bundle.zip" .);rm -rf "$release_stage";(cd "$OUT"&&sha256sum sustainable-catalyst-lab-v0.159.0-release-bundle.zip>>SHA256SUMS.txt)
echo "PASS - Lab v0.159.0 packages written to $OUT"
