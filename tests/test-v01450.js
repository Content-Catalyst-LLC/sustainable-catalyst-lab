const fs=require('fs'),vm=require('vm');
const ctx={window:{},document:{}};vm.createContext(ctx);
vm.runInContext(fs.readFileSync('assets/js/modules/simulation-computational-experiment-workspace-v01450.js','utf8'),ctx);
vm.runInContext(fs.readFileSync('assets/js/modules/project-workspace-simulation-v01450.js','utf8'),ctx);
const a=ctx.window.SCLabSimulationComputationalExperimentWorkspaceV01450,p=ctx.window.SCLabProjectWorkspaceSimulationV01450;
if(!a||a.version!=='0.145.0'||a.labExecutesSimulation!==false||a.verificationValidationSeparated!==true||a.modeledOutputIsEvidence!==false||a.automaticPreferredScenario!==false)throw new Error('v0.145.0 client contract failed');
const e=a.normalizeExperiment({experimentId:'e1',model:{simulationFamily:'ode'},scenarios:[{}],runs:[{}]}); if(e.model.simulationFamily!=='ode'||e.automaticScientificValidity!==false)throw new Error('normalization failed');
if(!p||p.viewModel(e).scientificValidityCertified!==false)throw new Error('project workspace failed');
console.log('PASS: Lab v0.145.0 JS contracts');
