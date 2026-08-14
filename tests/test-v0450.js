'use strict';
const fs=require('fs');
const read=p=>fs.readFileSync(p,'utf8');
const studio=read('assets/js/modules/model-studio-v0450.js');
const engine=read('assets/js/modules/scientific-visualization-engine-v0440.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
 [studio.includes("VERSION='0.45.0'"),'Model Studio browser release version'],
 [studio.includes('dynamicSystem')&&studio.includes('simulateDynamic')&&studio.includes('estimateDynamic'),'dynamic-system browser workflow'],
 [studio.includes('X: -k*X')&&studio.includes('S: -beta*S*I/Pop'),'ODE templates wired'],
 [studio.includes("api('dynamic-systems/simulate'")&&studio.includes("api('dynamic-systems/estimate'"),'dynamic-system compute calls'],
 [studio.includes('ScientificVisualizationEngineV0440'),'v0.45 consumes shared v0.44 graph engine'],
 [engine.includes('wheel')&&engine.includes('pointerdown'),'interactive graph foundation retained'],
 [template.includes('Dynamic Systems, ODE Models &amp; Parameter Estimation'),'v0.45 Model Studio heading'],
 [template.includes('data-ms-v0450-dynamic-equations'),'derivative-equation UI'],
 [template.includes('data-ms-v0450-dynamic-simulate'),'ODE simulation action'],
 [template.includes('data-ms-v0450-dynamic-estimate'),'parameter-estimation action'],
 [template.includes('data-ms-v0450-dynamic-phase'),'phase-portrait surface'],
 [template.includes('data-ms-v0450-dynamic-residual'),'estimation residual surface'],
 [plugin.includes("'scientific-visualization-engine-v0440','model-studio-v0450'"),'shared graph engine loads before v0.45 Model Studio'],
 [compute.includes('/compute/core/model-studio/dynamic-systems/simulate')&&compute.includes('/compute/core/model-studio/dynamic-systems/estimate'),'WordPress compute proxies registered']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
