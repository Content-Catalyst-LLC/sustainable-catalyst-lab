(function(w,d){'use strict';
function api(){return w.SCLabComputationalLinguisticsResearchWorkspaceV01430||null;}
function hydrate(state){const a=api();return a?a.normalizeSession(state):state||{};}
function selectAnalysis(state,analysis){const a=api(),s=hydrate(state);if(a&&a.analyses.includes(analysis))s.activeAnalysis=analysis;return s;}
function viewModel(state){const a=api(),s=hydrate(state),c=s.corpus||{};return {version:'0.143.0',session:s,analysisFamilies:a?a.analyses:[],activeAnalysis:s.activeAnalysis,textCount:(c.texts||[]).length,representationCount:(c.representations||[]).length,originalLanguageFirst:true,scientificValidityCertified:false};}
w.SCLabProjectWorkspaceComputationalLinguisticsV01430={version:'0.143.0',hydrate:hydrate,selectAnalysis:selectAnalysis,viewModel:viewModel};
})(window,document);
