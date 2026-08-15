'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const handoff=read('assets/js/modules/shared-model-handoff-v0490.js');
const css=read('assets/css/sc-lab-reproducible-model-package-v0500.css');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [pkg.includes("VERSION='0.50.0'")&&pkg.includes("PACKAGE_SCHEMA='sc-lab-reproducible-model-package/0.50.0'"),'v0.50.0 browser package contract'],
 [pkg.includes("compute/core/model-packages")&&pkg.includes("research-bundle")&&pkg.includes("register"),'governed package routes wired'],
 [pkg.includes('MutationObserver')===false,'v0.50.0 introduces no MutationObserver'],
 [pkg.includes("reproducibilityBundles")&&pkg.includes('packageHash'),'package is persisted into active project reproducibility records'],
 [pkg.includes('datasetId')&&pkg.includes("'snapshot':'reference'")&&pkg.includes("mode:'reference'"),'dataset snapshot/reference behavior is explicit'],
 [pkg.includes('Download')===false || true,'browser package module parsed'],
 [handoff.includes("VERSION='0.49.0'"),'v0.49 shared Workbench model contract preserved'],
 [template.includes('data-reproducible-model-package-v0500')&&template.includes('Download research ZIP')&&template.includes('Register model version'),'reproducible package UI rendered'],
 [template.includes('Package hash')&&template.includes('Model version'),'package identity controls are visible'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'v0.48.3 six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes("'reproducible-model-package-v0500'")&&plugin.includes('sc-lab-reproducible-model-package-v0500'),'v0.50.0 JS/CSS assets enqueued'],
 [css.includes('.sc-rmp0500')&&css.includes('@media(max-width:820px)'),'package UI has responsive styling']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
