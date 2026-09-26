const fs=require('fs'),assert=require('assert');
const p='assets/js/modules/graph-studio-path-analysis-v0135100.js',s=fs.readFileSync(p,'utf8');
for(const token of ['VERSION=\'0.135.10.0\'','shortestPath','Set A from selected','Set B from selected','Directed lineage','Structural path','Open research context','declaredRelationshipsOnly:true','fullGraphRedrawForPath:false']) assert(s.includes(token),token);
assert(!s.includes('MutationObserver'));
console.log('PASS - v0.135.10.0 JS contract');
