const fs=require('fs'),vm=require('vm');
const ctx={window:{},document:{}};vm.createContext(ctx);
vm.runInContext(fs.readFileSync('assets/js/modules/graph-network-science-research-workspace-v01460.js','utf8'),ctx);
vm.runInContext(fs.readFileSync('assets/js/modules/project-workspace-graph-network-v01460.js','utf8'),ctx);
const a=ctx.window.SCLabGraphNetworkScienceResearchWorkspaceV01460,p=ctx.window.SCLabProjectWorkspaceGraphNetworkV01460;
if(!a||a.version!=='0.146.0'||a.labExecutesLargeGraphAlgorithms!==false||a.explicitEdgeSemantics!==true||a.automaticRelationshipInference!==false||a.automaticCausalInference!==false||a.graphMetricIsEvidence!==false)throw new Error('v0.146.0 client contract failed');
const s=a.normalizeStudy({studyId:'s1',graph:{networkType:'directed',nodes:[{id:'a'}],edges:[{id:'e',source:'a',target:'b',semantics:'candidate'}]}});if(s.graph.networkType!=='directed'||s.graph.edges[0].candidateOnly!==true||s.automaticScientificValidity!==false)throw new Error('normalization failed');
if(!p||p.viewModel(s).graphMetricIsEvidence!==false)throw new Error('project workspace failed');
console.log('PASS: Lab v0.146.0 JS contracts');
