(function(w){'use strict';
const Lab=w.SCLab=w.SCLab||{};
const defaultBoard=[['usgs-earthquakes','',4],['nasa-eonet','',4],['nasa-space-telescopes','James Webb Hubble Chandra',4],['obis-marine','Cetacea',4],['pubmed-science','environmental monitoring materials biology chemistry',4],['arxiv-physics','all:physics OR all:materials OR all:engineering',4]];
async function loadBoard(requests=defaultBoard){const results=await Promise.allSettled(requests.map(args=>Lab.Feeds.load(...args)));return results.flatMap((r,i)=>r.status==='fulfilled'?(r.value.records||[]).map(x=>({...x,connectorId:requests[i][0]})):[]).sort((a,b)=>String(b.observedAt||'').localeCompare(String(a.observedAt||'')));}
function taxonSummary(records){const counts={};(records||[]).forEach(r=>{const name=r.taxonomy?.scientificName||r.title||'Unknown';const key=String(name).split(' ').slice(0,2).join(' ');counts[key]=(counts[key]||0)+1;});return Object.entries(counts).sort((a,b)=>b[1]-a[1]);}
function depthSeries(records){return (records||[]).map((r,i)=>({index:i+1,depth:Number(r.location?.depthM??r.metrics?.depthM)})).filter(x=>Number.isFinite(x.depth));}
function telescope(record){const text=`${record.title||''} ${(record.keywords||[]).join(' ')}`.toLowerCase();if(text.includes('webb')||text.includes('jwst'))return 'JWST';if(text.includes('hubble'))return 'Hubble';if(text.includes('chandra'))return 'Chandra';if(text.includes('spitzer'))return 'Spitzer';return 'Other';}
Lab.Observations={defaultBoard,loadBoard,taxonSummary,depthSeries,telescope};
})(window);
