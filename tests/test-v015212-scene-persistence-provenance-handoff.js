const fs=require('fs');
const linked=fs.readFileSync('assets/js/sc-lab-linked-scientific-views-v015212.js','utf8');
const persist=fs.readFileSync('assets/js/sc-lab-scene-persistence-provenance-handoff-v015212.js','utf8');
const safe=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015212.js','utf8');
const checks=[
 ['version linked',linked.includes("0.152.0.12")],
 ['linked selection retained',linked.includes('sc-lab-linked-selection/1.0')],
 ['response surface retained',linked.includes('simulation.parameter_sweep')&&linked.includes('runSurface')],
 ['uncertainty retained',linked.includes('uncertainty.monte_carlo_propagation')],
 ['sensitivity retained',linked.includes('sensitivity.local_finite_difference')],
 ['scene snapshot',linked.includes('function sceneSnapshot')&&linked.includes("sc-lab-4d-scene-state/1.0")],
 ['scene restore',linked.includes('function restoreScene')&&linked.includes('restoringScene')===false],
 ['runtime exposes snapshot',linked.includes('sceneSnapshot:sceneSnapshot')],
 ['runtime exposes restore',linked.includes('restoreScene:restoreScene')],
 ['persistence schema',persist.includes("sc-lab-persisted-4d-scene/1.0")],
 ['provenance schema',persist.includes("sc-lab-4d-scene-provenance/1.0")],
 ['handoff schema',persist.includes("sc-lab-research-object-handoff/1.0")],
 ['canonical research object',persist.includes("sc-lab-canonical-research-object/0.105.0")],
 ['workspace snapshot',persist.includes("objectType:'workspace-snapshot'")],
 ['browser local persistence',persist.includes('localStorage')&&persist.includes('maxScenes')],
 ['session handoff',persist.includes('sessionStorage')&&persist.includes('sc-lab:research-object-handoff')],
 ['SHA-256 digest',persist.includes("digest('SHA-256'")],
 ['explicit no core submission boundary',persist.includes('automaticCoreSubmission:false')],
 ['no MutationObserver linked',!linked.includes('MutationObserver')],
 ['no interval polling linked',!linked.includes('setInterval(')],
 ['no MutationObserver persistence',!persist.includes('MutationObserver')],
 ['no interval polling persistence',!persist.includes('setInterval(')],
 ['safe no observer',!safe.includes('MutationObserver')],
 ['safe no interval',!safe.includes('setInterval(')]
];
for(const [label,ok] of checks){if(!ok){console.error('FAIL:',label);process.exit(1);}}
console.log('PASS - v0.152.0.12 scene persistence, provenance, and research-object handoff JS contract');
