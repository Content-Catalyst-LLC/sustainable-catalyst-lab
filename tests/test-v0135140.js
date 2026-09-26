const fs=require('fs');function assert(x,m){if(!x)throw new Error(m)}
const s=fs.readFileSync('assets/js/modules/graph-studio-review-audit-v0135140.js','utf8');
for(const token of ["VERSION='0.135.14.0'",'Review audit','reviewStateMachine:true','actionVerification:true','appendOnlyResolutionAudit:true','explicitResolutionConfirmation:true','fullGraphRedrawForAudit:false','resolutionMutation:false','graphStudioReviewAudits','scLabGraphStudioReviewAuditV0135140'])assert(s.includes(token),token);
const ws=fs.readFileSync('assets/js/modules/project-workspace-review-audit-v0135140.js','utf8');assert(ws.includes('Graph Studio review audit'),'workspace audit context');console.log('PASS - v0.135.14.0 JS contract');
