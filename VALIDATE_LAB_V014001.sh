#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$ROOT"
python3 -m py_compile backend/app/scientific_research_operating_system_v01400.py backend/app/main.py
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-scientific-research-operating-system-v01400.php >/dev/null
php -l includes/class-sc-lab-integrity-v02632.php >/dev/null
php tests/test-v014001-release-integrity.php
node tests/test-v01400.js
(
  cd backend
  python3 -m pytest -q \
    tests/test_scientific_research_operating_system_v01400.py \
    tests/test_scholarly_study_original_research_package_v01390.py \
    tests/test_research_program_intelligence_v01380.py \
    tests/test_research_change_impact_living_analysis_v01370.py
)
python3 - <<'PY2'
import json,re
m=json.load(open('build/sc-lab-release-manifest.json'))
assert m['releaseVersion']=='0.140.0.1'
assert m['featureVersion']=='0.140.0.1'
assert m['scientificResearchOperatingSystemVersion']=='0.140.0'
assert m['v01400RequiredRouteCount']==25 and m['v014001RequiredRouteCount']==25
files=m.get('wordpressCriticalFiles',{})
assert files and len(files)>100
for p in files:
    assert not re.match(r'^(backend|data|tests|scripts|sdk|examples|docs)/',p),p
print(f'PASS: {len(files)} immutable WordPress runtime files in v0.140.0.1 manifest')
# Canonical route contract check mirrors the production integrity layer.
tpl=open('templates/lab-app.php',encoding='utf-8').read()
alias_src=open('includes/class-sc-lab-runtime-repair-v02631.php',encoding='utf-8').read()
contracts={'marine':'marine-biology','climate':'climate-maps','evidence':'evidence-decisions','astronomy-observations':'space-telescopes'}
for alias,canonical in contracts.items():
    assert f"'{alias}' => '{canonical}'" in alias_src,(alias,canonical)
    assert re.search(r'data-lab-module=([\"\'])'+re.escape(canonical)+r'\1',tpl),canonical
print('PASS: canonical Lab route contracts and target panels verified')
from backend.app.main import app
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}
req={x for x in paths if x.startswith('/v1/scientific-research-operating-system/v01400')}
assert len(req)==25,len(req)
print('PASS: 25 v0.140.0 Scientific Research OS FastAPI routes preserved')
PY2
echo 'PASS - Lab v0.140.0.1 local validation complete.'
