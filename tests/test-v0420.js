'use strict';
const fs=require('fs');
function read(path){return fs.readFileSync(path,'utf8');}
const engine=read('assets/js/modules/scientific-visualization-engine-v0410.js');
const studio=read('assets/js/modules/model-studio-v0420.js');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const checks=[
  [engine.includes("VERSION='0.41.0'"),'shared graph engine remains v0.41 foundation'],
  [studio.includes("VERSION='0.42.0'"),'Model Studio browser release version'],
  [studio.includes("MODEL_SCHEMA='sc-lab-model-studio-model/0.42.0'"),'v0.42 model contract'],
  [studio.includes("equations/validate"),'equation validation endpoint'],
  [studio.includes("equations/preview"),'equation preview endpoint'],
  [studio.includes("Michaelis-Menten saturation model"),'scientific model templates'],
  [studio.includes("parameter-values"),'parameter preview values'],
  [template.includes('data-ms-v0420-equation-validation'),'safe equation validation UI'],
  [template.includes('NO EVAL'),'explicit execution boundary'],
  [template.includes('data-ms-v0420-evaluated-rows'),'evaluated row inspection'],
  [plugin.includes("'scientific-visualization-engine-v0410','model-studio-v0420'"),'shared engine loads before v0.42 Model Studio']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
