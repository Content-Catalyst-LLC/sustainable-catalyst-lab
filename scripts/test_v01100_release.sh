#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.110.0 integration/regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_platform_core_v3_findings_validation_v01080.py \
  backend/tests/test_platform_core_v3_visual_scene_v01090.py \
  backend/tests/test_platform_core_v3_scholarly_package_v01100.py \
  backend/tests/test_reproducible_runs_v0282.py \
  backend/tests/test_publication_studio_v0370.py \
  backend/tests/test_manuscript_assembly_v0371.py \
  backend/tests/test_public_reproduction_portal_v0372.py \
  backend/tests/test_reproducible_model_package_v0500.py

echo "==> v0.110.0 FastAPI package/scholarly contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_scholarly_package_v01100 import (
 build_core_package_binding,build_provenance_manifest,build_scholarly_interoperability_plan,
 bridge_citations,bridge_datasets_notebooks,health,manifest,map_legacy_package,normalize_package
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
required={
'/v1/platform-core-v3-scholarly-packages/health','/v1/platform-core-v3-scholarly-packages/manifest','/v1/platform-core-v3-scholarly-packages/schema',
'/v1/platform-core-v3-scholarly-packages/packages/normalize','/v1/platform-core-v3-scholarly-packages/packages/bind',
'/v1/platform-core-v3-scholarly-packages/scholarly/package','/v1/platform-core-v3-scholarly-packages/scholarly/plan',
'/v1/platform-core-v3-scholarly-packages/citations/bridge','/v1/platform-core-v3-scholarly-packages/descriptors/bridge',
'/v1/platform-core-v3-scholarly-packages/provenance/manifest','/v1/platform-core-v3-scholarly-packages/publications/bind',
'/v1/platform-core-v3-scholarly-packages/validations/record','/v1/platform-core-v3-scholarly-packages/legacy-package/map',
'/v1/platform-core-v3-visual-scene/health','/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-executions/health','/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'9','session_key':'s1','title':'Study','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:1','researcher_ref':'researcher:r1'}
pkg={'schema':'sc-lab-reproducibility-package/0.37.0','id':'pkg1','title':'Replication package','packageVersion':'1.2.0','packageHash':'a'*64,'resources':[{'id':'d1','object_ref':'lab:dataset:d1'},{'id':'fig1','object_ref':'lab:visual:fig1'}],'citations':[{'cited_object_ref':'library:source:s1','citation_format':'csl-json','citation_data':{'title':'Source'}}],'datasets':[{'id':'d1','dataset_ref':'lab:dataset:d1','content_hash':'b'*64}],'notebooks':[{'id':'n1','notebook_ref':'lab:notebook:n1','environment_ref':'lab:env:e1','execution_ref':'lab:execution:r1'}]}
n=normalize_package({'context':ctx,'package':pkg}); assert n['package']['package_type']=='replication_package'
b=build_core_package_binding({'context':ctx,'package':pkg}); assert b['automatic_submission'] is False and b['data']['package_ref']=='lab:reproducibility-package:pkg1'
plan=build_scholarly_interoperability_plan({'context':ctx,'package':pkg}); assert plan['operation_count']>=5 and plan['automatic_reproducibility_certification'] is False
cit=bridge_citations({'context':ctx,'package':pkg}); desc=bridge_datasets_notebooks({'context':ctx,'package':pkg}); prov=build_provenance_manifest({'context':ctx,'package':pkg})
assert cit['requires_core_package_id'] is True and desc['requires_core_package_id'] is True and prov['lineage_is_declared_not_inferred'] is True
legacy=map_legacy_package({'context':ctx,'package':pkg}); assert legacy['automatic_publication'] is False and legacy['automatic_certification'] is False
h=health(); m=manifest(); assert h['lab_release_version']=='0.110.0' and h['minimum_core_release']=='3.0.0'; assert m['boundaries']['core_certifies_reproducibility'] is False
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - thirteen v0.110.0 scholarly-package endpoints plus retained v0.104-v0.109 surfaces')
print('PASS - Lab reproducibility/publication packages map to reference-first Core package contracts')
print('PASS - citations/descriptors/provenance remain declared interoperability metadata')
print('PASS - Core publication, identifier minting, notebook execution, scientific validation, and reproducibility certification remain disabled')
PYTEST

echo "==> v0.110.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-scholarly-package-v01100.schema.json','platform-core-v3-scholarly-package-policy-v01100.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.110 scholarly-package contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.110.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-scholarly-package-v01100.php >/dev/null
php tests/test-v01100.php

echo "==> v0.110.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.110.0' and m['featureVersion']=='0.110.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreReproducibilityScholarlyPackageVersion']=='0.110.0'
assert m['v01100RequiredRouteCount']==13
assert re.search(r'^ \* Version: 0\.110\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.110.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.110.0 Reproducibility & Scholarly Package Bridge release gate"
