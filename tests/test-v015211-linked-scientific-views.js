const fs=require('fs');
const js=fs.readFileSync('assets/js/sc-lab-linked-scientific-views-v015211.js','utf8');
const safe=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015211.js','utf8');
const checks=[
 ['version',js.includes("0.152.0.11")],
 ['response surface retained',js.includes('simulation.parameter_sweep')&&js.includes('runSurface')],
 ['uncertainty retained',js.includes('uncertainty.monte_carlo_propagation')&&js.includes('runUncertainty')],
 ['sensitivity retained',js.includes('sensitivity.local_finite_difference')&&js.includes('runSensitivity')],
 ['ensemble retained',js.includes('sc-lab-seed-replication-ensemble/1.0')&&js.includes('runEnsemble')],
 ['shared selection schema',js.includes('sc-lab-linked-selection/1.0')],
 ['shared event',js.includes('sc-lab:linked-selection')],
 ['surface selection',js.includes('surfaceSelection')&&js.includes('4d-response-surface')],
 ['analysis selection',js.includes('analysisSelection')&&js.includes('uncertainty-diagnostic')&&js.includes('sensitivity-diagnostic')&&js.includes('ensemble-diagnostic')],
 ['parameter snapshot',js.includes('parameterRows')&&js.includes('data-v015211-table')],
 ['history',js.includes('selectionHistoryLimit')&&js.includes('restoreHistorySelection')],
 ['pins',js.includes('pinSelection')&&js.includes('pinLimit')],
 ['graph handoff',js.includes('sc-lab-graph-studio-selection-handoff/1.0')&&js.includes('sessionStorage')&&js.includes('graphStudioHandoff')],
 ['selection export',js.includes('sc-lab-linked-selection-export/1.0')],
 ['selection marker',js.includes('drawLinkedSurfaceSelection')&&js.includes('drawLinkedAnalysisSelection')],
 ['no MutationObserver',!js.includes('MutationObserver')],
 ['no interval polling',!js.includes('setInterval(')],
 ['safe no observer',!safe.includes('MutationObserver')],
 ['safe no interval',!safe.includes('setInterval(')]
];
for(const [label,ok] of checks){if(!ok){console.error('FAIL:',label);process.exit(1);}}
console.log('PASS - v0.152.0.11 linked scientific views JS contract');
