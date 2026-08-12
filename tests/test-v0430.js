'use strict';
const fs=require('fs');
function read(path){return fs.readFileSync(path,'utf8');}
const engine=read('assets/js/modules/scientific-visualization-engine-v0410.js');
const studio=read('assets/js/modules/model-studio-v0430.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const proxy=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
  [engine.includes("VERSION='0.41.0'"),'shared graph engine remains v0.41 foundation'],
  [studio.includes("VERSION='0.43.0'"),'Model Studio browser release version'],
  [studio.includes("MODEL_SCHEMA='sc-lab-model-studio-model/0.43.0'"),'v0.43 model contract'],
  [studio.includes("cross-validation/run"),'cross-validation endpoint integration'],
  [studio.includes("diagnostics/run"),'diagnostics endpoint integration'],
  [studio.includes("comparison/run"),'scientific comparison endpoint integration'],
  [studio.includes('renderDiagnosticGraphs'),'diagnostic graph rendering'],
  [studio.includes('akaikeWeight'),'Akaike evidence display'],
  [template.includes('data-ms-v0430-run-cv'),'cross-validation UI action'],
  [template.includes('data-ms-v0430-observed-graph'),'observed-vs-predicted surface'],
  [template.includes('data-ms-v0430-residual-graph'),'residual diagnostic surface'],
  [template.includes('data-ms-v0430-qq-graph'),'Q-Q diagnostic surface'],
  [template.includes('data-ms-v0430-comparison-models'),'multi-model comparison selector'],
  [plugin.includes("'scientific-visualization-engine-v0410','model-studio-v0430'"),'shared engine loads before v0.43 Model Studio'],
  [proxy.includes('/compute/core/model-studio/cross-validation/run'),'WordPress CV proxy'],
  [proxy.includes('/compute/core/model-studio/comparison/run'),'WordPress comparison proxy']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
