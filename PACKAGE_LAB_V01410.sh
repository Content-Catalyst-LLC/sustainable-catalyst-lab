#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-$ROOT/dist-v0.141.0}"
rm -rf "$OUT"; mkdir -p "$OUT"
"$ROOT/VALIDATE_LAB_V01410.sh" "$ROOT"
repo_stage="$(mktemp -d)"; plugin_stage="$(mktemp -d)"; backend_stage="$(mktemp -d)"
trap 'rm -rf "$repo_stage" "$plugin_stage" "$backend_stage"' EXIT
mkdir -p "$repo_stage/sustainable-catalyst-lab-main" "$plugin_stage/sustainable-catalyst-lab" "$backend_stage/sustainable-catalyst-lab-backend-v0.141.0/backend"
rsync -a --delete --exclude='.git/' --exclude='dist-v0.139.0/' --exclude='dist-v0.139.0.1/' --exclude='dist-v0.140.0/' --exclude='dist-v0.141.0/' "$ROOT/" "$repo_stage/sustainable-catalyst-lab-main/"
rsync -a --delete \
  --exclude='.git/' --exclude='backend/' --exclude='/data/' --exclude='tests/' --exclude='scripts/' --exclude='sdk/' --exclude='examples/' --exclude='docs/' \
  --exclude='dist-v0.139.0/' --exclude='dist-v0.139.0.1/' --exclude='dist-v0.140.0/' --exclude='dist-v0.141.0/' --exclude='*.zip' \
  "$ROOT/" "$plugin_stage/sustainable-catalyst-lab/"
rsync -a --delete --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='*.pyc' "$ROOT/backend/" "$backend_stage/sustainable-catalyst-lab-backend-v0.141.0/backend/"
(
  cd "$repo_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.141.0-repository.zip" sustainable-catalyst-lab-main
  cd "$plugin_stage" && zip -qr "$OUT/sustainable-catalyst-lab-v0.141.0-wordpress.zip" sustainable-catalyst-lab
  cd "$backend_stage" && zip -qr "$OUT/sustainable-catalyst-lab-backend-v0.141.0.zip" sustainable-catalyst-lab-backend-v0.141.0
)
python3 - "$OUT/sustainable-catalyst-lab-v0.141.0-wordpress.zip" <<'PY'
import sys, zipfile, tempfile, json, hashlib
from pathlib import Path
zp=Path(sys.argv[1])
with tempfile.TemporaryDirectory() as td:
    with zipfile.ZipFile(zp) as z: z.extractall(td)
    root=Path(td)/'sustainable-catalyst-lab'
    m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
    missing=[]; bad=[]
    for rel, exp in m.get('wordpressCriticalFiles',{}).items():
        p=root/rel
        if not p.is_file(): missing.append(rel); continue
        act=hashlib.sha256(p.read_bytes()).hexdigest()
        if act != exp: bad.append(rel)
    assert not missing, ('packaged manifest missing files', missing[:20])
    assert not bad, ('packaged manifest hash mismatch', bad[:20])
    print(f"PASS: packaged WordPress manifest verifies {len(m.get('wordpressCriticalFiles',{}))} files; 0 missing; 0 mismatched")
PY
cp "$ROOT/DEPLOY_LAB_V01410_CONTABO.sh" "$OUT/"
cp "$ROOT/PUSH_LAB_V01410_FINAL.sh" "$OUT/"
cp "$ROOT/VALIDATE_LAB_V01410.sh" "$OUT/"
cp "$ROOT/RELEASE_NOTES_0.141.0_MACHINE_LEARNING_EXPERIMENT_WORKSPACE.md" "$OUT/"
cp "$ROOT/MACHINE_LEARNING_EXPERIMENT_WORKSPACE_0.141.0.md" "$OUT/"
(
  cd "$OUT"
  shasum -a 256 sustainable-catalyst-lab-v0.141.0-repository.zip sustainable-catalyst-lab-v0.141.0-wordpress.zip sustainable-catalyst-lab-backend-v0.141.0.zip > SHA256SUMS.txt
  zip -qr sustainable-catalyst-lab-v0.141.0-release-bundle.zip \
    sustainable-catalyst-lab-v0.141.0-repository.zip sustainable-catalyst-lab-v0.141.0-wordpress.zip sustainable-catalyst-lab-backend-v0.141.0.zip \
    DEPLOY_LAB_V01410_CONTABO.sh PUSH_LAB_V01410_FINAL.sh VALIDATE_LAB_V01410.sh \
    RELEASE_NOTES_0.141.0_MACHINE_LEARNING_EXPERIMENT_WORKSPACE.md MACHINE_LEARNING_EXPERIMENT_WORKSPACE_0.141.0.md SHA256SUMS.txt
)
echo "PASS - Lab v0.141.0 artifacts packaged in $OUT"
