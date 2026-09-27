const fs=require('fs');
const code=fs.readFileSync('assets/js/modules/graph-studio-review-workspace-consolidation-v0135210.js','utf8');
for(const s of ["VERSION='0.135.21.0'",'graphStudioReviewWorkspaceCertifications','deterministicHydration:true','chromiumCertificationHarness:true', 'automaticScientificValidity:false','automaticPublicationAcceptance:false','fullGraphRedraw:false']){
  if(!code.includes(s))throw Error('missing contract token '+s);
}
if(!code.includes("a.dataset.gs135210Consolidated='1'"))throw Error('consolidation ownership marker missing');
console.log('PASS: v0.135.21.0 JS static contract');
