const fs=require('fs'); const s=fs.readFileSync('assets/js/modules/graph-studio-object-explorer-v013590.js','utf8');
function ok(x,m){if(!x) throw new Error(m)}
ok(s.includes("VERSION='0.135.9.0'"),'version');
ok(s.includes("S.scope==='neighbors'?1:2"),'bounded neighborhoods');
ok(s.includes('data-gs13590-open-project'),'cross-workspace action');
ok(s.includes('data-gs13590-select'),'related object selection');
ok(s.includes('fullGraphRedrawForScope:false'),'incremental scope');
ok(!s.includes('new MutationObserver'),'no mutation observer');
console.log('PASS - v0.135.9.0 object explorer JS contract');
