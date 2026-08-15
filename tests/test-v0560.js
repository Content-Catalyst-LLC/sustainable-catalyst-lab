'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/advanced-experimental-design-v0560.js');
const py=read('backend/app/advanced_experimental_design.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const graph=read('assets/js/modules/graph-studio-v0470.js');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const checks=[
 [js.includes("VERSION='0.56.0'")&&js.includes('AdvancedExperimentalDesignV0560'),'v0.56 browser contract'],
 [py.includes('generate_optimal_design')&&py.includes('sequential_plan')&&py.includes('design_diagnostics'),'advanced design backend implemented'],
 [py.includes('d-optimal')&&py.includes('maximin'),'D-optimal and maximin criteria implemented'],
 [py.includes('information-gain')&&py.includes('response-guided'),'sequential strategies implemented'],
 [py.includes('automaticExecutionAuthorized')&&py.includes('automaticStoppingAuthorized'),'automatic execution and stopping disabled in records'],
 [py.includes('designHash')&&py.includes('planHash')&&py.includes('specHash'),'reproducible design lineage hashes implemented'],
 [template.includes('data-advanced-design-v0560')&&template.includes('Advanced experimental design &amp; sequential experimentation'),'v0.56 remains contextual inside Design Studies'],
 [template.includes('data-doe-v0560-generate')&&template.includes('data-doe-v0560-sequential'),'initial and sequential controls rendered'],
 [js.includes('analysisPackets')&&pkg.includes("'analysisPackets'"),'v0.50 reproducible package path receives experimental-design evidence'],
 [js.includes('sc-lab:open-graph-studio')&&graph.includes('openHandoff'),'advanced design evidence hands off to Graph Studio'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-advanced-experimental-design-v0560')&&plugin.includes("'advanced-experimental-design-v0560'"),'v0.56 assets registered'],
 [compute.includes('/compute/core/design-studies/v0560/optimal-design')&&compute.includes('/compute/core/design-studies/v0560/sequential-plan'),'WordPress v0.56 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.56 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
