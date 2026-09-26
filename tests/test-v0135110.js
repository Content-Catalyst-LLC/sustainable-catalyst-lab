const fs=require('fs'); const s=fs.readFileSync('assets/js/modules/graph-studio-competing-paths-v0135110.js','utf8');
function assert(x,m){if(!x)throw new Error(m)}
for(const token of ["VERSION='0.135.11.0'",'enumeratePaths','Competing paths','declaredEvidenceContextOnly:true','fullGraphRedrawForPathSelection:false','truthRanking:false','causalInference:false']) assert(s.includes(token),token);
const ws=fs.readFileSync('assets/js/modules/project-workspace-path-comparison-v0135110.js','utf8'); assert(ws.includes('Graph Studio competing-path context'),'workspace context');
console.log('PASS - v0.135.11.0 JS contract');
