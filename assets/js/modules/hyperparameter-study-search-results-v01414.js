(function(w){'use strict';
const NS='SCLabHyperparameterStudySearchResultsV01414';
function esc(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function trialRows(results){return Array.isArray(results?.trials)?results.trials:[];}
function objectiveSeries(results,name){return trialRows(results).map(t=>({trialId:t.trialId,number:t.number,status:t.status,value:t.objectives?.[name]??null}));}
function parameterRows(results){const trials=trialRows(results),names=[...new Set(trials.flatMap(t=>Object.keys(t.parameters||{})))].sort();return {columns:names,rows:trials.map(t=>({trialId:t.trialId,status:t.status,values:Object.fromEntries(names.map(n=>[n,t.parameters?.[n]??null]))}))};}
function candidateBadge(record){return record?.candidateSetRequiresReview===true?'review candidate':'descriptive result';}
function renderStatus(target,audit){const el=typeof target==='string'?document.querySelector(target):target;if(!el)return null;const counts=audit?.counts||{};el.innerHTML='<div class="sc-lab-hps-status-v01414">'+Object.keys(counts).map(k=>`<span><strong>${esc(counts[k])}</strong> ${esc(k)}</span>`).join('')+'</div>';return el;}
w[NS]={version:'0.141.4',trialRows,objectiveSeries,parameterRows,candidateBadge,renderStatus,automaticWinnerSelection:false,automaticModelPromotion:false,workspaceExecutionAuthority:true,boundary:'Search results are descriptive research objects; Lab does not select or promote a winning model.'};
})(window);
