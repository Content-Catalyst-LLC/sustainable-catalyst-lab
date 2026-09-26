const fs=require('fs');
function assert(x,m){if(!x)throw new Error(m)}
const s=fs.readFileSync('assets/js/modules/graph-studio-review-resolution-v0135130.js','utf8');
for(const token of ["VERSION='0.135.13.0'",'Review resolution','appendOnlyDecisionLineage:true','revisionActionsExplicit:true','fullGraphRedrawForResolution:false','annotationMutation:false','graphStudioReviewResolutions','scLabGraphStudioReviewResolutionV0135130']) assert(s.includes(token),token);
const ws=fs.readFileSync('assets/js/modules/project-workspace-review-resolution-v0135130.js','utf8');
assert(ws.includes('Graph Studio review resolution'),'workspace resolution context');
console.log('PASS - v0.135.13.0 JS contract');
