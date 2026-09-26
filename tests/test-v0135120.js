const fs=require('fs');
function assert(x,m){if(!x)throw new Error(m)}
const s=fs.readFileSync('assets/js/modules/graph-studio-review-threads-v0135120.js','utf8');
for(const token of ["VERSION='0.135.12.0'",'Review thread','claimLinkageExplicitOnly:true','fullGraphRedrawForAnnotation:false','evidenceWeightInference:false','graphStudioReviewThreads','scLabGraphStudioReviewThreadV0135120']) assert(s.includes(token),token);
const ws=fs.readFileSync('assets/js/modules/project-workspace-review-thread-v0135120.js','utf8');
assert(ws.includes('Graph Studio provenance review thread'),'workspace review context');
console.log('PASS - v0.135.12.0 JS contract');
