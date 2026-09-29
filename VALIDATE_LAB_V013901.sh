#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$ROOT"
python3 -m py_compile backend/app/release_integrity_scope_repair_v013901.py backend/app/main.py
php -l sustainable-catalyst-lab.php >/dev/null
python3 - <<'PY'
from backend.app.main import app
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}
required={
 '/v1/release-integrity-scope-repair/v013901/health',
 '/v1/release-integrity-scope-repair/v013901/policy',
 '/v1/scholarly-study-original-research-package/v01390/health',
 '/v1/research-program-intelligence/v01380/health',
 '/v1/research-change-impact/v01370/health',
}
missing=sorted(required-paths)
assert not missing, missing
print('PASS: v0.139.0.1 repair routes and predecessor health routes registered')
PY
(
  cd backend
  python3 -m pytest -q \
    tests/test_release_integrity_scope_repair_v013901.py \
    tests/test_scholarly_study_original_research_package_v01390.py \
    tests/test_research_program_intelligence_v01380.py \
    tests/test_research_change_impact_living_analysis_v01370.py
)
python3 - <<'PY'
import json, hashlib
from pathlib import Path
root=Path('.')
m=json.loads((root/'build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.139.0.1'
assert m['featureVersion']=='0.139.0.1'
missing=[]; bad=[]
for rel, expected in m.get('wordpressCriticalFiles',{}).items():
    p=root/rel
    if not p.is_file(): missing.append(rel); continue
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected: bad.append(rel)
assert not missing, ('missing WordPress critical files in source', missing[:10])
assert not bad, ('WordPress critical hash mismatch', bad[:10])
print(f"PASS: source manifest verifies {len(m.get('wordpressCriticalFiles',{}))} WordPress-shipped files")
PY
echo 'PASS - Lab v0.139.0.1 local validation complete.'
