const fs=require('fs');function assert(x,m){if(!x)throw new Error(m)}
const s=fs.readFileSync('assets/js/modules/graph-studio-revision-impact-v0135160.js','utf8');
for(const token of ["VERSION='0.135.16.0'",'Revision impact','graphStudioRevisionImpactAnalyses','potentiallyAffectedNodeIds','dependencyNodeIds','declaredDependenciesOnly:true','potentialImpactOnly:true','fullGraphRedrawForImpact:false','automaticScientificInvalidation:false','backwardCompatibleV0135150:true','scLabGraphStudioRevisionImpactV0135160'])assert(s.includes(token),token);
const ws=fs.readFileSync('assets/js/modules/project-workspace-revision-impact-v0135160.js','utf8');assert(ws.includes('Revision impact & scientific dependencies'),'workspace impact context');
console.log('PASS - v0.135.16.0 JS contract');
