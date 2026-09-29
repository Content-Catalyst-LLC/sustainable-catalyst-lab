const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync('assets/js/modules/reproducible-neural-research-package-v01418.js','utf8');
const ctx={window:{}};vm.createContext(ctx);vm.runInContext(src,ctx);
const x=ctx.window.SCLabReproducibleNeuralResearchPackageV01418;
if(!x||x.version!=='0.141.8') throw new Error('version');
for(const k of ['workspaceExecutionAuthority','platformCoreCanonicalAuthority']) if(x[k]!==true) throw new Error(k);
for(const k of ['labExecutesTraining','labExecutesReproduction','automaticScientificValidity','automaticReproductionCertification','automaticReplicationCertification','packageCompletenessIsScientificValidity','packageCompletenessIsReproduction','packageCompletenessIsReplication','predictionIsEvidence']) if(x[k]!==false) throw new Error(k);
if(x.sectionCount({components:[{section:'embeddings'},{section:'embeddings'}]},'embeddings')!==2) throw new Error('sectionCount');
console.log('PASS: Lab v0.141.8 JS contracts');
