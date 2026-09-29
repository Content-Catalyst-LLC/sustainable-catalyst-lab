(function(w){'use strict';
const NS='SCLabAblationStudyFrameworkV01415';
function rows(results){return Array.isArray(results?.variants)?results.variants:[];}
function baseline(results){return rows(results).find(v=>v.isBaseline===true)||null;}
function factorLabels(v){return Array.isArray(v?.factors)?v.factors.map(f=>`${f.action||'change'}:${f.component||'component'}`):[];}
function deltaRows(matrix){return Array.isArray(matrix?.rows)?matrix.rows:[];}
function contrastBadge(record){return record?.controlledContrast===true?'controlled contrast':'comparability warning';}
w[NS]={version:'0.141.5',rows,baseline,factorLabels,deltaRows,contrastBadge,workspaceExecutionAuthority:true,labExecutesTraining:false,causalEffectInferred:false,automaticRanking:false,automaticWinnerSelection:false,automaticModelPromotion:false,boundary:'Ablation deltas are descriptive controlled contrasts; Lab does not infer causality or select a winning model.'};
})(window);
