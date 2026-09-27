const fs=require('fs'),vm=require('vm');
const code=fs.readFileSync('assets/js/modules/graph-studio-review-closure-v0135200.js','utf8');
if(!code.includes("VERSION='0.135.20.0'"))throw Error('version missing');
if(!code.includes('graphStudioReviewClosurePackages'))throw Error('collection missing');
for(const s of ['automaticScientificValidity:false','automaticPublicationAcceptance:false','majorityVoting:false','consensusScoring:false','fullGraphRedraw:false'])if(!code.includes(s))throw Error('boundary missing '+s);
console.log('PASS: v0.135.20.0 JS static contract');
