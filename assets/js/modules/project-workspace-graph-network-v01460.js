(function(w,d){'use strict';
function api(){return w.SCLabGraphNetworkScienceResearchWorkspaceV01460||null;}
function hydrate(state){const a=api();return a?a.normalizeStudy(state):state||{};}
function selectPanel(state,panel){const s=hydrate(state);s.activePanel=String(panel||'structure');return s;}
function viewModel(state){const s=hydrate(state),g=s.graph||{};return {version:'0.146.0',study:s,activePanel:s.activePanel||'structure',nodeCount:g.nodeCount||0,edgeCount:g.edgeCount||0,networkType:g.networkType||'simple',explicitEdgeSemantics:true,automaticRelationshipInference:false,automaticCausalInference:false,graphMetricIsEvidence:false,scientificValidityCertified:false};}
w.SCLabProjectWorkspaceGraphNetworkV01460={version:'0.146.0',hydrate:hydrate,selectPanel:selectPanel,viewModel:viewModel};
})(window,document);
