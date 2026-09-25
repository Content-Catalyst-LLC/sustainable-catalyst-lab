const fs=require('fs'),p=require('path');
const root=p.resolve(__dirname,'..');
const s=fs.readFileSync(p.join(root,'assets/js/modules/graph-studio-native-provenance-v013585.js'),'utf8');
function need(x,m){if(!x){console.error('FAIL - '+m);process.exit(1)}}
need(s.includes("VERSION='0.135.8.5.2'"),'version');
need(s.includes('function incremental('),'incremental update engine');
need(s.includes('function updateVisibility()'),'visibility updates');
need(s.includes('function updateLayout()'),'layout geometry updates');
need(!/function setRelation\([^)]*\)[^{]*\{[^}]*redraw\(\)/s.test(s),'relation does not full redraw');
need(!/function setLayout\([^)]*\)[^{]*\{[^}]*redraw\(\)/s.test(s),'layout does not full redraw');
console.log('PASS - v0.135.8.5.2 JS incremental interaction regression contract');
