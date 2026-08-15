'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const ui=read('assets/js/modules/presentation-runtime-v0482.js');
const plugin=read('includes/class-sc-lab-plugin.php');
const template=read('templates/lab-app.php');
const checks=[
 [ui.includes("VERSION='0.48.2'")&&ui.includes('PresentationRuntimeV0482'),'v0.48.2 browser runtime contract'],
 [ui.includes('new MutationObserver')===false,'no document-wide MutationObserver in v0.48.2 runtime'],
 [ui.includes("D.addEventListener('sc-lab:app-ready'")&&ui.includes('requestAnimationFrame'),'event-driven startup and coalesced rendering'],
 [ui.includes("if(node.textContent!==text)node.textContent=text"),'outer version synchronization is idempotent'],
 [ui.includes("app.dataset.activeModule!=='overview'")&&ui.includes('projectRendering')===false,'overview-only render guard present'],
 [plugin.includes("'presentation-runtime-v0482'")&&!plugin.includes("'presentation-repair-v0481','workflow"),'v0.48.2 runtime replaces v0.48.1 loaded script'],
 [template.includes('data-v0481-workspace-switcher')&&template.includes('GRAPH STUDIO / PROJECT FIGURE'),'v0.48.1 presentation preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three related application cards/links preserved']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
