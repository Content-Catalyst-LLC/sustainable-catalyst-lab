const fs=require('fs');
const js=fs.readFileSync('assets/js/sc-lab-4d-front-door-v015207.js','utf8');
const safe=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015207.js','utf8');
const checks=[
 ['version',js.includes("0.152.0.7")],
 ['4d canvas',js.includes('[data-v0710-canvas]')],
 ['compute health',js.includes('computeHealthUrl')],
 ['compute capabilities',js.includes('computeCapabilitiesUrl')],
 ['compute run',js.includes('computeRunUrl')],
 ['parameter sweep',js.includes('simulation.parameter_sweep')],
 ['explicit compute button',js.includes('data-v015207-run-compute')],
 ['demo response',js.includes("response:")],
 ['demo uncertainty',js.includes("uncertainty:")],
 ['demo sensitivity',js.includes("sensitivity:")],
 ['demo ensemble',js.includes("ensemble:")],
 ['demo spatiotemporal',js.includes("spatiotemporal:")],
 ['PNG export',js.includes("toDataURL('image/png')")],
 ['JSON export',js.includes('sc-lab-4d-front-door-state/1.0')],
 ['no MutationObserver',!js.includes('MutationObserver')],
 ['no interval polling',!js.includes('setInterval(')],
 ['animation bounded to rAF',js.includes('requestAnimationFrame')],
 ['safe shell no observer',!safe.includes('MutationObserver')],
 ['safe shell no interval',!safe.includes('setInterval(')]
];
for(const [label,ok] of checks){if(!ok){console.error('FAIL:',label);process.exit(1);}}
console.log('PASS - v0.152.0.7 interactive 4D JS contract');
