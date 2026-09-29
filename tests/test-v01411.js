const fs=require('fs');
const js=fs.readFileSync('assets/js/modules/neural-architecture-training-configuration-v01411.js','utf8');
if(!js.includes("VERSION='0.141.1'")) throw new Error('v0.141.1 JS version missing');
if(!js.includes('labExecutesTraining=false')) throw new Error('Workspace execution boundary missing');
if(!js.includes('predictions are not evidence')) throw new Error('prediction/evidence boundary missing');
console.log('PASS: Lab v0.141.1 JS contracts');
