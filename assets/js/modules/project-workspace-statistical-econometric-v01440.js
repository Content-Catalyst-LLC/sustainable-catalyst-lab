(function(w,d){'use strict';
function api(){return w.SCLabStatisticalEconometricResearchWorkspaceV01440||null;}
function hydrate(state){const a=api();return a?a.normalizeSession(state):state||{};}
function selectAnalysis(state,analysis){const a=api(),s=hydrate(state);if(a&&a.analysisFamilies.includes(analysis))s.activeAnalysis=analysis;return s;}
function viewModel(state){const a=api(),s=hydrate(state);return {version:'0.144.0',session:s,analysisFamilies:a?a.analysisFamilies:[],activeAnalysis:s.activeAnalysis||'',estimandCount:(s.estimands||[]).length,specificationCount:(s.specifications||[]).length,estimateCount:(s.estimates||[]).length,explicitEstimandModelSeparation:true,automaticWinnerSelection:false,scientificValidityCertified:false};}
w.SCLabProjectWorkspaceStatisticalEconometricV01440={version:'0.144.0',hydrate:hydrate,selectAnalysis:selectAnalysis,viewModel:viewModel};
})(window,document);
