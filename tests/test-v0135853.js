const fs=require('fs'); const s=fs.readFileSync('assets/js/modules/graph-studio-native-provenance-v013585.js','utf8');
function ok(x,m){if(!x) throw new Error(m)}
ok(s.includes("VERSION='0.135.8.5.3'"),'version');
ok(s.includes('function relationshipContext()'),'relationship context');
ok(s.includes('zeroMatchRelationshipState'),'zero match diagnostics');
ok(s.includes('impossibleRelationshipAutoReset:false'),'no auto reset');
ok(s.includes('data-gs135853-relation-state'),'explicit status');
ok(s.includes("selectedNode=id;S.selectedEdge=null;return incremental('node-selection',{controls:true"),'node updates context controls');
console.log('PASS - v0.135.8.5.3 JS context-aware relationship contract');
