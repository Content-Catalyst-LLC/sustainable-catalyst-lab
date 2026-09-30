const fs=require('fs');
const js=fs.readFileSync('assets/js/sc-lab-uncertainty-sensitivity-ensemble-v015210.js','utf8');
const safe=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015210.js','utf8');
const checks=[
 ['version',js.includes("0.152.0.10")],
 ['response surface retained',js.includes('simulation.parameter_sweep')&&js.includes('runSurface')],
 ['monte carlo',js.includes('uncertainty.monte_carlo_propagation')&&js.includes('runUncertainty')],
 ['local sensitivity',js.includes('sensitivity.local_finite_difference')&&js.includes('runSensitivity')],
 ['seed ensemble',js.includes('sc-lab-seed-replication-ensemble/1.0')&&js.includes('runEnsemble')],
 ['mc bound',js.includes('maxMonteCarloSamples')&&js.includes('50000')],
 ['ensemble bound',js.includes('maxEnsembleMembers')&&js.includes('7')],
 ['analysis plot',js.includes('data-v015210-analysis-canvas')&&js.includes('drawAnalysis')],
 ['explicit actions',js.includes('data-v015210-run-uncertainty')&&js.includes('data-v015210-run-sensitivity')&&js.includes('data-v015210-run-ensemble')],
 ['no MutationObserver',!js.includes('MutationObserver')],
 ['no interval polling',!js.includes('setInterval(')],
 ['safe no observer',!safe.includes('MutationObserver')],
 ['safe no interval',!safe.includes('setInterval(')]
];
for(const [label,ok] of checks){if(!ok){console.error('FAIL:',label);process.exit(1);}}
console.log('PASS - v0.152.0.10 uncertainty/sensitivity/ensemble JS contract');
