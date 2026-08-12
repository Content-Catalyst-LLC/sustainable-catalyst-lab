'use strict';
const fs=require('fs');
function read(path){return fs.readFileSync(path,'utf8');}
const engine=read('assets/js/modules/scientific-visualization-engine-v0410.js');
const studio=read('assets/js/modules/model-studio-v0410.js');
const numerical=read('assets/js/modules/numerical-visualization-studio.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const checks=[
  [engine.includes("VERSION='0.41.0'"),'shared graph engine version'],
  [engine.includes("spec.kind==='scatter'"),'true scatter rendering'],
  [engine.includes('niceTicks'),'numerical ticks'],
  [engine.includes('sc-sve0410-tooltip'),'tooltip inspection'],
  [studio.includes("MODEL_SCHEMA='sc-lab-model-studio-model/0.41.0'"),'model contract'],
  [studio.includes('model-calibration'),'calibration handoff'],
  [studio.includes('model-registry'),'registry handoff'],
  [numerical.includes('ScientificVisualizationEngineV0410.render'),'legacy numerical studio delegates to shared renderer'],
  [template.includes('data-lab-module="model-studio"'),'Model Studio panel'],
  [template.includes('data-ms-v0410-graph'),'Model Studio graph host'],
  [plugin.includes("'scientific-visualization-engine-v0410','model-studio-v0410'"),'engine loads before Model Studio']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
