'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/dynamic-systems-v0540.js');
const py=read('backend/app/dynamic_systems_v0540.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const graph=read('assets/js/modules/graph-studio-v0470.js');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const checks=[
 [js.includes("VERSION='0.54.0'")&&js.includes('DynamicSystemsV0540'),'v0.54 Dynamic Systems II browser contract'],
 [js.includes('dynamic-systems/v0540/')&&js.includes("api('bifurcation'")&&js.includes("api('phase'"),'v0.54 governed compute routes used'],
 [py.includes('_normalize_events')&&py.includes('_event_functions')&&py.includes('terminal'),'safe ODE event detection implemented'],
 [py.includes('_normalize_regimes')&&py.includes('parameterValues')&&py.includes('stateValues'),'scheduled regime changes implemented'],
 [py.includes('bifurcation_scan')&&py.includes('transientFraction')&&py.includes('formal bifurcation proof'),'bounded numerical bifurcation evidence implemented'],
 [py.includes('phase_analysis')&&py.includes('_classify_eigenvalues')&&py.includes('nullcline'),'advanced phase/equilibrium analysis implemented'],
 [py.includes('arbitraryCode')&&py.includes('formalBifurcationProof')&&py.includes('automaticRegimeInference'),'dynamic-system governance boundaries explicit'],
 [template.includes('data-ds-v0540-root')&&template.includes('Dynamic Systems II'),'v0.54 remains contextual inside Model Studio'],
 [template.includes('data-ds-v0540-events')&&template.includes('data-ds-v0540-regimes'),'events and regimes controls rendered'],
 [template.includes('data-ds-v0540-bifurcation')&&template.includes('data-ds-v0540-phase'),'bifurcation and phase controls rendered'],
 [js.includes('sc-lab:open-graph-studio')&&graph.includes('openHandoff'),'Dynamic Systems II figures hand off to Graph Studio'],
 [pkg.includes("'analysisPackets'")&&js.includes('dynamic-systems-v0540'),'v0.50 reproducible package path receives v0.54 evidence'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-dynamic-systems-v0540'),'v0.54 stylesheet/module registered'],
 [compute.includes('/compute/core/model-studio/dynamic-systems/v0540/simulate')&&compute.includes('/bifurcation')&&compute.includes('/phase'),'WordPress v0.54 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.54 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
