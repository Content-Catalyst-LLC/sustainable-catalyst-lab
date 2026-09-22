#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/backend"

echo "==> v0.115.0 statistical visualization + Core integration regression suite"
"$PYTHON_BIN" -m pytest -q \
 backend/tests/test_platform_core_v3_*.py \
 backend/tests/test_visualization_engine_v0730.py \
 backend/tests/test_visualization_engine_v0740.py \
 backend/tests/test_large_data_visualization_v0760.py \
 backend/tests/test_scientific_scene_v0770.py \
 backend/tests/test_linked_views_v0790.py \
 backend/tests/test_uncertainty_ensemble_distribution_v0820.py \
 backend/tests/test_provenance_aware_figures_v0830.py \
 backend/tests/test_gpu_renderer_architecture_v0840.py \
 backend/tests/test_webgl2_scientific_renderer_v0850.py \
 backend/tests/test_webgpu_scientific_renderer_v0870.py \
 backend/tests/test_advanced_scientific_scene_v0880.py \
 backend/tests/test_scientific_visualization_design_system_v01140.py \
 backend/tests/test_advanced_statistical_uncertainty_graphics_v01150.py

echo "==> v0.115.0 required FastAPI routes + behavior fixtures"
"$PYTHON_BIN" - <<'PYTEST'
from app.main import app
from app.advanced_statistical_uncertainty_graphics_v01150 import *
paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
base='/v1/advanced-statistical-uncertainty-graphics'
required={f'{base}/health',f'{base}/manifest',f'{base}/catalog',f'{base}/distributions/normalize',f'{base}/distributions/kde',f'{base}/distributions/figure',f'{base}/intervals/figure',f'{base}/fan-chart/figure',f'{base}/posterior/figure',f'{base}/coefficients/forest',f'{base}/calibration/reliability',f'{base}/diagnostics/residuals',f'{base}/qq/figure',f'{base}/sensitivity/figure',f'{base}/uncertainty/decomposition',f'{base}/coverage/figure',f'{base}/small-multiples/compose',f'{base}/publication/build'}
assert not(required-paths),sorted(required-paths)
pub={'caption':'Deployment statistical fixture.','source':'Deployment fixture.','method':'Declared fixture method.'}
cal=build_calibration_figure({'bins':[{'predicted':.1,'observed':.2,'count':20},{'predicted':.8,'observed':.75,'count':30}],'publication':pub})
assert cal['graphic_type']=='calibration-reliability' and cal['statistical_metadata']['automatic_model_quality_certification'] is False
fan=build_fan_chart({'quantile_levels':[.1,.25,.5,.75,.9],'records':[{'x':0,'values':[1,2,3,4,5]},{'x':1,'values':[2,3,4,5,6]}],'publication':pub}); assert len(fan['statistical_metadata']['bands'])==2
sens=build_sensitivity_figure({'method':'sobol','indices':[{'parameter':'a','st':.8,'s1':.6},{'parameter':'b','st':.2,'s1':.1}],'publication':pub}); assert sens['statistical_metadata']['ranked_effects'][0]['name']=='a' and sens['statistical_metadata']['automatic_significance_inference'] is False
cov=build_coverage_figure({'records':[{'lower':0,'upper':2,'truth':1},{'lower':0,'upper':1,'truth':2}],'publication':pub}); assert cov['statistical_metadata']['coverage_rate']==.5
publication=build_publication_figure({'advanced_figure':cal,'profile':'journal-double','alt_text':'Reliability diagram comparing predicted probabilities and observed frequencies.'}); assert publication['publication_ready'] is True and publication['scientific_validity_certified'] is False
m=manifest(); assert m['graphic_type_count']==16 and m['boundaries']['automatic_truth_determination'] is False
print(f'INFO: {len(paths)} FastAPI path routes registered')
print('PASS: eighteen v0.115 advanced statistical/uncertainty graphics routes loaded')
print('PASS: calibration, fan chart, sensitivity, coverage, publication, and explicit-assumption boundaries verified')
PYTEST

echo "==> v0.115.0 mirrored JSON contracts"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import json
for name in ['advanced-statistical-uncertainty-graphics-v01150.schema.json','advanced-statistical-uncertainty-graphics-policy-v01150.json']:
 a=Path('contracts',name).read_bytes(); b=Path('backend/contracts',name).read_bytes(); json.loads(a); json.loads(b); assert a==b,name
print('PASS - v0.115 statistical-graphics contracts parse and mirror byte-for-byte')
PYTEST

echo "==> v0.115.0 PHP syntax + WordPress assertions"
php -l sustainable-catalyst-lab.php >/dev/null
php -l includes/class-sc-lab-plugin.php >/dev/null
php -l includes/class-sc-lab-advanced-statistical-uncertainty-graphics-v01150.php >/dev/null
php tests/test-v01150.php

echo "==> v0.115.0 release identity + manifest integrity"
"$PYTHON_BIN" - <<'PYTEST'
from pathlib import Path
import hashlib,json,re
m=json.loads(Path('build/sc-lab-release-manifest.json').read_text())
assert m['releaseVersion']=='0.115.0' and m['featureVersion']=='0.115.0'
assert m['advancedStatisticalUncertaintyGraphicsVersion']=='0.115.0'
assert m['v01150RequiredRouteCount']==18 and m['v01150GraphicTypeCount']==16
assert re.search(r'^ \* Version: 0\.115\.0$',Path('sustainable-catalyst-lab.php').read_text(),re.M)
for section in ('wordpressCriticalFiles','backendCriticalFiles'):
 for rel,expected in m[section].items():
  p=Path(rel); assert p.is_file(),rel; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
print(f"PASS - v0.115.0 manifest integrity ({len(m['wordpressCriticalFiles'])} WordPress runtime + {len(m['backendCriticalFiles'])} backend files)")
PYTEST

echo "PASS - Sustainable Catalyst Lab v0.115.0 Advanced Statistical & Uncertainty Graphics release gate"
