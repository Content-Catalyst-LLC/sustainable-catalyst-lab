const fs=require('fs'),vm=require('vm');const ctx={window:{},document:{}};vm.createContext(ctx);
vm.runInContext(fs.readFileSync('assets/js/modules/graph-machine-learning-experiment-workspace-v01470.js','utf8'),ctx);
vm.runInContext(fs.readFileSync('assets/js/modules/project-workspace-graph-ml-v01470.js','utf8'),ctx);
const a=ctx.window.SCLabGraphMachineLearningExperimentWorkspaceV01470,p=ctx.window.SCLabProjectWorkspaceGraphMLV01470;
if(!a||a.version!=='0.147.0'||a.labExecutesGraphMLTraining!==false||a.candidatePredictionsRemainCandidates!==true||a.automaticRelationshipEstablishment!==false||a.automaticWinnerSelection!==false||a.predictionIsEvidence!==false)throw new Error('v0.147.0 client contract failed');
const s=a.normalizeStudy({task:{taskType:'link-prediction'},predictions:[{taskType:'link-prediction',sourceNodeRef:'a',targetNodeRef:'b',score:.9}]});if(s.predictions[0].candidateOnly!==true||s.predictions[0].relationshipEstablished!==false||s.predictions[0].evidenceEdgeCreated!==false)throw new Error('candidate link boundary failed');
if(!p||p.viewModel(s).predictionIsEvidence!==false)throw new Error('project workspace failed');console.log('PASS: Lab v0.147.0 JS contracts');
