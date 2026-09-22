#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> v0.112.0 integration/regression tests"
PYTHONPATH=backend "$PYTHON_BIN" -m pytest -q \
  backend/tests/test_platform_core_v3_adapter_v01040.py \
  backend/tests/test_platform_core_v3_object_mapping_v01050.py \
  backend/tests/test_platform_core_v3_research_context_v01060.py \
  backend/tests/test_platform_core_v3_execution_lineage_v01070.py \
  backend/tests/test_platform_core_v3_findings_validation_v01080.py \
  backend/tests/test_platform_core_v3_visual_scene_v01090.py \
  backend/tests/test_platform_core_v3_scholarly_package_v01100.py \
  backend/tests/test_platform_core_v3_scientific_investigation_v01110.py \
  backend/tests/test_platform_core_v3_integration_certification_v01120.py \
  backend/tests/test_scientific_study_lifecycle_v0610.py \
  backend/tests/test_scientific_claims_traceability_v0620.py \
  backend/tests/test_scientific_evidence_grading_v0650.py \
  backend/tests/test_scientific_argumentation_v0660.py \
  backend/tests/test_causal_inference_v0670.py \
  backend/tests/test_reproducible_model_package_v0500.py

echo "==> v0.112.0 FastAPI certification contract fixture"
PYTHONPATH=backend "$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.platform_core_v3_integration_certification_v01120 import (
 CASE_CATALOG,PRODUCT_REF,assess_roundtrip,build_case_plans,build_full_submission_plan,
 build_product_plan,build_run_plan,build_suite_plan,catalog,compatibility_report,health,manifest
)
path_routes=[r for r in app.routes if isinstance(getattr(r,'path',None),str)]; paths={r.path for r in path_routes}
base='/v1/platform-core-v3-integration-certification'
required={
 f'{base}/health',f'{base}/manifest',f'{base}/schema',f'{base}/catalog',f'{base}/suites/plan',f'{base}/products/plan',f'{base}/cases/plan',f'{base}/runs/plan',
 f'{base}/case-results/plan',f'{base}/exchange-checks/plan',f'{base}/trace-checks/plan',f'{base}/reproduction-checks/plan',f'{base}/evidence/plan',f'{base}/findings/plan',
 f'{base}/roundtrip/assess',f'{base}/compatibility/check',f'{base}/full-plan',
 '/v1/platform-core-v3-scientific-investigations/health','/v1/platform-core-v3-scholarly-packages/health','/v1/platform-core-v3-visual-scene/health',
 '/v1/platform-core-v3-research-intelligence/health','/v1/platform-core-v3-executions/health','/v1/platform-core-v3-context/health','/v1/platform-core-v3-objects/health','/v1/platform-core-v3-adapter/health'}
assert not (required-paths),sorted(required-paths)
ctx={'project_ref':'project:p1','session_id':'12','session_key':'s12','title':'Certification','workflow_ref':'lab:workflow:w1','project_state_ref':'core:state:12','researcher_ref':'researcher:r1'}
s=build_suite_plan({'context':ctx}); p=build_product_plan({'suite_id':'suite:1'}); c=build_case_plans({'suite_id':'suite:1'}); r=build_run_plan({'suite_id':'suite:1','product_id':'product-row:1'}); full=build_full_submission_plan({'context':ctx})
assert s['automatic_submission'] is False and p['data']['product_ref']==PRODUCT_REF and c['count']==18 and r['automatic_product_invocation'] is False and len(full['steps'])==7
results=[{'case_key':x[0],'status':'pass'} for x in CASE_CATALOG]; a=assess_roundtrip({'results':results}); assert a['declared_conformance'] is True and a['scientific_validity_certified'] is False and a['truth_determined'] is False
ready={'release':'3.1.0','contract':'sc.research.platform-integration-certification.v1'}
for k in ('certification_suite_registry_by_core','certification_product_registry_by_core','conformance_case_registry_by_core','conformance_run_registry_by_core','conformance_result_registry_by_core','exchange_check_registry_by_core','trace_check_registry_by_core','reproduction_check_registry_by_core','certification_evidence_registry_by_core','certification_finding_registry_by_core','revision_history_by_core','immutable_certification_snapshots_by_core'): ready[k]=True
for k in ('invoke_product_by_core','execute_conformance_case_by_core','certify_scientific_validity_by_core','certify_product_quality_by_core','authorize_product_by_certification_by_core','rank_products_by_core','infer_missing_evidence_by_core','infer_reproducibility_by_core','resolve_failed_case_by_core','determine_truth_by_core'): ready[k]=False
assert compatibility_report(ready)['status']=='compatible'
h=health(); m=manifest(); cat=catalog(); assert h['lab_release_version']=='0.112.0' and h['certified_layer_count']==8 and cat['case_count']==18; assert m['boundaries']['core_determines_truth'] is False
print(f'PASS - {len(path_routes)} FastAPI path routes registered (informational only)')
print('PASS - seventeen v0.112.0 integration-certification endpoints plus retained v0.104-v0.111 surfaces')
print('PASS - eight integration layers and eighteen required conformance cases')
print('PASS - Core certification plans remain explicit and non-submitting')
print('PASS - product invocation, case execution, scientific/product-quality certification, ranking, inferred reproducibility, remediation, and truth determination remain disabled')
PYTEST

echo "==> v0.112.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
names=['platform-core-v3-integration-certification-v01120.schema.json','platform-core-v3-integration-certification-policy-v01120.json']
for name in names:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.112 integration-certification contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.112.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-platform-core-v3-integration-certification-v01120.php >/dev/null
php tests/test-v01120.php

echo "==> v0.112.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.112.0' and m['featureVersion']=='0.112.0'
assert m['platformCoreMinimumVersion']=='3.0.0'
assert m['platformCoreIntegrationCertificationVersion']=='0.112.0'
assert m['platformCoreIntegrationCertificationContract']=='sc.research.platform-integration-certification.v1'
assert m['v01120RequiredRouteCount']==17 and m['v01120CertifiedLayerCount']==8 and m['v01120ConformanceCaseCount']==18
assert re.search(r'^ \* Version: 0\.112\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.112.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.112.0 Platform Core Integration Certification release gate"
