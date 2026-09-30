const fs=require('fs');
const js=fs.readFileSync('assets/js/sc-lab-response-surface-parameter-explorer-v015209.js','utf8');
const safe=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015209.js','utf8');
const checks=[
 ['version',js.includes("0.152.0.9")],['method',js.includes('simulation.parameter_sweep')],['four models',js.includes('logistic_growth')&&js.includes('projectile_range')&&js.includes('photovoltaic_output')&&js.includes('michaelis_menten')],
 ['bounded X',js.includes('maxXSamples')],['bounded Y',js.includes('maxYLevels')],['bounded W',js.includes('maxWSlices')],['bounded requests',js.includes('requests>35')],['bounded evaluations',js.includes('evaluations>1435')],
 ['surface run',js.includes('runSurface')],['baseline',js.includes('baselineCompatible')],['saved configs',js.includes('localStorage')],['csv export',js.includes("type:'text/csv'")],['json export',js.includes('sc-lab-response-surface-export/1.0')],['png export',js.includes("toDataURL('image/png')")],
 ['no MutationObserver',!js.includes('MutationObserver')],['no interval polling',!js.includes('setInterval(')],['rAF animation',js.includes('requestAnimationFrame')],['safe no observer',!safe.includes('MutationObserver')],['safe no interval',!safe.includes('setInterval(')]
];
for(const [label,ok] of checks){if(!ok){console.error('FAIL:',label);process.exit(1);}}
console.log('PASS - v0.152.0.9 response-surface JS contract');
