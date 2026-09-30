const fs=require('fs');
const js=fs.readFileSync('assets/js/sc-lab-safe-bootstrap-v015205.js','utf8');
const required=['0.152.0.5','[data-lab-module]','[data-lab-module-button]','[data-open-module]','sc-lab:safe-module-opened'];
for(const marker of required){if(!js.includes(marker)){console.error('missing',marker);process.exit(1);}}
for(const forbidden of ['MutationObserver','setInterval(','requestAnimationFrame(','sc-lab-optional-modules-v015204.js']){
  if(js.includes(forbidden)){console.error('forbidden',forbidden);process.exit(2);}
}
console.log('PASS - v0.152.0.5 bounded safe bootstrap contract');
