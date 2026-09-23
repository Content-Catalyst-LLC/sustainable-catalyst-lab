(function(w){'use strict';
const VERSION='0.127.0';
function cfg(){return w.SCLabScientificTimeSeriesLaboratoryV01270Config||{};}
async function getJSON(url){if(!url)throw new Error('Time-Series Laboratory endpoint is not configured.');const r=await fetch(url,{credentials:'same-origin'});if(!r.ok)throw new Error('Time-Series Laboratory request failed: '+r.status);return r.json();}
w.SCLabScientificTimeSeriesLaboratoryV01270={version:VERSION,health:()=>getJSON(cfg().healthUrl),manifest:()=>getJSON(cfg().manifestUrl),schema:()=>getJSON(cfg().schemaUrl),catalog:()=>getJSON(cfg().catalogUrl),boundaries:{automaticFrequencyInference:false,automaticModelSelection:false,automaticStationarityDecision:false,automaticCausalInterpretation:false}};
})(window);
