const fs=require('fs');
const js=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015206.js','utf8');
const required=[
  '0.152.0.6',
  '.sc-lab-frame__version strong',
  'labReleaseVersion',
  '.sc-lab-production-banner-v0266',
  'sc-lab-production-over-budget-v0266',
  '[data-lab-module]',
  '[data-lab-module-button]',
  'sc-lab:safe-module-opened'
];
for(const marker of required){if(!js.includes(marker)){console.error('missing',marker);process.exit(1);}}
for(const forbidden of ['MutationObserver','setInterval(','requestAnimationFrame(','sc-lab-optional-modules-v015204.js','presentation-repair-v0481.js']){
  if(js.includes(forbidden)){console.error('forbidden',forbidden);process.exit(2);}
}
console.log('PASS - v0.152.0.6 bounded stabilization bootstrap contract');
