const fs=require('fs');function assert(x,m){if(!x)throw new Error(m)}
const s=fs.readFileSync('assets/js/modules/graph-studio-verification-artifacts-v0135150.js','utf8');
for(const token of ["VERSION='0.135.15.0'",'Verification artifacts','graphStudioVerificationArtifactBundles','typedVerificationArtifacts:true','multiArtifactEvidenceBundles:true','auditEventBinding:true','sha256ArtifactFingerprints:true','backwardCompatibleV0135140:true','fullGraphRedrawForVerificationArtifacts:false','auditHistoryMutation:false','truthRanking:false','scLabGraphStudioVerificationArtifactsV0135150'])assert(s.includes(token),token);
const ws=fs.readFileSync('assets/js/modules/project-workspace-verification-artifacts-v0135150.js','utf8');assert(ws.includes('Graph Studio verification artifact bundles'),'workspace verification context');
console.log('PASS - v0.135.15.0 JS contract');
