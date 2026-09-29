(function(w){'use strict';
const NS='SCLabModelComparisonMatrixV01413';
function esc(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function normalizeRows(matrix){return Array.isArray(matrix?.rows)?matrix.rows:[];}
function columns(matrix){if(Array.isArray(matrix?.columns)&&matrix.columns.every(x=>typeof x==='string'))return matrix.columns;const rows=normalizeRows(matrix);return rows.length?Object.keys(rows[0]).filter(k=>k!=='values'&&k!=='deltas'):[];}
function renderTable(target,matrix){const el=typeof target==='string'?document.querySelector(target):target;if(!el)return null;const rows=normalizeRows(matrix),cols=columns(matrix);let h='<div class="sc-lab-comparison-scroll-v01413"><table class="sc-lab-comparison-matrix-v01413"><thead><tr>'+cols.map(c=>`<th>${esc(c)}</th>`).join('')+'</tr></thead><tbody>';h+=rows.map(r=>'<tr>'+cols.map(c=>`<td>${esc(r[c])}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>';el.innerHTML=h;return el.querySelector('table');}
function comparabilityBadges(pair){const d=pair?.dimensions||{};return Object.keys(d).map(k=>({dimension:k,state:d[k].unknown?'unknown':(d[k].same?'same':'different')}));}
function sortRows(rows,key,dir){const a=[...(rows||[])],m=dir==='desc'?-1:1;return a.sort((x,y)=>String(x?.[key]??'').localeCompare(String(y?.[key]??''))*m);}
w[NS]={version:'0.141.3',renderTable,comparabilityBadges,sortRows,boundary:'Matrix order and metric differences do not rank, endorse, or promote models.'};
})(window);
