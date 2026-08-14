'use strict';
const fs=require('fs');
const read=p=>fs.readFileSync(p,'utf8');
const studio=read('assets/js/modules/model-studio-v0460.js');
const engine=read('assets/js/modules/scientific-visualization-engine-v0440.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
 [studio.includes("VERSION='0.46.0'"),'Model Studio browser release version'],
 [studio.includes('surfaceStudy')&&studio.includes('fitSurface')&&studio.includes('exploreSurface')&&studio.includes('optimizeSurface'),'response-surface browser workflow'],
 [studio.includes("api('response-surfaces/fit'")&&studio.includes("api('response-surfaces/explore'")&&studio.includes("api('response-surfaces/optimize'"),'response-surface compute calls'],
 [studio.includes('T=20:80:C')&&studio.includes('Catalyst yield response surface'),'response-surface example wired'],
 [studio.includes('ScientificVisualizationEngineV0440'),'v0.46 consumes shared v0.44 graph engine'],
 [engine.includes("spec.kind==='heatmap'")&&engine.includes('wheel')&&engine.includes('pointerdown'),'interactive heatmap/graph foundation retained'],
 [template.includes('Response Surfaces, Optimization &amp; Design-Space Exploration'),'v0.46 Model Studio heading'],
 [template.includes('data-ms-v0460-surface-factors'),'factor-bound UI'],
 [template.includes('data-ms-v0460-surface-fit'),'surface-fit action'],
 [template.includes('data-ms-v0460-surface-explore'),'design-space exploration action'],
 [template.includes('data-ms-v0460-surface-optimize'),'bounded optimization action'],
 [template.includes('data-ms-v0460-surface-heatmap'),'response-surface heatmap surface'],
 [plugin.includes("'scientific-visualization-engine-v0440','model-studio-v0460'"),'shared graph engine loads before v0.46 Model Studio'],
 [compute.includes('/compute/core/model-studio/response-surfaces/fit')&&compute.includes('/compute/core/model-studio/response-surfaces/explore')&&compute.includes('/compute/core/model-studio/response-surfaces/optimize'),'WordPress response-surface compute proxies registered']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
