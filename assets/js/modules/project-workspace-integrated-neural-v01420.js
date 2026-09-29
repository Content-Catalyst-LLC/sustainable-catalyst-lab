(function(w,d){'use strict';
function api(){return w.SCLabIntegratedNeuralResearchWorkspaceV01420||null;}
function hydrate(state){const a=api();return a?a.normalizeSession(state):state||{};}
function selectPanel(state,panel){const a=api(),s=hydrate(state);if(a&&a.panels.some(p=>p.id===panel))s.activePanel=panel;return s;}
function selectObject(state,objectId){const s=hydrate(state);s.focusedObjectId=String(objectId||'');return s;}
function viewModel(state){const a=api(),s=hydrate(state);return {version:'0.142.0',session:s,panels:a?a.panels:[],counts:a?a.panelCounts(s):{},activePanel:s.activePanel,focusedObjectId:s.focusedObjectId,scientificValidityCertified:false};}
w.SCLabProjectWorkspaceIntegratedNeuralV01420={version:'0.142.0',hydrate:hydrate,selectPanel:selectPanel,selectObject:selectObject,viewModel:viewModel};
})(window,document);
