
(function(w){'use strict';
const V='0.138.0';
function rows(program){return Array.isArray(program&&program.studies)?program.studies:[];}
function shared(program){const idx={};rows(program).forEach(s=>(s.nodes||[]).forEach(n=>{if(!n||!n.id)return;idx[n.id]=idx[n.id]||[];idx[n.id].push(s.studyId||s.id);}));return Object.entries(idx).filter(([,ids])=>new Set(ids).size>1).map(([objectId,ids])=>({objectId,studyIds:[...new Set(ids)].sort()}));}
w.SCLabResearchProgramIntelligenceV01380={version:V,studyCount:p=>rows(p).length,sharedObjectIndex:shared,boundary:'Program relationships and change propagation are descriptive; human scientific judgment remains required.'};
})(window);
