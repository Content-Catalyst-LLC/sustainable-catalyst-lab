(function(w){'use strict';
const VERSION='0.126.0';
function cfg(){return w.SCLabSpatialSpatiotemporalResearchStudioV01260Config||{};}
async function getJSON(url){if(!url)throw new Error('Spatial Studio endpoint is not configured.');const r=await fetch(url,{credentials:'same-origin'});if(!r.ok)throw new Error('Spatial Studio request failed: '+r.status);return r.json();}
w.SCLabSpatialSpatiotemporalResearchStudioV01260={version:VERSION,health:()=>getJSON(cfg().healthUrl),manifest:()=>getJSON(cfg().manifestUrl),schema:()=>getJSON(cfg().schemaUrl),catalog:()=>getJSON(cfg().catalogUrl),boundaries:{automaticReprojection:false,automaticSpatialJoin:false,automaticCausalInterpretation:false,automaticSignificanceLabels:false}};
})(window);
