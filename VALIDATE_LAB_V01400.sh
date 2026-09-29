#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$ROOT"
python3 -m py_compile backend/app/scientific_research_operating_system_v01400.py backend/app/main.py
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-scientific-research-operating-system-v01400.php >/dev/null
node tests/test-v01400.js
(
  cd backend
  python3 -m pytest -q \
    tests/test_scientific_research_operating_system_v01400.py \
    tests/test_scholarly_study_original_research_package_v01390.py \
    tests/test_research_program_intelligence_v01380.py \
    tests/test_research_change_impact_living_analysis_v01370.py
)
php tests/test-v01400-release-integrity.php
python3 - <<'PY'
from backend.app.main import app
paths={x.path for x in app.routes if isinstance(getattr(x,'path',None),str)}
req={x for x in paths if x.startswith('/v1/scientific-research-operating-system/v01400')}
assert len(req)==25, len(req)
print('PASS: 25 v0.140.0 FastAPI routes registered')
PY
echo 'PASS - Lab v0.140.0 local validation complete.'
