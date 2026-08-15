'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const handoff=read('assets/js/modules/shared-model-handoff-v0490.js');
const modelStudio=read('assets/js/modules/model-studio-v0460.js');
const css=read('assets/css/sc-lab-shared-model-handoff-v0490.css');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [handoff.includes("VERSION='0.49.0'")&&handoff.includes("MODEL_SCHEMA='sc-catalyst-computational-model/0.49.0'")&&handoff.includes("HANDOFF_SCHEMA='sc-catalyst-model-handoff/0.49.0'"),'v0.49.0 shared browser contract'],
 [handoff.includes("STORAGE_KEY='sc_catalyst_model_handoff_v0490'")&&handoff.includes("LEGACY_KEY='sc_workbench_handoff'"),'modern and legacy Workbench storage transports'],
 [handoff.includes("LEGACY_EVENT='sc:workbench-handoff'")&&handoff.includes("EVENT='sc:catalyst-model-handoff'"),'modern and legacy handoff events'],
 [handoff.includes('MutationObserver')===false,'v0.49.0 introduces no MutationObserver'],
 [handoff.includes("compute/core/model-handoff")&&handoff.includes("outbound/workbench")&&handoff.includes("inbound/workbench"),'governed backend validation is wired'],
 [handoff.includes("SCLabConfig?.routes?.workbench")&&handoff.includes("sc_model_handoff"),'Workbench deep link uses configured route'],
 [modelStudio.includes('function loadModel(model)')&&modelStudio.includes('loadModel,currentModel'),'Model Studio exposes governed inbound load adapter'],
 [template.includes('data-model-handoff-v0490')&&template.includes('Open model in Workbench')&&template.includes('Import pending Workbench model'),'dedicated model exchange UI rendered'],
 [template.includes('Equation</span>')&&template.includes('Parameters + bounds')&&template.includes('Initial conditions')&&template.includes('Provenance'),'preserved scientific fields are visible'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'v0.48.3 six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes("'shared-model-handoff-v0490'")&&plugin.includes('sc-lab-shared-model-handoff-v0490'),'v0.49.0 JS/CSS assets enqueued'],
 [css.includes('.sc-mh0490')&&css.includes('@media(max-width:760px)'),'model exchange UI has responsive styling']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
